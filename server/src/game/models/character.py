
from django.db import models
from django.contrib.auth.models import User

from django.utils.translation import ugettext as _


class Character(models.Model):
    """
    A game character.

    The available characters are fixed by the game rules.

    Related fields:
        objectives (game.models.character.CharacterObjective):
            character objectives and scores
    """
    name = models.CharField(max_length=64, unique=True)
    bio = models.CharField(max_length=512)


class CharacterObjective(models.Model):
    """
    A Character's mission objective.
    """
    character = models.ForeignKey('Character', related_name='objectives', on_delete=models.CASCADE)
    description = models.CharField(max_length=256)
    points = models.IntegerField()
