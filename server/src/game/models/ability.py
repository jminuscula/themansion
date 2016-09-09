
from django.db import models

from utils import ChoicesEnum
from functools import wraps

from game.models.character import Character
from game.models.weapon import Weapon, CharacterWeapon


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

    def phase_start(self, *args, **kwargs):
        return self.filter(available=True, ability__action_phase=AbilityActionPhase.STARTGAME)


class CharacterAbility(models.Model):
    """
    Game character's ability tracking.

    Checks for usage limit, availability, etc.
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

    def run(self, *args, **kwargs):
        """
        executes this ability's specific method
        """
        ability_fn_name = '_ability_{}'.format(self.ability.name)
        ability_fn_name = ability_fn_name.replace(' ', '_')
        ability_fn_name = ability_fn_name.lower()

        ability_fn = getattr(self, ability_fn_name)
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
    def _ability_family_privilege(self, *args, game=None):
        """
        The Host and The Undertaker have their identities revealed between them
        """
        the_undertaker = Character.objects.get(game=game, persona__title='The Undertaker')
        the_host = Character.objects.get(game=game, persona__title='The Host')

        the_undertaker.post_message(
            'As The Undertaker, you know The Host is {}'.format(the_host.player.username)
        )

        the_host.post_message(
            'As The Host, you know The Undertaker is {}'.format(the_undertaker.player.username)
        )

    @disable_after_run
    def _ability_cutting_edge(self, *args, game=None):
        """
        The character gets a knife
        """
        knife = Weapon.objects.get(name='Knife')
        CharacterWeapon.objects.create(character=self.character, weapon=knife)
