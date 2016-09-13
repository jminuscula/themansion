
from unittest import mock
from .utils import DefaultGameModeTestCase

from game.models import CharacterAbility, Night
from game.exceptions import GameUnstarted, GameComplete


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

    def test_next_stage_can_not_advance_unstarted_game(self):
        with self.assertRaises(GameUnstarted):
            self.game.next_stage()

    def test_next_stage_advances_from_night_to_day(self):
        self.game.start()
        self.assertTrue(self.game.current_night is not None)
        self.assertEqual(self.game.days.all().count(), 0)

        self.game.next_stage()
        self.assertEqual(self.game.days.all().count(), 1)
        self.assertTrue(self.game.current_day is not None)

    def test_next_stage_advances_from_day_to_night(self):
        self.game.start()
        self.game.next_stage()
        self.assertTrue(self.game.current_day is not None)

        nights = self.game.nights.all().count()
        self.game.next_stage()
        self.assertTrue(self.game.current_night is not None)
        self.assertEqual(self.game.nights.all().count(), nights + 1)

    def test_next_stage_raises_game_complete_after_last_night(self):
        self.game.start()
        for i in range(self.game.night_turns * 2):
            self.game.next_stage()

        with self.assertRaises(GameComplete):
            self.game.next_stage()
