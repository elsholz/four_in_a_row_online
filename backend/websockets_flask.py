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

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return ('index.html 123')


@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})


for x in range(10):
    @socketio.on(str(x))
    def test_function(json):
        emit(f'{x} response', {'success': True})


# what sockets are needed for: everything where players are connected to one namespace, which is one game
# what normal app routes are used for: everything that only applies to on player

def create_game_interface(game_name):
    @socketio.on(f"game_{game_name}")
    def handle_data(json):
        """Endpoint for all data input and data output by players and to players."""
        json = {
            'request_type': ['join_game']
        }

        return JSON.dump(json)


@app.route('/games', methods=["GET"])
def list_games(request):
    pass


@app.route('/games/<slug>', methods=["GET"])
def retrieve_game(slug):
    pass


@app.route('/games', methods=["POST"])
def create_game(request):
    data = request.data
    game_name = data['game_name']

if __name__ == '__main__':
    socketio.run(app)
