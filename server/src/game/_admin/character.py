
from django.contrib import admin

from game import models


@admin.register(models.Persona)
class PersonaAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Ability)
class AbilityAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CharacterAbility)
class CharacterAbilityAdmin(admin.ModelAdmin):
    pass


class CharacterAbilityInlineAdmin(admin.TabularInline):
    model = models.CharacterAbility
    extra = 0


@admin.register(models.Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CharacterObjective)
class CharacterObjectiveAdmin(admin.ModelAdmin):
    pass


class CharacterObjectiveInlineAdmin(admin.TabularInline):
    model = models.CharacterObjective
    extra = 0


@admin.register(models.Character)
class CharacterAdmin(admin.ModelAdmin):
    inlines = [
        CharacterAbilityInlineAdmin,
        CharacterObjectiveInlineAdmin,
    ]


class CharacterInlineAdmin(admin.TabularInline):
    model = models.Character
    extra = 0
