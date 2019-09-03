import random
from enum import Enum
from four_in_a_row_online.game_logic.data import Rules, CardDeck, PlayField, Player, TokenStyle, Field


class Game:
    class State(Enum):
        lobby = 0
        started = 1
        finished = 2
        quit = 3

    class CannotBeStarted(RuntimeError):
        """Exception so signalize that the game cannot be started, for example if there are not enough players."""

        class Reason(Enum):
            not_enough_players = 'not_enough_players'
            not_all_players_ready = 'not_all_players_ready'

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
        # TODO: Optional: move play field creation to the rules.apply part, when the game is started
        self._play_field = None  # PlayField(dimensions=(self.rules.play_field_width, self.rules.play_field_height))
        self._game_state = Game.State.lobby
        self._current_turn = None
        self.card_deck = card_deck
        self.initial_players = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        """Give out a beautiful oversight of the game."""
        # nl = '\n'
        # return f'Game(\n\tname={self.name}\n\trules={self.rules},\n\tparticipants=[\n{f"{nl}".join(' + f'[f"        name={p.name}, token_style={p.token_style}, is_ready={p.is_ready}" for p in self.participants])}\n    ],\n\t_play_field={self._play_field},' \
        #        f'\n\tgame_sate={self._game_state},\n\t_current_turn={self._current_turn}\n)'

        # TODO: test
        return f'Game(\n' + ',\n\t'.join([f'{x}={str(x)}' for x in self.__dict__]) + '\n)'

    def start_game(self, host_decision=False):
        """Function called from the backend to start the game, if it can be started.f"""

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

            # apply the rules, e.g. shuffle the turn order on start
            self.rules.apply(game=self, game_starts_now=True)
            self.initial_players = self.participants[:]

    def place_token(self, player, loc_x, loc_y):
        # print(self._play_field.can_place_token(self.rules, player, loc_x, loc_y))
        if self._game_state == Game.State.started and player == self.participants[self._current_turn]:
            try:
                self._play_field.place_token(self.rules, player, loc_x, loc_y)
            except PlayField.IllegalTokenLocation:
                raise Game.IllegalAction()
        else:
            raise Game.IllegalAction()

        if self._current_turn < len(self.participants) - 1:
            self._current_turn += 1
        else:
            self._current_turn = 0

        print(f'Player {player.name} placed token on playfield at {(loc_x, loc_y)}.')

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
