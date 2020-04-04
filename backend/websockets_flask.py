"""
Flask and Socket.io- Websockets based backend.
Request types are abstracted as custom events.

Custom events are:

player_join
send_chat_message
place_token
place_card
start_game
quit_game
"""
from flask import json as JSON
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os
import pathlib
from base64 import b64encode
from loguru import logger


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

    socketio = SocketIO(app)
    # map slugs to GameConnection objects
    game_connections = {}

    @app.route('/games', methods=["GET"])
    def list_games():
        logger.debug("GET request to /games. Serving list of games…")
        return JSON.dumps([])

    @app.route('/games/<slug>', methods=["GET"])
    def retrieve_game():
        logger.debug("GET request to /games/{slug}. Sending game info…")
        return JSON.dumps([])

    @app.route('/games', methods=["POST"])
    def create_game():
        logger.debug("POST request to /games. Creating game…")
        return JSON.dumps([])
        data = request.data
        game_name = data['game_name']

        GameSocket(data)


if __name__ == '__main__':
    RequestHandler.socketio.run(RequestHandler.app)
