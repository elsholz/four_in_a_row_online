from flask import json as JSON
from flask import Flask, request
from flask_socketio import SocketIO
import os
import pathlib
from base64 import b64encode
from werkzeug import exceptions
from slugify import slugify
from four_in_a_row_online.game_logic import data, logic
import jsonschema
from four_in_a_row_online.backend.schema import create_game_schema
from time import sleep
from threading import Thread, Lock
import datetime
from four_in_a_row_online.loggers.loggers import games_logger, requests_logger, stats_logger


class GameSocket:
    def __init__(self, game: logic.Game):
        self.game = game
        self.players_by_key = {}

        @RequestHandler.socketio.on("connect", namespace="/" + self.game.slug)
        def handle_player_join(json=None):
            player_key = b64encode(os.urandom(2 ** 5))
            requests_logger.debug(f"A player has tried to connect to game {self.game.slug}")
            return JSON.dumps({"Welcome to": "game123"})

        @RequestHandler.socketio.on("disconnect", namespace="/" + self.game.slug)
        def handle_player_leave(json=None):
            requests_logger.debug(f"A player has tried to disconnect from game {self.game.slug}")
            pass

        @RequestHandler.socketio.on("chat_message", namespace="/" + self.game.slug)
        def handle_chat_message(json=None):
            requests_logger.debug(f"A player has tried to send a chat message to game {self.game.slug}")
            pass

        @RequestHandler.socketio.on("start_game", namespace="/" + self.game.slug)
        def handle_start_game(json=None):
            requests_logger.debug(f"A player has tried to start the game {self.game.slug}")
            pass

        @RequestHandler.socketio.on("quit_game", namespace="/" + self.game.slug)
        def handle_quit_game(json=None):
            requests_logger.debug(f"A player has tried to quit the game {self.game.slug}")
            pass

        @RequestHandler.socketio.on("game_action", namespace="/" + self.game.slug)
        def handle_game_action(json=None):
            requests_logger.debug(f"A player has tried to make a game action in game {self.game.slug}")
            pass


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
    app.config['CORS_HEADERS'] = 'Content-Type'

    socketio = SocketIO(app, ping_timeout=2, ping_interval=1)
    # map slugs to game socket objects
    game_sockets = {}
    game_sockets_lock = Lock()

    # for testing
    @staticmethod
    @socketio.on("connect")
    def handle_connect():
        requests_logger.debug("A socket.io connection has been established.")

    # for testing
    @staticmethod
    @socketio.on("disconnect")
    def handle_disconnect():
        requests_logger.debug("A socket.io client has been disconnected.")

    @staticmethod
    @app.route('/games', methods=["GET"])
    def list_games():
        requests_logger.debug("GET request to /games. Serving list of games…")
        response = JSON.dumps(list(RequestHandler.game_connections.values()))
        return response

    @staticmethod
    @app.route('/games/<slug>', methods=["GET"])
    def retrieve_game(slug=None):
        slug = slugify(slug)
        requests_logger.debug(f"GET request to /games/{{{slug}}}. Sending game info…")
        if slug:
            try:
                game = RequestHandler.game_sockets.get(slug)
                response = JSON.dumps(game)
            except KeyError:
                response = exceptions.NotFound(f"Game with slug {slug} not found.")
        else:
            response = exceptions.BadRequest("Need to specify game slug")
        return response

    @staticmethod
    def manage_games():
        while True:
            with RequestHandler.game_sockets_lock:
                players_sum = 0
                for game_slug, sock in list(RequestHandler.game_sockets.items()):
                    seconds_since_start = (datetime.datetime.now() - sock.game.creation_time).seconds
                    num_players = len(sock.players_by_key)
                    players_sum += num_players
                    if not num_players and seconds_since_start > 10:
                        # no players are connencted to the game
                        del RequestHandler.game_sockets[game_slug]
                        games_logger.debug(
                            f"Deleted: Game {game_slug} has no players connected to it,"
                            f" so it got deleted. Was active for {seconds_since_start}s.")

                    else:
                        games_logger.debug(
                            f"Active: Game {game_slug} has {len(sock.players_by_key)} "
                            f"players in it, {seconds_since_start}s since start.")
                stats_logger.info(f"{len(RequestHandler.game_sockets)} active games with {players_sum} active players.")
            sleep(10)

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
    @app.route('/')
    def test_js():
        return open("../tests/index.html").read()


if __name__ == '__main__':
    game_manager = Thread(target=RequestHandler.manage_games)
    game_manager.start()
    RequestHandler.socketio.run(RequestHandler.app)
