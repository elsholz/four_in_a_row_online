"""Schemas for incoming json data on socketio connections"""
from four_in_a_row_online.game_logic import game_actions

type_ = "type"
boolean = "boolean"
string = "string"
integer = "integer"
number = "number"

rules_schema = {
    type_: "object",
    "properties": {
        "shuffle_turn_order_on_start": {type_: boolean},
        "finish_game_on_disconnect": {type_: boolean},
        "finish_game_on_win": {type_: boolean},
        "allow_reconnect": {type_: boolean},
        "winning_row_length": {type_: integer},
        "field_has_bounds": {type_: boolean},
        "enable_cards": {type_: boolean},
        "enable_cheats": {type_: boolean},
        "play_field_width": {type_: integer},
        "play_field_height": {type_: integer},
        "enable_gravity": {type_: boolean},
        "card_placement_cooldown": {type_: integer},
    }
}

card_deck_schema = {
    type_: "object",
    "properties": {
        "ShuffleTurnOrder": {type_: boolean},
        "ReverseTurnOrder": {type_: boolean},
        "SkipNextTurn": {type_: boolean},
    }
}

token_style_schema = {
    type_: "object",
    "properties": {
        "color": {
            type_: "array",
            "minItems": 4,
            "maxItems": 4,
            "items": {type_: integer}
        }
    }
}

player_schema = {
    type_: "object",
    "properties": {
        "name": {type_: string},
        "token_style": token_style_schema
    }
}

change_rules_schema = {
    type_: "object",
    "properties": {
        "rules": rules_schema
    }
}

change_card_deck_schema = {
    type_: "object",
    "properties": {
        "card_deck": card_deck_schema
    }
}

create_lobby_schema = {
    type_: "object",
    "properties": {
        "lobby_name": {type_: string},
        "allow_rule_voting": {type_: boolean},
        "list_publicly": {type_: boolean},
        "max_number_of_players": {type_: integer},
        "enable_chat": {type_: boolean},
        "start_game_if_all_ready": {type_: boolean},
        "variable_player_count": {type_: boolean},
    }
}

chat_message_schema = {
    type_: "object",
    "properties": {
        "message": {type_: string},
    }
}

game_action_schema = {
    type_: "object",
    "properties": {
        "action": {
            type_: string,
            "enum": list(map(str, game_actions.ActionType))
        },
        "arguments": {
            type_: "array",
            "items": {
                type_: "object"
            }
        }
    }
}
