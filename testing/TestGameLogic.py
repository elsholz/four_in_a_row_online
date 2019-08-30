from unittest import TestCase, main
from four_in_a_row_online.game_logic.data import *
from loguru import logger


class TestGameLogic(TestCase):
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
        rules = [Rules.random_init() for _ in range(8)]

        for r in rules:
            self.assertNotEqual(r, Rules.unique_random([r]))
            self.assertNotEqual(r, Rules.unique_random(rules))
            self.assertEqual(r, r)
            
    def test_card_deck(self):
        self.assertEqual(len(CardDeck.default_init().__dict__), len(CardDeckData.data_fields))
        card_decks = [CardDeck.random_init() for _ in range(8)]

        for cd in card_decks:
            self.assertNotEqual(cd, CardDeck.unique_random([cd]))
            self.assertNotEqual(cd, CardDeck.unique_random(card_decks))
            self.assertEqual(cd, cd)


if __name__ == '__main__':
    main()
