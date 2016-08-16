
from django.contrib import admin

from game import models


@admin.register(models.Weapon)
class WeaponAdmin(admin.ModelAdmin):
    pass
