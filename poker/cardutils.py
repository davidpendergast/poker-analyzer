import collections
import math
import random
import re
import typing
import functools
import itertools

import poker.hands
import profiling
import const

RANKS = 'AKQJT98765432'
SUITS = ['s', 'h', 'd', 'c']

# Hole card patterns
PAIRS = "22+"
STRONG_ACES = "AK, AQ, AJ"
BROADWAYS = "KJ, KQ, QJ"
SUITED_CONNECTORS = "32s-AKs"
SUITED_GAPPERS = "42s-AQs"

_CARD_CODES_ORDERED_BY_PREFLOP_EQUITY = []
_CARD_CODES_ORDERED_BY_PREFLOP_EQUITY_WITH_DUPES = []


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


def all_combos_of_card_code(cc):
    if cc[0] == cc[1]:
        for i1 in range(4):
            for i2 in range(i1 + 1, 4):
                yield (f"{cc[0]}{SUITS[i1]}", f"{cc[1]}{SUITS[i2]}")
    else:
        for s1 in SUITS:
            for s2 in SUITS:
                if s1 == s2 and cc[-1] == 'o':
                    continue
                elif s1 != s2 and cc[-1] == 's':
                    continue
                else:
                    yield (f"{cc[0]}{s1}", f"{cc[1]}{s2}")


def all_card_codes() -> str:
    for yrank in RANKS:
        for xrank in RANKS:
            if RANKS.index(xrank) <= RANKS.index(yrank):
                yield to_card_code((f"{yrank}s", f"{xrank}h"))  # pairs and off-suits
            else:
                yield to_card_code((f"{yrank}s", f"{xrank}s"))  # suited


def number_of_combos(cc) -> int:
    if cc[0] == cc[1]:
        return 6
    elif cc[-1] == 's':
        return 4
    elif cc[-1] == 'o':
        return 12
    elif cc == '??':
        return -1
    else:
        return 16


def get_best_preflop_card_codes(min_pcnt, max_pcnt=1.):
    if len(_CARD_CODES_ORDERED_BY_PREFLOP_EQUITY) == 0:
        import poker.preflop_db as db
        _CARD_CODES_ORDERED_BY_PREFLOP_EQUITY.extend(all_card_codes())
        _CARD_CODES_ORDERED_BY_PREFLOP_EQUITY.sort(key=lambda cc: db.get_avg_equity_vs_all(cc))
        for cc in _CARD_CODES_ORDERED_BY_PREFLOP_EQUITY:
            for _ in range(number_of_combos(cc)):
                _CARD_CODES_ORDERED_BY_PREFLOP_EQUITY_WITH_DUPES.append(cc)

    start_idx = int(min_pcnt * len(_CARD_CODES_ORDERED_BY_PREFLOP_EQUITY_WITH_DUPES))
    end_idx = int(max_pcnt * len(_CARD_CODES_ORDERED_BY_PREFLOP_EQUITY_WITH_DUPES))
    res = []
    seen = set()
    for i in range(start_idx, end_idx):
        cc = _CARD_CODES_ORDERED_BY_PREFLOP_EQUITY_WITH_DUPES[i]
        if cc not in seen:
            res.append(cc)
            seen.add(cc)
    return res


def cards_match_pattern(cards, pattern_code: str):
    patterns = re.split(r'[ ,]+', pattern_code.strip())
    for pattern in patterns:
        code = to_card_code(cards)
        if "%" in pattern:
            # "33%" (means best 33% of pre-flop hands)
            # "60-20%" (means best 60-20% of pre-flop hands)
            pattern = pattern.replace('%', '')
            if "-" in pattern:
                min_pcnt = 1 - float(pattern.split("-")[0]) / 100.
                max_pcnt = 1 - float(pattern.split("-")[1]) / 100.
            else:
                min_pcnt = 1 - float(pattern) / 100.
                max_pcnt = 1.0
            return code in get_best_preflop_card_codes(min_pcnt, max_pcnt=max_pcnt)

        elif "+" not in pattern and "-" not in pattern:
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


def sort_by_rank(cards: typing.Sequence[str]) -> typing.List[str]:
    res = list(cards)
    res.sort(key=lambda c: SUITS.index(c[1]))  # for consistency
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


def are_unique(cards):
    return len(set(cards)) == len(cards)


@functools.total_ordering
class EvalHand:

    def __init__(self, hole_cards, board):
        self.hole_cards = tuple(hole_cards)
        self.board = tuple(board)

        made = EvalHand._calc_hand(list(hole_cards) + list(board))
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

    @staticmethod
    def _calc_hand(cards):
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
                elif len(best) == 4 and best[0][0] == '5' and by_suit[s][0][0] == 'A':
                    return HandTypes.STRAIGHT_FLUSH, best + [by_suit[s][0]], []  # wheel (5432A)

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
        elif len(best_straight) == 4 and best_straight[0][0] == '5' and cards[0][0] == 'A':
            return HandTypes.STRAIGHT, best_straight + [cards[0]], []  # wheel (5432A)

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


def calc_equities(h_list, board, limit=float('inf')) -> typing.List[float]:
    """
    :param h_list: list of hands [('Ad', 'Ks'), ('Qh', 'Qs'), ...].
    :param board: list of cards on board ['4h', '4d', 'Jd'].
    :param limit: how many run-outs to simulate (or inf, to simulate them all).
    :return: list of each hand's equity.
    """
    if len(h_list) == 2 and len(board) == 0:
        # if it's a H2H pre-flop lookup, use cache
        import poker.preflop_db as db
        eq = db.get_equity(h_list[0], h_list[1])
        return [eq, 1 - eq]
    else:
        if len(board) == 0:
            # multi-way equities pre-flop are very costly to calculate, always need to limit this
            limit = min(limit, const.EQUITY_CALC_N_ITERS)

        wins = calc_wins(h_list, board, limit=limit)
        denom = sum(wins)
        return [w / denom for w in wins]


def calc_wins(h_list, board, limit=float('inf')) -> typing.List[float]:
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

        n_possible_outcomes = 1
        for i in range(to_draw):
            n_possible_outcomes *= (len(domain) - i)
        n_possible_outcomes /= math.factorial(to_draw)  # order of draws doesn't matter

        def gen():
            if limit >= n_possible_outcomes:
                for res in itertools.combinations(domain, to_draw):
                    yield res
            else:
                for _ in range(int(limit)):
                    yield random.sample(domain, to_draw)

        for draws in gen():
            w = calc_wins(h_list, board + list(draws))
            for i in range(len(wins)):
                wins[i] += w[i]

    return wins


def calc_payouts(hand: 'poker.hands.Hand') -> typing.Dict[str, float]:
    antes = 0
    amounts_put_in = {}
    active_players = set()
    players_and_cards = {}

    for player in hand.players:
        active_players.add(player.name_and_id)
        amounts_put_in[player.name_and_id] = -round(player.street_nets['pre-flop'] * 100 +
                                                    player.street_nets['flop'] * 100 +
                                                    player.street_nets['turn'] * 100 +
                                                    player.street_nets['river'] * 100)
        antes += -round(player.street_nets['ante'] * 100)
        if player.known_cards() == 2:
            players_and_cards[player.name_and_id] = player.cards
    all_in_players = set()

    for a in hand.all_actions():
        if a.is_fold():
            active_players.remove(a.player_id)
            continue
        elif a.is_all_in():
            active_players.remove(a.player_id)
            all_in_players.add(a.player_id)

    if len(active_players) + len(all_in_players) == 1:
        # if all but one folded, they get the entire pot.
        total = sum(v for v in amounts_put_in.values()) + antes
        return {next(iter(active_players.union(all_in_players))): total / 100.}

    remaining_players = [pid for pid in active_players.union(all_in_players)]
    remaining_players.sort(key=lambda pid: amounts_put_in[pid])

    pots = []
    for idx, cur_pid in enumerate(remaining_players):
        limit = amounts_put_in[cur_pid]
        if limit <= 0:
            continue
        pot = {"value": 0, "players": set()}
        for pid in amounts_put_in:
            if amounts_put_in[pid] >= limit:
                pot["players"].add(pid)
                pot["value"] += limit
                amounts_put_in[pid] -= limit
            else:
                # player contributed to pot but later folded
                pot["value"] += amounts_put_in[pid]
                amounts_put_in[pid] = 0
        pots.append(pot)

    pots[0]["value"] += antes

    payouts = []
    boards = hand.get_boards()
    for idx, b in enumerate(boards):
        sub_pots = []
        for p in pots:
            sub_pot = {"players": p["players"], "value": p["value"] // len(boards)}
            extra = p["value"] - len(boards) * sub_pot["value"]
            if idx < extra:
                sub_pot["value"] += 1  # extra pennies go into earlier pots
            sub_pots.append(sub_pot)
        payouts.append(_get_payout_for_board(hand, b, players_and_cards, remaining_players, sub_pots))

    if len(payouts) == 1:
        return payouts[0]
    else:
        # recombine split pots
        total_payout = {}
        for payout in payouts:
            for pid, value in payout.items():
                if pid not in total_payout:
                    total_payout[pid] = 0
                total_payout[pid] += value
        return total_payout


def _get_payout_for_board(hand, board, players_and_cards, remaining_players, pots):
    made_hands = {pid: EvalHand(players_and_cards[pid], tuple(board)) for pid in players_and_cards if (pid in remaining_players)}
    sorted_hands = [(mh, pid) for pid, mh in made_hands.items()]
    sorted_hands.sort(reverse=True)

    grouped_hands = []
    for mh in sorted_hands:
        if len(grouped_hands) == 0:
            grouped_hands.append([mh])
        elif grouped_hands[-1][0][0] == mh[0]:
            grouped_hands[-1].append(mh)
        else:
            grouped_hands.append([mh])

    def _split_up_pot(pot):
        winners = []
        for group in grouped_hands:
            for mh, g_pid in group:
                if g_pid in pot["players"]:
                    winners.append(g_pid)
            if len(winners) > 0:
                break

        if len(winners) == 0:
            raise ValueError(f"Couldn't find a winner for pot: {p}, {grouped_hands}")

        per_player = pot["value"] // len(winners)

        # logic for splitting non-evenly divisible pots
        extra = pot["value"] - per_player * len(winners)
        if extra > 0:
            winners.sort(key=lambda w_pid: hand.get_player(w_pid).position)

        res = {}
        for w_pid in winners:
            res[w_pid] = per_player
            if extra > 0:
                res[w_pid] += 1
                extra -= 1
        return res

    res = {}
    for p in pots:
        split = _split_up_pot(p)
        for pid in split:
            if pid not in res:
                res[pid] = 0
            res[pid] += split[pid]

    return {pid: res[pid] / 100. for pid in res}


def calc_all_in_equities(hand) -> typing.Dict[str, float]:
    pass


def format_pcnt(pcnt: float, cap=True) -> str:
    if cap:
        pcnt = max(0., min(.999, pcnt))
    res = f"{pcnt * 100:.1f}%"
    if len(res) < 5:
        res = f" {res}"
    return res


def safe_eq(coll1, coll2, thresh=0.00001):
    if isinstance(coll1, (int, float)):
        return abs(coll1 - coll2) < thresh
    elif isinstance(coll1, dict):
        if set(coll1.keys()) != set(coll2.keys()):
            return False
        else:
            for k in coll1:
                if not safe_eq(coll1[k], coll2[k], thresh=thresh):
                    return False
        return True
    elif isinstance(coll1, collections.Sequence):
        if len(coll1) != len(coll2):
            return False
        for v1, v2 in zip(coll1, coll2):
            if not safe_eq(v1, v2, thresh=thresh):
                return False
        return True
    else:
        return coll1 == coll2


if __name__ == "__main__":
    tests = {
        # "str_flush":    ['Js', 'Qs', 'Qd', '3s', 'Ts', '9s', '8s'],
        "wheel_stfsh":  ['5c', '3c', 'Ac', '7h', '4c', '2c', 'Tc'],
        # "quad_4s":      ['4h', '4d', 'Ks', '8c', '4c', '8s', '4c'],
        # "full_hs":      ['Js', 'Qs', 'Qd', '8h', 'Ts', '8c', '8s'],
        # # "full_hs2":     ['Js', 'Qs', 'Qd', '8h', 'Qh', '8c', '8s'],
        # "flush":        ['Js', 'Qs', 'Qd', '3s', '2s', '9s', '8s'],
        # "straight":     ['Js', 'Qs', 'Qd', '3s', 'Tc', '9c', '8s'],
        "wheel":        ['5h', '3c', 'Ad', '7h', '4c', '2s', 'Tc'],
        # "trip_3s":      ['3s', '3d', '4h', 'Ks', '2d', '3h', '7d'],
        # "twp_pair":     ['As', '3d', '4h', '7s', '2d', '3h', '7d'],
        # "pair_3s":      ['As', '3d', '4h', 'Ks', '2d', '3h', '7d'],
        # "ace_high":     ['Qc', '4h', '3s', 'As', 'Ts', '9c', '8s'],
    }
    evals = []
    for t in tests:
        evals.append(EvalHand(tests[t][0:2], tests[t][2:]))
        print(f"{t:<16}{evals[-1]}")
    evals.sort()
    print(evals)

    evals = {
       # "AKs vs AKs": ((['As', 'Ks'], ['Ad', 'Kd']), []),
       #  "44 vs 44": ((['4s', '4d'], ['4c', '4h']), []),
        "AKs vs AKo vs QQ": ((['As', 'Ks'], ['Ad', 'Kc'], ['Qs', 'Qc']), []),
    }

    # profiling.start()
    # for k, v in evals.items():
    #     print(f"{k}: {calc_equities(v[0], v[1])}")
    # profiling.stop()