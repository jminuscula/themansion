
from django.db import models
from django.contrib.auth.models import User

from django.utils.translation import ugettext as _


class Player(models.Model):
    """
    A game player.

    Represents a Real Life (tm) person handling a character in a particular game.

    Related fields:
        kills (game.models.player.Kill): assasinations as killer
        deaths (game.models.player.Kill): assasinations as victim
        weapons (game.models.weapon.PlayerWeapon): carried weapons
        terrorizations (game.models.player.Terror): given terrors
        terrors (game.models.player.Terror): received terrors
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey('Game', on_delete=models.CASCADE)

    character = models.ForeignKey('Character', on_delete=models.PROTECT)
    alive = models.BooleanField(default=True)
    turns_to_die = models.IntegerField(blank=True, null=True)
    current_room = models.ForeignKey('GameRoom', blank=True, null=True, on_delete=models.PROTECT,
                                     related_name='players_here')
    hidden = models.BooleanField(default=False)

    weapons = models.ManyToManyField('Weapon', through='PlayerWeapon')

    class Meta:
        unique_together = (('game', 'user'), )
        unique_together = (('game', 'character'), )
        default_related_name = 'players'

    def __str__(self):
        return "{} ({})".format(self.user, self.character.title)


class Terror(models.Model):
    """
    A terror.

    One or more ghosts (dead players) may terrorize a living player when found
    alone in the same room. Terrors score points for dead players, thus keeping
    them in play after they're killed or executed.
    """
    ghost = models.ForeignKey('Player', related_name='terrorizations', on_delete=models.CASCADE)
    terrorized = models.ForeignKey('Player', related_name='terrors', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)


class Kill(models.Model):
    """
    An assesination in the game.
    """
    killer = models.ForeignKey('Player', related_name='kills', on_delete=models.CASCADE)
    killed = models.ForeignKey('Player', related_name='deaths', on_delete=models.CASCADE)
    room = models.ForeignKey('GameRoom', related_name='killings', on_delete=models.PROTECT)
    weapon = models.ForeignKey('PlayerWeapon', on_delete=models.PROTECT)

    class Meta:
        unique_together = (('killer', 'killed'), )
