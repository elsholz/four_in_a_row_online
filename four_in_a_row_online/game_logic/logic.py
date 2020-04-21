from enum import Enum
from four_in_a_row_online.game_logic.data import PlayField, TokenStyle
from slugify import slugify
import datetime


class Game:
    def json(self):
        return {self.slug: {
            "name": self.name,
            "rules": self.rules.json(),
            "host": self.participants[0].json(),
            "participants": [x.json() for x in self.participants],
            "play_field": self._play_field.json(),
            "game_state": str(self._game_state),
            "current_turn": self.current_turn,
            "card_deck": self.card_deck.json(),
            "initial_players": [x.json() for x in self.initial_players or []],
            "creation_time": self.creation_time
        }}

    class State(Enum):
        started = "STARTED"
        finished = "FINISHED"
        quit = "QUIT"

    class CannotBeStarted(RuntimeError):
        """Exception so signalize that the game cannot be started, for example if there are not enough players."""

        class Reason(Enum):
            not_enough_players = 'not_enough_players'
            not_all_players_ready = 'not_all_players_ready'

        def __init__(self, reason: Reason):
            self.reason = reason

    class InvalidPlayer(ValueError):
        """This Exception is raised, if a Player tries to join a lobby that has some other player already
         with the same name, for example."""

    class IllegalAction(ValueError):
        """This Error signalizes that an action a player tried to execute did not succeed, because
        the current state of the game didn't allow it."""

    class LobbyFull(RuntimeError):
        """This Error is raised, if some player tries to join a game who's lobby has no more space."""

    def __init__(self, name, rules, card_deck, players):
        self.name = name
        self.rules = rules
        self.participants = players
        self._play_field = PlayField(dimensions=(self.rules.play_field_width, self.rules.play_field_height))
        self._game_state = Game.State.lobby
        self._current_turn = None
        self.card_deck = card_deck
        self.initial_players = None
        self._slug = slugify(f"game_{self.name}")
        self.creation_time = datetime.datetime.now()

    def __repr__(self):
        return str(self)

    def __str__(self):
        """Give out a beautiful oversight of the game."""
        return f'Game(\n' + ',\n\t'.join([f'{x}={str(x)}' for x in self.__dict__]) + '\n)'

    @property
    def slug(self):
        return self._slug

    @property
    def current_turn(self):
        return self._current_turn

    def place_token(self, player, loc_x, loc_y):
        # print(self._play_field.can_place_token(self.rules, player, loc_x, loc_y))
        if self._game_state == Game.State.started and player == self.participants[self._current_turn]:
            try:
                self._play_field.place_token(self.rules, player, loc_x, loc_y)
            except PlayField.IllegalTokenLocation:
                raise Game.IllegalAction()
        else:
            raise Game.IllegalAction()

        self.next_turn()

        print(f'Player {player.name} placed token on playfield at {(loc_x, loc_y)}.')

    def next_turn(self):
        self._current_turn = (self._current_turn + 1) % len(self.participants)

    def render_play_field(self):
        p = self._play_field
        x, y = p.dimensions
        for yi in reversed(range(y)):
            for xi in range(x):
                print(p.fields[yi][xi].location, end=' ')
            print()

    def finish_game(self):
        pass

    def quit_game(self):
        pass
