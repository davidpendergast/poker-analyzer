import typing
import math

import ui.utils as utils


DARK_GRAY = (32, 32, 32)
BLACK = (0, 0, 0)
RED = (234, 153, 153)
WHITE = (255, 255, 255)
GREEN = (87, 187, 138)


def lerp(t, c1, c2):
    return utils.int_lerps(c1, c2, t)


def profit_gradient(v):
    if v < 0:
        return lerp(abs(v), WHITE, RED)
    else:
        return lerp(v, WHITE, GREEN)


def rainbow(t) -> typing.Tuple[int, int, int]:
    r = int(255 * (math.sin(math.pi * 2 * t) * 0.5 + 0.5))
    g = int(255 * (math.sin(math.pi * 2 * (t + 0.25)) * 0.5 + 0.5))
    b = int(255 * (math.sin(math.pi * 2 * (t + 0.5)) * 0.5 + 0.5))
    return r, g, b