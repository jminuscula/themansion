
from django.contrib import admin

from game import models
from .player import PlayerInlineAdmin
from .room import GameRoomInlineAdmin


@admin.register(models.Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [
        PlayerInlineAdmin,
        GameRoomInlineAdmin,
    ]
