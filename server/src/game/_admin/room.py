
from django.contrib import admin

from game import models


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):
    pass


class GameRoomInlineAdmin(admin.TabularInline):
    model = models.GameRoom
    extra = 0

@admin.register(models.GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    pass
