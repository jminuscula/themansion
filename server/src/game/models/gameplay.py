
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from utils import ChoicesEnum
from mansion import settings

from game.models.ability import CharacterAbility
from game.exceptions import GameUnstarted, GameComplete


class Game(models.Model):
    """
    A `The Mansion` game.

    Coordinates gameplay by keeping track of players, rooms,
    and managing rounds.
    """
    created_by = models.ForeignKey(User, related_name='games_owned', on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)

    game_rooms = models.ManyToManyField('Room', through='GameRoom')
    starting_room = models.ForeignKey('GameRoom', null=True, blank=True, related_name='starting_room')
    night_turns = models.IntegerField(default=settings.GAME_NIGHT_TURNS)
    current_night = models.ForeignKey('Night', null=True, blank=True, on_delete=models.CASCADE,
                                      related_name='current_night')
    current_day = models.ForeignKey('Day', null=True, blank=True, on_delete=models.CASCADE,
                                    related_name='current_day')

    def __str__(self):
        return "Game {}".format(self.pk)

    def start(self):
        """
        Kickstarts the game
        """
        self.current_night = Night.objects.create(game=self)
        self.save()

        for ability in CharacterAbility.objects.phase_start():
            ability.run(game=self)

    def next_stage(self):
        """
        Cycles through Nights and Days until the end of the game is reached
        """
        if self.current_day is None and self.current_night is None:
            raise GameUnstarted
        elif self.nights.all().count() == settings.GAME_NUMBER_NIGHTS:
            raise GameComplete

        elif self.current_day is None:
            stage_number = self.current_night.number
            self.current_day = Day.objects.create(game=self, number=stage_number)
            self.current_night = None

        elif self.current_night is None:
            stage_number = self.current_day.number + 1
            self.current_night = Night.objects.create(game=self, number=stage_number)
            self.current_day = None

        return self.save()

    def broadcast_message(self, msg):
        for character in self.characters.all():
            character.post_message(msg)


class Night(models.Model):
    """
    A night phase of a game.

    A game has `GAME_NUMBER_NIGHTS` number of nights. During a Night phase,
    players must perform `GAME_NIGHT_TURNS` number of actions.
    """
    game = models.ForeignKey('game', on_delete=models.CASCADE, related_name='nights')
    number = models.IntegerField(default=0)
    turns_left = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.turns_left is None:
            self.turns_left = self.game.night_turns
        return super().save(*args, **kwargs)

    def is_new(self):
        return self.turns_left == self.game.night_turns


@receiver(post_save, sender=Night)
def set_current_night(sender, instance, *args, **kwargs):
    """
    Sets the current night for the game if there isn't one.
    """
    if instance.game.current_night is None:
        instance.game.current_night = instance
        return instance.game.save(update_fields=('current_night', ))


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
    night = models.ForeignKey('Night', related_name='actions', on_delete=models.CASCADE)
    character = models.ForeignKey('Character', related_name='night_turns', on_delete=models.PROTECT)
    action = models.CharField(max_length=32, choices=NightActions.choices())
    confirmed = models.BooleanField(default=False)
    character_target = models.ForeignKey('Character', null=True, on_delete=models.PROTECT)
    room_target = models.ForeignKey('GameRoom', null=True, on_delete=models.PROTECT)
    weapon_target = models.ForeignKey('Weapon', null=True, on_delete=models.PROTECT)

    objects = NightActionManager


@receiver(post_save, sender=NightAction)
def check_night_is_complete(sender, instance, *args, **kwargs):
    """
    Checks if this is the last confirmed action of the night,
    and advances the game in that case.
    """
    if instance.night.turns_left > 0:
        return

    action_count = instance.night.actions.confirmed().count()
    characters_count = instance.night.game.characters.all().count()

    if action_count == characters_count:
        return instance.night.game.next_stage()


class Day(models.Model):
    """
    A day phase of a game.

    During the day phase alive players will vote for one or more executions.
    """
    game = models.ForeignKey('game', on_delete=models.CASCADE, related_name='days')
    number = models.IntegerField(default=0)


@receiver(post_save, sender=Day)
def set_current_day(sender, instance, *args, **kwargs):
    """
    Sets the current day for the game if there isn't one.
    """
    if instance.game.current_day is None:
        instance.game.current_day = instance
        return instance.game.save(update_fields=('current_day', ))
