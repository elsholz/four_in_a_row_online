import pytest
from game_logic.data import *
from game_logic.game_logic import *

n = 'This is the game name'
p = Player(name='PlayerA', token_style=TokenStyle(color=(255, 0, 0, 255), img_src='img source'))
p2 = Player(name='PlayerB', token_style=TokenStyle(color=(255, 0, 0, 255), img_src='img source'))
r = Rules(
    shuffle_turn_order_on_start=True,
    enable_chat=True,
    finish_game_on_disconnect=False,
    finish_game_on_win=True,
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
r2 = Rules(
    shuffle_turn_order_on_start=True,
    enable_chat=True,
    finish_game_on_disconnect=False,
    finish_game_on_win=True,
    allow_reconnect=True,
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
cd = CardDeck(
    card_shuffle_turn_order=False,
    card_reverse_turn_order=False,
    card_skip_next_turn=False,
    card_placing_cooldown=False,
)

g = Game(name=n, host=p, rules=r, card_deck=cd)


class TestGameLogic:
    class TestGameCreation:
        def test_new_game(self):
            assert g._current_turn is None
            assert g._game_state == GameState.lobby

            with pytest.raises(Game.GameCannotBeStarted):
                g.start_game()

            assert len(g.participants) == 1

            assert g.host == p

        def test_something_else(self):
            assert 1 == 1

    class TestPlayerJoin:
        def test_add_new_player(self):
            g.player_join(p=p2)

            assert len(g.participants) == 2

        def test_existing_player_join(self):
            with pytest.raises(Game.InvalidPlayer):
                g.player_join(p2)
            with pytest.raises(Game.InvalidPlayer):
                g.player_join(p)

            g.rules = r2
            with pytest.raises(Game.InvalidPlayer):
                g.player_join(p)

            with pytest.raises(Game.LobbyFull):
                g.player_join(Player(
                    name='Another player', token_style=TokenStyle(
                        color=(255, 150, 0, 255), img_src='img source')
                ))
            print(len(g.participants))
            g.player_leave(p)
            print(len(g.participants))
            g.player_join(p)
            print(len(g.participants))
            p.is_ready = True
            p2.is_ready = True
            g.start_game()
            g.player_leave(p)
            g.rules = r
            # don't allow reconnects
            with pytest.raises(Game.InvalidPlayer):
                g.player_join(p)

            g.rules = r2
            g.player_join(p)
            assert len(g.participants) == 2

        def test_indistinguishable_player_join(self):
            pass
            # TODO: check for distinguishable token styles
            # with pytest.raises(Game.IncalidPlayer):
            #    g.join(Player(
            #        name='Another player', token_style=TokenStyle(color=(255, 0, 0, 255), img_src='img source')
            #    ))

    class TestPlayerLeave:
        def test_non_existing_player_leave(self):
            with pytest.raises(Game.InvalidPlayer):
                g.player_leave(Player(
                    name='PlayerC', token_style=TokenStyle(color=(255, 0, 0, 255), img_src='img source')
                ))

            g.player_leave(p)
            assert g.host == p2
            assert len(g.participants) == 1


class TestBackend:
    assert True


class TestFrontend:
    assert True
