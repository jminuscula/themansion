
from django.db import models


class Persona(models.Model):
    """
    A game persona.

    Personas will be controlled by players via Characters.
    """
    name = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=64)
    bio = models.TextField()

    def __str__(self):
        return "{} ({})".format(self.name, self.title)
