import pytest
from data import *
from game_logic import *


class TestGameLogic:
    class TestGameCreation:
        def test_new_game(self):
            n: str = 'This is the game name'
            p: Player = Player(name='PlayerA', token_style=TokenStyle(color=(255, 0, 0, 255), img_src='img source'))
            p2: Player = Player(name='PlayerB', token_style=TokenStyle(color=(255, 0, 0, 255), img_src='img source'))
            r: Rules = Rules(
                shuffle_turn_order_on_start=True,
                enable_chat=True,
                quit_game_on_disconnect=False,
                quit_game_on_win=True,
                allow_reconnect=False,
                winning_row_length=4,
                field_has_bounds=True,
                enable_cards=True,
                enable_cheats=False,
                number_of_players=2,
                start_game_if_all_ready=True,

                play_field_width=6,
                play_field_height=5,
                enable_gravity=True,
            )
            cd: CardDeck = CardDeck(
                card_shuffle_turn_order=False,
                card_reverse_turn_order=False,
                card_skip_next_turn=False,
                card_placing_cooldown=False,
            )

            g: Game = Game(name=n, participants=[p], rules=r, card_deck=cd)

            assert g._current_turn is None
            assert g._game_state == GameState.lobby

            with pytest.raises(Game.GameCannotBeStarted):
                g.start_game()

            assert len(g.participants) > 0



class TestBackend:
    assert True


class TestFrontend:
    assert True
