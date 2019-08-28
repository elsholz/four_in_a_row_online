from collections import namedtuple
from dataclasses import dataclass
import webcolors
import random


class DataContainer:
    data_fields = None
    defaults = None
    randomization = None

    @classmethod
    def random_init(cls):
        return cls(**dict([(field, cls.randomization[field]()) for field in cls.data_fields]))

    @classmethod
    def default_init(cls):
        return cls(**dict([field, cls.defaults[field]] for field in cls.data_fields))

    @classmethod
    def unique_random(cls, existing):
        while True:
            random_object = cls.random_init()
            # check that no object is equal to the random object
            if all([not x == random_object for x in existing]):
                return random_object


class CardDeckData:
    data_fields = [x.strip() for x in '''card_shuffle_turn_order
                card_reverse_turn_order
                card_skip_next_turn
                card_placing_cooldown'''.splitlines()]

    defaults = dict(zip(
        data_fields,
        [True, True, True, 4]
    ))

    randomization = dict(zip(
        data_fields,
        [lambda: bool(random.getrandbits(1))] * 3 + [lambda: random.randrange(0, 10)]
    ))


class CardDeck(
    CardDeckData, namedtuple(
        'CardDeck',
        field_names=CardDeckData.data_fields,
        defaults=CardDeckData.defaults.items()
    ), DataContainer
):
    pass


@dataclass
class RulesData:
    data_fields = [x.strip() for x in '''shuffle_turn_order_on_start
        enable_chat
        finish_game_on_disconnect
        finish_game_on_win
        allow_reconnect
        winning_row_length
        field_has_bounds
        enable_cards
        enable_cheats
        number_of_players
        start_game_if_all_ready
        play_field_width
        play_field_height
        enable_gravity'''.splitlines()]

    defaults = dict(zip(
        data_fields,
        [True, True, True, True, False, 4, True, False, False, 2, True, 8, 6, True]
    ))

    randomization = dict(zip(
        data_fields,
        [lambda: bool(random.getrandbits(1)) for _ in range(5)] + [lambda: random.randrange(2, 16)] +
        [lambda: bool(random.getrandbits(1)) for _ in range(3)] + [lambda: random.randrange(2, 10)] +
        [lambda: bool(random.getrandbits(1))] + [lambda: random.randrange(2, 10)] * 2 +
        [lambda: bool(random.getrandbits(1))]
    ))


class Rules(
    RulesData,
    namedtuple(
        'Rules',
        field_names=RulesData.data_fields,
        defaults=RulesData.defaults.items()
    ),
    DataContainer
):
    pass


@dataclass
class TokenStyleData:
    data_fields = [x.strip() for x in '''color
                img_src'''.splitlines()]

    defaults = dict(zip(
        data_fields,
        [(255, 3, 5, 255), None]
    ))

    randomization = dict(zip(
        data_fields,
        [lambda: tuple(random.randrange(0, 255) for _ in range(4))] + [lambda: None]
    ))


@dataclass
class TokenStyle(TokenStyleData, DataContainer):
    color: (int, int, int, int)
    img_src: str

    def __init__(self, color, img_src):
        self.color = color
        self.img_src = img_src
        if len(color) > 3:
            # assert some visibility
            assert color[-1] > 124

    @staticmethod
    def distinguishable(a, b):
        # returns True, if the token styles are distinguishable
        # take into account alpha values. Maybe
        return sum([abs(col_a - col_b) for col_a, col_b in zip(a.color, b.color)]) > (4 * 30)

    @classmethod
    def distinguishable_init(cls, existing):
        while True:
            token_style = cls.random_init()
            if all([TokenStyle.distinguishable(token_style, x) for x in existing]):
                return token_style


class PlayerData():
    data_fields = [x.strip() for x in '''name
    token_style
    is_ready'''.splitlines()]

    defaults = dict(zip(
        data_fields,
        ['player host', TokenStyle.default_init(), False]
    ))

    randomization = dict(zip(
        data_fields,
        ['player no ' + str(random.randrange(100, 999))] + [TokenStyle.random_init()] + [
            lambda: bool(random.getrandbits(1))]
    ))


@dataclass
class Player(PlayerData, DataContainer):
    name: str
    token_style: TokenStyle
    is_ready: bool

    # data_fields = PlayerData
    # defaults = PlayerData.defaults
    # randomization = PlayerData.randomization

    def __init__(self, name, token_style):
        self.name = name
        self.token_style = token_style
        self.is_ready = False


@dataclass
class PlayField:
    class IllegalTokenLocation(Exception):
        pass

    dimensions: (int, int)
    fields: []

    def __init__(self, dimensions):
        self.dimensions = dimensions
        x, y = self.dimensions
        self.fields = [[Field((x, y)) for x in range(x)] for y in range(y)]

    def _check_for_winning_rows(self, rules, player):
        applicable_fields = [f for row in self.fields for f in row if f.occupation == player]
        start_points = set()
        for field in applicable_fields:
            if rules.field_has_bounds:
                if set() == {
                    f for f in applicable_fields if
                    abs(f.location[0] - field.location[0]) > 1 or
                    abs(f.location[1] - field.location[1]) > 1
                }:
                    start_points.add(field)
            else:
                if set() == {
                    f for f in applicable_fields if
                    abs((1 + f.location[0]) % self.dimensions[0] - field.location[0]) == 1 or
                    abs((1 + f.location[1]) % self.dimensions[1] - field.location[1]) == 1
                }:
                    start_points.add(field)

        for pivot in start_points:
            # create row object for each direction. For each direction go through until the next field is no longer
            # within applicable_fields
            pass

    def place_token(self, rules, player, loc_x, loc_y):
        def pt():
            self.fields[loc_y][loc_x].occupation = player

        x, y = self.dimensions
        if 0 <= loc_x < x and 0 <= loc_y < y:
            if rules.enable_gravity:
                if ((loc_y == 0 or self.fields[loc_y - 1][loc_x].occupation is not None) and
                        self.fields[loc_y][loc_x].occupation is None):
                    pt()
                else:
                    print(loc_x, loc_y, self.fields[loc_y - 1][loc_x].occupation, self.fields[loc_y][loc_x])
                    raise PlayField.IllegalTokenLocation()
            else:
                if self.fields[loc_y][loc_x] is None:
                    pt()
        else:
            raise PlayField.IllegalTokenLocation()


@dataclass
class Field:
    occupation: Player
    location: (int, int)

    def __init__(self, location):
        self.occupation = None
        self.location = location
