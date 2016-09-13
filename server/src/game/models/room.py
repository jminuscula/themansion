
from django.db import models

from utils import ChoicesEnum

from game.exceptions import RoomActionError


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
    closeable = models.BooleanField(default=True)
    connections = models.ManyToManyField('self',
                                         blank=True,
                                         symmetrical=False,
                                         related_name='passages',
                                         related_query_name='connected_with')

    def __str__(self):
        return self.name


class RoomAction(models.Model):
    """
    Room especial action.

    This class serves as a dispatcher for especial room actions.
    """
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    def get_action_fn(self):
        """
        Get this actions's specific method
        """
        action_fn_name = '_ability_{}'.format(self.name)
        action_fn_name = action_fn_name.replace(' ', '_')
        action_fn_name = action_fn_name.lower()

        return getattr(self, action_fn_name)

    def run(self, *args, **kwargs):
        """
        Execute this action's specific method
        """
        action_fn = self.get_action_fn()
        if action_fn is None:
            raise RoomActionError('room action "{}" can not be executed'.format(self.name))

        return action_fn(self, *args, **kwargs)

    def _action_reload(self):
        """
        Yield a bullet for the player if possible
        """

    def _action_switch_light(self):
        """
        Switch the room light.
        Dark rooms do not inform players about other characters in the room.
        """


class GameRoom(models.Model):
    """
    A room in a specific game.

    Related fields:
        killings (game.models.player.Kill): assasinations in this room
    """
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    is_open = models.BooleanField(default=True)
    dark = models.BooleanField(default=False)
    weapons = models.ManyToManyField('Weapon', blank=True)
    actions = models.ManyToManyField('RoomAction', blank=True)

    class Meta:
        unique_together = (('game', 'room'), )
        default_related_name = 'rooms'

    class GameRoomManager(models.Manager):

        def open(self):
            return self.filter(is_open=True)

        def closed(self):
            return self.filter(is_open=False)

    objects = GameRoomManager()

    def __str__(self):
        return "{} in {}".format(self.room.name, self.game)

    def close(self):
        self.is_open = False
        self.save(update_fields=('is_open', ))

    def open(self):
        self.is_open = True
        self.save(update_fields=('is_open', ))

    def get_actions(self):
        """
        Returns the names of the actions available in this room.
        """
        return [action.name for action in self.action.objects.all()]
