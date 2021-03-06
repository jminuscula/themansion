
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from game.models.message import GameMessage
from game.models.stage import Night

class Character(models.Model):
    """
    A Character represents a persona being played by a real world Player.

    Characters may have different abilities and objectives in each game, and
    hold the gameplay properties related to their persona.
    """
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='characters')
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

    def post_message(self, msg):
        current_stage = {'current_day': self.game.current_day}
        if self.game.current_day is None:
            current_stage = {'current_night': self.game.current_night}

        return GameMessage.objects.create(character=self,
                                          current_room=self.current_room,
                                          message=msg,
                                          **current_stage)

    def available_actions(self):  # TODO
        """
        Returns all available action that the character may execute at this point.
        """

    def hide(self):
        self.hidden = True
        return self.save(update_fields=('hidden', ))

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
