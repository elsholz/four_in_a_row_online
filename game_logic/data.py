from collections import namedtuple
from dataclasses import dataclass
import webcolors
import random


class DataContainer:
    """Super class for all objects that can be initialized randomly or have a default. Basically just a tool to make
    testing a bit easier, since objects can be randomly generated."""
    data_fields = None
    defaults = None
    randomization = None
    constraints = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

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
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

@dataclass
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

    constraints = None


@dataclass()
class CardDeck(CardDeckData, DataContainer):
    def __init__(self, **kwargs):
        DataContainer.__init__(self, **kwargs)
        
    def __eq__(self, other):
        return DataContainer.__eq__(self, other) 


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


@dataclass
class Rules(RulesData, DataContainer):
    def __init__(self, **kwargs):
        DataContainer.__init__(self, **kwargs)
       
    def __eq__(self, other):
        return DataContainer.__eq__(self, other) 

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
        [lambda: tuple(random.randrange(0, 255) for _ in range(3)) + (random.randrange(125, 255),)] + [lambda: None]
    ))


@dataclass
class TokenStyle(TokenStyleData, DataContainer):
    """Represent the visual apperance of a player's play token. The TokenStyle will only contain a color, represented
    as a tuple of RGBα values. To assure visibility, the α value must be at least 124. To allow a player to use their
    chosen TokenStyle, the color has to be distinguishable from all the other player's token's colors."""

    class TooTransparent(ValueError):
        """The color's alpha value is too low."""

    class OutOfRange(ValueError):
        """The color's values are not within the allowed range."""

    color: (int, int, int, int)
    img_src: str

    def __init__(self, color, img_src=None):
        self.color = color
        self.img_src = img_src
        if len(color) > 3:
            # assert some visibility
            if not color[-1] > 124:
                raise TokenStyle.TooTransparent()
        for value in color:
            if not 0 <= value <= 255:
                raise TokenStyle.OutOfRange()

    @staticmethod
    def distinguishable(a, b):
        """Determines whether two TokenStyles are distinguishable by the human eye. Based on simple math."""
        # returns True, if the token styles are distinguishable
        # take into account alpha values. Maybe
        return sum([abs(col_a - col_b) for col_a, col_b in zip(a.color, b.color)]) > (4 * 30)

    @classmethod
    def istinguishable_init(cls, existing):
        """Instantiates the class TokenStyle randomly until an instance is distinguishable from a list of other
        TokenStyles in which case that instance is then returned."""
        while True:
            token_style = cls.random_init()
            if all([TokenStyle.distinguishable(token_style, x) for x in existing]):
                return token_style

    def __eq__(self, other):
        """Override the euqality operator to improve readability. Checks for excact matches shall always make use of
        the `is` operator."""
        return not TokenStyle.distinguishable(self, other)


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
        [lambda : ('player no ' + str(random.randrange(100, 999)))] + [TokenStyle.random_init] + [
            lambda: bool(random.getrandbits(1))]
    ))


@dataclass
class Player(PlayerData, DataContainer):
    """Data class to represent a player."""
    name: str
    token_style: TokenStyle
    is_ready: bool

    # data_fields = PlayerData
    # defaults = PlayerData.defaults
    # randomization = PlayerData.randomization

    def __init__(self, name, token_style, is_ready=False):
        self.name = name
        self.token_style = token_style
        self.is_ready = False
    


@dataclass
class PlayField:
    """Data class to represent a play field of variable size."""

    class IllegalTokenLocation(ValueError):
        """Exception to signify that the token can't be placed at the selected location."""
        pass

    dimensions: (int, int)
    fields: []

    def __init__(self, dimensions):
        self.dimensions = dimensions
        x, y = self.dimensions
        self.fields = [[Field((x, y)) for x in range(x)] for y in range(y)]

    def _check_for_winning_rows(self, rules, player):
        """Check, if there are any rows on the field long enough for the specified player to win the game."""
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
    """Data class to represent a single field on a play field. The field can be occupied or empty. 
    The absolute location of the field in the play field is also saved."""
    occupation: Player
    location: (int, int)

    def __init__(self, location):
        self.occupation = None
        self.location = location
