
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from utils import ChoicesEnum

from game.models.message import GameMessage


class Character(models.Model):
    """
    A Character represents a persona being played by a real world Player.

    Characters may have different abilities and objectives in each game, and
    hold the gameplay properties related to their persona.
    """
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='characters')
    player = models.ForeignKey(User, on_delete=models.CASCADE)

    persona = models.ForeignKey('Persona', on_delete=models.CASCADE)
    abilities = models.ManyToManyField('Ability', through='CharacterAbility')
    objectives = models.ManyToManyField('Objective', through='CharacterObjective')

    alive = models.BooleanField(default=True)
    turns_to_die = models.IntegerField(blank=True, null=True)
    current_room = models.ForeignKey('GameRoom', blank=True, null=True, on_delete=models.PROTECT,
                                     related_name='players_here')
    hidden = models.BooleanField(default=False)

    weapons = models.ManyToManyField('Weapon', through='CharacterWeapon')

    def __str__(self):
        return "{} as {} on {}".format(self.player, self.persona.title, self.game)

    def post_message(self, msg):
        current_stage = {'current_day': self.game.current_day}
        if self.game.current_day is None:
            current_stage = {'current_night': self.game.current_night}

        return GameMessage.objects.create(character=self,
                                          current_room=self.current_room,
                                          message=msg,
                                          **current_stage)

    def available_actions(self):  # TODO
        """
        Returns all available action that the character may execute at this point.
        """
        # TODO
        # Only considering night actions for now
        if not self.game.current_night:
            return []

        if self.game.current_night.is_new():
            return ['initial_move']

        character_actions = ['ability.{}'.format(self.abilities.phase_night())]
        room_actions = ['room.{}'.format(self.current_room.get_actions())]

        return character_actions + room_actions

    def _action_initial_move(self, *args, room=None):
        return self._action_move(*args, room=room)

    def _action_move(self, *args, room=None):
        return CharacterAction.objects.create(
            character=self,
            night=self.game.current_night,
            action=CharacterActions.MOVE,
            room_target=room,
            confirmed=True,
        )

    def _action_atack_kill(self, *args, character=None):
        pass

    def hide(self):
        self.hidden = True
        return self.save(update_fields=('hidden', ))


class CharacterActions(ChoicesEnum):
    """
    All the actions a player may execute during a night's turn.
    Special actions depend on each character.
    """
    MOVE = 'move'
    ATTACK_KILL = 'attack_kill'
    ATTACK_DEFEND = 'attack_defend'
    ATTACK_BLANK = 'attack_blank'
    PICK_WEAPON = 'pick_weapon'
    SPECIAL = 'special'
    CLOSE_DOOR = 'close_door'
    OPEN_DOOR = 'open_door'


class CharacterActionManager(models.Manager):

    def confirmed(self):
        return self.filter(confirmed=True)

    def pending(self):
        return self.filter(confirmed=False)


class CharacterAction(models.Model):
    """
    An action executed by a character in a specific turn. The available actions
    are defined by `CharacterActions`, and described by a combination of targets:
        player: attacked player
        room: attack location, movement destination
        weapon: attack weapon, collected weapon

    Some actions need confirmation.
    """
    night = models.ForeignKey('Night', related_name='actions', on_delete=models.CASCADE)
    character = models.ForeignKey('Character', related_name='night_turns', on_delete=models.PROTECT)
    action = models.CharField(max_length=32, choices=CharacterActions.choices())
    confirmed = models.BooleanField(default=False)
    character_target = models.ForeignKey('Character', null=True, on_delete=models.PROTECT)
    room_target = models.ForeignKey('GameRoom', null=True, on_delete=models.PROTECT)
    weapon_target = models.ForeignKey('Weapon', null=True, on_delete=models.PROTECT)

    objects = CharacterActionManager


@receiver(post_save, sender=CharacterAction)
def check_night_is_complete(sender, instance, *args, **kwargs):
    """
    Checks if this is the last confirmed action of the night,
    and advances the game in that case. Decreases the turns left otherwise.
    """
    action_count = instance.night.actions.confirmed().count()
    characters_count = instance.night.game.characters.all().count()

    if action_count == characters_count:
        if instance.night.turns_left > 0:
            return instance.night.game.next_stage()
        instance.night.turns_left -= 1
        return instance.night.save(update_fields=('turns_left', ))


class Terror(models.Model):
    """
    A terror.

    One or more ghosts (dead players) may terrorize a living player when found
    alone in the same room. Terrors score points for dead players, thus keeping
    them in play after they're killed or executed.
    """
    ghost = models.ForeignKey('Character', related_name='terrorizations', on_delete=models.CASCADE)
    terrorized = models.ForeignKey('Character', related_name='terrors', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)


class Kill(models.Model):
    """
    An assesination in the game.
    """
    killer = models.ForeignKey('Character', related_name='kills', on_delete=models.CASCADE)
    killed = models.ForeignKey('Character', related_name='deaths', on_delete=models.CASCADE)
    room = models.ForeignKey('GameRoom', related_name='killings', on_delete=models.PROTECT)
    weapon = models.ForeignKey('CharacterWeapon', on_delete=models.PROTECT)

    class Meta:
        unique_together = (('killer', 'killed'), )
