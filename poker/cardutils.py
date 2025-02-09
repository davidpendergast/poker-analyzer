import re

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
