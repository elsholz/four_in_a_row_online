from flask import json as JSON
from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO
import os
import pathlib
from base64 import b64encode
from werkzeug import exceptions
from slugify import slugify
from four_in_a_row_online.game_logic import data, logic
import jsonschema
from four_in_a_row_online.backend import schema
from time import sleep
from threading import Thread, Lock
from flask_session import Session
import datetime
from four_in_a_row_online.loggers.loggers import games_logger, requests_logger, stats_logger
from ast import literal_eval
from collections import OrderedDict


class Lobby:
    def __init__(self, lobby_name, lobby_slug, allow_rule_voting, list_publicly, max_number_of_players):
        self.games = []
        self.current_game = None
        self.players_by_session = OrderedDict()
        self.lobby_name = lobby_name
        self.lobby_slug = lobby_slug
        self.allow_rule_voting = allow_rule_voting
        self.list_publicly = list_publicly
        self.max_number_of_players = max_number_of_players
        self.creation_time = datetime.datetime.now()
        self.name_space = '/' + self.lobby_slug

        self.next_rules = data.Rules.default_init()
        self.next_card_deck = data.CardDeck.default_init()

        @RequestHandler.socketio.on("connect", namespace=self.name_space)
        def handle_player_join(json=None):
            if "connection_id" not in session:
                session["connection_id"] = b64encode(os.urandom(2 ** 5))
            requests_logger.debug(
                f"{session.get('connection_id', None)} connected to game {self.lobby_name} at /{self.lobby_slug}."
            )

            if json:
                if jsonschema.validate(json, schema.player_schema):
                    token_style_data = json["token_style"]
                    token_style = data.TokenStyle(color=tuple(token_style_data["color"]))
                    player = data.Player(json['player_name'], token_style)
                    if not self.current_game and len(self.players_by_session) < max_number_of_players:
                        self.players_by_session[session["connection_id"]] = player


                    ########
                    def player_join(self, p):
                        if self._game_state == logic.Game.State.started:
                            if not self.rules.allow_reconnect:
                                raise logic.Game.InvalidPlayer()
                            else:
                                if p not in self.participants:
                                    if not any(p.name == x.name for x in self.initial_players):
                                        self.participants.append(p)
                        else:
                            if any([
                                not data.TokenStyle.distinguishable(x.token_style, p.token_style)
                                for x in self.participants
                            ]) or any([p.name == x.name for x in self.participants]):
                                raise logic.Game.InvalidPlayer()

                            if not len(self.participants) < self.rules.number_of_players:
                                raise logic.Game.LobbyFull(len(self.participants))

                        self.participants.append(p)
                else:
                    return JSON.dumps({"Error": {
                        "type": "schema_error",
                        "message": "The json data provided does not match the required schema."
                    }})
            else:
                return JSON.dumps({"Error": {
                    "type": "data_missing",
                    "message": "You need to provide json data."
                }})

        @RequestHandler.socketio.on("disconnect", self.name_space)
        def handle_player_leave():
            player = self.players_by_session.get(session.get("connection_id", None), None)
            requests_logger.debug(f"{session.get('connection_id', None)} disconnected from {self.lobby_name} "
                                  f"at /{self.lobby_slug}")
            if player:
                del self.players_by_session[session["connection_id"]]

                ####################
                def player_leave(self, p):
                    # NOTE: Backend will only make one copy per player for certain (except for reconnects)
                    if p in self.participants:
                        print('before:', self.participants)
                        self.participants.remove(p)
                        print('after:', self.participants)
                    else:
                        raise logic.Game.InvalidPlayer

                    if len(self.participants) == 0:
                        self.quit_game()

                    elif p == self.host:
                        self.host = self.participants[0]

                    if self.rules.finish_game_on_disconnect:
                        self.finish_game()
                        # self._game_state = GameState.lobby

        @RequestHandler.socketio.on("chat_message", namespace=self.name_space)
        def handle_chat_message(json=None):
            player = self.players_by_session.get(session.get("connection_id", None), None)
            if json:
                if jsonschema.validate(json, schema.player_schema):
                    pass
                else:
                    return JSON.dumps({"Error": {
                        "type": "schema_error",
                        "message": "The json data provided does not match the required schema."
                    }})
            else:
                return JSON.dumps({"Error": {
                    "type": "data_missing",
                    "message": "You need to provide json data."
                }})
            requests_logger.debug(f"A player has tried to send a chat message to game {self.lobby_name}")

        # TODO: endpoint for updating rules in the lobby
        # store current rules in lobby
        # on start game request check if game can be started and create game object if possible
        # enable players to change their ready state

        @RequestHandler.socketio.on("vote_rules")
        def vote_on_rules(json=None):
            player = self.players_by_session.get(session.get("connection_id", None), None)
            if player:
                requests_logger.debug(f'Player {player} is trying to vote on rules on {self.name_space}')
                if json:
                    if jsonschema.validate(json, schema.game_action_schema):
                        pass
                    else:
                        return jsonify({"Error": {
                            "type": "schema_error",
                            "message": "The json data provided does not match the required schema.",
                        }})
                else:
                    return jsonify({"Error": {
                        "type": "data_missing",
                        "message": "You need to provide json data.",
                    }})
            else:
                requests_logger.debug(f'A foreign connection has tried to vote on rules on {self.name_space}')

        @RequestHandler.socketio.on("start_game", namespace=self.name_space)
        def handle_start_game(json=None):
            requests_logger.debug(f"A player has tried to start the game {self.lobby_name}")
            player = self.players_by_session.get(session.get("connection_id", None), None)
            if player:
                requests_logger.debug(f'Player {player} is trying to start {self.name_space}')

                # no data is needed as the rules for a new game are stored in the lobby object
                def start_game(self, host_decision=False):
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
                                        raise logic.Game.CannotBeStarted(
                                            logic.Game.CannotBeStarted.Reason.not_enough_players)

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
                                            raise logic.Game.CannotBeStarted(
                                                logic.Game.CannotBeStarted.Reason.not_enough_players)

                            # Case 2: Not all players are ready → Game cannot be started
                            else:
                                raise logic.Game.CannotBeStarted(
                                    logic.Game.CannotBeStarted.Reason.not_all_players_ready)

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
                                    raise logic.Game.CannotBeStarted(
                                        logic.Game.CannotBeStarted.Reason.not_enough_players)

                    if game_can_be_started(host_decision):
                        self._game_state = logic.Game.State.started
                        self._current_turn = 0

                        # if self.rules.shuffle_turn_order_on_start:
                        #    random.shuffle(self.participants)
                        # replaced by:
                        # self.rules.apply(game=self)

                        self.initial_players = self.participants[:]
            else:
                requests_logger.debug(f'A foreign connection has tried to start {self.name_space}')
            quit()
            ############################################################################

            if json:
                try:
                    jsonschema.validate(instance=json, schema=schema.create_game_schema)
                    game_name = json.get("game_name")

                    rules = data.Rules(**json.get("rules"))
                    card_deck = data.CardDeck(**json.get("card_deck"))
                    host_player_data = json.get("player")

                    host_player = data.Player(
                        host_player_data["name"],
                        data.TokenStyle(**host_player_data["token_style"])
                    )

                    if game_name and rules and card_deck and host_player:
                        new_game = logic.Game(game_name, host_player, rules, card_deck)
                        with RequestHandler.game_sockets_lock:
                            if new_game.slug in RequestHandler.game_sockets:
                                raise ValueError()
                            connection = GameSocket(game=new_game)
                            RequestHandler.game_sockets.update({new_game.slug: connection})
                        requests_logger.debug(f"POST request to /games successful. "
                                              f"Created new Game \"{new_game.slug}\"")
                        return JSON.dumps(new_game.json())
                    else:
                        raise ValueError()
                except jsonschema.exceptions.SchemaError as e:
                    requests_logger.debug("POST request to /games failed. Data incomplete.")
                    return exceptions.BadRequest(f"Data incomplete, Key Error: {e.args}")
                except ValueError as e:
                    requests_logger.debug("POST request to /games failed. Invalid Data.")
                    return exceptions.BadRequest(f"Data invalid. {e.args}")
                except Exception as e:
                    requests_logger.debug(f"Start game request by {session['connection_id']} to {self.name_space}"
                                          f"failed with unhandled Error.")
                    raise e
            else:
                return exceptions.BadRequest("You need to provide json data.")

        @RequestHandler.socketio.on("quit_game", namespace=self.name_space)
        def handle_quit_game(json=None):
            requests_logger.debug(f"A player has tried to quit the game {self.lobby_name}")
            player = self.players_by_session.get(session.get("connection_id", None), None)
            if player:
                requests_logger.debug(f'Player {player} is trying to quit {self.name_space}')
            else:
                requests_logger.debug(f'A foreign connection has tried to quit {self.name_space}')

        @RequestHandler.socketio.on("game_action", namespace=self.name_space)
        def handle_game_action(json=None):
            requests_logger.debug(f"A player has tried to make a game action in game {self.lobby_name}")
            player = self.players_by_session.get(session.get("connection_id", None), None)
            if player:
                requests_logger.debug(f'Player {player} is trying to commit a game action on {self.name_space}')
                if json:
                    if jsonschema.validate(json, schema.game_action_schema):
                        pass
                    else:
                        return jsonify({"Error": {
                            "type": "schema_error",
                            "message": "The json data provided does not match the required schema.",
                        }})
                else:
                    return jsonify({"Error": {
                        "type": "data_missing",
                        "message": "You need to provide json data.",
                    }})
            else:
                requests_logger.debug(f'A foreign connection has tried to commit a game action on {self.name_space}')
                return jsonify({"Error": {
                    "type": "insufficient_authorization",
                    "message": "you are not a player an hence not allowed to commit a game action.",
                }})

    def json(self):
        return {
            "lobby_name": self.lobby_name,
            "lobby_slug": self.lobby_slug,
            "allow_rule_voting": self.allow_rule_voting,
            "list_publicly": self.list_publicly,
            "max_number_of_players": self.max_number_of_players,
        }


class RequestHandler:
    app = Flask(__name__)
    CONFIG_DIR = pathlib.Path.home() / pathlib.Path('.config/fiaro/')
    SECRET_FILE_PATH = CONFIG_DIR / pathlib.Path('secret.txt')
    if not os.path.exists(SECRET_FILE_PATH):
        try:
            pathlib.Path.mkdir(pathlib.Path(SECRET_FILE_PATH).parents[0], parents=True)
        except FileExistsError:
            pass
        with open(SECRET_FILE_PATH, 'w') as secret_file:
            print("Creating secret key")
            secret_file.write(b64encode(os.urandom(2 ** 5)).decode())
    with open(SECRET_FILE_PATH) as secret_file:
        app.config['SECRET_KEY'] = secret_file.read()
    Session(app)

    socketio = SocketIO(app, manage_sessions=False, ping_timeout=2, ping_interval=1)
    lobbies = {}
    lobbies_lock = Lock()

    @staticmethod
    @socketio.on("connect")
    def handle_connect():
        if session.get("connection_id", None) is None:
            session["connection_id"] = b64encode(os.urandom(2 ** 5))
        requests_logger.debug(f"{session['connection_id']} connected. The sid is: {request.sid}, request: {request}")

    @staticmethod
    @socketio.on("disconnect")
    def handle_disconnect():
        requests_logger.debug(f"{session.get('connection_id', 0)} has been disconnected.")

    @staticmethod
    @app.route('/games', methods=["GET"])
    def list_games():
        requests_logger.debug("GET request to /games. Serving list of games…")
        response = jsonify(list(RequestHandler.lobbies.values()))
        return response

    @staticmethod
    @app.route('/games/<slug>', methods=["GET"])
    def retrieve_game(slug=None):
        slug = slugify(slug)
        requests_logger.debug(f"GET request to /games/{{{slug}}}. Sending game info…")
        if slug:
            try:
                game = RequestHandler.lobbies.get(slug)
                response = jsonify(game)
            except KeyError:
                response = exceptions.NotFound(f"Game with slug {slug} not found.")
        else:
            response = exceptions.BadRequest("Need to specify game slug")
        return response

    @staticmethod
    def manage_lobbies():
        while True:
            with RequestHandler.lobbies_lock:
                players_sum = 0
                for game_slug, sock in list(RequestHandler.lobbies.items()):
                    seconds_since_start = (datetime.datetime.now() - sock.creation_time).seconds
                    num_players = len(sock.players_by_session)
                    players_sum += num_players
                    if not num_players and seconds_since_start > 10:
                        # no players are connected to the game
                        del RequestHandler.lobbies[game_slug]
                        games_logger.debug(
                            f"Deleted: Game {game_slug} has no players connected to it,"
                            f" so it got deleted. Was active for {seconds_since_start}s.")

                    else:
                        games_logger.debug(
                            f"Active: Game {game_slug} has {len(sock.players_by_session)} "
                            f"players in it, {seconds_since_start}s since start.")
                stats_logger.info(f"{len(RequestHandler.lobbies)} active games with {players_sum} active players.")
            sleep(10)

    @staticmethod
    @app.route('/lobbies', methods=["POST"])
    def create_lobby():
        request_data = request.json
        try:
            jsonschema.validate(instance=request_data, schema=schema.create_lobby_schema)
            lobby_name = request_data.get("lobby_name")
            lobby_slug = "lobby-" + slugify(request_data.get("lobby_name"))
            allow_rule_voting = request_data.get("allow_rule_voting")
            list_publicly = request_data.get("list_publicly")
            max_number_of_players = request_data.get("max_number_of_players")

            if all(x is not None for x in
                   [lobby_name, lobby_slug, allow_rule_voting, list_publicly, max_number_of_players]):
                with RequestHandler.lobbies_lock:
                    if lobby_slug in RequestHandler.lobbies:
                        raise ValueError("Game slug has been used already")
                    lobby = Lobby(lobby_name, lobby_slug, allow_rule_voting, list_publicly, max_number_of_players)
                    RequestHandler.lobbies.update({lobby_slug: lobby})
                requests_logger.debug(f"POST request to /games successful. "
                                      f"Created new Game \"{lobby_slug}\"")
                return jsonify(lobby.json())
            else:
                raise ValueError()
        except jsonschema.exceptions.SchemaError as e:
            requests_logger.debug("POST request to /games failed. Data incomplete.")
            return exceptions.BadRequest(f"Data incomplete, Key Error: {e.args}")
        except ValueError as e:
            requests_logger.debug("POST request to /games failed. Invalid Data.")
            return exceptions.BadRequest(f"Data invalid. {e.args}")
        except Exception as e:
            requests_logger.debug("POST request to /games failed with unhandled Error.")
            raise e

    @staticmethod
    @app.route('/test')
    def test_root():
        """Test socketio conncetions to root or unhandled namespaces."""
        return open("../tests/index.html").read()

    @staticmethod
    @app.route('/testgame')
    def test_game():
        """Test socketio connections to the lobby-my-test-lobby namespace."""
        return open("../tests/test.html").read()


if __name__ == '__main__':
    game_manager = Thread(target=RequestHandler.manage_lobbies)
    # game_manager.start()
    CONFIG_FILE_PATH = RequestHandler.CONFIG_DIR / pathlib.Path("fiaro.conf")
    host = None
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH) as config_file:
            conf = literal_eval(config_file.read())
            if 'host' in conf:
                host = conf["host"]

    if host:
        RequestHandler.socketio.run(RequestHandler.app, host=conf["host"])
    else:
        RequestHandler.socketio.run(RequestHandler.app)
