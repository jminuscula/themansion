import sys

from game.models.room import RoomType
from game.models.ability import AbilityActionPhase


class ActionManager:

    @classmethod
    def _get_action_by_name(cls, action_name):
        action_name = action_name.replace('_', ' ').title().replace(' ', '')
        return getattr(sys.modules[__name__], 'Action' + action_name)

    @classmethod
    def _get_action_from_nightaction(cls, nightAction):
        return ActionManager._get_action_by_name(nightAction.action)

    @classmethod
    def get_available_actions(cls, character):
        action_names = ['Move', 'Wait', 'Hide']
        available_actions = {}
        for action_name in action_names:
            action = cls._get_action_by_name(action_name)
            if action.is_available(character):
                options = action.available_options(character)
                available_actions[action.name] = options

        return available_actions

    @classmethod
    def execute_nightaction(cls, nightAction):
        cls._get_action_by_name(nightAction.action) \
            .execute(nightAction)

    @classmethod
    def actions_by_priority(cls, nightActions):
        # a list of Actions from nightActions
        actions = list(map(ActionManager._get_action_from_nightaction, nightActions))
        # pairing every NightAction with its Action
        actions_map = dict(zip(nightActions, actions))
        # sort by action priority
        return sorted(actions_map, key=lambda a: actions_map[a].priority)


class BaseAction:
    # the lower the priority number, the sooner it's executed

    @classmethod
    def is_enabled_by_ability(cls, character):
        night_abilities = character.abilities.filter(action_phase=AbilityActionPhase.NIGHT).all()
        for ability in night_abilities:
            if character.execute_ability(ability, action=cls):
                return True

        return False

    @classmethod
    def is_available(cls, character):
        raise NotImplementedError

    @classmethod
    def available_options(cls, character):
        """
        Usually 1 or 2 of these should be returned in specific implementations.
        There are a few actions without options. Returning {} will be enough.
        {
            'room_target': ['Basement', 'Kitchen'],
            'character_target': ['jacobo', 'sofia'],
            'weapon_target': ['Knife', 'Gun']
        }
        """
        return {}

    @classmethod
    def execute(cls, nightAction):
        raise NotImplementedError


class ActionMove(BaseAction):
    name = 'Move'
    priority = 6

    @classmethod
    def is_available(cls, character):
        if cls.is_enabled_by_ability(character):
            return True
        # TODO don't make it available if there are no open rooms available
        return True

    @classmethod
    def available_options(cls, character):
        current_room = character.current_room

        # this take the connected rooms, and finds the gamerooms for them;
        # then filter out the closed ones.
        # this is a bit weird. I think connections should be done in GameRoom. TODO
        available_rooms = current_room.room.connections.all()
        available_gamerooms = []
        for room in available_rooms:
            # this basic_info thing is just a temporary thing for the API
            available_gamerooms.append(character.game.rooms.filter(room=room, is_open=True).first().basic_info())

        return available_gamerooms

    @classmethod
    def execute(cls, nightAction):
            nightAction.character.current_room = nightAction.room_target
            return nightAction.character.save()


class ActionWait(BaseAction):
    name = "Wait"
    priority = 9

    @classmethod
    def is_available(cls, character):
        return True

    @classmethod
    def execute(cls, nightAction):
        pass


class ActionHide(BaseAction):
    name = "Hide"
    priority = 1

    @classmethod
    def is_available(cls, character):
        # if you're alone (hidden people don't count) in the observatory
        # or anywhere if you have the ability
        if cls.is_enabled_by_ability(character):
            return True
        room = character.current_room
        people = room.list_people_visible()
        return len(people) == 1 and people[0] == character \
            and (room.room.room_type == RoomType.OBSERVATORY)


    @classmethod
    def execute(cls, nightAction):
        nightAction.character.hide()
