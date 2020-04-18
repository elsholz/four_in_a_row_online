from flask import json as JSON
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import os
import pathlib
from base64 import b64encode
from werkzeug import exceptions
from slugify import slugify
from four_in_a_row_online.game_logic import data, logic
import jsonschema
from four_in_a_row_online.backend.schema import create_game_schema, create_lobby_schema, player_schema
from time import sleep
from threading import Thread, Lock
import datetime
from four_in_a_row_online.loggers.loggers import games_logger, requests_logger, stats_logger


class Lobby:
    def __init__(self, lobby_name, lobby_slug, allow_rule_voting, list_publicly, max_number_of_players):
        self.games = []
        self.current_game = None
        self.players_by_key = {}
        self.lobby_name = lobby_name
        self.lobby_slug = lobby_slug
        self.allow_rule_voting = allow_rule_voting
        self.list_publicly = list_publicly
        self.max_number_of_players = max_number_of_players

        @RequestHandler.socketio.on("connect", namespace="/" + self.lobby_name)
        def handle_player_join(json=None):
            requests_logger.debug(f"A player has tried to connect to game {self.lobby_name}."
                                  f" The connection ID is: {session['id']}")
            if json:
                if jsonschema.validate(json, player_schema):
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

            player_key = b64encode(os.urandom(2 ** 5))
            return JSON.dumps({"Welcome to": "game123"})

        @RequestHandler.socketio.on("disconnect", namespace="/" + self.lobby_name)
        def handle_player_leave(json=None):
            requests_logger.debug(f"A player has tried to disconnect from game {self.lobby_name}")
            if json:
                if jsonschema.validate(json, player_schema):
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
            pass

        @RequestHandler.socketio.on("chat_message", namespace="/" + self.lobby_name)
        def handle_chat_message(json=None):
            if json:
                if jsonschema.validate(json, player_schema):
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
            pass

        @RequestHandler.socketio.on("start_game", namespace="/" + self.lobby_name)
        def handle_start_game(json=None):
            requests_logger.debug(f"A player has tried to start the game {self.lobby_name}")

        @RequestHandler.socketio.on("quit_game", namespace="/" + self.lobby_name)
        def handle_quit_game(json=None):
            requests_logger.debug(f"A player has tried to quit the game {self.lobby_name}")

        @RequestHandler.socketio.on("game_action", namespace="/" + self.lobby_name)
        def handle_game_action(json=None):
            requests_logger.debug(f"A player has tried to make a game action in game {self.lobby_name}")
            if json:
                if jsonschema.validate(json, player_schema):
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


class RequestHandler:
    app = Flask(__name__)

    SECRET_FILE_PATH = pathlib.Path.home() / pathlib.Path('.config/fiaro/secret.txt')
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

    socketio = SocketIO(app, ping_timeout=2, ping_interval=1)
    lobbies = {}
    lobbies_lock = Lock()

    # for testing
    @staticmethod
    @socketio.on("connect")
    def handle_connect():
        # if not session.get("connection_id", None):
        #    session["connection_id"] = b64encode(os.urandom(32))
        requests_logger.debug(f"A socket.io connection has been established. "
                              f"The connection id is {['connection_id']}")

    @staticmethod
    @socketio.on("disconnect")
    def handle_disconnect():
        requests_logger.debug(f"The socket.io client with connection id {('connection_id', 0)} "
                              f"has been disconnected.")

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
                    seconds_since_start = (datetime.datetime.now() - sock.game.creation_time).seconds
                    num_players = len(sock.players_by_key)
                    players_sum += num_players
                    if not num_players and seconds_since_start > 10:
                        # no players are connected to the game
                        del RequestHandler.lobbies[game_slug]
                        games_logger.debug(
                            f"Deleted: Game {game_slug} has no players connected to it,"
                            f" so it got deleted. Was active for {seconds_since_start}s.")

                    else:
                        games_logger.debug(
                            f"Active: Game {game_slug} has {len(sock.players_by_key)} "
                            f"players in it, {seconds_since_start}s since start.")
                stats_logger.info(f"{len(RequestHandler.lobbies)} active games with {players_sum} active players.")
            sleep(10)

    @staticmethod
    @app.route('/lobbies', methods=["POST"])
    def create_lobby():
        request_data = request.json
        try:
            jsonschema.validate(instance=request_data, schema=create_lobby_schema)
            lobby_name = request_data.get("lobby_name")
            lobby_slug = slugify(request_data.get("lobby_name"))
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
                return jsonify(lobby)
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
    @app.route('/games', methods=["POST"])
    def create_game():
        request_data = request.json
        try:
            jsonschema.validate(instance=request_data, schema=create_game_schema)
            game_name = request_data.get("game_name")

            rules = data.Rules(**request_data.get("rules"))
            card_deck = data.CardDeck(**request_data.get("card_deck"))
            host_player_data = request_data.get("player")

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
            requests_logger.debug("POST request to /games failed with unhandled Error.")
            raise e

    @staticmethod
    @app.route('/test')
    def test_js():
        return open("../tests/index.html").read()


if __name__ == '__main__':
    game_manager = Thread(target=RequestHandler.manage_lobbies)
    game_manager.start()
    RequestHandler.socketio.run(RequestHandler.app)
