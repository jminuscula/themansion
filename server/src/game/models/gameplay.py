
from django.db import models
from django.contrib.auth.models import User

from django.utils.translation import ugettext as _


class Game(models.Model):
    """
    A `The Mansion` game.

    Coordinates gameplay by keeping track of players, rooms,
    and managing rounds.
    """
    created_by = models.ForeignKey(User, related_name='games_owned', on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)

    game_rooms = models.ManyToManyField('Room', through='GameRoom')
    game_players = models.ManyToManyField(User, through='Player')

    def __str__(self):
        return "Game {}".format(self.pk)
