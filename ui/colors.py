import typing
import math


def rainbow(t) -> typing.Tuple[int, int, int]:
    r = int(255 * (math.sin(math.pi * 2 * t) * 0.5 + 0.5))
    g = int(255 * (math.sin(math.pi * 2 * (t + 0.25)) * 0.5 + 0.5))
    b = int(255 * (math.sin(math.pi * 2 * (t + 0.5)) * 0.5 + 0.5))
    return r, g, b