import typing

import pygame
import poker.filters as filters
import poker.hands as hands
import poker.cardutils as cardutils

import ui.sprites as sprites
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

    def get_title(self) -> str:
        return str(self)

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


class _CardSquare(Element):

    def __init__(self, parent: 'CardGrid', code: str):
        super().__init__()
        self.code = code  # e.g. AKs
        self.max_profit_color = 5.  # bbs
        self.set_parent(parent)

    def get_title(self) -> str:
        return self.code

    def get_parent(self) -> 'CardGrid':
        return super().get_parent()

    def get_rel_rect(self):
        return self.get_parent().get_rect_for(self.code)

    def _get_subgroup(self) -> hands.HandGroup:
        return self.get_parent().get_group_for(self.code)

    def get_font(self) -> pygame.Font:
        return sprites.Sprites.FONT_SMALL

    def render_at(self, surf: pygame.Surface, abs_xy):
        dims = self.get_dims()
        rect = [abs_xy[0], abs_xy[1], dims[0], dims[1]]

        hand_group = self._get_subgroup()
        avg_bbs = hand_group.avg_bbs_per_play()
        if len(hand_group) == 0:
            bg_color = colors.DARK_GRAY
        else:
            bg_color = colors.profit_gradient(avg_bbs / self.max_profit_color)
        outline_color = colors.lerp(0.5, bg_color, (0, 0, 0))

        pygame.draw.rect(surf, bg_color, rect)
        pygame.draw.rect(surf, outline_color, rect, width=1)

        ins = 2

        font = self.get_font()
        label_txt = sprites.Sprites.FONT.render(self.code, False, colors.BLACK)
        surf.blit(label_txt, (rect[0] + ins * 2, rect[1] + ins * 2))

        group = self.get_parent().get_group_for(self.code)
        quantity_txt = font.render(f"{len(group)}", False, colors.BLACK)
        surf.blit(quantity_txt, (rect[0] + rect[2] - quantity_txt.get_width() - ins, rect[1] + ins))

        avg_bbs = group.avg_bbs_per_play()
        plus = '+' if avg_bbs > 0 else ''
        bbs_per_100_txt = font.render(f"{plus}{avg_bbs:.1f}bb", False, colors.BLACK)
        surf.blit(bbs_per_100_txt, (rect[0] + ins, rect[1] + rect[3] - bbs_per_100_txt.get_height() - ins))

        # win_pcnt = group.win_pcnt(after_vpip=True)
        # win_pcnt_txt = font.render(f"{win_pcnt * 100.:.0f}%", False, colors.BLACK)
        # surf.blit(win_pcnt_txt, (rect[0] + rect[2] - win_pcnt_txt.get_width() - ins,
        #                             rect[1] + rect[3] - win_pcnt_txt.get_height() - ins))


class CardGrid(Element):

    def __init__(self, rect, group: hands.HandGroup):
        super().__init__()
        self.group = group

        self.grid_dims = (len(cardutils.RANKS),) * 2
        self._rect = rect
        self._squares = {}  # card_code -> ((x, y), CardSquare, subgroup)
        self._build_sub_elements()

    def _build_sub_elements(self):
        for idx, cc in enumerate(cardutils.all_card_codes()):
            y = idx // self.grid_dims[0]
            xy = (idx - (y * self.grid_dims[0]), y)
            square = _CardSquare(self, cc)
            self._squares[cc] = xy, square, self.group.filter(filters.HeroCardFilter(cc))

    def get_title(self):
        return self.group.desc

    def set_rect(self, rect):
        self._rect = rect

    def get_rel_rect(self) -> typing.Tuple[int, int, int, int]:
        return self._rect

    def get_rect_for(self, cardcode: str):
        (x, y), _, _ = self._squares[cardcode]
        x_segs = ui.utils.subdivide_evenly_and_center(self.get_dims()[0], self.grid_dims[0])
        y_segs = ui.utils.subdivide_evenly_and_center(self.get_dims()[1], self.grid_dims[1])
        return [x_segs[x][0], y_segs[y][0], x_segs[x][1], y_segs[y][1]]

    def get_group_for(self, cardcode: str) -> hands.HandGroup:
        return self._squares[cardcode][2]


