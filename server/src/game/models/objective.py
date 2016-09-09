
from django.db import models
from django.utils.translation import ugettext as _

from utils import ChoicesEnum



class ObjectiveTrigger(ChoicesEnum):
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


class Objective(models.Model):
    """
    A Character's mission objective.
    """
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=256)
    trigger = models.CharField(max_length=16, choices=ObjectiveTrigger.choices())
    points = models.IntegerField()

    def __str__(self):
        return self.name


class CharacterObjective(models.Model):
    """
    Game character's objetive tracking.
    """
    character = models.ForeignKey('Character', on_delete=models.CASCADE)
    objective = models.ForeignKey('Objective', on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    complete = models.BooleanField(default=False)

    class Meta:
        unique_together = (('character', 'objective'), )

    def __str__(self):
        return "{} for {}".format(self.objective.name, self.character)
