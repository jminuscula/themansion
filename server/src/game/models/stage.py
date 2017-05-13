
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from utils import ChoicesEnum
from mansion import settings


class Night(models.Model):
    """
    A night phase of a game.

    A game has `GAME_NUMBER_NIGHTS` number of nights. During a Night phase,
    there must be `GAME_NIGHT_TURNS` number of NightTurns.
    """
    game = models.ForeignKey('game', on_delete=models.CASCADE, related_name='nights')
    number = models.IntegerField(default=0)
    current_turn = models.ForeignKey('NightTurn', null=True, blank=True, on_delete=models.CASCADE,
                                      related_name='current_turn')

    def __str__(self):
        return "Night {} in game {}".format(self.number, self.game)

    def turn_count(self):
        return self.night_turns.count()

    def is_new(self):
        return self.turn_count() == 0

    def next_turn(self):
        turn_count = self.turn_count() + 1
        if turn_count > settings.GAME_NIGHT_TURNS:
            return self.game.next_stage()

        self.current_turn = NightTurn.objects.create(night=self, number=turn_count)
        return self.save()

@receiver(post_save, sender=Night)
def start_new_night(sender, instance, *args, **kwargs):
    """
    If the night is new, start it
    """
    if instance.is_new():
        return instance.next_turn()


class NightTurn(models.Model):
    """
    A turn in a specific night of a specific game
    """
    night = models.ForeignKey('Night', related_name='night_turns', on_delete=models.CASCADE)
    number = models.IntegerField(default=0)

    def __str__(self):
        return "Turn {} in {}".format(self.number, self.night)

class NightActions(ChoicesEnum):
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


class NightActionManager(models.Manager):

    def confirmed(self):
        return self.filter(confirmed=True)

    def pending(self):
        return self.filter(confirmed=False)


class NightAction(models.Model):
    """
    An action executed by a player in a specific turn. The available actions
    are defined by `NightActions`, and described by a combination of targets:
        player: attacked player
        room: attack location, movement destination
        weapon: attack weapon, collected weapon

    Some actions need confirmation.
    """
    night_turn = models.ForeignKey('NightTurn', related_name='actions', on_delete=models.CASCADE)
    character = models.ForeignKey('Character', related_name='night_turns', on_delete=models.PROTECT)
    action = models.CharField(max_length=32, choices=NightActions.choices())
    confirmed = models.BooleanField(default=False)
    character_target = models.ForeignKey('Character', null=True, on_delete=models.PROTECT)
    room_target = models.ForeignKey('GameRoom', null=True, on_delete=models.PROTECT)
    weapon_target = models.ForeignKey('Weapon', null=True, on_delete=models.PROTECT)

    objects = NightActionManager()

    def __str__(self):
        return "{} by {} in {}".format(self.action, self.character.persona.name, self.night_turn)

@receiver(post_save, sender=NightAction)
def check_if_turn_is_complete(sender, instance, *args, **kwargs):
    """
    Checks if this is the last confirmed action of the turn,
    and advances the night in that case.
    """
    action_count = instance.night_turn.actions.confirmed().count()
    characters_count = instance.night_turn.night.game.characters.all().count()

    if action_count == characters_count:
        return instance.night_turn.night.next_turn()


class Day(models.Model):
    """
    A day phase of a game.

    During the day phase alive players will vote for one or more executions.
    """
    game = models.ForeignKey('game', on_delete=models.CASCADE, related_name='days')
    number = models.IntegerField(default=0)

    def end(self):
        return self.game.next_stage()


@receiver(post_save, sender=Day)
def set_current_day(sender, instance, *args, **kwargs):
    """
    Sets the current day for the game if there isn't one.
    """
    if instance.game.current_day is None:
        instance.game.current_day = instance
        return instance.game.save(update_fields=('current_day', ))
