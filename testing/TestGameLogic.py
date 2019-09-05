from unittest import TestCase, main
from four_in_a_row_online.game_logic.data import *
from four_in_a_row_online.game_logic.game_logic import *


class TestData(TestCase):
    def test_token_style(self):
        # approve default behavior
        self.assertGreater(TokenStyle.default_init().color[3], 0)
        self.assertEqual(4, len(TokenStyle.default_init().color))
        self.assertTrue(all([0 <= c <= 255 for c in TokenStyle.default_init().color]))
        self.assertIsNone(TokenStyle.default_init().img_src)

        # approve explicitly specified behavior
        self.assertEqual(TokenStyle((255, 128, 64, 125)).color[3], 125)
        self.assertEqual(4, len(TokenStyle(color=(255, 255, 255, 255)).color))
        self.assertTrue(all([0 <= c <= 255 for c in TokenStyle((255, 255, 255, 255)).color]))
        self.assertIsNone(TokenStyle((123, 123, 123, 127)).img_src)

        with self.assertRaises(TokenStyle.TooTransparent):
            TokenStyle((123, 123, 123, 124))

        with self.assertRaises(TokenStyle.OutOfRange):
            TokenStyle((-1, 123, 123, 128))

        # approve random behavior
        random_token_styles = [TokenStyle.random_init() for _ in range(16)]

        for ts_a in random_token_styles:
            for ts_b in random_token_styles:
                if ts_a is ts_b:
                    self.assertEqual(ts_a, ts_b)
                else:
                    if ts_a == ts_b:
                        self.assertFalse(TokenStyle.distinguishable(ts_a, ts_b))

        for ts in random_token_styles:
            self.assertNotEqual(ts, TokenStyle.unique_random([ts]))
            self.assertNotEqual(ts, TokenStyle.unique_random(random_token_styles))
            self.assertEqual(ts, ts)

    def test_rules(self):
        self.assertEqual(len(Rules.default_init().__dict__), len(RulesData.data_fields))
        self.assertEqual(len(RulesData.defaults), len(RulesData.randomization))
        rules = [Rules.random_init() for _ in range(16)]

        for r in rules:
            self.assertNotEqual(r, Rules.unique_random([r]))
            self.assertNotEqual(r, Rules.unique_random(rules))
            self.assertEqual(r, r)
            # check that there is no number of players specified if the player count is variables
            self.assertEqual(r.variable_player_count, r.number_of_players is None)

    def test_card_deck(self):
        self.assertEqual(len(CardDeck.default_init().__dict__), len(CardDeckData.data_fields))
        self.assertEqual(len(CardDeckData.defaults), len(CardDeckData.randomization))
        card_decks = [CardDeck.random_init() for _ in range(16)]

        for cd in card_decks:
            self.assertNotEqual(cd, CardDeck.unique_random([cd]))
            self.assertNotEqual(cd, CardDeck.unique_random(card_decks))
            self.assertEqual(cd, cd)

    def test_player(self):
        self.assertEqual(len(Player.default_init().__dict__), len(PlayerData.data_fields))
        self.assertEqual(len(PlayerData.defaults), len(PlayerData.randomization))
        players = [Player.random_init() for _ in range(16)]

        for p in players:
            self.assertNotEqual(p, Player.unique_random([p]))
            self.assertNotEqual(p, Player.unique_random(players))
            self.assertEqual(p, p)

    def test_play_field(self):
        rules = Rules.default_init()

        four_x_four = PlayField(dimensions=(rules.play_field_width, rules.play_field_height))
        p1, p2 = Player.random_init(), Player.random_init()
        print(f'Player 1: {p1}\t Player 2:{p2}')

        four_x_four.place_token(rules, player=p1, loc_x=0, loc_y=0)

        # four_x_four.pretty_print()

        # assert error is raised, if player tries to put token where
        # 1. one of his tokens is already placed
        with self.assertRaises(PlayField.IllegalTokenLocation):
            four_x_four.place_token(rules, player=p1, loc_y=0, loc_x=0)
        # 2. one of his opponents tokens is already placed
        with self.assertRaises(PlayField.IllegalTokenLocation):
            four_x_four.place_token(rules, player=p2, loc_y=0, loc_x=0)

        with self.assertRaises(PlayField.IllegalTokenLocation):
            four_x_four.place_token(rules, player=p2, loc_y=2, loc_x=0)

        four_x_four.place_token(rules, player=p2, loc_y=1, loc_x=0)
        four_x_four.place_token(rules, player=p2, loc_y=2, loc_x=0)

        with self.assertRaises(PlayField.IllegalTokenLocation):
            four_x_four.place_token(rules, player=p2, loc_y=2, loc_x=2)
        # set rules to no gravity: token should be able to float
        rules.enable_gravity = False
        four_x_four.place_token(rules, player=p2, loc_y=2, loc_x=2)

        a = """
        Stuff left to test:
        
        player tries to place a token at a position where there is already on of their tokens
        player tries to place flying token without gravity
        player tries to place token where opponent token is already placed
        player tries to place token out of bounds
        specify reasons for invalid token locations        
        """
        print(four_x_four.pretty_print())

    def test_field(self):
        """Is there even anything to test here? Probably not…"""
        pass


class TestGameLogic(TestCase):
    def test_basic_game_creation(self):
        card_deck = CardDeck(
            card_shuffle_turn_order=True,
            card_reverse_turn_order=True,
            card_skip_next_turn=True,
            card_placing_cooldown=True,
        )

        rules = Rules.default_init()
        rules.__dict__.update({
            "shuffle_turn_order_on_start": True,
            "enable_chat": True,
            "finish_game_on_disconnect": True,
            "finish_game_on_win": True,
            "allow_reconnect": True,
            "winning_row_length": True,
            "field_has_bounds": True,
            "enable_cards": True,
            "enable_cheats": True,
            "number_of_players": 3,
            "start_game_if_all_ready": True,

            "play_field_width": 3,
            "play_field_height": 2,
            "enable_gravity": True
        })

        player_host = Player(name='im the host',
                             token_style=TokenStyle(color=(253, 3, 5), img_src=None))
        game = Game(name='test game 1', host=player_host, rules=rules, card_deck=card_deck)

        for a, b in zip([card_deck, rules, player_host, [player_host], 'test game 1'],
                        [game.card_deck, game.rules, game.host, game.participants, game.name]):
            self.assertEqual(a, b)

        with self.assertRaises(Game.CannotBeStarted):
            game.start_game()

        with self.assertRaises(Game.InvalidPlayer):
            game.player_join(p=player_host)

        with self.assertRaises(Game.InvalidPlayer):
            game.player_join(p=Player(name=player_host.name, token_style=TokenStyle.random_init()))

        # with self.assertRaises(Game.LobbyFull):
        #    game.player_join(Player.unique_random(game.participants))


if __name__ == '__main__':
    main()
