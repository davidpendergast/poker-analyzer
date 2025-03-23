import typing
import unittest
import poker.hands
import poker.actions as actions
import poker.cardutils as cardutils
import datetime


def _create_hand(players, actions: typing.List[actions.Action], board, gains, sb_cost=0.05, bb_cost=0.1):
    """
    :param players: [("pname @ 123", 10.5, "AsKh"), ("pname2 @ 456", 8.75, "4h4d"), ...]
    :return:
    """
    dt = datetime.datetime.now()
    configs = {
            "logfile": "test_hand_for_ut",
            "sb_cost": sb_cost,
            "bb_cost": bb_cost,
            "ante_cost": 0.0,
        }
    hero_id = players[0][0]
    players = [poker.hands.Player(p[0], p[1], idx, (p[2][:2], p[2][2:])) for idx, p in enumerate(players)]

    def _get_player(player_id):
        for p in players:
            if p.name_and_id == player_id:
                return p

    hand = poker.hands.Hand(dt, dt, configs, 0, hero_id, players)
    hand.board = board
    for a in actions:
        player = _get_player(a.player_id)
        hand.get_mutable_actions_for_street(a.street).append(a)
        player.street_nets[a.street] -= a.amount

    for pid in gains:
        player = _get_player(pid)
        player.gain = gains[pid]

    return hand


class Testcases(unittest.TestCase):

    def test_pf_equities(self):
        eqs = cardutils.calc_equities([('4h', '4d'), ('Jd', 'Js')], ['Ah', 'Kc', '3d'])
        self.assertEqual([0.1, 0.9], eqs)

    def test_all_in_equities(self):
        h = _create_hand([("A", 10, "AhAd"), ("B", 15, "KhKd")],
                         [
                             actions.Action("A", 0.05, actions.SB, actions.PRE_FLOP),
                             actions.Action("B", 0.10, actions.BB, actions.PRE_FLOP),
                             actions.Action("A", 9.95, actions.OPEN, actions.PRE_FLOP, all_in=True),
                             actions.Action("B", 9.90, actions.CALL, actions.PRE_FLOP)
                          ], ["Jh", "4c", "Td", "Ks", "3h"], {"B": 20})

        self.assertEqual(False, h.did_player_win("A"))
        self.assertEqual(True, h.did_player_win("B"))
        self.assertEqual({"B": 20}, cardutils.calc_payouts(h))


if __name__ == "__main__":
    unittest.main()
