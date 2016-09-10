
from django.test import TestCase

from django.contrib.auth.models import User
from .utils import NewGameTestCase
from game.models import Game, CharacterWeapon, Character, Ability, CharacterAbility


class TestDefaultGameMode(NewGameTestCase):

    def test_stealth_hides(self):
        stealth = CharacterAbility.objects.get(character__game=self.game, ability__name="stealth")
        stealth.run()
        character = Character.objects.get(pk=stealth.character.pk)
        self.assertTrue(character.hidden)

    def test_reload(self):
        reload_ability = CharacterAbility.objects.get(character__game=self.game, ability__name="reload")
        reload_ability.run()
        gun = CharacterWeapon.objects.get(character=reload_ability.character, weapon__weapon_type="gun")
        self.assertEqual(gun.ammo, 2)
