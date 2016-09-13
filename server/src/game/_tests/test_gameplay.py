
from unittest import mock
from .utils import DefaultGameModeTestCase

from game.models import CharacterAbility


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
