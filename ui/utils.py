import random
import typing

import pygame
import pygame._sdl2 as sdl2

import sys, os, math


T = typing.TypeVar('T')


# from (my own) https://github.com/davidpendergast/pygame-utils/blob/main/rainbowize.py
def make_fancy_scaled_display(
        size,
        scale_factor=0.,
        extra_flags=0,
        outer_fill_color=None,
        smooth: bool = None) -> pygame.Surface:
    """Creates a SCALED pygame display with some additional customization options.

        Args:
            size: The base resolution of the display surface.
            extra_flags: Extra display flags (aside from SCALED) to give the display, e.g. pygame.RESIZABLE.
            scale_factor: The initial scaling factor for the window.
                    For example, if the display's base size is 64x32 and this arg is 5, the window will be 320x160
                    in the physical display. If this arg is 0 or less, the window will use the default SCALED behavior
                    of filling as much space as the computer's display will allow.
                    Non-integer values greater than 1 can be used here too. Positive values less than 1 will act like 1.
            outer_fill_color: When the display surface can't cleanly fill the physical window with an integer scale
                    factor, a solid color is used to fill the empty space. If provided, this param sets that color
                    (otherwise it's black by default).
            smooth: Whether to use smooth interpolation while scaling.
                    If True: The environment variable PYGAME_FORCE_SCALE will be set to 'photo', which according to
                        the pygame docs, "makes the scaling use the slowest, but highest quality anisotropic scaling
                        algorithm, if it is available." This gives a smoother, blurrier look.
                    If False: PYGAME_FORCE_SCALE will be set to 'default', which uses nearest-neighbor interpolation.
                    If None: PYGAME_FORCE_SCALE is left unchanged, resulting in nearest-neighbor interpolation (unless
                        the variable has been set beforehand). This is the default behavior.
        Returns:
            The display surface.
    """

    # if smooth is not None:
    #     # must be set before display.set_mode is called.
    #     os.environ['PYGAME_FORCE_SCALE'] = 'photo' if smooth else 'default'

    # create the display in "hidden" mode, because it isn't properly sized yet
    res = pygame.display.set_mode(size, pygame.SCALED | extra_flags | pygame.HIDDEN)

    window = sdl2.Window.from_display_module()

    # due to a bug, we *cannot* let this Window object get GC'd
    # https://github.com/pygame-community/pygame-ce/issues/1889
    globals()["sdl2_Window_ref"] = window  # so store it somewhere safe...

    # resize the window to achieve the desired scale factor
    if scale_factor > 0:
        initial_scale_factor = max(scale_factor, 1)  # scale must be >= 1
        window.size = (int(size[0] * initial_scale_factor),
                       int(size[1] * initial_scale_factor))
        window.position = sdl2.WINDOWPOS_CENTERED  # recenter it too

    # set the out-of-bounds color
    if outer_fill_color is not None:
        renderer = sdl2.Renderer.from_window(window)
        renderer.draw_color = pygame.Color(outer_fill_color)

    # show the window (unless the HIDDEN flag was passed in)
    if not (pygame.HIDDEN & extra_flags):
        window.show()

    return res

def int_mults(v, a):
    return tuple(int(v[i] * a) for i in range(len(v)))

def int_sub(v1, v2):
    return tuple(int(v1[i] - v2[i]) for i in range(len(v1)))

def sub(v1, v2):
    return tuple(v1[i] - v2[i] for i in range(len(v1)))

def add(v1, v2):
    return tuple(v1[i] + v2[i] for i in range(len(v1)))

def mult(v, a):
    return tuple(v[i] * a for i in range(len(v)))

def lerp(start, end, t, clamp=True):
    if (isinstance(start, (float, int))):
        val = start + t * (end - start)
        if clamp:
            lower = min(start, end)
            upper = max(start, end)
            return max(lower, min(upper, val))
        else:
            return val
    else:
        return tuple(lerp(start[i], end[i], t, clamp=clamp) for i in range(len(start)))

def int_lerp(i1, i2, t):
    return round(i1 + t * (i2 - i1))


def int_lerps(v1, v2, t, clamp=True):
    return tuple(int_lerp(v1[i], v2[i], t, clamp=clamp) for i in range(len(v1)))


def tint_color(c1, c2, strength, max_shift=255):
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    return (int(r1 + min(max_shift, strength * (r2 - r1))),
            int(g1 + min(max_shift, strength * (g2 - g1))),
            int(b1 + min(max_shift, strength * (b2 - b1))))


def dist2(p1, p2):
    return (p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1])

def dist(p1, p2):
    return math.sqrt(dist2(p1, p2))


def mag(v):
    return dist(v, (0,) * len(v))


def set_length(v, a):
    m = mag(v)
    if m == 0:
        return (a,) + (0,) * (len(v) - 1)
    else:
        return mult(v, a / m)

def eq(v1, v2, thresh=0):
    if len(v1) != len(v2):
        return False
    for (i1, i2) in zip(v1, v2):
        if abs(i1 - i2) > thresh:
            return False
    return True


def ccw_angle_to_rads(v1, v2):
    val = math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1])
    if val < 0:
        return val + 2 * math.pi
    else:
        return val


def bounding_box(pts):
    min_x = float('inf')
    max_x = -float('inf')
    min_y = float('inf')
    max_y = -float('inf')
    for (x, y) in pts:
        min_x = min(x, min_x)
        max_x = max(x, max_x)
        min_y = min(y, min_y)
        max_y = max(y, max_y)
    return (min_x, min_y, max_x - min_x, max_y - min_y)


def map_from_rect_to_rect(pt, r1, r2):
    x1 = (pt[0] - r1[0]) / r1[2]
    y1 = (pt[1] - r1[1]) / r1[3]
    return (x1 * r2[2] + r2[0], y1 * r2[3] + r2[1])


def subdivide_evenly_and_center(length, n, integer=True):
    """Returns [(x0, seg_length), (x1, seg_length), ..., (xn, seg_length)]"""
    res = []
    if not integer:
        for i in range(n):
            res.append((i * length / n, length / n))
    else:
        segment_length = int(length / n)
        offset = (length - (segment_length * n)) / 2
        for i in range(n):
            res.append((offset + segment_length * i, segment_length))
    return res


def circle_contains(center, radius, pt):
    return dist(center, pt) <= radius


def dot_prod(p1, p2):
    if isinstance(p1, int) or isinstance(p1, float):
        return p1 * p2
    else:
        return sum(i1 * i2 for (i1, i2) in zip(p1, p2))


def cross_prod(v1, v2):
    a1 = v1[0] if len(v1) >= 1 else 0
    a2 = v1[1] if len(v1) >= 2 else 0
    a3 = v1[2] if len(v1) >= 3 else 0

    b1 = v2[0] if len(v2) >= 1 else 0
    b2 = v2[1] if len(v2) >= 2 else 0
    b3 = v2[2] if len(v2) >= 3 else 0

    return (det2x2(a2, a3, b2, b3),
            -det2x2(a1, a3, b1, b3),
            det2x2(a1, a2, b1, b2))


def dist_from_point_to_line(p, l1, l2, segment=False):
    return mag(vector_from_point_to_line(p, l1, l2, segment=segment))


def vector_from_point_to_line(p, l1, l2, segment=False):
    if l1 == l2:
        return sub(p, l1)  # kind of a lie, if segment == False
    else:
        a = l1
        n = set_length(sub(l2, a), 1)  # unit vector along line

        # copied from wikipedia "Distance from a point to a line: Vector formulation"
        a_minus_p = sub(a, p)
        n_with_a_useful_length = set_length(n, dot_prod(a_minus_p, n))
        vec_to_line = sub(a_minus_p, n_with_a_useful_length)

        if segment:
            pt_on_line = add(p, vec_to_line)
            if (dot_prod(sub(pt_on_line, l1), sub(l2, l1)) > 0 and
                    dot_prod(sub(pt_on_line, l2), sub(l1, l2)) > 0):
                return vec_to_line  # the closest point is between the two end points
            else:
                if dist(l1, p) < dist(l2, p):  # otherwise choose the closer endpoint
                    return sub(l1, p)
                else:
                    return sub(l2, p)


def det2x2(a, b, c, d):
    return a * d - b * c


def line_line_intersection(xy1, xy2, xy3, xy4):
    x1, y1 = xy1
    x2, y2 = xy2
    x3, y3 = xy3
    x4, y4 = xy4

    det = det2x2

    denominator = det(
        det(x1,  1, x2, 1),
        det(y1,  1, y2, 1),
        det(x3,  1, x4, 1),
        det(y3,  1, y4, 1)
    )

    if denominator == 0:
        # lines are parallel
        return None

    p_x_numerator = det(
        det(x1, y1, x2, y2),
        det(x1,  1, x2,  1),
        det(x3, y3, x4, y4),
        det(x3,  1, x4,  1)
    )

    p_y_numerator = det(
        det(x1, y1, x2, y2),
        det(y1,  1, y2, 1),
        det(x3, y3, x4, y4),
        det(y3,  1, y4, 1)
    )

    return (p_x_numerator / denominator,
            p_y_numerator / denominator)


def projection(v1, v2):
    """finds the vector projection of v1 onto v2, or None if it doesn't exist"""
    v2_mag = mag(v2)
    if v2_mag == 0:
        return None
    else:
        v1_dot_v2 = dot_prod(v1, v2)
        return set_length(v2, v1_dot_v2 / v2_mag)


def rejection(v1, v2):
    """finds the vector rejection of v1 onto v2, or None if it doesn't exist"""
    proj_v1_onto_v2 = projection(v1, v2)
    if proj_v1_onto_v2 is None:
        return None
    else:
        return sub(v1, proj_v1_onto_v2)

def center_rect_in_rect(to_move, in_rect):
    return [
        in_rect[0] + in_rect[2] / 2 - to_move[2] / 2,
        in_rect[1] + in_rect[3] / 2 - to_move[3] / 2,
        to_move[2], to_move[3]
    ]

def rect_expand(rect, all_sides=0, left=0, right=0, top=0, bottom=0):
    return [rect[0] - all_sides - left,
            rect[1] - all_sides - top,
            rect[2] + all_sides * 2 + left + right,
            rect[3] + all_sides * 2 + top + bottom]

def iterate_pairwise(l):
    for i in range(len(l)):
        yield (l[i], l[(i + 1) % len(l)])

def circular_lists_equal(l1, l2, thresh=0):
    if len(l1) != len(l2):
        return False

    if not eq(list(sorted(l1)), list(sorted(l2)), thresh=thresh):
        return False

    n = len(l1)
    for offs in range(n):
        all_good = True
        for i in range(n):
            if abs(l1[i] - l2[(i + offs) % n]) > thresh:
                all_good = False
                break
        if all_good:
            return True
    return False

def lightly_shuffle(items: typing.List[T], strength=0.25) -> typing.List[T]:
    """
    :param items: list of items to shuffle
    :param strength: [0, 1.0) 0 is no shuffling, 1 is (nearly) fully shuffled.
    """
    weighted_items = []
    n = len(items)
    for i in range(n):
        weighted_items.append((i + n * random.random() * strength, i, items[i]))
    weighted_items.sort()
    return list(map(lambda t: t[2], weighted_items))


def time_to_str(seconds=0., minutes=0., hours=0.,  # NOQA
                decimals: typing.Union[int, typing.Tuple[int, int]] = (1, 3),
                show_hours_as_minutes=False) -> str:
    """Formats a quantity of elapsed time into a human-readable string.

        The format will be one of the following:
            h:mm:ss[.xxx...]
               m:ss[.xxx...]
                  s[.xxx...]
        Args:
            decimals: The minimum and maximum number of decimal places to display. If a single number is given,
                      it will be interpreted as an exact number of decimal places to include.
            show_hours_as_minutes: If True, the hours places will be shown as minutes, going above 60 if needed.
    """
    total_secs = hours * 60 * 60 + minutes * 60 + seconds

    is_neg = total_secs < 0
    total_secs = abs(total_secs)

    if isinstance(decimals, tuple):
        min_dec, max_dec = decimals
    else:
        min_dec, max_dec = (decimals, decimals)

    frac = total_secs - int(total_secs)
    if max_dec <= 0:
        frac_str = ""
    else:
        frac_str = '{num:.{prec}f}'.format(num=frac, prec=max_dec)[2:]
        if len(frac_str) < min_dec:
            # lengthen the decimal part if it's too short
            frac_str = frac_str + '0' * (min_dec - len(frac_str))
        else:
            # slice off unnecessary trailing zeros
            while frac_str.endswith('0') and len(frac_str) > min_dec:
                frac_str = frac_str[:-1]
    total_secs = int(total_secs)

    s = total_secs % 60

    if not show_hours_as_minutes:
        m = (total_secs // 60) % 60
        hr = (total_secs // 3600)
    else:
        m = (total_secs // 60)
        hr = 0

    s2 = f"{s}".zfill(2)  # "2" -> "02"
    m2 = f"{m}".zfill(2)  # "2" -> "02"

    if hr > 0:
        res = f"{hr}:{m2}:{s2}"
    elif m > 0:
        res = f"{m}:{s2}"
    else:
        res = f"{s}"

    if len(frac_str) > 0:
        res = f"{res}.{frac_str}"

    if is_neg:
        res = f"-{res}"

    return res


# yoinkers from https://stackoverflow.com/a/13790741
def res_path(filepath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, filepath)