import sys

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
        action_names = ['Move', 'Wait']
        available_actions = {}
        for action_name in action_names:
            action = cls._get_action_by_name(action_name)
            options = action.available_options(character)
            if options is not None:
                available_actions[action.name] = options

        return available_actions

    @classmethod
    def execute_nightAction(cls, nightAction):
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
    @classmethod
    def available_options(self, character):
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


class ActionMove(BaseAction):
    name = 'Move'
    priority = 3

    @classmethod
    def execute(self, nightAction):
            nightAction.character.current_room = nightAction.room_target
            return nightAction.character.save()

    @classmethod
    def available_options(self, character):
        current_room = character.current_room

        # this take the connected rooms, and finds the gamerooms for them;
        # then filter out the closed ones.
        # this is a bit weird. I think connections should be done in GameRoom. TODO
        available_rooms = current_room.room.connections.all()
        available_gamerooms = []
        for room in available_rooms:
            available_gamerooms.append(character.game.rooms.filter(room=room, is_open=True).first().basic_info())

        return available_gamerooms

    @classmethod
    def is_available(self, character):
        return True

class ActionWait(BaseAction):
    name = "Wait"
    priority = 7

    def execute(self):
        pass

    @classmethod
    def is_available(self, character):
        return True
