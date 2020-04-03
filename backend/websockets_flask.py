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
from flask import json

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return ('index.html 123')


@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})


socketio.emi


@app.route('/games/list')
def list_games():
    list_of_games = []
    return json.dumps(list_of_games)


@app.route('/games')
def game_info():
    return


@app.route('/games/join')
def join_game():
    return


@app.route('/games/create')
def create_game():
    return


@socketio.on('json')
def handle_json(content):
    return {
        'place_token'
        'place_card'
        
    }[content.action_type](content)


if __name__ == '__main__':
    socketio.run(app)
