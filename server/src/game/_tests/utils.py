from django.test import TestCase
from django.contrib.auth.models import User

from game.modes import DefaultGameMode


class NewGameTestCase(TestCase):
    fixtures = ['initial_data']

    def setUp(self):
        for i in range(10):
            User.objects.create(username='player{}'.format(i), password='password')

        self.players = User.objects.all()
        self.owner = self.players[0]
        self.game = DefaultGameMode.create(self.owner, self.players)

    def tearDown(self):
        self.game.delete()
        self.players.delete()
