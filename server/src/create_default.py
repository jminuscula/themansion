from django.contrib.auth.models import User
from game.modes import DefaultGameMode

tomas = User.objects.get(username="tomas")
players = User.objects.all()

game = DefaultGameMode.create(owner=tomas, players=players[:9])
