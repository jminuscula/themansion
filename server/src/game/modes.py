
import abc

from game.models.gameplay import Game
from game.models.weapon import Weapon
from game.models.room import Room, GameRoom
from game.models.character import (Character,
                                   CharacterAbility, GameCharacterAbility,
                                   CharacterObjective, GameCharacterObjective)


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
    def create_game_room(cls, game, room, weapons):
        pass

    @classmethod
    def create(cls, owner):
        game = Game.objects.create(created_by=owner)

        for character in cls.get_characters():
            abilities = cls.get_abilities_for_character(character)
            for ability in abilities:
                cls.create_game_character_ability(game, character, ability)

            objectives = cls.get_objectives_for_character(character)
            for objective in objectives:
                cls.create_game_character_objective(game, character, objective)

        for room in cls.get_rooms():
            weapons = cls.get_weapons_for_room(room)
            cls.create_game_room(game, room, weapons)

        return game


class DefaultCharactersMixin:

    DEFAULT_CHARACTER_TITLES = [
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
    def get_characters(cls):
        try:
            characters = []
            for title in cls.DEFAULT_CHARACTER_TITLES:
                character = Character.objects.get(title=title)
                characters.append(character)
            return characters
        except Character.DoesNotExist:
            raise GameModeUnavailable('character "{}" is not available'.format(title))


class DefaultAbilitiesMixin:

    DEFAULT_CHARACTER_ABILITIES = {
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
            abilities = cls.DEFAULT_CHARACTER_ABILITIES[character.title]
            char_abilities = []
            for abl_name in abilities:
                ability = CharacterAbility.objects.get(name=abl_name)
                char_abilities.append(ability)
            return char_abilities
        except CharacterAbility.DoesNotExist:
            raise GameModeUnavailable('room "{}" is not available'.format(abl_name))
        except KeyError:
            raise GameModeUnavailable('character "{}" has no abilities defined'.format(character.title))

    @classmethod
    def create_game_character_ability(cls, game, character, ability):
        return GameCharacterAbility.objects.create(game=game,
                                                   character=character,
                                                   ability=ability)


class DefaultObjectivesMixin:

    DEFAULT_CHARACTER_OBJECTIVES = {
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
            objectives = cls.DEFAULT_CHARACTER_OBJECTIVES[character.title]
            char_objectives = []
            for obj_name in objectives:
                objective = CharacterObjective.objects.get(name=obj_name)
                char_objectives.append(objective)
            return char_objectives
        except CharacterObjective.DoesNotExist:
            raise GameModeUnavailable('objective "{}" is not available'.format(obj_name))
        except KeyError:
            raise GameModeUnavailable('character "{}" is not available'.format(character.title))

    @classmethod
    def create_game_character_objective(cls, game, character, objective):
        return GameCharacterObjective.objects.create(game=game,
                                                     character=character,
                                                     objective=objective)


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
