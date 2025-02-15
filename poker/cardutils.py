import re
import typing
import functools
import itertools

RANKS = 'AKQJT98765432'
SUITS = ['s', 'h', 'd', 'c']

# Hole card patterns
PAIRS = "22+"
STRONG_ACES = "AK, AQ, AJ"
BROADWAYS="KJ, KQ, QJ"
SUITED_CONNECTORS = "32s-AKs"
SUITED_GAPPERS = "42s-AQs"


class HandTypes:
    # Made Hands
    STRAIGHT_FLUSH = "Straight Flush"
    QUADS = "Quads"
    FULL_HOUSE = "Full House"
    FLUSH = "Flush"
    STRAIGHT = "Straight"
    TRIPS = "Trips"
    TWO_PAIR = "Two Pair"
    PAIR = "Pair"
    HIGH_CARD = "High Card"

    ORDERED_BY_STRENGTH = [
        HIGH_CARD,
        PAIR,
        TWO_PAIR,
        TRIPS,
        STRAIGHT,
        FLUSH,
        FULL_HOUSE,
        QUADS,
        STRAIGHT_FLUSH
    ]

    # Draws
    FLUSH_DRAW = "Flush Draw"
    RR_FLUSH_DRAW = "RR_FLUSH_DRAW"
    OESD = "Open Ended Straight Draw"
    GSSD = "Gut Shot Straight Draw"

    # Qualitative Hands
    ONE_OVERCARD = "Overcard"
    TWO_OVERCARDS = "Two Overcards"
    SET = "Set"
    WEAK_TRIPS = "Weak Trips"
    OVERPAIR = "Overpair"
    TOP_PAIR = "Top Pair"
    MIDDLE_POCKET_PAIR = "Middle Pocket Pair"
    MIDDLE_PAIR = "Middle Pair"
    BOTTOM_PAIR = "Bottom Pair"
    UNDERPAIR = "Underpair"
    NUTS = "The Nuts"

class BoardTypes:
    MONOCHROME = "Monochrome"
    TWO_OF_A_SUIT = "Two of a Suit"
    THREE_OF_A_SUIT = "Three of a Suit"
    FOUR_OF_A_SUIT = "Four of a Suit"
    FIVE_OF_A_SUIT = "Five of a Suit"

    UNPAIRED = "Unpaired"
    PAIRED = "Paired"
    TRIPLED = "Tripled"
    DOUBLE_PAIRED = "Double Paired"
    THREE_CONNECTED = "Three Connected"
    FOUR_CONNECTED = "Four Connected"

def to_card_code(cards) -> str:
    """
    (Ad, Kd) -> AKs
    (6s, 6c) -> 66
    (Jh, Td) -> JTo
    """
    if cards == (None, None):
        return '??'
    elif cards[1] is None:
        return cards[0][0] + '?'
    else:
        c0 = cards[0]
        c1 = cards[1]
        if RANKS.index(c0[0]) <= RANKS.index(c1[0]):
            res = c0[0] + c1[0]
        else:
            res = c1[0] + c0[0]

        if res[0] == res[1]:
            return res  # Pair
        elif cards[0][1] == cards[1][1]:
            return res + "s"  # Suited
        else:
            return res + "o"  # Off-Suited


def all_card_codes() -> str:
    for yrank in RANKS:
        for xrank in RANKS:
            if RANKS.index(xrank) <= RANKS.index(yrank):
                yield to_card_code((f"{yrank}s", f"{xrank}h"))  # pairs and off-suits
            else:
                yield to_card_code((f"{yrank}s", f"{xrank}s"))  # suited


def cards_match_pattern(cards, pattern_code: str):
    patterns = re.split(r'[ ,]+', pattern_code.strip())
    for pattern in patterns:
        code = to_card_code(cards)
        if "+" not in pattern and "-" not in pattern:
            if code == pattern:
                return True  # exact match
            if (not pattern.endswith("s") and not pattern.endswith("o")
                    and (code.endswith("s") or code.endswith("o"))
                    and code[:2] == pattern):
                return True  # AKo and AKs should match AK
        elif "+" in pattern:
            if pattern[0] == pattern[1]:  # a 66+ type pattern
                idx = RANKS.index(pattern[0])
                for r in RANKS[0:idx+1]:
                    if cards_match_pattern(cards, f"{r}{r}"):
                        return True
            else:
                # an A5+ style pattern (meaning A5, A6, ... AK)
                r1 = pattern[0]
                r2 = pattern[1]
                p = f"{r1}X"
                if pattern[2] in ("s", "o"):
                    p += pattern[2]
                for idx in range(RANKS.index(r2), RANKS.index(r1)):
                    if cards_match_pattern(cards, p):
                        return True
        elif "-" in pattern:
            p1, p2 = pattern.split("-")
            if (p1.endswith("s") and p2.endswith("o")) or (p1.endswith("o") and p2.endswith("s")):
                raise ValueError(f"Non-uniform suitedness codes in range-based pattern: {pattern}")
            suit = "o" if (p1.endswith("o") or p2.endswith("o")) else ("s" if (p1.endswith("s") or p2.endswith("s")) else "")
            if p1[0] == p1[1]:
                if p2[0] != p2[1]:
                    raise ValueError(f"Invalid range-based pattern: {pattern}")
                # 66-TT type pattern (pairs)
                idx1 = RANKS.index(p1[0])
                idx2 = RANKS.index(p2[0])
                for i in range(min(idx1, idx2), max(idx1, idx2) + 1):
                    if cards_match_pattern(cards, f"{RANKS[i]}{RANKS[i]}"):
                        return True
            elif p1[0] == p2[0]:
                # A5-A9 type range (kickers)
                idx1 = RANKS.index(p1[1])
                idx2 = RANKS.index(p2[1])
                for i in range(min(idx1, idx2), max(idx1, idx2) + 1):
                    if cards_match_pattern(cards, f"{p1[0]}{RANKS[i]}{suit}"):
                        return True
            else:
                # JTs-87s type range (gappers)
                p1_idx1 = RANKS.index(p1[0])
                p1_idx2 = RANKS.index(p1[1])
                p2_idx1 = RANKS.index(p2[0])
                p2_idx2 = RANKS.index(p2[1])
                if p1_idx1 - p1_idx2 != p2_idx1 - p2_idx2:
                    raise ValueError(f"Invalid range-based pattern: {pattern}")
                gap = p1_idx1 - p1_idx2

                for i in range(min(p1_idx1, p2_idx1), max(p1_idx1, p2_idx1) + 1):
                    if cards_match_pattern(cards, f"{RANKS[i]}{RANKS[i-gap]}{suit}"):
                        return True
    return False


def all_cards(ignore=()) -> typing.Generator[str, None, None]:
    for r in RANKS:
        for s in SUITS:
            res = f"{r}{s}"
            if res not in ignore:
                yield res


def sort_by_rank(cards: typing.List[str]) -> typing.List[str]:
    res = list(cards)
    res.sort(key=lambda c: RANKS.index(c[0]))
    return res


def get_ranks(cards: typing.List[str]) -> typing.List[int]:
    return list(map(lambda c: c[0], cards))


def compare_by_ranks(cards1, cards2):
    for c1, c2 in zip(cards1, cards2):
        r1 = RANKS.index(c1[0])
        r2 = RANKS.index(c2[0])
        if r1 != r2:
            return 1 if r1 < r2 else -1
    return 0


def split_by_suits(cards) -> typing.Dict[str, typing.List[str]]:
    res = {}
    for c in cards:
        if c[1] not in res:
            res[c[1]] = []
        res[c[1]].append(c)
    return res


def split_by_ranks(cards) -> typing.Dict[str, typing.List[str]]:
    res = {}
    for c in cards:
        if c[0] not in res:
            res[c[0]] = []
        res[c[0]].append(c)
    return res


def find_kickers(made_hand, cards):
    res = []
    for c in cards:
        if len(made_hand) + len(res) >= 5:
            return res
        if c not in made_hand:
            res.append(c)
    return res


@functools.total_ordering
class EvalHand:

    def __init__(self, hole_cards, board):
        self.hole_cards = tuple(hole_cards)
        self.board = tuple(board)

        made = calc_hand(list(hole_cards) + list(board))
        self.made_type = made[0]
        self.made_cards = made[1]
        self.made_kickers = made[2]

    def is_complete(self):
        return len(self.board) >= 5

    def __lt__(self, other: 'EvalHand'):
        my_str = HandTypes.ORDERED_BY_STRENGTH.index(self.made_type)
        other_str = HandTypes.ORDERED_BY_STRENGTH.index(other.made_type)
        if my_str != other_str:
            return my_str < other_str

        cmp = compare_by_ranks(self.made_cards, other.made_cards)
        if cmp != 0:
            return cmp < 0

        cmp = compare_by_ranks(self.made_kickers, other.made_kickers)
        return cmp < 0

    def __eq__(self, other: 'EvalHand'):
        return not (self < other) and not (other < self)

    def __hash__(self):
        return hash((self.made_type, get_ranks(self.made_cards), get_ranks(self.made_kickers)))

    def __repr__(self):
        return str(self)

    def __str__(self):
        res = f"{self.made_type} [{' '.join(self.made_cards)}]"
        if len(self.made_kickers) > 0:
            res = f"{res} ({' '.join(self.made_kickers)})"
        return res


def calc_hand(cards):
    """returns: (HAND_TYPE, cards, kicker(s))
    """
    cards = sort_by_rank(cards)
    by_suit = split_by_suits(cards)
    by_rank = split_by_ranks(cards)
    trips = [g for g in by_rank.values() if len(g) == 3]
    pairs = [g for g in by_rank.values() if len(g) == 2]

    # STRAIGHT_FLUSHES
    for s in by_suit:
        if len(by_suit[s]) >= 5:
            best = []
            for c in by_suit[s]:
                if len(best) == 0:
                    best.append(c)
                elif len(best) == 5:
                    break
                elif RANKS.index(best[-1][0]) == RANKS.index(c[0]) - 1:
                    best.append(c)
                else:
                    best.clear()
                    best.append(c)
            if len(best) == 5:
                return HandTypes.STRAIGHT_FLUSH, best, []

    # QUADS
    for rank_group in by_rank.values():
        if len(rank_group) == 4:
            best = list(rank_group)
            return HandTypes.QUADS, best, find_kickers(best, cards)

    # FULL HOUSES
    if len(trips) >= 1 and (len(trips) + len(pairs)) >= 2:
        best = list(trips[0])
        if len(trips) > 1:
            best.extend(trips[1][0:2])
        else:
            best.extend(pairs[0])
        return HandTypes.FULL_HOUSE, best, []

    # FLUSHES
    for suit_group in by_suit.values():
        if len(suit_group) >= 5:
            return HandTypes.FLUSH, suit_group[:5], []

    # STRAIGHTS
    best_straight = []
    for c in cards:
        if len(best_straight) == 0:
            best_straight.append(c)
        elif len(best_straight) == 5:
            break
        elif RANKS.index(best_straight[-1][0]) == RANKS.index(c[0]) - 1:
            best_straight.append(c)
        elif RANKS.index(best_straight[-1][0]) == RANKS.index(c[0]):
            pass  # dupe rank inside the straight, has no effect
        else:
            best_straight.clear()
            best_straight.append(c)
    if len(best_straight) == 5:
        return HandTypes.STRAIGHT, best_straight, []

    # TRIPS
    if len(trips) == 1:
        return HandTypes.TRIPS, trips[0], find_kickers(trips[0], cards)

    # TWO_PAIRS
    if len(pairs) >= 2:
        best = pairs[0] + pairs[1]
        return HandTypes.TWO_PAIR, best, find_kickers(best, cards)

    # PAIRS
    if len(pairs) == 1:
        return HandTypes.PAIR, pairs[0], find_kickers(pairs[0], cards)

    # HIGH_CARDS
    return HandTypes.HIGH_CARD, [cards[0]], cards[1:5]


def calc_equities(h_list, board) -> typing.List[float]:
    wins = calc_wins(h_list, board)
    denom = sum(wins)
    return [w / denom for w in wins]


def calc_wins(h_list, board) -> typing.List[float]:
    wins = [0] * len(h_list)
    if len(board) >= 5:
        evals = [(EvalHand(h, board), idx) for (idx, h) in enumerate(h_list)]
        evals.sort(reverse=True)
        winners = []
        for i in range(len(evals)):
            if i == 0 or evals[i][0] >= evals[i - 1][0]:
                winners.append(evals[i])
            else:
                break
        for _, idx in winners:
            wins[idx] += 1 / len(winners)
    else:
        used_cards = set()
        for (c1, c2) in h_list:
            used_cards.add(c1)
            used_cards.add(c2)
        for c in board:
            used_cards.add(c)

        domain = list(all_cards(ignore=used_cards))
        to_draw = 5 - len(board)

        for draws in itertools.combinations(domain, to_draw):
            w = calc_wins(h_list, board + list(draws))
            for i in range(len(wins)):
                wins[i] += w[i]

    return wins


if __name__ == "__main__":
    tests = {
        "str_flush":    ['Js', 'Qs', 'Qd', '3s', 'Ts', '9s', '8s'],
        "quad_4s":      ['4h', '4d', 'Ks', '8c', '4c', '8s', '4c'],
        "full_hs":      ['Js', 'Qs', 'Qd', '8h', 'Ts', '8c', '8s'],
        # "full_hs2":     ['Js', 'Qs', 'Qd', '8h', 'Qh', '8c', '8s'],
        "flush":        ['Js', 'Qs', 'Qd', '3s', '2s', '9s', '8s'],
        "straight":     ['Js', 'Qs', 'Qd', '3s', 'Tc', '9c', '8s'],
        "trip_3s":      ['3s', '3d', '4h', 'Ks', '2d', '3h', '7d'],
        "twp_pair":     ['As', '3d', '4h', '7s', '2d', '3h', '7d'],
        "pair_3s":      ['As', '3d', '4h', 'Ks', '2d', '3h', '7d'],
        "ace_high":     ['Qc', '4h', '3s', 'As', 'Ts', '9c', '8s'],
    }
    # evals = []
    # for t in tests:
    #     evals.append(EvalHand(tests[t][0:2], tests[t][2:]))
    #     print(f"{t:<16}{evals[-1]}")
    # evals.sort()
    # print(evals)

    evals = {
       # "AKs vs AKs": ((['As', 'Ks'], ['Ad', 'Kd']), []),
       #  "44 vs 44": ((['4s', '4d'], ['4c', '4h']), []),
        "AKs vs AKo vs QQ": ((['As', 'Ks'], ['Ad', 'Kc'], ['Qs', 'Qc']), []),
    }

    for k, v in evals.items():
        print(f"{k}: {calc_equities(v[0], v[1])}")
    print()