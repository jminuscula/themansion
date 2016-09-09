
from django.db import models
from django.utils.translation import ugettext as _

from utils import ChoicesEnum


class AbilityActionPhase(ChoicesEnum):
    """
    Moments when a character's ability may be triggered.

    Abilities may perform additional availability checks, such as checking for
    a specifc room, or limiting the number of uses.
    """
    PASSIVE = 'passive'  # passive abilities can't be triggered (ie -start with weapon)
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
        verbose_name_plural = _('abilities')

    def __str__(self):
        return self.name


class CharacterAbility(models.Model):
    """
    Game character's ability tracking.

    Checks for usage limit, availability, etc.
    """
    character = models.ForeignKey('Character')
    ability = models.ForeignKey('Ability')
    available = models.BooleanField(default=True)

    class Meta:
        unique_together = (('character', 'ability'), )
        verbose_name_plural = _('character abilities')

    def __str__(self):
        return "{} for {}".format(self.ability.name, self.character)
