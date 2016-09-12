
from .utils import DefaultGameModeTestCase

from game.models import CharacterWeapon, Character, CharacterAbility, GameRoom
from game.exceptions import AbilityError


class AbilityTestCase(DefaultGameModeTestCase):

    def test_stealth_hides(self):
        stealth = CharacterAbility.objects.get(character__game=self.game, ability__name="stealth")
        stealth.run()
        character = Character.objects.get(pk=stealth.character.pk)
        self.assertTrue(character.hidden)

    def test_reload_yields_two_bullets(self):
        reload_ability = CharacterAbility.objects.get(character__game=self.game, ability__name="reload")
        reload_ability.run()
        gun = CharacterWeapon.objects.get(character=reload_ability.character, weapon__weapon_type="gun")
        self.assertEqual(gun.ammo, 2)

    def test_cutting_edge_provides_knife(self):
        cutting_edge = CharacterAbility.objects.get(character__game=self.game, ability__name='cutting edge')
        cutting_edge.run()
        CharacterWeapon.objects.get(character=cutting_edge.character, weapon__name='Knife')

    def test_gatekeeper_can_close_current_room_room(self):
        gameroom = GameRoom.objects.filter(is_open=True, room__closeable=True)[0]
        gatekeeper = CharacterAbility.objects.get(character__game=self.game, ability__name='gatekeeper')
        gatekeeper.character.current_room = gameroom
        gatekeeper.save()

        gatekeeper.run(room=gameroom)
        gameroom.refresh_from_db()
        self.assertFalse(gameroom.is_open)

    def test_gatekeeper_can_close_connected_room(self):
        gameroom = GameRoom.objects.filter(is_open=True, room__closeable=True)[0]
        gatekeeper = CharacterAbility.objects.get(character__game=self.game, ability__name='gatekeeper')
        gatekeeper.character.current_room = gameroom
        gatekeeper.save()

        connected = GameRoom.objects.filter(pk__in=gameroom.room.connections.all(),
                                            is_open=True, room__closeable=True)[0]
        gatekeeper.run(room=connected)
        connected.refresh_from_db()
        self.assertFalse(connected.is_open)

    def test_gatekeeper_can_not_close_closed_room(self):
        gatekeeper = CharacterAbility.objects.get(character__game=self.game, ability__name='gatekeeper')
        gameroom = GameRoom.objects.filter(room__closeable=True)[0]
        gameroom.is_open = False
        gameroom.save(update_fields=('is_open', ))

        gatekeeper.character.current_room = gameroom
        gatekeeper.save()

        with self.assertRaises(AbilityError):
            gatekeeper.run(room=gameroom)

    def test_gatekeeper_can_not_close_uncloseable_room(self):
        gatekeeper = CharacterAbility.objects.get(character__game=self.game, ability__name='gatekeeper')
        gameroom = GameRoom.objects.all()[0]
        gameroom.room.closeable = False
        gameroom.room.save(update_fields=('closeable', ))

        gatekeeper.character.current_room = gameroom
        gatekeeper.save()

        with self.assertRaises(AbilityError):
            gatekeeper.run(room=gameroom)

    def test_gatekeeper_can_not_close_distant_room(self):
        gatekeeper = CharacterAbility.objects.get(character__game=self.game, ability__name='gatekeeper')
        gameroom = GameRoom.objects.all()[0]

        gatekeeper.character.current_room = gameroom
        gatekeeper.save()
        distant = GameRoom.objects.all().exclude(pk=gameroom.pk)[0]

        with self.assertRaises(AbilityError):
            gatekeeper.run(room=distant)
