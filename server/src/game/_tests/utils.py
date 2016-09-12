
from django.test import TestCase
from django.contrib.auth.models import User

from game.modes import DefaultGameMode
from game.models import Character, Game


class DefaultGameModeTestCase(TestCase):
    fixtures = ['initial_data']

    def setUp(self):
        for i in range(10):
            User.objects.create(username='player{}'.format(i), password='password')

        self.players = User.objects.all()
        self.owner = self.players[0]
        self.game = DefaultGameMode.create(self.owner, self.players)

    def tearDown(self):
        Character.objects.all().delete()
        Game.objects.all().delete()
        User.objects.all().delete()
