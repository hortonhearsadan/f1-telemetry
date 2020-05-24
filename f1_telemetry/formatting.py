import curses

# curses.COLOR_MERC = curses.init_color(101,1,0,0)

team_colours_rgb_by_id = {
    0: (0, 210, 190),
    1: (220, 0, 0),
    2: (30, 65, 255),
    3: (255, 255, 255),
    4: (245, 150, 200),
    5: (255, 245, 0),
    6: (70, 155, 255),
    7: (240, 215, 135),
    8: (255, 135, 0),
    9: (155, 0, 0),
}


def init_team_colour_pairs():
    curses.start_color()
    for i, rgb in team_colours_rgb_by_id.items():
        j = 100 + i  # avoid collision with real colours
        curses.init_color(j, *rgb)
        curses.init_pair(j, curses.COLOR_WHITE, j)
