"""This module contains all available rules."""

import random


class Card:
    card_by_name = dict()

    @staticmethod
    def play(*args, **kwargs):
        raise NotImplementedError()


class ShuffleTurnOrder(Card):
    @staticmethod
    def play(*args, **kwargs):
        game = kwargs.get('game', None)
        if game:
            random.shuffle(game.participants)


class ReverseTurnOrder(Card):
    @staticmethod
    def play(*args, **kwargs):
        game = kwargs.get('game', None)
        if game:
            # turn_id = 3, len = 5
            # [1, 2, 3, 4, 5]
            #           ^
            # 4 → Reverse Turn Order
            # [5, 4, 3, 2, 1]
            #
            # [2, 1, 5, 4, 3]
            #              ^
            game.participants.reverse()
            split = len(game.participants) - (game.current_turn() - 1) % len(game.participants)
            game.participants = game.participants[split:] + game.participants[:split]


class SkipNextTurn(Card):
    @staticmethod
    def play(*args, **kwargs):
        game = kwargs.get('game', None)
        if game:
            game.next_turn()

Card.card_by_name = {
    x.__name__: x for x in [ShuffleTurnOrder, ReverseTurnOrder, SkipNextTurn]
}
