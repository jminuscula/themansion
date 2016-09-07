
from django.db import models
from django.contrib.auth.models import User

from utils import ChoicesEnum
from django.utils.translation import ugettext as _


class WeaponType(ChoicesEnum):
    """
    Available weapon types.

    Each weapon has different properties such as triggering modes or action time.
    Attacks are resolved in decreasing priority.
    """
    GUN = 'gun'
    KNIFE = 'knife'
    STUNT = 'stunt'
    POISON = 'poison'


class Weapon(models.Model):
    """
    A `The Mansion` weapon.

    Available weapons are fixed by the game rules.
    - Resource weapons do not disappear from their initial room when picked up by players.
    - Intention weapons inform players in the room when its action has been selected.
    - Effect turns triggers the weapon action only after said number of turns.
    """
    name = models.CharField(max_length=16, unique=True)
    description = models.CharField(max_length=256)
    weapon_type = models.CharField(max_length=16, choices=WeaponType.choices())
    max_ammo = models.IntegerField(blank=True, null=True)
    starting_ammo = models.IntegerField(blank=True, null=True)
    starting_room = models.ForeignKey('Room', on_delete=models.PROTECT)
    resource = models.BooleanField(default=False)
    intention = models.BooleanField(default=True)
    effect_turns = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class PlayerWeapon(models.Model):
    """
    A weapon carried by a player.
    """
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    weapon = models.ForeignKey('Weapon', on_delete=models.CASCADE)
    picked_at = models.ForeignKey('GameRoom', on_delete=models.PROTECT)
    ammo = models.IntegerField(null=True)
