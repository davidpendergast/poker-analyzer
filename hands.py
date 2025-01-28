import collections
import locale
import typing

import cardutils
import actions


class Hand:

    def __init__(self, datetime, configs, hand_idx, hero_id, players):
        self.datetime = datetime
        self.configs = configs
        self.hand_idx = hand_idx
        self.hero_id = hero_id

        self.players = players
        self.board = []

        self.pre_flop_actions = []
        self.flop_actions = []
        self.turn_actions = []
        self.river_actions = []

    def __hash__(self):
        return hash((self.datetime, self.hand_idx, self.hero_id))

    def __eq__(self, other):
        return (self.datetime == other.datetime
                and self.hand_idx == other.hand_idx
                and self.hero_id == other.hero_id)

    def __str__(self):
        res = f"Hand #{self.hand_idx}"
        players_str = []
        for p in self.players:
            if p.net() != 0:
                players_str.append(p.summary_str())
        return res + str(players_str)

    def all_actions(self, player_id=None, street=actions.ANY):
        streets = actions.unpack_street(street)
        if actions.PRE_FLOP in streets:
            for a in self.pre_flop_actions:
                if player_id is None or Player.names_eq(a.player_id, player_id):
                    yield a
        if actions.FLOP in streets:
            for a in self.flop_actions:
                if player_id is None or Player.names_eq(a.player_id, player_id):
                    yield a
        if actions.TURN in streets:
            for a in self.turn_actions:
                if player_id is None or Player.names_eq(a.player_id, player_id):
                    yield a
        if actions.RIVER in streets:
            for a in self.river_actions:
                if player_id is None or Player.names_eq(a.player_id, player_id):
                    yield a

    def did_hero_vpip(self, street=actions.PRE_FLOP):
        for a in self.all_actions(player_id=self.hero_id, street=street):
            if a.is_vpip():
                return True
            if a.action_type == actions.FOLD:
                return False
        return False

    def did_hero_win(self):
        return self.get_hero().net() > 0

    def hero_got_to_street(self, street):
        for n in self.players_involved_at_street(street):
            if Player.names_eq(n, self.hero_id):
                return True
        return False

    def hand_got_to_street(self, street):
        return len(self.players_involved_at_street(street)) >= 2

    def is_multiway(self, street=actions.FLOP):
        return len(self.players_involved_at_street(street)) > 2

    def players_involved_at_street(self, street) -> typing.Set[str]:
        streets = actions.unpack_street(street)
        in_hand_pre = set()
        in_hand = set()
        for a in self.pre_flop_actions:
            if a.action_type in (actions.SB, actions.BB, actions.ANTE, actions.CALL, actions.OPEN,
                                 actions.RAISE, actions.CHECK, actions.FOLD):
                in_hand_pre.add(a.player_id)
                in_hand.add(a.player_id)
            if a.action_type == actions.FOLD:
                in_hand.remove(a.player_id)
        if actions.PRE_FLOP in streets:
            return in_hand_pre
        elif actions.FLOP in streets:
            return in_hand if len(in_hand) > 1 else set()

        for a in self.flop_actions:
            if a.action_type == actions.FOLD:
                in_hand.remove(a.player_id)
        if actions.TURN in streets:
            return in_hand if len(in_hand) > 1 else set()

        for a in self.turn_actions:
            if a.action_type == actions.FOLD:
                in_hand.remove(a.player_id)
        if actions.RIVER in streets:
            return in_hand if len(in_hand) > 1 else set()

        for a in self.river_actions:
            if a.action_type == actions.FOLD:
                in_hand.remove(a.player_id)
        if actions.SHOWDOWN in streets:
            return in_hand if len(in_hand) > 1 else set()  # showdown
        else:
            return set()

    def get_position_to_player_mapping(self) -> typing.Dict[str, typing.List[str]]:
        # semi-complicated due to dead/inactive players and arbitrary
        # groupings for EP, MP, LP at various table-sizes.
        res = {}
        seen_players = []

        for a in self.pre_flop_actions:
            if len(seen_players) > 0 and a.player_id == seen_players[0]:
                break  # we've looped
            if a.action_type == actions.SB:
                res[actions.SB] = [a.player_id]
            elif a.action_type == actions.BB:
                res[actions.BB] = [a.player_id]
            seen_players.append(a.player_id)

        # placeholders for dead SB and BB (note all Nones are removed at the end)
        if actions.SB not in res:
            res[actions.SB] = [None]
            seen_players.insert(0, None)
        if actions.BB not in res:
            res[actions.BB] = [None]
            seen_players.insert(1, None)

        # blinds are always the blinds
        res[actions.BLINDS] = [res[actions.SB][0], res[actions.BB][0]]

        # last player to act is always the button (note they may be the BB too)
        res[actions.BTN] = [seen_players[-1]]

        res[actions.ANY] = list(seen_players)  # ordered list of all players

        # first player to act after blinds is UTG
        if len(seen_players) >= 4:
            res[actions.UTG] = [seen_players[2]]

        # last player to act before button is CO
        if len(seen_players) >= 5:
            res[actions.CO] = [seen_players[3]]

        # 2nd last player to act before button is HJ
        if len(seen_players) >= 6:
            res[actions.HJ] = [seen_players[3]]

        # 3rd last player to act before button is LJ
        if len(seen_players) >= 7:
            res[actions.LJ] = [seen_players[3]]

        #    [EP][MP][LP]
        # 2: [SB][  ][BTN]
        # 3: [SB][BB][BTN]
        # 4: [SB BB][UTG][BTN]
        # 5: SB BB [UTG] [CO] [BTN]
        # 6: SB BB [UTG] [HJ] [CO BTN]
        # 7: SB BB [UTG] [LJ HJ] [CO BTN]
        # 8: SB BB [UTG UTG+] [LJ HJ] [CO BTN]

        # remaining players are UTG+
        if len(seen_players) >= 8:
            res[actions.UTG_PLUS] = seen_players[3:len(seen_players)-4]

        # god i wish there was an easier way to do this
        if len(seen_players) == 2:
            # 2: [SB][  ][BTN]
            sb, btn = seen_players
            res[actions.EARLY_POS] = [sb]
            res[actions.LATE_POS] = [btn]
        elif len(seen_players) == 3:
            # 3: [SB][BB][BTN]
            sb, bb, btn = seen_players
            res[actions.EARLY_POS] = [sb]
            res[actions.MID_POS] = [bb]
            res[actions.LATE_POS] = [btn]
        elif len(seen_players) == 4:
            # 4: [SB BB][UTG][BTN]
            sb, bb, utg, btn = seen_players
            res[actions.EARLY_POS] = [sb, bb]
            res[actions.MID_POS] = [utg]
            res[actions.LATE_POS] = [btn]
        elif len(seen_players) == 5:
            # 5: SB BB [UTG] [CO] [BTN]
            sb, bb, utg, co, btn = seen_players
            res[actions.EARLY_POS] = [utg]
            res[actions.MID_POS] = [co]
            res[actions.LATE_POS] = [btn]
        elif len(seen_players) == 6:
            # 6: SB BB [UTG] [HJ] [CO BTN]
            sb, bb, utg, hj, co, btn = seen_players
            res[actions.EARLY_POS] = [utg]
            res[actions.MID_POS] = [hj]
            res[actions.LATE_POS] = [co, btn]
        elif len(seen_players) == 7:
            # 7: SB BB [UTG] [LJ HJ] [CO BTN]
            sb, bb, utg, lj, hj, co, btn = seen_players
            res[actions.EARLY_POS] = [utg]
            res[actions.MID_POS] = [lj, hj]
            res[actions.LATE_POS] = [co, btn]
        elif len(seen_players) >= 8:
            # 8: SB BB [UTG UTG+] [LJ HJ] [CO BTN]
            res[actions.EARLY_POS] = res[actions.UTG] + res[actions.UTG_PLUS]
            res[actions.MID_POS] = res[actions.LJ] + res[actions.HJ]
            res[actions.LATE_POS] = res[actions.CO] + res[actions.BTN]

        # finally, remove all Nones
        clean_res = {}
        for k, v in res.items():
            v_clean = [pl for pl in v if pl is not None]
            if len(v_clean) > 0:
                clean_res[k] = v_clean

        return clean_res

    def get_bb_cost(self):
        return self.configs['bb_cost']

    def get_sb_cost(self):
        return self.configs['sb_cost']

    def get_ante_cost(self):
        return self.configs['ante_cost']

    def get_player(self, name) -> 'typing.Optional[Player]':
        for p in self.players:
            if p.matches_name(name):
                return p
        return None

    def get_hero(self) -> 'typing.Optional[Player]':
        return self.get_player(self.hero_id)


class Player:

    def __init__(self, name, stack, position, cards):
        self.name = name
        self.stack = stack
        self.position = position
        self.cards = cards

        self.street_nets = {
            "pre-flop": 0,
            "flop": 0,
            "turn": 0,
            "river": 0
        }
        self.gain = 0

    @staticmethod
    def names_eq(id1, id2) -> bool:
        if ' @ ' in id1 and ' @ ' in id2:
            return ' @ '.split(id1)[1] == ' @ '.split(id2)[1]  # Compare by IDs
        elif ' @ ' in id1:
            n1, n2 = id1.split(' @ ')
            return id2 == n1 or id2 == n2
        elif ' @ ' in id2:
            n1, n2 = id2.split(' @ ')
            return id1 == n1 or id1 == n2
        else:
            return id1 == id2

    def matches_name(self, name):
        return Player.names_eq(self.name, name)

    def net(self):
        return sum(self.street_nets.values()) + self.gain

    def get_id(self):
        if self.name is not None and '@' in self.name:
            return self.name[self.name.rindex('@') + 2:]

    def summary_str(self) -> str:
        n = self.name.split(" @ ")[0]
        net = self.net()
        hand = str(self.cards[0] or "??") + str(self.cards[1] or "??")
        return f"{n} [{hand}] ({net:.2f})"

    def get_card_code(self):
        return cardutils.to_card_code(self.cards)


    def __repr__(self):
        return f"{type(self).__name__}({self.name=}, {self.stack=}, {self.position=}, {self.cards=}, {self.net=})"


class HandGroup(collections.abc.Sequence):

    def __init__(self, list_of_hands: typing.Sequence[Hand], desc="Group"):
        self.desc = desc
        self.hands = list(list_of_hands)

    def append(self, hand):
        self.hands.append(hand)

    def extend(self, hand_seq: typing.Sequence[Hand]):
        self.hands.extend(hand_seq)

    def __len__(self):
        return len(self.hands)

    def __iter__(self):
        for h in self.hands:
            yield h

    def __getitem__(self, item):
        return self.hands[item]

    def intersect(self, other: 'HandGroup') -> 'HandGroup':
        my_hands = set(self.hands)
        other_hands = set(other.hands)
        return HandGroup(list(my_hands.intersection(other_hands)),
                         desc=f"({self.desc} n {other.desc})")

    def union(self, other: 'HandGroup') -> 'HandGroup':
        my_hands = set(self.hands)
        other_hands = set(other.hands)
        return HandGroup(list(my_hands.union(other_hands)),
                         desc=f"({self.desc} u {other.desc})")

    def filter(self, filter: 'filters.Filter', desc=None) -> 'HandGroup':
        new_hands = [h for h in self.hands if filter.test(h)]
        return HandGroup(new_hands, desc=desc if desc is not None else f"F({self.desc})")

    def vpip_pcnt(self):
        if len(self) == 0:
            return 0
        else:
            cnt = 0
            for h in self.hands:
                if h.did_hero_vpip():
                    cnt += 1
            return cnt / len(self)

    def net_gain(self):
        res = 0
        for h in self.hands:
            res += h.get_hero().net()
        return res

    def total_flux(self):
        res = 0
        for h in self.hands:
            res += abs(h.get_hero().net())
        return res

    def avg_gain_per_play(self):
        if len(self) == 0:
            return 0
        else:
            return self.net_gain() / len(self)

    def net_bbs(self):
        res = 0
        for h in self.hands:
            res += h.get_hero().net() / h.get_bb_cost()
        return res

    def avg_bbs_per_play(self):
        if len(self) == 0:
            return 0
        else:
            return self.net_bbs() / len(self)

    def median_bbs(self):
        if len(self) == 0:
            return 0
        else:
            bbs = [h.net() / h.get_bb_cost() for h in self.hands]
            bbs.sort()
            if len(bbs) % 2 == 0:
                return (bbs[len(bbs) // 2] + bbs[len(bbs) // 2 + 1]) / 2
            else:
                return bbs[len(bbs) // 2]

    def win_pcnt(self):
        wins = 0
        losses = 0
        for h in self.hands:
            if h.did_hero_win():
                wins += 1
            else:
                losses += 1
        if wins + losses == 0:
            return 0
        else:
            return wins / (wins + losses)

    def win_at_showdown_pcnt(self):
        wins = 0
        losses = 0
        for h in self.hands:
            if h.hero_got_to_street(actions.SHOWDOWN):
                if h.did_hero_win():
                    wins += 1
                else:
                    losses += 1
        if wins + losses == 0:
            return 0
        else:
            return wins / (wins + losses)

    def session_count(self):
        sessions = set()
        for h in self.hands:
            if 'logfile' in h.configs and h.configs['logfile'] is not None:
                sessions.add(h.configs['logfile'])
        return len(sessions)

    def summary(self):
        desc = f"{self.desc}: "
        avg_bbs = f"{self.avg_bbs_per_play():.1f}bb"
        total = f"{locale.currency(self.net_gain())}"
        in_x_hands = f"in {len(self)} hand(s)"
        vpip_pcnt = f"{min(99.9, self.vpip_pcnt() * 100):.1f}%"
        win_pcnt = f"{min(99.9, self.win_pcnt() * 100):.1f}%"
        win_at_sd_pcnt = f"{min(99.9, self.win_at_showdown_pcnt() * 100):.1f}%"
        return (f"{desc:<32}{avg_bbs:<12}{total:<12}{in_x_hands:<16}"
                f"[VPIP={vpip_pcnt:>5}, WIN={win_pcnt:>5}, WaSD={win_at_sd_pcnt:>5}]")

    def get_hole_card_freqs(self):
        res = {}
        for h in self.hands:
            cc = h.get_hero().get_card_code()
            if cc not in res:
                res[cc] = 0
            res[cc] += 1
        return res