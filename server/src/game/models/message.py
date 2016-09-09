
from django.db import models


class GameMessage(models.Model):
    """
    A Game message to a player.

    Messages are crucial to the game development, as they are required
    for certain actions and events.
    """
    character = models.ForeignKey('Character',
                                  blank=True, null=True, on_delete=models.SET_NULL,
                                  related_name='messages')
    current_night = models.ForeignKey('Night', blank=True, null=True, on_delete=models.SET_NULL)
    current_day = models.ForeignKey('Day', blank=True, null=True, on_delete=models.SET_NULL)
    current_room = models.ForeignKey('GameRoom', blank=True, null=True, on_delete=models.SET_NULL)
    message = models.TextField()
    received_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Message for "{}" ({})'.format(self.character, self.received_on)
