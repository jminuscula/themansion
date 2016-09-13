
from django.db import models
from django.contrib.auth.models import User

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
    turns_left = models.IntegerField(default=settings.GAME_NIGHT_TURNS)

    def save(self, *args, **kwargs):
        saved = super().save(*args, **kwargs)
        if self.game.current_night is None:
            self.game.current_night = self
            self.game.save(update_fields=('current_night', ))
        return saved

    @property
    def is_new(self):
        return self.turns == settings.GAME_NIGHT_TURNS


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

    def save(self, *args, **kwargs):
        saved = super().save(*args, **kwargs)
        if self.game.current_day is None:
            self.game.current_day = self
            self.game.save()
        return saved
