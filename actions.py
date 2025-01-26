
# Streets
PRE_FLOP="pre-flop"
FLOP="flop"
TURN="turn"
RIVER="river"
SHOWDOWN="showdown"


# Action Types
BB = 'bb'  # Player posts their big blind
SB = 'sb'  # Player posts their small blind
ANTE = 'ante'  # Player posts their ante

CALL = 'call'   # Player calls a previous open, blind, or raise.
OPEN = 'open'   # Player places the first bet on a street.
RAISE = 'raise' # Player raises after another has opened.

CHECK = 'check'
FOLD = 'fold'

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
