from enum import Enum
from four_in_a_row_online.game_logic.data import PlayField, TokenStyle
from slugify import slugify
import datetime


class Game:
    def json(self):
        return {self.slug: {
            "name": self.name,
            "rules": self.rules.json(),
            "host": self.host.json(),
            "participants": [x.json() for x in self.participants],
            "play_field": self._play_field.json(),
            "game_state": str(self._game_state),
            "current_turn": self.current_turn,
            "card_deck": self.card_deck.json(),
            "initial_players": [x.json() for x in self.initial_players or []],
            "creation_time": self.creation_time
        }}

    class State(Enum):
        lobby = "LOBBY"
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

    def __init__(self, name, host, rules, card_deck):
        self.name = name
        self.rules = rules
        self.host = host
        self.participants = [host]
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

    def start_game(self, host_decision=False):
        """"""

        def game_can_be_started(_host_decision):
            """Decide if the game can be started. Otherwise raise an exception stating the reason for the failure
            to be handled by the backend."""
            if self.rules.start_game_if_all_ready:
                # Case 1: All Players are ready
                if all(p.is_ready for p in self.participants):
                    # Case 1.1: Number of players variable
                    if self.rules.variable_player_count:
                        # Case 1.1.1: Enough Players in Lobby → start game
                        if len(self.participants) > 1:
                            return True
                        # Case 1.1.2: Not enough players for a game → Game cannot be started
                        else:
                            raise Game.CannotBeStarted(Game.CannotBeStarted.Reason.not_enough_players)

                    # Case 1.2: Number of Players fixed
                    else:
                        # Case 1.2.1: Lobby is full → start game
                        if len(self.participants) == self.rules.number_of_players:
                            return True
                        # Case 1.2.2: Not enough players → Game cannot be started
                        else:
                            # Case 1.2.2.1: Host decided for the game to start → start game
                            if _host_decision:
                                return True
                            # Case 1.2.2.2: No host decision → Game cannot be started
                            else:
                                raise Game.CannotBeStarted(Game.CannotBeStarted.Reason.not_enough_players)

                # Case 2: Not all players are ready → Game cannot be started
                else:
                    raise Game.CannotBeStarted(Game.CannotBeStarted.Reason.not_all_players_ready)

            else:
                # Case 1: Lobby full → start game
                if len(self.participants) == self.rules.number_of_players:
                    return True

                # Case 2: Lobby not full (Host initiated start)
                else:
                    # Case 2.1: Enough players → start game
                    if len(self.participants) > 1:
                        return True
                    # Case 2.2: Not enough players → Game cannot be started
                    else:
                        raise Game.CannotBeStarted(Game.CannotBeStarted.Reason.not_enough_players)

        if game_can_be_started(host_decision):
            self._game_state = Game.State.started
            self._current_turn = 0

            # if self.rules.shuffle_turn_order_on_start:
            #    random.shuffle(self.participants)
            # replaced by:
            # self.rules.apply(game=self)

            self.initial_players = self.participants[:]

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

    def player_join(self, p):
        if self._game_state == Game.State.started:
            if not self.rules.allow_reconnect:
                raise Game.InvalidPlayer()
            else:
                if p not in self.participants:
                    if not any(p.name == x.name for x in self.initial_players):
                        self.participants.append(p)
        else:
            if any([
                not TokenStyle.distinguishable(x.token_style, p.token_style)
                for x in self.participants
            ]) or any([p.name == x.name for x in self.participants]):
                raise Game.InvalidPlayer()

            if not len(self.participants) < self.rules.number_of_players:
                raise Game.LobbyFull(len(self.participants))

        self.participants.append(p)

    def player_leave(self, p):
        # NOTE: Backend will only make one copy per player for certain (except for reconnects)
        if p in self.participants:
            print('before:', self.participants)
            self.participants.remove(p)
            print('after:', self.participants)
        else:
            raise Game.InvalidPlayer

        if len(self.participants) == 0:
            self.quit_game()

        elif p == self.host:
            self.host = self.participants[0]

        if self.rules.finish_game_on_disconnect:
            self.finish_game()
            # self._game_state = GameState.lobby

    def finish_game(self):
        pass

    def quit_game(self):
        pass
