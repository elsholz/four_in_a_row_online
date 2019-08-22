from collections import namedtuple
from dataclasses import dataclass
import webcolors

webcolors.CSS3_HEX_TO_NAMES

CardDeck = namedtuple(
    typename='CardDeck',
    field_names='''
    card_shuffle_turn_order
    card_reverse_turn_order
    card_skip_next_turn
    card_placing_cooldown
    '''
)

Rules = namedtuple(
    typename='Rules',
    field_names='''    
    shuffle_turn_order_on_start
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
    enable_gravity
    '''
)


@dataclass
class TokenStyle:
    color: (int, int, int, int)
    img_src: str

    def __init__(self, color, img_src):
        self.color = color
        self.img_src = img_src

    @staticmethod
    def distinguishable(a, b):
        # returns True, if the token styles are distinguishable
        return True


@dataclass
class Player:
    name: str
    token_style: TokenStyle
    is_ready: bool

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
