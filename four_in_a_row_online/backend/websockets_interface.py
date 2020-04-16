import websockets
import asyncio
import json
import game_logic
import datetime
from bidict import bidict

from dataclasses import dataclass


@dataclass
class ChatMessage:
    message: str
    timestamp: datetime.datetime
    sender: game_logic.Player

    def __init__(self, message, timestamp, sender):
        self.message = message
        self.timestamp = timestamp
        self.sender = sender


# TODO
def error_handling(connection):
    try:
        await connection.send('An Error occured')
    except Exception as e:
        pass


# TODO: WIP
def type_checking(objs, types, requirements=[]):
    for o, t, req in zip(objs, types, requirements):
        assert isinstance(o, t)
        assert req(o)


# TODO
def place_token(con, data):
    pass
    variables = [loc_x, loc_y] = [None] * 2

    player = player_by_connection[con]
    g = game_by_players[player]

    g.place_token(player=player, loc_x=loc_x, loc_y=loc_y)


# TODO: DONE
def join_game(con, data):
    processed_data = []
    variables = [player_name, game_name, token_style] = [None] * 3

    for var_name, default in zip([v.__name__ for v in variables], [None, None, None]):
        processed_data.append(data.get(var_name, default))

    type_checking(objs=processed_data, types=[str, str, list], requirements=[
        lambda x: not str.isspace(x) and not x == '' and 0 < len(x) <= 30,
        lambda x: not str.isspace(x) and not x == '' and 0 < len(x) <= 30,
        lambda x: len(x) == 2 and len(x[0]) == 4 and isinstance(x[1], str) and not str.isspace(x[1])
    ])

    [player_name, game_name, token_style] = processed_data

    new_player = game_logic.Player(
        name=player_name, token_style=game_logic.TokenStyle(*token_style)
    )
    game = game_by_name[game_name]
    game.player_join(new_player)
    player_by_connection.update({con: new_player})


# TODO: DONE
def create_game(con, data):
    processed_data = []
    variables = [game_name, rules, card_deck] = [None] * 3

    for var_name, default in zip([v.__name__ for v in variables], [None, None, None]):
        processed_data.append(data.get(var_name, default))

    r = game_logic.Rules(rules)
    cd = game_logic.CardDeck(card_deck)

    processed_data = processed_data[:1]
    processed_data.append(r)
    processed_data.append(cd)

    type_checking(objs=processed_data, types=[str, game_logic.Rules, game_logic.CardDeck], requirements=[
        lambda x: not str.isspace(x) and not x == '' and 0 < len(x) <= 30,
        lambda x: None,
        lambda x: None
    ])

    g = game_logic.Game(*processed_data)
    assert game_name not in game_by_name.keys()
    game_by_name.update({game_name: g})
    join_game(con, data)


# TODO: DONE
def change_ready_state(con, data):
    new_ready_state = data['ready_state']
    type_checking(objs=[new_ready_state], types=[bool], requirements=[
        lambda x: None
    ])
    p = player_by_connection[con]
    p.is_ready = new_ready_state


# TODO: DONE
def send_chat_message(con, data):
    p = player_by_connection[con]
    message = data['message']
    type_checking([message], types=[str], requirements=[
        lambda x: 0 < len(x) < 200 and not str.isspace(x)
    ])
    time_stamp = datetime.datetime.now()
    c_mes = ChatMessage(message=message, timestamp=time_stamp, sender=p)

    spread_information(information=c_mes, game=game_by_players[p])


possible_request_types = dict(
    [(f.__name__, f) for f in [
        place_token, join_game, create_game, change_ready_state, send_chat_message
    ]]
)


async def spread_information(information, game):
    for p in game.participants:
        player_by_connection[p].send(json.dumps(information))


async def ws_server(ws, path):
    data = await ws.recv()

    if path == '/four_in_a_row':
        try:
            data = json.load(data)
            for d_item in data:
                request_type = d_item['request_type']

                action = possible_request_types[request_type]

                action(con=ws, data=d_item)

        except Exception as e:
            print(e)

    else:
        await ws.send('Please make only ws requests to valid paths, e.g. /four_in_a_row')


game_by_players = {}  # {Player: Game},
# p1, p2 ∈ Player ∧ G ∈ Game: ((gbp[p1] = G) ∧ (gbp[p2] = G)) → (p1 = p2) ∨ ¬(p1 = p2)
game_by_name = bidict()
player_by_connection = bidict()

start_server = websockets.serve(ws_server, 'localhost', 5001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
