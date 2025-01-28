import typing

import cardutils
import actions
import hands


def hero_saw_flop(hand) -> bool:
    return hand.hero_got_to_street(actions.FLOP)

class Filter:

    def __init__(self):
        pass

    def test(self, hand: 'hands.Hand') -> bool:
        return True

    def __or__(self, other: 'Filter'):
        return OrFilter([self, other])

    def __and__(self, other: 'Filter'):
        return AndFilter([self, other])

    def __invert__(self):
        return NotFilter(self)


class HeroCardFilter(Filter):

    def __init__(self, pattern):
        super().__init__()
        self.pattern = pattern

    def test(self, hand: hands.Hand) -> bool:
        hero = hand.get_hero()
        return cardutils.cards_match_pattern(hero.cards, self.pattern)


class HeroSawStreet(Filter):

    def __init__(self, street):
        super().__init__()
        self.street = street

    def test(self, hand: hands.Hand) -> bool:
        return hand.hero_got_to_street(self.street)


class HeroVPIP(Filter):

    def __init__(self, street=actions.PRE_FLOP):
        super().__init__()
        self.street = street

    def test(self, hand: 'hands.Hand') -> bool:
        for a in hand.all_actions(player_id=hand.hero_id, street=self.street):
            if a.is_vpip():
                return True
        return False


class HeroAtPosition(Filter):

    def __init__(self, pos):
        super().__init__()
        self.pos = pos if isinstance(pos, tuple) else (pos,)

    def test(self, hand: 'hands.Hand') -> bool:
        pp = hand.get_position_to_player_mapping()
        for pos in self.pos:
            if pos in pp:
                for p in pp[pos]:
                    if hands.Player.names_eq(hand.hero_id, p):
                        return True
        return False


class Multiway(Filter):

    def __init__(self, street, at_least=2, at_most=float('inf')):
        super().__init__()
        self.street = street
        self.at_least = at_least
        self.at_most = at_most

    def test(self, hand: hands.Hand) -> bool:
        return self.at_most >= len(hand.players_involved_at_street(self.street)) >= self.at_least


class CompoundFilter(Filter):

    def __init__(self, subfilters: typing.Sequence[Filter]):
        super().__init__()
        self.subfilters = subfilters


class AndFilter(CompoundFilter):

    def __init__(self, subfilters: typing.Sequence[Filter]):
        super().__init__(subfilters)

    def test(self, hand: hands.Hand) -> bool:
        return all(f.test(hand) for f in self.subfilters)


class OrFilter(CompoundFilter):

    def __init__(self, subfilters: typing.Sequence[Filter]):
        super().__init__(subfilters)

    def test(self, hand: hands.Hand) -> bool:
        return any(f.test(hand) for f in self.subfilters)


class NotFilter(Filter):

    def __init__(self, subfilter: Filter):
        super().__init__()
        self.subfilter = subfilter

    def test(self, hand: 'hands.Hand') -> bool:
        return not self.subfilter.test(hand)

