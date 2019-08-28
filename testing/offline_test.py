from loguru import logger
import pytest
from four_in_a_row_online.game_logic import game_logic
import os
import unittest


class TestGameCreation(unittest.TestCase):
    '''
    cd = game_logic.CardDeck(
        card_shuffle_turn_order=True,
        card_reverse_turn_order=True,
        card_skip_next_turn=True,
        card_placing_cooldown=True,
    )

    r = game_logic.Rules(
        shuffle_turn_order_on_start=True,
        enable_chat=True,
        quit_game_on_disconnect=True,
        quit_game_on_win=True,
        allow_reconnect=True,
        winning_row_length=True,
        field_has_bounds=True,
        enable_cards=True,
        enable_cheats=True,
        number_of_players=3,
        start_game_if_all_ready=True,

        play_field_width=3,
        play_field_height=2,
        enable_gravity=True,
    )

    p = game_logic.Player(name='player host', token_style=game_logic.TokenStyle(color=(255, 0, 0, 255), img_src=None))

    game = game_logic.Game(name='test game 1', host=p, rules=r, card_deck=None)
    # print(game)
    game.render_play_field()
    p2 = game_logic.Player(name='player 2', token_style=game_logic.TokenStyle(color=(0, 255, 0, 255), img_src=None))
    p3 = game_logic.Player(name='player 3', token_style=game_logic.TokenStyle(color=(0, 0, 255, 255), img_src=None))
    game.player_join(p=p2)
    game.player_join(p=p3)

    p2.is_ready = True
    p3.is_ready = True
    p.is_ready = True

    print(game)

    game.start_game()
    print('GAME STATE:', str(game._game_state))
    print(game)

    game.place_token(player=game.participants[0], loc_x=0, loc_y=0)

    print(game._play_field)
    '''

    def test_basic_game_creation(self):
        card_deck = game_logic.CardDeck(
            card_shuffle_turn_order=True,
            card_reverse_turn_order=True,
            card_skip_next_turn=True,
            card_placing_cooldown=True,
        )

        rules = game_logic.Rules(
            shuffle_turn_order_on_start=True,
            enable_chat=True,
            finish_game_on_disconnect=True,
            finish_game_on_win=True,
            allow_reconnect=True,
            winning_row_length=True,
            field_has_bounds=True,
            enable_cards=True,
            enable_cheats=True,
            number_of_players=3,
            start_game_if_all_ready=True,

            play_field_width=3,
            play_field_height=2,
            enable_gravity=True,
        )

        player_host = game_logic.Player(name='im the host',
                                        token_style=game_logic.TokenStyle(color=(253, 3, 5), img_src=None))
        game = game_logic.Game(name='test game 1', host=player_host, rules=rules, card_deck=card_deck)

        for a, b in zip([card_deck, rules, player_host, [player_host], 'test game 1'],
                        [game.card_deck, game.rules, game.host, game.participants, game.name]):
            self.assertEqual(a, b)
            logger.debug('\n' + str(a) + '\n' + str(b))

        with self.assertRaises(game_logic.Game.GameCannotBeStarted):
            game.start_game()

        with self.assertRaises(game_logic.Game.InvalidPlayer):
            game.player_join(p=player_host)

        with self.assertRaises(game_logic.Game.InvalidPlayer):
            game.player_join(p=game_logic.Player(name=player_host.name, token_style=game_logic.TokenStyle.random()))

        with self.assertRaises(game_logic.Game.LobbyFull):
            game.player_join()


class TestRandomCardDeck(unittest.TestCase):
    def test_basic(self):
        self.assertNotEqual(game_logic.CardDeck.random(), game_logic.CardDeck.random())


class TestRandomRules(unittest.TestCase):
    def test_basic(self):
        self.assertNotEqual(game_logic.Rules.random(), game_logic.Rules.random())


if __name__ == '__main__':
    unittest.main()
