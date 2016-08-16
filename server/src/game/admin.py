
from django.contrib import admin

from game import models


@admin.register(models.Game)
class GameAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Character)
class CharacterAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CharacterAbility)
class CharacterAbilityAdmin(admin.ModelAdmin):
    pass


@admin.register(models.GameCharacterAbility)
class GameCharacterAbilityAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CharacterObjective)
class CharacterObjectiveAdmin(admin.ModelAdmin):
    pass


@admin.register(models.GameCharacterObjective)
class GameCharacterObjectiveAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):
    pass


@admin.register(models.GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Weapon)
class WeaponAdmin(admin.ModelAdmin):
    pass
