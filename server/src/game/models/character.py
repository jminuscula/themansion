
from django.db import models
from django.contrib.auth.models import User

from utils import ChoicesEnum

from django.utils.translation import ugettext as _


class Character(models.Model):
    """
    A game character.

    The available characters are fixed by the game rules
    """
    name = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=64)
    bio = models.TextField()
    character_abilities = models.ManyToManyField('CharacterAbility', through='GameCharacterAbility')
    character_objectives = models.ManyToManyField('CharacterObjective', through='GameCharacterObjective')

    def __str__(self):
        return "{} ({})".format(self.name, self.title)


class CharacterAbilityActionPhase(ChoicesEnum):
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


class CharacterAbility(models.Model):
    """
    A character's special ability.
    """
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=512)
    room = models.ManyToManyField('Room', blank=True)
    action_phase = models.CharField(max_length=16,
                                    null=True,
                                    choices=CharacterAbilityActionPhase.choices())

    class Meta:
        verbose_name_plural = _('character abilities')

    def __str__(self):
        return self.name


class GameCharacterAbility(models.Model):
    """
    Game character's ability tracking.

    Checks for usage limit, availability, etc.
    """
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    character = models.ForeignKey('Character', related_name='characters')
    ability = models.ForeignKey('CharacterAbility')
    available = models.BooleanField(default=True)

    class Meta:
        unique_together = (('game', 'character', 'ability'))
        verbose_name_plural = _('game character abilities')
        default_related_name = 'abilities'

    def __str__(self):
        return "{} for {} on {}".format(self.ability.name, self.character.title, self.game)


class CharacterObjetiveTrigger(ChoicesEnum):
    """
    Moment when an objetive must be checked for completion.
    """
    KILL = 'kill'  # player kills
    EXECUTE = 'execute'
    TERRORIZE = 'terrorize'

    KILLED = 'killed'  # player is killed
    EXECUTED = 'executed'
    TERRORIZED = 'terrorized'
    DEAD = 'dead'  # player is killed or executed

    ENDGAME = 'endgame'


class CharacterObjective(models.Model):
    """
    A Character's mission objective.
    """
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=256)
    trigger = models.CharField(max_length=16, choices=CharacterObjetiveTrigger.choices())
    points = models.IntegerField()

    def __str__(self):
        return self.name


class GameCharacterObjective(models.Model):
    """
    Game character's objetive tracking.
    """
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    character = models.ForeignKey('Character', on_delete=models.CASCADE)
    objective = models.ForeignKey('CharacterObjective', on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return "{} for {} on {}".format(self.objective.name, self.character.title, self.game)

    class Meta:
        unique_together = (('game', 'character', 'objective'))
        default_related_name = 'objectives'
