
from django.db import models
from django.contrib.auth.models import User

from utils import ChoicesEnum
from django.utils.translation import ugettext as _


class RoomType(ChoicesEnum):
    """
    Available room types.

    Each room type has an specific behavior. Several rooms of the same type may be
    available to the Mansion.
    """
    BASIC = 'basic'
    HALL = 'hall'
    KITCHEN = 'kitchen'
    DORMITORY = 'dormitory'
    OBSERVATORY = 'observatory'
    LIBRARY = 'library'
    BASEMENT = 'basement'


class Room(models.Model):
    """
    A `The Mansion` room.

    Available rooms are fixed by the game rules. Each room has different properties and
    enables especial actions for the players. Rooms are connected so player movement is
    restricted.

    Rooms have doors that may be closed by ghosts and open by living players.
    """
    name = models.CharField(max_length=64, unique=True)
    room_type = models.CharField(max_length=16, choices=RoomType.choices())
    connections = models.ManyToManyField('self',
                                         related_name='connections',
                                         related_query_name='connected_with')

    def __str__(self):
        return self.name


class GameRoom(models.Model):
    """
    A room in a specific game.

    Related fields:
        killings (game.models.player.Kill): assasinations in this room
    """
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    weapons = models.ManyToManyField('Weapon')
    is_open = models.BooleanField(default=True)

    class Meta:
        unique_together = (('game', 'room'), )

    class GameRoomManager(models.Manager):

        def open(self):
            return self.filter(is_open=True)

        def closed(self):
            return self.filter(is_open=False)

    objects = GameRoomManager()

    def __str__(self):
        return "{} in {}".format(self.name, self.game)
