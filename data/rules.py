"""
Contains all rules that are currently available. All Rules inherit from the Rule class and
can be initialized as per default, randomly or as specified explicitly. Also rules can
be applied to a game object.
"""

from random import shuffle, getrandbits


class Rule:
    """Class to represent a single rule."""

    # TODO: how to interact with other rules? What about conflicts, I mean?
    # Edit: Make do constraint checking in the collection class (e.g. Rules)
    defaults = {}
    randomization = {}

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def random_init(cls):
        raise NotImplementedError()

    @classmethod
    def default_init(cls):
        raise NotImplementedError()

    def apply(self, *args, **kwargs):
        raise NotImplementedError()


class ShuffleTurnOrderOnStart(Rule):
    def __init__(self, *args, **kwargs):
        super(ShuffleTurnOrderOnStart, self).__init__()

    @classmethod
    def random_init(cls):
        return cls(value=bool(getrandbits(1)))

    @classmethod
    def default_init(cls):
        return cls(value=False)

    def apply(self, *args, **kwargs):
        if self.value and kwargs.get('game_starts_now', False):
            shuffle(kwargs.get('game').participants)


class EnableChat(Rule):
    def __init__(self, *args, **kwargs):
        super(EnableChat, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class FinishGameOnDisconnect(Rule):
    def __init__(self, *args, **kwargs):
        super(FinishGameOnDisconnect, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class FinishGameOnWin(Rule):
    def __init__(self, *args, **kwargs):
        super(FinishGameOnWin, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class AllowReconnect(Rule):
    def __init__(self, *args, **kwargs):
        super(AllowReconnect, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class WinningRowLength(Rule):
    def __init__(self, *args, **kwargs):
        super(WinningRowLength, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class FieldHasBounds(Rule):
    def __init__(self, *args, **kwargs):
        super(FieldHasBounds, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class EnableCards(Rule):
    def __init__(self, *args, **kwargs):
        super(EnableCards, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class EnableCheats(Rule):
    def __init__(self, *args, **kwargs):
        super(EnableCheats, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class NumberOfPlayers(Rule):
    def __init__(self, *args, **kwargs):
        super(NumberOfPlayers, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class StartGameIfAllReady(Rule):
    def __init__(self, *args, **kwargs):
        super(StartGameIfAllReady, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class VariablePlayerCount(Rule):
    def __init__(self, *args, **kwargs):
        super(VariablePlayerCount, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class PlayFieldWidth(Rule):
    def __init__(self, *args, **kwargs):
        super(PlayFieldWidth, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class PlayFieldHeight(Rule):
    def __init__(self, *args, **kwargs):
        super(PlayFieldHeight, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass


class EnableGravity(Rule):
    def __init__(self, *args, **kwargs):
        super(EnableGravity, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls):
        return cls(**Rule.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls):
        return cls(**Rule.defaults.get(cls.__name__))

    def apply(self, *args, **kwargs):
        pass
