import curses
from curses import wrapper
from four_in_a_row_online.game_logic.data import *



def main(stdscr, players):
    stdscr.clear()
    curses.curs_set(0)

    target = (0, 0)

    curses.noecho()
    curses.cbreak()

    rules = Rules.default_init()

    play_field = PlayField(dimensions=(rules.play_field_width, rules.play_field_height))

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)

    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    turn_id = random.randrange(0, 5)
    while True:
        last_line = 1
        stdscr.addstr(0, 0, ' ' + ' ' * 7 * (target[0]) + 'x' * 8 + ' ' * 7 * (7 - target[0]))
        for line in play_field.pretty_print().splitlines():
            for ind, character in enumerate(line):
                colors = {
                    'o': (' ', curses.color_pair(3)),
                    'x': (' ', curses.color_pair(4)),
                    '#': (' ', curses.color_pair(5)),
                    '*': (' ', curses.color_pair(6))
                }
                stdscr.addstr(last_line, 1 + ind, colors.get(character, (character, None))[0],
                              colors.get(character, (None, curses.color_pair(1)))[1])
            last_line += 1
        stdscr.addstr(last_line, 0, players[0].name,
                      curses.color_pair(2) if turn_id % len(players) == 0 else curses.color_pair(1))
        stdscr.addstr(last_line, 50, players[1].name,
                      curses.color_pair(2) if turn_id % len(players) == 1 else curses.color_pair(1))

        if len(players) > 2:
            stdscr.addstr(last_line + 1, 0, players[2].name,
                          curses.color_pair(2) if turn_id % len(players) == 2 else curses.color_pair(1))
        if len(players) > 3:
            stdscr.addstr(last_line + 1, 50, players[3].name,
                          curses.color_pair(2) if turn_id % len(players) == 3 else curses.color_pair(1))
        col = ' ' * 4 * (target[1]) + 'x' * 5 + ' ' * 4 * (5 - target[1])

        col = ''.join(list(reversed(col)))

        for y in range(5 + 4 * (rules.play_field_height - 1)):
            stdscr.addstr(y + 1, 0, col[y])

        stdscr.refresh()
        key = stdscr.getkey()

        if key == '\n':
            try:
                current_player = players[turn_id % len(players)]
                play_field.place_token(rules, current_player, loc_x=target[0], loc_y=target[1])

                rows = play_field._check_for_winning_rows(rules, current_player)
                if rows:
                    stdscr.clear()
                    stdscr.addstr(0, 0, f'Player {current_player.name} Wins!')
                    stdscr.addstr(1, 0, 'Press q to exit')
                    stdscr.refresh()
                    while True:
                        if stdscr.getkey() == 'q':
                            curses.endwin()
                            exit(0)
                turn_id += 1
            except PlayField.IllegalTokenLocation as e:
                pass

        else:
            target = {
                'h': lambda: (target[0] - 1, target[1]),
                'j': lambda: (target[0], target[1] - 1),
                'k': lambda: (target[0], target[1] + 1),
                'l': lambda: (target[0] + 1, target[1]),
            }.get(key, lambda: target)()

            if not 0 <= target[0] < rules.play_field_width:
                target = 0, target[1]
            if not 0 <= target[1] < rules.play_field_height:
                target = target[0], 0


player_count = int(input("How many players? "))
players = []
for _ in range(player_count):
    p = Player.random_init()
    p.name = input(f"Name for Player{_}? ")
    players.append(p)

wrapper(main, players)
