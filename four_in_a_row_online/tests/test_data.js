var fs = require('fs');

test_game = {
    rules: {
        shuffle_turn_order_on_start: true,
        enable_chat: true,
        finish_game_on_disconnect: true,
        finish_game_on_win: true,
        allow_reconnect: false,
        winning_row_length: 4,
        field_has_bounds: true,
        enable_cards: false,
        enable_cheats: false,
        start_game_if_all_ready: true,
        variable_player_count: false,
        play_field_width: 7,
        play_field_height: 6,
        enable_gravity: true,
        game_is_public: true,
        card_placement_cooldown: 3
    },
    card_deck: {
        "ShuffleTurnOrder": true,
        "ReverseTurnOrder": true,
        "SkipNextTurn": true
    },
    player: {
        name: "TestPlayer123",
        token_style: {
            color: [
                255,
                255,
                255,
                255
            ],/*
            img: false*/
            /*img: {
                name: "",
                color_variant: "default"
            }*/
        }
    }
}

test_lobby = {
    lobby_name: "My test game lobby",
    allow_rule_voting: false,
    list_publicly: true,
    max_number_of_players: 2,
    player_key: "asdhja67h32"
}

fs.writeFile('test_game.json', JSON.stringify(test_game, null, 4), function (err) {
    if (err) throw err
})

fs.writeFile('test_lobby.json', JSON.stringify(test_lobby, null, 4), function (err) {
    if (err) throw err
})

// on a post, the host player retrieves the host key that is generated on the server
// when joining a lobby, each connection gets a connection key
delete test_lobby["player_key"]

fs.writeFile('test_lobby_post.json', JSON.stringify(test_lobby, null, 4), function (err) {
    if (err) throw err
})


