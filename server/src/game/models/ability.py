
from django.db import models

from utils import ChoicesEnum


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
