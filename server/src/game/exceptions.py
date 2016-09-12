

class GameException(Exception):

    @property
    def msg(self):
        return getattr(self, 'error', None) or str(self)


class GameModeUnavailable(GameException):
    """
    The necessary elements for the game mode are not available
    """


class InvalidPlayerCount(GameException):
    """
    The number of players for the game is not between the mode limits
    """


class AbilityError(GameException):
    """
    The ability conditions are not met and can not be executede
    """
