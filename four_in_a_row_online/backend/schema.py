import jsonschema

studentSchema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "rollnumber": {"type": "number"},
        "marks": {"type": "number"},
    },
}
rules_schema = {
    "type": "object",
    "properties": {
        "shuffle_turn_order_on_start": {"type": "boolean"},
        "enable_chat": {"type": "boolean"},
        "finish_game_on_disconnect": {"type": "boolean"},
        "finish_game_on_win": {"type": "boolean"},
        "allow_reconnect": {"type": "boolean"},
        "winning_row_length": {"type": "integer"},
        "field_has_bounds": {"type": "boolean"},
        "enable_cards": {"type": "boolean"},
        "enable_cheats": {"type": "boolean"},
        "number_of_players": {"type": "integer"},
        "start_game_if_all_ready": {"type": "boolean"},
        "variable_player_count": {"type": "boolean"},
        "play_field_width": {"type": "integer"},
        "play_field_height": {"type": "integer"},
        "enable_gravity": {"type": "boolean"},
        "game_is_public": {"type": "boolean"},
        "card_placement_cooldown": {"type": "integer"},
    }
}
card_deck_schema = {
    "type": "object",
    "properties": {
        "ShuffleTurnOrder": {"type": "boolean"},
        "ReverseTurnOrder": {"type": "boolean"},
        "SkipNextTurn": {"type": "boolean"},
    }
}
token_style_schema = {
    "type": "object",
    "properties": {
        # TODO: Check if array of numbers
        "color": {
            "type": "array",
            "items": {"type": "integer"}
        }
    }
}
player_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "token_style": token_style_schema
    }
}

create_game_schema = {
    "type": "object",
    "properties": {
        "rules": rules_schema,
        "card_deck": card_deck_schema,
        "player": player_schema,
    }
}

create_lobby_schema = {
    "type": "object",
    "properties": {
        "lobby_name": {"type:string"},
        "allow_rule_voting": {"type": "boolean"},
        "list_publicly": {"type": "boolean"},
        "max_number_of_players": {"type": "integer"},
    }
}

chat_message_schema = {

}

game_action_schema = {

}


