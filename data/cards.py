"""This module contains all available rules."""

import random
from four_in_a_row_online.game_logic.game_logic import Game


class Card:
    card_by_name = dict()

    @staticmethod
    def play(*args, **kwargs):
        raise NotImplementedError()


class ShuffleTurnOrder(Card):
    @staticmethod
    def play(*args, **kwargs):
        game: Game = kwargs.get('game', None)
        if game:
            random.shuffle(game.participants)


class ReverseTurnOrder(Card):
    @staticmethod
    def play(*args, **kwargs):
        game: Game = kwargs.get('game', None)
        if game:
            # TODO: Mute the list thus that the player who had the last turn
            # TODO: has the next turn.

            # [1, 2, 3, 4, 5]
            #           ^
            # 4 → Reverse Turn Order
            # [5, 4, 3, 2, 1]
            # [2, 1, 5, 4, 3]
            #              ^
            game.participants.reverse()
            # game.participants = game.participants[] + game.participants[]


class SkipNextTurn(Card):
    @staticmethod
    def play(*args, **kwargs):
        game: Game = kwargs.get('game', None)
        if game:
            game.next_turn()
