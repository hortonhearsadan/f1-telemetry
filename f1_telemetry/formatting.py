import curses

from settings import DRIVER_NAME

TEAM_COLOUR_OFFSET = 100
STATUS_COLOUR_OFFSET = 200


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


def init_colours():
    curses.start_color()
    init_team_colour_pairs()

    init_status_colours()


def init_team_colour_pairs():
    for i, rgb in team_colours_rgb_by_id.items():
        j = TEAM_COLOUR_OFFSET + i  # avoid collision with real colours
        curses.init_color(j, *rgb)
        curses.init_pair(j, curses.COLOR_WHITE, j)


def init_status_colours():
    curses.init_pair(STATUS_COLOUR_OFFSET, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(STATUS_COLOUR_OFFSET + 1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(STATUS_COLOUR_OFFSET + 2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    curses.init_color(STATUS_COLOUR_OFFSET + 3, 255, 165, 0)
    curses.init_pair(
        STATUS_COLOUR_OFFSET + 3, STATUS_COLOUR_OFFSET + 3, curses.COLOR_BLACK
    )


def format_name(name: str):
    if name == DRIVER_NAME:
        split_names = name.split(" ")
        return split_names[0][0].upper() + ". " + split_names[-1].upper()
    return name


def get_damage_colour(percentage):
    if percentage <= 15:
        return curses.color_pair(STATUS_COLOUR_OFFSET)
    elif percentage <= 40:
        return curses.color_pair(STATUS_COLOUR_OFFSET + 2)
    elif percentage <= 60:
        return curses.color_pair(STATUS_COLOUR_OFFSET + 3)

    return curses.color_pair(STATUS_COLOUR_OFFSET + 1)
