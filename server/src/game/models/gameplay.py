
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from game.models.ability import CharacterAbility
from game.exceptions import GameUnstarted, GameComplete

from mansion import settings


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
