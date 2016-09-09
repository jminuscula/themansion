
from django.db import models
from django.contrib.auth.models import User


class Character(models.Model):
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)

    persona = models.ForeignKey('Persona', on_delete=models.CASCADE)
    abilities = models.ManyToManyField('Ability', through='CharacterAbility')
    objectives = models.ManyToManyField('Objective', through='CharacterObjective')

    alive = models.BooleanField(default=True)
    turns_to_die = models.IntegerField(blank=True, null=True)
    current_room = models.ForeignKey('GameRoom', blank=True, null=True, on_delete=models.PROTECT,
                                     related_name='players_here')
    hidden = models.BooleanField(default=False)

    weapons = models.ManyToManyField('Weapon', through='CharacterWeapon')


    def __str__(self):
        return "{} as {} on {}".format(self.player, self.persona.title, self.game)


class Terror(models.Model):
    """
    A terror.

    One or more ghosts (dead players) may terrorize a living player when found
    alone in the same room. Terrors score points for dead players, thus keeping
    them in play after they're killed or executed.
    """
    ghost = models.ForeignKey('Character', related_name='terrorizations', on_delete=models.CASCADE)
    terrorized = models.ForeignKey('Character', related_name='terrors', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)


class Kill(models.Model):
    """
    An assesination in the game.
    """
    killer = models.ForeignKey('Character', related_name='kills', on_delete=models.CASCADE)
    killed = models.ForeignKey('Character', related_name='deaths', on_delete=models.CASCADE)
    room = models.ForeignKey('GameRoom', related_name='killings', on_delete=models.PROTECT)
    weapon = models.ForeignKey('CharacterWeapon', on_delete=models.PROTECT)

    class Meta:
        unique_together = (('killer', 'killed'), )
