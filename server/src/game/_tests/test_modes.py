
from .utils import DefaultGameModeTestCase

from game.exceptions import InvalidPlayerCount
from game.modes import DefaultGameMode
from game.models import Game, CharacterWeapon


class DefaultGameTestCase(DefaultGameModeTestCase):

    def test_create_returns_a_game(self):
        game = DefaultGameMode.create(self.owner, self.players)
        self.assertEqual(type(game), Game)

    def test_create_returns_game_with_all_players(self):
        game = DefaultGameMode.create(self.owner, self.players)
        self.assertEqual(game.characters.count(), len(self.players))

    def test_create_raises_when_not_enough_players(self):
        with self.assertRaises(InvalidPlayerCount):
            DefaultGameMode.create(self.owner, self.players[:2])

    def test_create_raises_when_too_many_players(self):
        with self.assertRaises(InvalidPlayerCount):
            DefaultGameMode.create(self.owner, list(self.players) * 2)

    def test_create_gives_characters_weapons(self):
        game = DefaultGameMode.create(self.owner, self.players)
        gun_count = CharacterWeapon.objects.filter(character__game=game, weapon__name="Gun").count()
        self.assertEqual(len(self.players), gun_count)
