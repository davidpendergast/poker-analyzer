import os

import pygame

NAME_OF_GAME = "Ghast Poker Analyzer"
GAME_DIMS = (640, 480)
THRESH = 0.0001

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

