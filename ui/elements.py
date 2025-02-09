import typing

import pygame
import poker.hands as hands
import ui.colors as colors

_ELEMENT_UID_COUNTER = 0


def _next_element_uid():
    global _ELEMENT_UID_COUNTER
    _ELEMENT_UID_COUNTER += 1
    return _ELEMENT_UID_COUNTER - 1


class Element:

    def __init__(self, uid=None):
        self.uid = _next_element_uid() if uid is None else uid
        self.parent = None
        self.children = []
        self.rect = [0, 0, 0, 0]

    def get_parent(self) -> 'Element':
        return self.parent

    def all_ancestors(self, top_down_ordering=True, include_self=False):
        res = [self] if include_self else []
        cur = self.get_parent()
        while cur is not None:
            res.append(cur)
            cur = cur.get_parent()
        if top_down_ordering:
            res = reversed(res)
        for p in res:
            yield p

    def all_children(self, recurse=True):
        for c in self.children:
            yield c
            if recurse:
                for c2 in c.all_children(recurse=recurse):
                    yield c2

    def get_xy(self, absolute=False) -> typing.Tuple[int, int]:
        if not absolute:
            return self.rect[0], self.rect[1]
        else:
            x, y = 0, 0
            for e in self.all_ancestors(include_self=True):
                x += e.rect[0]
                y += e.rect[1]
            return x, y

    def get_rect(self, absolute=False):
        x, y = self.get_xy(absolute=absolute)
        return [x, y, self.rect[2], self.rect[3]]

    def render(self, surf, root_xy=(0, 0)):
        x = root_xy[0] + self.rect[0]
        y = root_xy[1] + self.rect[1]
        self.render_at(surf, abs_xy=(x, y))

    def render_at(self, surf: pygame.Surface, abs_xy):
        rect = [abs_xy[0], abs_xy[1], self.rect[2], self.rect[3]]
        color = colors.rainbow(pygame.time.get_ticks() / 1000. + self.uid / 10.)
        pygame.draw.rect(surf, color, rect, width=2)

    def __eq__(self, other):
        return self.uid == other.uid

    def __hash__(self):
        return hash(self.uid)


