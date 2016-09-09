
from django.test import TestCase

from django.contrib.auth.models import User

from game.modes import DefaultGameMode
from game.models import Game


class TestDefaultGameMode(TestCase):
    fixtures = ['initial_data']

    def setUp(self):
        for i in range(10):
            User.objects.create(username='player{}'.format(i), password='password')

        self.players = User.objects.all()
        self.owner = self.players[0]

    def test_create_returns_a_game(self):
        game = DefaultGameMode.create(self.owner, self.players)
        self.assertEqual(type(game), Game)

    def test_create_returns_game_with_all_players(self):
        game = DefaultGameMode.create(self.owner, self.players)
        self.assertEqual(game.characters.count(), len(self.players))

    def test_create_raises_value_error_when_not_enough_players(self):
        with self.assertRaises(ValueError):
            DefaultGameMode.create(self.owner, self.players[:2])

    def test_create_raises_value_error_when_too_many_players(self):
        with self.assertRaises(ValueError):
            DefaultGameMode.create(self.owner, list(self.players) * 2)
