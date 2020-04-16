from dataclasses import dataclass
import random
from four_in_a_row_online.data import cards
from tools import flatten


class DataContainer:
    """Super class for all objects that can be initialized randomly or have a default. Basically just a tool to make
    testing a bit easier, since objects can be randomly generated."""
    data_fields = None
    defaults = None
    randomization = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def random_init(cls):
        return cls(**dict([(field, cls.randomization[field]()) for field in cls.data_fields]))

    @classmethod
    def default_init(cls):
        return cls(**{field: cls.defaults[field] for field in cls.data_fields})

    @classmethod
    def unique_random(cls, existing):
        while True:
            random_object = cls.random_init()
            # check that no object is equal to the random object
            if all([not x == random_object for x in existing]):
                return random_object

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return f'{self.__class__.__name__}(' + \
               f'{", ".join([k + "=" + str(v) for k, v in self.__dict__.items()])}' \
               + ')'

    def json(self):
        return {x: self.__dict__.get(x) for x in self.data_fields}


@dataclass
class CardDeckData:
    """Containing defaults and randomization for initialization of Card Decks."""

    data_fields = [
        x.__name__ for x in [
            cards.ShuffleTurnOrder,
            cards.ReverseTurnOrder,
            cards.SkipNextTurn,
        ]
    ]

    defaults = dict(zip(
        data_fields,
        [True, True, True]
    ))

    randomization = dict(zip(
        data_fields,
        [lambda: bool(random.getrandbits(1))] * 3
    ))


@dataclass
class CardDeck(CardDeckData, DataContainer):
    """Represents a Deck of cards. Cards can be placed by players, and represent a unique play action
    that alters the state of the game. Cards also have a cool down, so cards cannot be applied
    directly after one another. More detailed characteristics of cards and their role in the
    game mechanics is yet to be explored."""

    def __init__(self, **kwargs):
        DataContainer.__init__(self, **kwargs)

    def __eq__(self, other):
        return DataContainer.__eq__(self, other)

    @staticmethod
    def place_card(card: cards.Card, *args, **kwargs):
        card.play(*args, **kwargs)


@dataclass
class RulesData:
    """Class providing information for random rules initialization and default rules."""
    # TODO allow spectators
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
        variable_player_count
        play_field_width
        play_field_height
        enable_gravity
        game_is_public
        card_placement_cooldown'''.splitlines()]

    defaults = dict(zip(
        data_fields,
        [True, True, True, True, False, 4, True, False, False, 2, True, False, 7, 6, True, True, 3]
    ))

    randomization = dict(zip(
        data_fields,
        [lambda: bool(random.getrandbits(1)) for _ in range(5)] + [lambda: random.randrange(2, 16)] +
        [lambda: bool(random.getrandbits(1)) for _ in range(3)] + [lambda: random.randrange(2, 10)] +
        [lambda: bool(random.getrandbits(1))] * 2 + [lambda: random.randrange(2, 10)] * 2 +
        [lambda: bool(random.getrandbits(1))] * 2 + [lambda: random.randrange(0, 10)]
    ))


@dataclass
class Rules(RulesData, DataContainer):
    """Represents a set of rules, that apply to a game. Rules can both affect the game mecahnics directly
    or affect some meta data for the game. An instance of the latter case is the rul `game_is_public`,
    which is used to define whether or not the game will be accessible to players via a list of all
    available games, or if they can just be joined directly."""

    def __init__(self, **kwargs):
        DataContainer.__init__(self, **kwargs)

    def __eq__(self, other):
        return DataContainer.__eq__(self, other)

    def random_init(*args, **kwargs):
        obj = Rules(**dict([(field, RulesData.randomization[field]()) for field in RulesData.data_fields]))

        if not obj.start_game_if_all_ready:
            obj.variable_player_count = False

        if obj.variable_player_count:
            obj.number_of_players = None
        return obj


@dataclass
class TokenStyleData:
    """Holds data for randomization and default initialization of token styles."""
    data_fields = [x.strip() for x in '''color'''.splitlines()]
    # img_src

    defaults = dict(zip(
        data_fields,
        [(255, 3, 5, 255), ]  # None]
    ))

    randomization = dict(zip(
        data_fields,
        [lambda: tuple(random.randrange(0, 255) for _ in range(3)) + (random.randrange(125, 255),)]  # + [lambda: None]
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

    # img_src: str

    def __init__(self, color):  # , img_src=None):
        self.color = color
        # self.img_src = img_src
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
    def is_dinguishable_init(cls, existing):
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


class PlayerData:
    """Offering default and randomization values and functions for player class initialization."""
    data_fields = [x.strip() for x in '''name
    token_style
    is_ready'''.splitlines()]

    defaults = dict(zip(
        data_fields,
        ['player host', TokenStyle.default_init(), False]
    ))

    randomization = dict(zip(
        data_fields,
        [lambda: ('player no ' + str(random.randrange(100, 999)))] + [TokenStyle.random_init] + [
            lambda: bool(random.getrandbits(1))]
    ))


class Player(PlayerData, DataContainer):
    """Represents a player."""

    data_fields = PlayerData.data_fields
    defaults = PlayerData.defaults
    randomization = PlayerData.randomization

    def __init__(self, name, token_style, is_ready=False):
        self.name = name
        self.token_style = token_style
        self.is_ready = is_ready

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

    @classmethod
    def unique_random(cls, existing):
        while True:
            random_object = cls.random_init()
            # check that no object is equal to the random object
            if all([(not x == random_object) and (not x.token_style == random_object.token_style) for x in existing]):
                return random_object


@dataclass
class PlayField:
    """Data class to represent a play field of variable size."""

    class IllegalTokenLocation(ValueError):
        """Exception to signify that the token can't be placed at the selected location."""
        pass

    dimensions: (int, int)
    fields: []
    player_colors_pretty_print: dict

    def __init__(self, dimensions):
        self.dimensions = dimensions
        width, height = self.dimensions
        self.fields = [[Field((x, y)) for x in range(width)] for y in range(height)]
        self.player_colors_pretty_print = {}

    def _check_for_winning_rows(self, rules, player):
        """Check, if there are any rows on the field long enough for the specified player to win the game."""

        # New Idea:
        # 1.    For all cells that are held by the specified player on the play field:
        #           Add to the dictionary a tuple of the field's coordinates mapped to all directions.
        # 2.    Save all locations (which are the keys of the dictionary) to a list.
        # 3.    Iterate through the newly created list:
        #           For each location, get either the directions or an empty list from the dictionary and
        #           iterate through all directions
        #           For each direction, go in that direction as far as possible
        #           For each step that does not break the row, for that step's location remove the direction

        applicable_fields = [f for row in self.fields for f in row if f.occupation == player]

        directions = [
            # x, y
            (-1, 1), (0, 1), (1, 1), (1, 0)
        ]

        # 1.
        origins = {cell.location: list(directions) for cell in applicable_fields}

        # 2. and 3.
        for current_location in list(origins.keys()):
            directions = origins.get(current_location, [])

            for current_direction in list(directions):
                # Follow the current direction as far as possible
                row = [current_location]
                next_location = current_location
                br = False

                while True:
                    next_location = flatten(next_location, current_direction)

                    if br:
                        directions.remove(current_direction)
                        break
                    if (
                            rules.field_has_bounds and (0 <= next_location[0] < rules.play_field_width)
                            and (0 <= next_location[1] < rules.play_field_height)
                    ):
                        if self.get_field(next_location[0], next_location[1]).occupation == player:
                            next_directions = origins.get(next_location, [])
                            if next_directions:
                                next_directions.remove(current_direction)
                            row.append(next_location)
                            if len(row) == rules.winning_row_length:
                                return row

                        else:
                            br = True
                    else:
                        br = True

    def get_field(self, x, y):
        return self.fields[y][x]

    def place_token(self, rules, player, loc_x, loc_y):
        if player not in self.player_colors_pretty_print:
            self.player_colors_pretty_print[player] = [
                'x', 'o', '*', '#'
            ][len(self.player_colors_pretty_print)]

        def pt():
            self.fields[loc_y][loc_x].occupation = player

        x, y = self.dimensions
        if 0 <= loc_x < x and 0 <= loc_y < y:
            if rules.enable_gravity:
                if ((loc_y == 0 or self.fields[loc_y - 1][loc_x].occupation is not None) and
                        self.fields[loc_y][loc_x].occupation is None):
                    pt()
                else:
                    # print(loc_x, loc_y, self.fields[loc_y - 1][loc_x].occupation, self.fields[loc_y][loc_x])
                    raise PlayField.IllegalTokenLocation()
            else:
                if self.fields[loc_y][loc_x].occupation is None:
                    pt()
                else:
                    raise PlayField.IllegalTokenLocation()
        else:
            raise PlayField.IllegalTokenLocation()

    def remove_token(self, x, y):
        self.fields[y][x].occupation = None

    def pretty_print(self, curses=False):
        res = ['']
        # self.player_colors_pretty_print[x.occupation]+ ansi.Fore.BLUE

        for line in reversed(self.fields):
            res.append(
                "".join(["|".join([''] + [
                    6 * self.player_colors_pretty_print[
                        x.occupation] if x.occupation else '      ' for x in line
                ] + ['']) + '\n'] * 3)
            )
        res.append('')
        joint = ('-' * ((len(res[1]) - 2) // 3)) + '\n'
        # print(joint)
        return joint.join(res)

    def json(self):
        return {
            "dimensions": self.dimensions,
            "fields": [
                [f.json() for f in row] for row in self.fields
            ]
        }


@dataclass
class Field:
    """Data class to represent a single cell on a play field. The field can be occupied or empty.
    The absolute location of the field in the play field is also saved."""
    occupation: Player
    location: (int, int)

    def __init__(self, location):
        self.occupation = None
        self.location = location

    def json(self):
        return {
            "occupation": self.occupation,
            "location": self.location
        }
