
from django.db import models
from django.utils.translation import ugettext as _


class Persona(models.Model):
    """
    A game persona.

    The available characters are fixed by the game rules
    """
    name = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=64)
    bio = models.TextField()

    def __str__(self):
        return "{} ({})".format(self.name, self.title)
