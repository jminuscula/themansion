
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from utils import ChoicesEnum
from mansion import settings

from game.models.ability import CharacterAbility


class Game(models.Model):
    """
    A `The Mansion` game.

    Coordinates gameplay by keeping track of players, rooms,
    and managing rounds.
    """
    created_by = models.ForeignKey(User, related_name='games_owned', on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)

    game_rooms = models.ManyToManyField('Room', through='GameRoom')
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

    @property
    def is_new(self):
        return self.turns == self.game.night_turns


@receiver(post_save, sender=Night)
def night_saved(sender, instance, *args, **kwargs):
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

    Some actions need confirmation
    """
    night = models.ForeignKey('Night', related_name='actions', on_delete=models.CASCADE)
    character = models.ForeignKey('Character', related_name='night_turns', on_delete=models.PROTECT)
    action = models.CharField(max_length=32, choices=NightActions.choices())
    confirmed = models.BooleanField(default=False)
    character_target = models.ForeignKey('Character', null=True, on_delete=models.PROTECT)
    room_target = models.ForeignKey('GameRoom', null=True, on_delete=models.PROTECT)
    weapon_target = models.ForeignKey('Weapon', null=True, on_delete=models.PROTECT)

    objects = NightActionManager


class Day(models.Model):
    """
    A day phase of a game.

    During the day phase alive players will vote for one or more executions.
    """
    game = models.ForeignKey('game', on_delete=models.CASCADE, related_name='days')
    number = models.IntegerField(default=0)




@receiver(post_save, sender=Day)
def day_saved(sender, instance, *args, **kwargs):
    if instance.game.current_day is None:
        instance.game.current_day = instance
        return instance.game.save(update_fields=('current_day', ))
