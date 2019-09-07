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



from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return ('index.html 123')


@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})

socketio.emi


if __name__ == '__main__':
    socketio.run(app)
