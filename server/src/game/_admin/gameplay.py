
from django.contrib import admin

from game import models
from .character import CharacterInlineAdmin
from .room import GameRoomInlineAdmin
from .stage import NightInlineAdmin


@admin.register(models.Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [
        NightInlineAdmin,
        CharacterInlineAdmin,
        GameRoomInlineAdmin,
    ]
