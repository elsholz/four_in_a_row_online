class Card:
    defaults = {}
    randomization = {}

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def random_init(cls, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def default_init(cls, *agrs, **kwargs):
        raise NotImplementedError()

    def play(self, *args, **kwargs):
        raise NotImplementedError()


class ShuffleTurnOrder(Card):
    def __init__(self, *args, **kwargs):
        super(ShuffleTurnOrder, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls, *args, **kwargs):
        return cls(**Card.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls, *args, **kwargs):
        return cls(**Card.defaults.get(cls.__name__))

    def play(self, *args, **kwargs):
        pass


class ReverseTurnOrder(Card):
    def __init__(self, *args, **kwargs):
        super(ReverseTurnOrder, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls, *args, **kwargs):
        return cls(**Card.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls, *args, **kwargs):
        return cls(**Card.defaults.get(cls.__name__))

    def play(self, *args, **kwargs):
        pass


class SkipNextTurn(Card):
    def __init__(self, *args, **kwargs):
        super(SkipNextTurn, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls, *args, **kwargs):
        return cls(**Card.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls, *args, **kwargs):
        return cls(**Card.defaults.get(cls.__name__))

    def play(self, *args, **kwargs):
        pass


class PlacingCooldown(Card):
    def __init__(self, *args, **kwargs):
        super(PlacingCooldown, self).__init__(*args, **kwargs)

    @classmethod
    def random_init(cls, *args, **kwargs):
        return cls(**Card.randomization.get(cls.__name__)())

    @classmethod
    def default_init(cls, *args, **kwargs):
        return cls(**Card.defaults.get(cls.__name__))

    def play(self, *args, **kwargs):
        pass
