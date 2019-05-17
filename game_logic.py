import random
from locales import *
from data import Rules, CardDeck, PlayField, Player, TokenStyle, Field

GameState = enum.Enum('GameState', 'lobby started finished quit')


class Game:
    class GameCannotBeStarted(Exception):
        pass

    class InvalidPlayer(Exception):
        pass

    class IllegalAction(Exception):
        pass

    class LobbyFull(Exception):
        pass

    def __init__(self, name, host, rules, card_deck):
        self.name = name
        self.rules = rules
        self.host = host
        self.participants = [host]
        self._play_field = PlayField(dimensions=(self.rules.play_field_width, self.rules.play_field_height))
        self._game_state = GameState.lobby
        self._current_turn = None
        self.card_deck = card_deck

    def __repr__(self):
        return str(self)

    def __str__(self):
        nl = '\n'
        return f'Game(\n\tname={self.name}\n\trules={self.rules},\n\tparticipants=[\n{f"{nl}".join([f"        name={p.name}, token_style={p.token_style}, is_ready={p.is_ready}" for p in self.participants])}\n    ],\n\t_play_field={self._play_field},' \
               f'\n\tgame_sate={self._game_state},\n\t_current_turn={self._current_turn}\n)'

    def start_game(self):
        if self.rules.start_game_if_all_ready and all([p.is_ready for p in self.participants]):
            self._game_state = GameState.started

        elif self.rules.number_of_players == len(self.participants):
            self._game_state = GameState.started
        else:
            if self.rules.start_game_if_all_ready:
                raise Game.GameCannotBeStarted('Not all players are ready')
            else:
                raise Game.GameCannotBeStarted('Not enough players')
        self._current_turn = 0
        if self.rules.shuffle_turn_order_on_start:
            random.shuffle(self.participants)
        self.initial_players = self.participants[:]

        # print(f'Started Game {self.name} with {len(self.participants)} players ({self.participants})')

    def place_token(self, player, loc_x, loc_y):
        # print(self._play_field.can_place_token(self.rules, player, loc_x, loc_y))
        if (self._game_state == GameState.started and player == self.participants[self._current_turn]):
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

    @DeprecationWarning
    def _start(self):
        if self.rules.shuffle_turn_order_on_start:
            random.shuffle(self.participants)
        self.initial_players = self.participants[:]

    def player_join(self, p):
        if self._game_state == GameState.started:
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
