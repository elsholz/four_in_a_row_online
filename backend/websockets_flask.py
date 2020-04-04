"""
Custom events are:

player_join
send_chat_message
place_token
place_card
start_game
quit_game
"""
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


class GameSocket:
    def __init__(self, game):
        self.game = game

        @RequestHandler.socketio.on("connect", namespace=self.game.slug)
        def handle_player_join(json):
            pass

        @RequestHandler.socketio.on("disconnect", namespace=self.game.slug)
        def handle_player_leave(json):
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
        logger.debug("POST request to /games. Creating game…")
        request_data = request.json

        try:
            game_name = request_data.get("game_name")
            assert game_name not in RequestHandler.game_connections.keys()
            rules = request_data.get("rules")

            card_deck = request_data.get("card_deck")
            host_player = request_data.get("player")

            new_game = logic.Game(game_name, host_player, rules, card_deck)
            connection = GameSocket(game=new_game)
            RequestHandler.game_connections.update({new_game.slug: connection})
            return JSON.dumps(new_game.json())
        except KeyError as e:
            return exceptions.BadRequest(f"Data incomplete, Key Error: {e.args}")


if __name__ == '__main__':
    RequestHandler.socketio.run(RequestHandler.app)
