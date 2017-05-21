
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver

from utils import ChoicesEnum
from mansion import settings
from game.actions import move_action
from game.models.weapon import WeaponType

class Night(models.Model):
    """
    A night phase of a game.

    A game has `GAME_NUMBER_NIGHTS` number of nights. During a Night phase,
    there must be `GAME_NIGHT_TURNS` number of NightTurns.
    """
    game = models.ForeignKey('game', on_delete=models.CASCADE, related_name='nights')
    number = models.IntegerField(default=0)
    current_turn = models.ForeignKey('NightTurn', null=True, blank=True, on_delete=models.CASCADE,
                                      related_name='current_turn')

    def __str__(self):
        return "Night {} in game {}".format(self.number, self.game)

    def turn_count(self):
        return self.night_turns.count()

    def is_new(self):
        return self.turn_count() == 0

    def next_turn(self):
        turn_count = self.turn_count()
        if turn_count >= settings.GAME_NIGHT_TURNS:
            return self.game.next_stage()

        self.current_turn = NightTurn.objects.create(night=self, number=turn_count)
        return self.save()

@receiver(post_save, sender=Night)
def start_new_night(sender, instance, *args, **kwargs):
    """
    If the night is new, restart the characters and start it
    """
    if instance.is_new():
        characters = instance.game.characters.all()
        for character in characters:
            character.current_room = instance.game.starting_room
            character.save()

        return instance.next_turn()


class NightTurn(models.Model):
    """
    A turn in a specific night of a specific game
    """
    night = models.ForeignKey('Night', related_name='night_turns', on_delete=models.CASCADE)
    number = models.IntegerField(default=0)

    def __str__(self):
        return "Turn {} in {}".format(self.number, self.night)

    def resolve(self):
        self.exectue_actions()
        self.deactivate_actions()
        self.night.next_turn()

    def exectue_actions(self):
        actions = self.actions.all()
        for action in actions:
            action.execute()

    def deactivate_actions(self):
        actions = self.actions.active()
        for action in actions:
            action.deactivate()

class NightActions(ChoicesEnum):
    """
    All the actions a player may execute during a night's turn.
    Special actions depend on each character.
    """
    MOVE = 'move'
    ATTACK_KILL = 'attack_kill'
    ATTACK_DEFEND = 'attack_defend'
    ATTACK_BLANK = 'attack_blank'
    PICK_WEAPON = 'pick_weapon'
    SPECIAL = 'special'
    CLOSE_DOOR = 'close_door'
    OPEN_DOOR = 'open_door'
    WAIT = 'wait'


class NightActionManager(models.Manager):

    def new_action(self, *args, **kwargs):
        """
        Creates a new action and deactivates last action from the character.
        """
        new_action = self.create(**kwargs)

        # mark previous actions as not active
        old_action = self.filter(character=new_action.character, active=True).exclude(pk=new_action.pk).first()
        if old_action:
            old_action.deactivate()

        # mark actions in this room, turn, and game as not confirmed
        room_actions = self.filter(character__current_room=new_action.character.current_room, confirmed=True, active=True) \
        .exclude(pk=new_action.pk).all()
        for action in room_actions:
            action.unconfirm()

        new_action.confirm()
        return new_action

    def active(self):
        return self.filter(active=True)

    def confirmed(self):
        return self.filter(active=True, confirmed=True)

    def pending(self):
        return self.filter(confirmed=False)

    def attacks(self):
        return self.filter(
            Q(action=NightActions.ATTACK_KILL) |
            Q(action=NightActions.ATTACK_BLANK) |
            Q(action=NightActions.ATTACK_DEFEND)
            )

    def priority(self, level):
        if level == 1:
            # Spy, hide, heal
            pass
        elif level == 2:
            return self.filter(action==NightActions.CLOSE_DOOR)
        elif level == 3:
            return self.attacks().filter(weapon_target__weapon_type=WeaponType.GUN)
        elif level == 4:
            return self.attacks().filter(weapon_target__weapon_type=WeaponType.KNIFE)
        elif level == 5:
            return self.attacks().filter(weapon_target__weapon_type=WeaponType.STUNT)
        elif level == 6:
            return self.filter(action=NightActions.MOVE)
        elif level == 7:
            return self.attacks().filter(weapon_target__weapon_type=WeaponType.POISON)

        else:
            return None


class NightAction(models.Model):
    """
    An action executed by a player in a specific turn. The available actions
    are defined by `NightActions`, and described by a combination of targets:
        player: attacked player
        room: attack location, movement destination
        weapon: attack weapon, collected weapon
    """
    night_turn = models.ForeignKey('NightTurn', related_name='actions', on_delete=models.CASCADE)
    character = models.ForeignKey('Character', related_name='night_actions', on_delete=models.PROTECT)
    action = models.CharField(max_length=32, choices=NightActions.choices())
    active = models.BooleanField(default=True)
    confirmed = models.BooleanField(default=False)
    character_target = models.ForeignKey('Character', null=True, on_delete=models.PROTECT)
    room_target = models.ForeignKey('GameRoom', null=True, on_delete=models.PROTECT)
    weapon_target = models.ForeignKey('Weapon', null=True, on_delete=models.PROTECT)

    objects = NightActionManager()

    def __str__(self):
        return "{} by {} in {}".format(self.action, self.character.persona.name, self.night_turn)

    def description(self):
        player = self.character.player.username
        confirmed = self.confirmed
        target = None
        tool = None
        if self.room_target:
            target = self.room_target.room.name
        elif self.character_target:
            target = self.character_target.player.username
            if weapon_target:
                tool = self.weapon_target.weapon.name
        elif self.weapon_target:
            target = self.weapon_target.weapon.name

        description = {
            'player': player,
            'action': self.action,
            'confirmed': confirmed,
            'target': target,
            'tool': tool
        }
        return description

    def deactivate(self):
        self.active = False
        self.save()

    def confirm(self):
        self.confirmed = True
        self.save()
        check_if_turn_is_complete(self.night_turn)

    def unconfirm(self):
        self.confirmed = False
        self.save()

    def execute(self):
        if self.action == NightActions.MOVE:
            move_action(self.character, self.room_target)

        if self.action == NightActions.WAIT:
            pass

def check_if_turn_is_complete(night_turn):
    """
    Checks if this is the last confirmed action of the turn,
    and advances the night in that case.
    """
    action_count = night_turn.actions.confirmed().count()
    characters_count = night_turn.night.game.characters.all().count()

    if action_count == characters_count:
        return night_turn.resolve()


class Day(models.Model):
    """
    A day phase of a game.

    During the day phase alive players will vote for one or more executions.
    """
    game = models.ForeignKey('game', on_delete=models.CASCADE, related_name='days')
    number = models.IntegerField(default=0)

    def end(self):
        return self.game.next_stage()


@receiver(post_save, sender=Day)
def set_current_day(sender, instance, *args, **kwargs):
    """
    Sets the current day for the game if there isn't one.
    """
    if instance.game.current_day is None:
        instance.game.current_day = instance
        return instance.game.save(update_fields=('current_day', ))
