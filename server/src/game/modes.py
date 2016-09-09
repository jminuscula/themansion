
import abc

from game.models.gameplay import Game
from game.models.weapon import Weapon
from game.models.room import Room, GameRoom
from game.models.persona import Persona
from game.models.ability import Ability, CharacterAbility
from game.models.objective import Objective, CharacterObjective
from game.models.character import Character


class GameModeUnavailable(Exception):
    pass


class BaseGameMode(metaclass=abc.ABCMeta):

    @abc.abstractclassmethod
    def get_characters(cls):
        pass

    @abc.abstractclassmethod
    def get_abilities_for_character(cls, character):
        pass

    @abc.abstractclassmethod
    def get_objectives_for_character(cls, character):
        pass

    @abc.abstractclassmethod
    def get_rooms(cls):
        pass

    @abc.abstractclassmethod
    def get_weapons_for_room(cls, room):
        pass

    @abc.abstractclassmethod
    def create_game_room(cls, room, weapons):
        pass

    @classmethod
    def create(cls, owner, players):
        game = Game.objects.create(created_by=owner)

        for character in cls.create_characters(game, players):
            for ability in cls.get_abilities_for_character(character):
                CharacterAbility.objects.create(character=character, ability=ability)

            for objective in cls.get_objectives_for_character(character):
                CharacterObjective.objects.create(character=character, objective=objective)

        for room in cls.get_rooms():
            weapons = cls.get_weapons_for_room(room)
            cls.create_game_room(game, room, weapons)

        return game


class DefaultCharactersMixin:

    DEFAULT_PERSONA_TITLES = [
        'The Psychologist',
        'The Bodyguard',
        'The Undertaker',
        'The Avenger',
        'The Host',
        'The Maniac',
        'The Ex-Marine',
        'The Manipulator',
        'The Reporter',
        'The Policeman',
    ]

    @classmethod
    def create_characters(cls, game, players):
        try:
            personas = []
            for title in cls.DEFAULT_PERSONA_TITLES:
                persona = Persona.objects.get(title=title)
                personas.append(persona)
        except Persona.DoesNotExist:
            raise GameModeUnavailable('persona "{}" is not available'.format(title))

        characters = []
        for (persona, player) in zip(personas, players):
            character = Character.objects.create(game=game, player=player, persona=persona)
            characters.append(character)
        return characters



class DefaultAbilitiesMixin:

    DEFAULT_ABILITIES = {
        'The Psychologist': ('profiling', ),
        'The Bodyguard': ('gun reflex', ),
        'The Undertaker': ('family privilege', ),
        'The Avenger': ('stealth', ),
        'The Host': ('gatekeeper', ),
        'The Maniac': ('cutting edge', ),
        'The Ex-Marine': ('reload', ),
        'The Manipulator': ('manipulation', ),
        'The Reporter': ('investigative work', ),
        'The Policeman': ('examination', ),
    }

    @classmethod
    def get_abilities_for_character(cls, character):
        try:
            abilities = []
            for abl_name in cls.DEFAULT_ABILITIES[character.persona.title]:
                ability = Ability.objects.get(name=abl_name)
                abilities.append(ability)
            return abilities
        except Ability.DoesNotExist:
            raise GameModeUnavailable('room "{}" is not available'.format(abl_name))
        except KeyError:
            raise GameModeUnavailable('character "{}" has no abilities defined'.format(character.title))


class DefaultObjectivesMixin:

    DEFAULT_OBJECTIVES = {
        'The Psychologist': ('Analysis', 'Mediation', ),
        'The Bodyguard': ('Security', 'Control', ),
        'The Undertaker': ('Identification', 'Loyalty', ),
        'The Avenger': ('Protection', 'Punishment', ),
        'The Host': ('Chaos', 'Order'),
        'The Maniac': ('Viciousness', 'Massacre', ),
        'The Ex-Marine': ('Lesson', 'Revenge', ),
        'The Manipulator': ('Discord', 'Manipulation', ),
        'The Reporter': ('Facts', 'History', ),
        'The Policeman': ('Law', 'Justice', ),
    }

    @classmethod
    def get_objectives_for_character(cls, character):
        try:
            objectives = []
            for obj_name in cls.DEFAULT_OBJECTIVES[character.persona.title]:
                objective = Objective.objects.get(name=obj_name)
                objectives.append(objective)
            return objectives
        except Objective.DoesNotExist:
            raise GameModeUnavailable('objective "{}" is not available'.format(obj_name))
        except KeyError:
            raise GameModeUnavailable('character "{}" is not available'.format(character.title))


class DefaultRoomsMixin:

    DEFAULT_ROOM_NAMES = [
        'Library',
        'Observatory',
        'Master Bedroom',
        'Kitchen',
        'Basement',
        'Hall',
    ]

    @classmethod
    def get_rooms(cls):
        try:
            rooms = []
            for room in cls.DEFAULT_ROOM_NAMES:
                rooms.append(Room.objects.get(name=room))
            return rooms
        except Room.DoesNotExist:
            raise GameModeUnavailable('room "{}" is not available'.format(room))

    @classmethod
    def create_game_room(cls, game, room, weapons):
        game_room = GameRoom.objects.create(game=game, room=room)
        for weapon in weapons:
            game_room.weapons.add(weapon)
        return game_room


class DefaultWeaponsMixin:

    DEFAULT_ROOM_WEAPONS = {
        'Library': ('Poison', ),
        'Observatory': ('Wrench', ),
        'Master Bedroom': ('Cane', ),
        'Kitchen': ('Knife', ),
        'Basement': ('Bullets', ),
        'Hall': ('Chandelier', ),
    }

    @classmethod
    def get_weapons_for_room(cls, room):
        try:
            weapons = []
            for weapon_name in cls.DEFAULT_ROOM_WEAPONS[room.name]:
                weapon = Weapon.objects.get(name=weapon_name)
                weapons.append(weapon)
            return weapons
        except Weapon.DoesNotExist:
            raise GameModeUnavailable('weapon "{}" is not available'.format(weapon_name))
        except KeyError:
            raise GameModeUnavailable('room "{}" has no weapons defined'.format(room.name))


class DefaultGameMode(DefaultCharactersMixin,
                      DefaultRoomsMixin,
                      DefaultWeaponsMixin,
                      DefaultAbilitiesMixin,
                      DefaultObjectivesMixin,
                      BaseGameMode):
    pass
