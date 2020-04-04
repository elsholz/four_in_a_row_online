test_game = {
    game_name: "My Test Game",
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
        number_of_players: 2,
        start_game_if_all_ready: true,
        variable_player_count: false,
        play_field_width: 7,
        play_field_height: 6,
        enable_gravity: true,
        game_is_public: true,
        card_placement_cooldown: 3
    },
    card_deck: [
        "ShuffleTurnOrder",
        "ReverseTurnOrder",
        "SkipNextTurn"
    ],
    player: {
        name: "",
        token_style: {
            color: [
                255,
                255,
                255,
                255
            ],
            img_src: ""
        }
    }
}

console.log(JSON.stringify(test_game, null, 4))
