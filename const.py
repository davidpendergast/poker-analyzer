import os

import pygame

NAME_OF_GAME = "Ghast Poker Analyzer"
GAME_DIMS = (960, 960)
THRESH = 0.0001
EQUITY_CALC_N_ITERS = 1000

HERO_ID = 'Ghast @ k-xm91OpZ6'              # ID of the player to track.
# HERO_ID = 'M1sf1re @ TNLfj8hFbJ'            # (for debug) M1sf1re
# HERO_ID = 'Ravi @ B8jVhFGWIY'               # (for debug) Ravi
# HERO_ID = 'Flow @ pvi7lGaAqX'               # (for debug) Flow
# HERO_ID = 'Freky @ rnl8dHxqtf'              # (for debug) Freky

LOG_DOWNLOADER_ID = 'k-xm91OpZ6'    # ID of the player who downloaded the logs.

LOG_DIR = "C:\\Users\\david\\Desktop\\Poker Notes\\logs"
EQUITY_DB = "assets\\preflop_equities_n1000.txt"
# LOG_DIR = "testdata"

IS_DEV = os.path.exists(".gitignore")

KEYS_HELD_THIS_FRAME = set()
KEYS_PRESSED_THIS_FRAME = set()
KEYS_RELEASED_THIS_FRAME = set()

MOUSE_XY = (0, 0)
MOUSE_PRESSED_AT_THIS_FRAME = {}   # btn -> xy
MOUSE_RELEASED_AT_THIS_FRAME = {}  # btn -> xy
MOUSE_BUTTONS_HELD_THIS_FRAME = set()

CLICK_DISTANCE_PX = 16


def clicked_or_any_pressed_this_frame(keys=(pygame.K_SPACE, pygame.K_RETURN)):
    return len(MOUSE_PRESSED_AT_THIS_FRAME) > 0 or any(k in KEYS_PRESSED_THIS_FRAME for k in keys)

