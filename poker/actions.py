import typing

# Streets
PRE_FLOP = "pre-flop"
FLOP = "flop"
TURN = "turn"
RIVER = "river"
SHOWDOWN = "showdown"
ORDERED_STREETS = [PRE_FLOP,
                   FLOP,
                   TURN,
                   RIVER,
                   SHOWDOWN]

ANY = "any"
POST_FLOP = "post-flop"
BEFORE_SHOWDOWN = "pre-showdown"


def unpack_street(street):
    if isinstance(street, tuple) or isinstance(street, list):
        return street
    elif street == ANY:
        return PRE_FLOP, FLOP, TURN, RIVER, SHOWDOWN
    elif street == POST_FLOP:
        return FLOP, TURN, RIVER, SHOWDOWN
    elif street == BEFORE_SHOWDOWN:
        return PRE_FLOP, FLOP, TURN, RIVER
    else:
        return (street,)


def street_range(first, last):
    if first is None:
        start_idx = 0
    else:
        first = unpack_street(first)[0]
        start_idx = ORDERED_STREETS.index(first)
    if last is None:
        end_idx = 0
    else:
        last = unpack_street(last)[-1]
        end_idx = ORDERED_STREETS.index(last) + 1

    if end_idx < start_idx:
        return []
    else:
        return ORDERED_STREETS[start_idx:end_idx]


# Pure Action Types
BB = 'bb'  # Player posts their big blind
SB = 'sb'  # Player posts their small blind
ANTE = 'ante'  # Player posts their ante
STRADDLE = 'straddle'  # player posts a straddle

CALL = 'call'   # Player calls a previous open, blind, or raise.
OPEN = 'open'   # Player places the first bet on a street.
RAISE = 'raise' # Player raises after another has opened.

CHECK = 'check'
FOLD = 'fold'

# Qualitative Action Types
LIMP = 'limp'
CALL_TO_CLOSE_ACTION = 'call_to_close'
CALL_WITH_ACTORS_BEHIND = 'call_without_close'
THREE_BET = 'three_bet'
FOUR_BET = 'four_bet'

# Positions
BTN = "BTN"
CO = "CO"
HJ = "HJ"
LJ = "LJ"
UTG_PLUS = "UTG+"
UTG = "UTG"
BB = 'bb'    # note: same var as in 'Action Types'
SB = 'sb'    # note: same var as in 'Action Types'

LATE_POS = "LP"
MID_POS = "MP"
EARLY_POS = "EP"
BLINDS = "BLINDS"

ANY = "any"       # note: same var as in 'Streets'


class Action:

    def __init__(self, player_id, amount, action_type, street, all_in=False):
        self.player_id = player_id
        self.amount = amount
        self.action_type = action_type
        self.street = street
        self.all_in = all_in

    def is_vpip(self):
        return self.action_type in (CALL, OPEN, RAISE)

    def is_aggro(self):
        return self.action_type in (OPEN, RAISE)

    def is_passive(self):
        return self.action_type in (CHECK, CALL)

    def is_fold(self):
        return self.action_type == FOLD

    def is_all_in(self):
        return self.all_in

    def __repr__(self):
        return f"{type(self).__name__}({self.player_id}, {self.amount}, {self.action_type}, {self.street}, {self.all_in=})"
