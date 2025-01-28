import typing

# Streets
PRE_FLOP = "pre-flop"
FLOP = "flop"
TURN = "turn"
RIVER = "river"
SHOWDOWN = "showdown"

ANY = "any"
POST_FLOP = "post-flop"
BEFORE_SHOWDOWN = "pre-showdown"


def unpack_street(street):
    if isinstance(street, tuple):
        return street
    elif street == ANY:
        return PRE_FLOP, FLOP, TURN, RIVER, SHOWDOWN
    elif street == POST_FLOP:
        return FLOP, TURN, RIVER, SHOWDOWN
    elif street == BEFORE_SHOWDOWN:
        return PRE_FLOP, FLOP, TURN, RIVER
    else:
        return (street,)


# Action Types
BB = 'bb'  # Player posts their big blind
SB = 'sb'  # Player posts their small blind
ANTE = 'ante'  # Player posts their ante

CALL = 'call'   # Player calls a previous open, blind, or raise.
OPEN = 'open'   # Player places the first bet on a street.
RAISE = 'raise' # Player raises after another has opened.

CHECK = 'check'
FOLD = 'fold'


# Positions
BTN = "BTN"
CO = "CO"
HJ = "HJ"
LJ = "LJ"
UTG_PLUS = "UTG+"
UTG = "UTG"
BB = 'bb'    # note: same var as in 'Action Types'
SB = 'sb'    # note: same var as in 'Action Types'

LATE_POS = "LP"   #
MID_POS = "MP"    #
EARLY_POS = "EP"  #
BLINDS = "BLINDS" #

class Action:

    def __init__(self, player_id, amount, action_type, street, all_in=False):
        self.player_id = player_id
        self.amount = amount
        self.action_type = action_type
        self.street = street
        self.all_in = all_in

    def is_vpip(self):
        return self.action_type in (CALL, OPEN, RAISE)

    def is_fold(self):
        return self.action_type == FOLD

    def is_all_in(self):
        return self.all_in
