
from django.contrib import admin

from game import models


class NightInlineAdmin(admin.TabularInline):
    model = models.Night
    extra = 0

class NightTurnInLineAdmin(admin.TabularInline):
    model = models.NightTurn
    extra = 0

@admin.register(models.Night)
class NightAdmin(admin.ModelAdmin):
    inlines = [
        NightTurnInLineAdmin,
    ]
