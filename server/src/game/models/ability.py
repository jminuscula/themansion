
from django.db import models
from django.db.models import Q

from utils import ChoicesEnum
from functools import wraps

from game.models.character import Character
from game.models.weapon import Weapon, CharacterWeapon
from game.models.room import GameRoom
from game.exceptions import AbilityError


class AbilityActionPhase(ChoicesEnum):
    """
    Moments when a character's ability may be triggered.

    Abilities may perform additional availability checks, such as checking for
    a specifc room, or limiting the number of uses.
    """
    STARTGAME = 'startgame'
    ROOM = 'room'
    DAY = 'day'
    NIGHT = 'night'
    VOTING = 'voting'


class Ability(models.Model):
    """
    A character's special ability.
    """
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=512)
    room = models.ManyToManyField('Room', blank=True)
    action_phase = models.CharField(max_length=16,
                                    null=True,
                                    choices=AbilityActionPhase.choices())

    class Meta:
        verbose_name_plural = 'abilities'

    def __str__(self):
        return self.name


class CharacterAbilityObjectManager(models.Manager):

    def available(self, *args, **kwargs):
        return self.filter(available=True)

    def phase_start(self, *args, **kwargs):
        return self.filter(ability__action_phase=AbilityActionPhase.STARTGAME)

    def phase_room(self, *args, **kwargs):
        return self.filter(ability__action_phase=AbilityActionPhase.ROOM)

    def phase_night(self, *args, **kwargs):
        night_q = (Q(ability__action_phase=AbilityActionPhase.ROOM) |
                   Q(ability__action_phase=AbilityActionPhase.NIGHT))
        return self.filter(night_q)


class CharacterAbility(models.Model):
    """
    Game character's ability.

    This class serves as a dispatcher for ability functions. It also tracks
    usage limit, availability, etc.
    """
    character = models.ForeignKey('Character')
    ability = models.ForeignKey('Ability')
    available = models.BooleanField(default=True)

    objects = CharacterAbilityObjectManager()

    class Meta:
        unique_together = (('character', 'ability'), )
        verbose_name_plural = 'character abilities'

    def __str__(self):
        return "{} for {}".format(self.ability.name, self.character)

    def get_ability_fn(self):
        """
        get this ability's specific method
        """
        ability_fn_name = '_ability_{}'.format(self.ability.name)
        ability_fn_name = ability_fn_name.replace(' ', '_')
        ability_fn_name = ability_fn_name.lower()

        return getattr(self, ability_fn_name)

    def run(self, *args, **kwargs):
        """
        executes this ability's specific method
        """
        ability_fn = self.get_ability_fn()
        if ability_fn is None:
            raise ValueError('ability "{}" can not be executed'.format(self.ability.name))

        return ability_fn(self, *args, **kwargs)

    def disable_after_run(fn):
        @wraps(fn)
        def disabling(self, *args, **kwargs):
            ret = fn(*args, **kwargs)
            self.available = False
            self.save()
            return ret
        return disabling

    @disable_after_run
    def _ability_family_privilege(self, *args, **kwargs):
        """
        The Host and The Undertaker have their identities revealed between them
        """
        the_undertaker = Character.objects.get(game=self.character.game, persona__title='The Undertaker')
        the_host = Character.objects.get(game=self.character.game, persona__title='The Host')

        the_undertaker.post_message(
            'As The Undertaker, you know The Host is {}'.format(the_host.player.username)
        )

        the_host.post_message(
            'As The Host, you know The Undertaker is {}'.format(the_undertaker.player.username)
        )

    @disable_after_run
    def _ability_cutting_edge(self, *args, **kwargs):
        """
        The character gets a knife
        """
        try:
            knife = Weapon.objects.get(name='Knife')
        except Weapon.DoesNotExist:
            raise AbilityError('Knife is not available in this game')

        return CharacterWeapon.objects.create(character=self.character, weapon=knife)

    def _ability_stealth(self, *args, **kwargs):
        """
        The character hides
        """
        self.character.hide()


    def _ability_reload(self, *args, **kwargs):
        """
        The character reloads 2 Bullets
        """
        try:
            gun = CharacterWeapon.objects.get(character=self.character, weapon__name="Gun")
        except CharacterWeapon.DoesNotExist:
            raise AbilityError('Character does not have a gun')

        gun.ammo = 2
        return gun.save()

    def _ability_gatekeeper(self, *args, room=None):
        """
        The character closes a door
        """
        current = self.character.current_room
        reachable_q = Q(pk=current.pk) | Q(room__pk__in=current.room.connections.all())
        open_rooms = GameRoom.objects.open().filter(reachable_q, room__closeable=True)

        if room not in open_rooms:
            raise AbilityError('Room is closed, not closable, or out of reach')

        return room.close()
