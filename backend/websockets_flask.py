from flask import json as JSON
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os
import pathlib
from base64 import b64encode
from loguru import logger
from werkzeug import exceptions
from slugify import slugify
from game_logic import logic, data
import jsonschema
from backend.schema import create_game_schema


class GameSocket:
    def __init__(self, game):
        print("Creating socket for:", game.slug, game)
        self.game = game
        self.players_by_key = {}

        @RequestHandler.socketio.on("connect", namespace="/" + self.game.slug)
        def handle_player_join(json=None):
            player_key = b64encode(os.urandom(2 ** 5))
            logger.debug(f"A player has tried to connect to game {self.game.slug}")
            return JSON.dumps({"Welcome to": "game123"})

        @RequestHandler.socketio.on("disconnect", namespace="/" + self.game.slug)
        def handle_player_leave(json=None):
            logger.debug(f"A player has tried to disconnect from game {self.game.slug}")
            pass

        @RequestHandler.socketio.on("chat_message", namespace="/" + self.game.slug)
        def handle_chat_message(json=None):
            logger.debug(f"A player has tried to send a chat message to game {self.game.slug}")
            pass

        @RequestHandler.socketio.on("start_game", namespace="/" + self.game.slug)
        def handle_start_game(json=None):
            logger.debug(f"A player has tried to start the game {self.game.slug}")
            pass

        @RequestHandler.socketio.on("quit_game", namespace="/" + self.game.slug)
        def handle_quit_game(json=None):
            logger.debug(f"A player has tried to quit the game {self.game.slug}")
            pass

        @RequestHandler.socketio.on("game_action", namespace="/" + self.game.slug)
        def handle_game_action(json=None):
            logger.debug(f"A player has tried to make a game action in game {self.game.slug}")
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
    # map slugs to GameConnection objects
    game_connections = {}

    # for testing
    @staticmethod
    @socketio.on("connect")
    def handle_connect():
        logger.debug("A socket.io connection has been established.")

    # for testing
    @staticmethod
    @socketio.on("disconnect")
    def handle_disconnect():
        logger.debug("A socket.io client has been disconnected.")

    @staticmethod
    @app.route('/games', methods=["GET"])
    def list_games():
        logger.debug("GET request to /games. Serving list of games…")
        response = JSON.dumps(list(RequestHandler.game_connections.values()))
        return response

    @staticmethod
    @app.route('/games/<slug>', methods=["GET"])
    def retrieve_game(slug=None):
        slug = slugify(slug)
        logger.debug(f"GET request to /games/{{{slug}}}. Sending game info…")
        if slug:
            try:
                game = RequestHandler.game_connections.get(slug)
                response = JSON.dumps(game)
            except KeyError:
                response = exceptions.NotFound(f"Game with slug {slug} not found.")
        else:
            response = exceptions.BadRequest("Need to specify game slug")
        return response

    @staticmethod
    @app.route('/games', methods=["POST"])
    def create_game():
        request_data = request.json
        print(request_data)
        try:
            jsonschema.validate(instance=request_data, schema=create_game_schema)
            game_name = request_data.get("game_name")
            assert game_name not in RequestHandler.game_connections.keys()

            print(request_data.get("rules"))
            rules = data.Rules(**request_data.get("rules"))
            card_deck = data.CardDeck(**request_data.get("card_deck"))
            host_player_data = request_data.get("player")

            host_player = data.Player(
                host_player_data["name"],
                data.TokenStyle(**host_player_data["token_style"])
            )

            if game_name and rules and card_deck and host_player:
                new_game = logic.Game(game_name, host_player, rules, card_deck)
                connection = GameSocket(game=new_game)
                RequestHandler.game_connections.update({new_game.slug: connection})
                logger.debug(f"POST request to /games successful. Created new Game \"{new_game.slug}\"")
                return JSON.dumps(new_game.json())
            else:
                raise KeyError()
        except jsonschema.exceptions.SchemaError or KeyError as e:
            logger.debug("POST request to /games failed. Data incomplete.")
            return exceptions.BadRequest(f"Data incomplete, Key Error: {e.args}")
        except Exception as e:
            logger.debug("POST request to /games failed with unhandled Error.")
            raise e

    @staticmethod
    @app.route('/test')
    def test_js():
        return open("../testing/test.html").read()


if __name__ == '__main__':
    RequestHandler.socketio.run(RequestHandler.app)
