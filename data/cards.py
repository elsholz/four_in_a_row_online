"""This module contains all available rules."""

import random


class Card:
    card_by_name = dict()

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    def __bool__(self):
        return self.__dict__.get('value', False)

    def play(self, *args, **kwargs):
        raise NotImplementedError()


class ShuffleTurnOrder(Card):
    def __init__(self, *args, **kwargs):
        super(ShuffleTurnOrder, self).__init__(*args, **kwargs)

    def play(self, *args, **kwargs):
        pass


class ReverseTurnOrder(Card):
    def __init__(self, *args, **kwargs):
        super(ReverseTurnOrder, self).__init__(*args, **kwargs)

    def play(self, *args, **kwargs):
        pass


class SkipNextTurn(Card):
    def __init__(self, *args, **kwargs):
        super(SkipNextTurn, self).__init__(*args, **kwargs)

    def play(self, *args, **kwargs):
        pass


Card.card_by_name.update(
    dict(
        zip(
            [
                x.strip() for x in '''card_shuffle_turn_order
                card_reverse_turn_order
                card_skip_next_turn'''.splitlines()
            ], [
                ShuffleTurnOrder,
                ReverseTurnOrder,
                SkipNextTurn
            ]
        )
    )
)
