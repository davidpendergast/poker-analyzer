import typing

import pygame
import poker as poker
import ui.colors as colors
import ui.utils

_ELEMENT_UID_COUNTER = 0


def _next_element_uid():
    global _ELEMENT_UID_COUNTER
    _ELEMENT_UID_COUNTER += 1
    return _ELEMENT_UID_COUNTER - 1


class Element:

    def __init__(self, uid=None):
        self.uid = _next_element_uid() if uid is None else uid
        self.parent: typing.Optional['Element'] = None
        self.children = []

    def get_parent(self) -> typing.Optional['Element']:
        return self.parent

    def set_parent(self, parent: typing.Optional['Element']):
        if self.parent == parent:
            # fail fast, don't want to allow UI bugs to go unnoticed
            raise ValueError(f"Element {self} already has parent {parent}.")
        if self.parent is not None:
            self.parent.children.remove(self)  # disconnect self from old parent
        self.parent = parent
        if self.parent is not None:
            self.parent.children.append(self)

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
        rel_rect = self.get_rel_rect()
        rel_xy = rel_rect[0], rel_rect[1]
        if not absolute:
            return rel_xy
        else:
            x, y = rel_xy
            for e in self.all_ancestors(include_self=True):
                x += e.get_xy(absolute=False)[0]
                y += e.get_xy(absolute=False)[1]
            return x, y

    def get_dims(self) -> typing.Tuple[int, int]:
        rect = self.get_rel_rect()
        return rect[2], rect[3]

    def get_abs_rect(self) -> typing.Tuple[int, int, int, int]:
        x, y = self.get_xy(absolute=True)
        dims = self.get_dims()
        return x, y, dims[0], dims[1]

    def get_rel_rect(self) -> typing.Tuple[int, int, int, int]:
        """Subclasses should override this"""
        raise NotImplementedError()

    def render(self, surf, root_xy=(0, 0)):
        rel_xy = self.get_xy(absolute=False)
        x = root_xy[0] + rel_xy[0]
        y = root_xy[1] + rel_xy[1]
        self.render_at(surf, abs_xy=(x, y))
        for c in self.all_children(recurse=True):
            c.render(surf, root_xy=(x, y))

    def render_at(self, surf: pygame.Surface, abs_xy):
        dims = self.get_dims()
        rect = [abs_xy[0], abs_xy[1], dims[0], dims[1]]
        color = colors.rainbow(pygame.time.get_ticks() / 1000. + self.uid / 10.)
        pygame.draw.rect(surf, color, rect, width=2)

    def __eq__(self, other):
        if other is None:
            return False
        else:
            return self.uid == other.uid

    def __hash__(self):
        return hash(self.uid)

    def __str__(self):
        return f"{type(self).__name__}(uid={self.uid})"


class CardSquare(Element):

    def __init__(self, parent: 'CardGrid', code: str):
        super().__init__()
        self.code = code  # e.g. AKs
        self.set_parent(parent)

    def get_parent(self) -> 'CardGrid':
        return super().get_parent()

    def get_rel_rect(self):
        return self.get_parent().get_rect_for(self.code)


class CardGrid(Element):

    def __init__(self, rect, group: poker.hands.HandGroup):
        super().__init__()
        self.group = group

        self.grid_dims = (len(poker.cardutils.RANKS),) * 2
        self._rect = rect
        self._squares = {}  # card_code -> ((x, y), CardSquare)
        self._build_sub_elements()

    def _build_sub_elements(self):
        for idx, cc in enumerate(poker.cardutils.all_card_codes()):
            y = idx // self.grid_dims[0]
            xy = (idx - (y * self.grid_dims[0]), y)
            square = CardSquare(self, cc)
            self._squares[cc] = xy, square

    def get_rel_rect(self) -> typing.Tuple[int, int, int, int]:
        return self._rect

    def get_rect_for(self, cardcode: str):
        (x, y), _ = self._squares[cardcode]
        x_segs = ui.utils.subdivide_evenly_and_center(self.get_dims()[0], self.grid_dims[0])
        y_segs = ui.utils.subdivide_evenly_and_center(self.get_dims()[1], self.grid_dims[1])
        return [x_segs[x][0], y_segs[y][0], x_segs[x][1], y_segs[y][1]]


