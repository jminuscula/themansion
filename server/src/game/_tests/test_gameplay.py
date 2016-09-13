
from unittest import mock
from .utils import DefaultGameModeTestCase

from game.models import CharacterAbility, Night


class GameplayTestCase(DefaultGameModeTestCase):

    def test_start_game_runs_gamestart_abilities(self):

        def patched_test(*mocks):
            self.game.start()
            for ability_mock in mocks:
                self.assertTrue(ability_mock.called)

        abilities = CharacterAbility.objects.phase_start()
        for ability in abilities:
            ability_fn_name = ability.get_ability_fn().__name__
            patched_test = mock.patch.object(CharacterAbility, ability_fn_name)(patched_test)

        patched_test()

    def test_start_game_adds_new_night(self):
        self.assertTrue(self.game.current_night is None)
        self.game.start()
        self.assertTrue(type(self.game.current_night) is Night)

    def test_nights_start_with_full_number_of_turns(self):
        night = Night.objects.create(game=self.game)
        self.assertEqual(night.turns_left, self.game.night_turns)

    def test_night_is_new_when_full_number_of_turns(self):
        night = Night.objects.create(game=self.game)
        self.assertTrue(night.is_new())

        night.turns_left -= 1
        night.save()
        self.assertFalse(night.is_new())
