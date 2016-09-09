
from django.contrib import admin

from game import models
from .character import CharacterInlineAdmin
from .room import GameRoomInlineAdmin


@admin.register(models.Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [
        CharacterInlineAdmin,
        GameRoomInlineAdmin,
    ]
