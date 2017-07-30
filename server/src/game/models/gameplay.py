
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from utils import ChoicesEnum
from mansion import settings

from game.models.characterAbility import CharacterAbility
from game.models.stage import Night, Day
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
