
from django.contrib import admin

from game import models


@admin.register(models.Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


class PlayerInlineAdmin(admin.TabularInline):
    model = models.Player
    extra = 0
