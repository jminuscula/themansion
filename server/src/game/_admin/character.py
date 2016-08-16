
from django.contrib import admin

from game import models


@admin.register(models.CharacterAbility)
class CharacterAbilityAdmin(admin.ModelAdmin):
    pass


@admin.register(models.GameCharacterAbility)
class GameCharacterAbilityAdmin(admin.ModelAdmin):
    pass


class GameCharacterAbilityInlineAdmin(admin.TabularInline):
    model = models.GameCharacterAbility
    extra = 0


@admin.register(models.CharacterObjective)
class CharacterObjectiveAdmin(admin.ModelAdmin):
    pass


@admin.register(models.GameCharacterObjective)
class GameCharacterObjectiveAdmin(admin.ModelAdmin):
    pass


class GameCharacterObjectiveInlineAdmin(admin.TabularInline):
    model = models.GameCharacterObjective
    extra = 0


@admin.register(models.Character)
class CharacterAdmin(admin.ModelAdmin):
    inlines = [
        GameCharacterAbilityInlineAdmin,
        GameCharacterObjectiveInlineAdmin,
    ]
