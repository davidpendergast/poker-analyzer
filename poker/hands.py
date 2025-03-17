import collections
import locale
import typing
import datetime

from poker import cardutils, actions


class Hand:

    def __init__(self,
                 timestamp: datetime.datetime,
                 end_timestamp: datetime.datetime,
                 configs,
                 hand_idx: int,
                 hero_id: str,
                 players: typing.List['Player']):

        self.timestamp = timestamp
        self.end_timestamp = end_timestamp
        self.configs = configs
        self.hand_idx = hand_idx
        self.hero_id = hero_id

        self.players: typing.List['Player'] = players
        self.board = []

        self.pre_flop_actions = []
        self.flop_actions = []
        self.turn_actions = []
        self.river_actions = []

    def __hash__(self):
        return hash((self.timestamp, self.hand_idx, self.hero_id))

    def __eq__(self, other):
        return (self.timestamp == other.timestamp
                and self.hand_idx == other.hand_idx
                and self.hero_id == other.hero_id)

    def __str__(self):
        net = locale.currency(self.get_hero().net())
        cards = self.get_hero().get_cards_str()
        stack = locale.currency(self.get_hero().stack)

        got_to_flop = self.hero_got_to_street(actions.FLOP)
        got_to_turn = self.hero_got_to_street(actions.TURN)
        got_to_river = self.hero_got_to_street(actions.RIVER)
        got_to_showdown = self.hero_got_to_street(actions.SHOWDOWN)

        preflop_acts = self.get_action_seq_string(street=actions.PRE_FLOP)
        res = f"Hand #{self.hand_idx:<3} {self.timestamp.date()} {net:<8} {stack:<8} {cards} | {preflop_acts}"
        if not got_to_flop:
            return res

        flop_acts = self.get_action_seq_string(street=actions.FLOP)
        res = f"{res} {'[' + ' '.join(self.board[0:3]) + ']'}{f' {flop_acts}' if len(flop_acts) > 0 else ''}"
        if not got_to_turn:
            return res

        turn_acts = self.get_action_seq_string(street=actions.TURN)
        res = f"{res} {'[' + ' '.join(self.board[3:4]) + ']'}{f' {turn_acts}' if len(turn_acts) > 0 else ''}"
        if not got_to_river:
            return res

        river_acts = self.get_action_seq_string(street=actions.RIVER)
        res = f"{res} {'[' + ' '.join(self.board[4:5]) + ']'}{f' {river_acts}' if len(river_acts) > 0 else ''}"
        if not got_to_showdown:
            return res

        # TODO summarize showdown
        return res

    def all_actions(self, player_id=None, street=actions.ANY) -> typing.Generator[actions.Action, None, None]:
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
        return self.did_player_vpip(None, street=street)

    def did_player_vpip(self, player_id, street=actions.PRE_FLOP):
        for a in self.all_actions(player_id=player_id or self.hero_id, street=street):
            if a.is_vpip():
                return True
            if a.action_type == actions.FOLD:
                return False
        return False

    def did_player_pfr(self, player_id):
        """returns: if player ever opened or raised pre-flop (PFR = pre-flop raise)"""
        return self.did_player_raise(player_id, street=actions.PRE_FLOP)

    def did_player_3bet_pre(self, player_id) -> typing.Tuple[bool, typing.Optional[str]]:
        """returns: (had_opportunity, 'raise'/'call'/'fold')"""
        raise_cnt = 0
        for a in self.all_actions(street=actions.PRE_FLOP):
            if a.is_aggro():
                if Player.names_eq(player_id, a.player_id):
                    if raise_cnt == 1:
                        return True, actions.RAISE  # player is 2nd raiser
                    else:
                        return False, None  # player didn't have opportunity
                else:
                    raise_cnt += 1
            elif Player.names_eq(player_id, a.player_id):
                if raise_cnt == 1:
                    return True, a.action_type  # player had opportunity but called or folded
                else:
                    return False, None  # player didn't have opportunity
        return False, None  # player wasn't in the hand

    def get_action_seq_string(self, street=actions.PRE_FLOP):
        res = []
        for act in self.all_actions(street=street):
            is_hero = Player.names_eq(self.hero_id, act.player_id)
            if act.action_type == actions.FOLD:
                if is_hero:
                    res.append('F')
                    break
            elif act.action_type in (actions.BB, actions.SB, actions.ANTE):
                continue
            elif act.action_type == actions.CALL:
                res.append('C' if is_hero else 'c')
            elif act.action_type in (actions.OPEN, actions.RAISE):
                res.append('R' if is_hero else 'r')
            elif act.action_type == actions.CHECK:
                res.append('X' if is_hero else 'x')
            if act.is_all_in():
                res.append('!')
        return "".join(res)

    def did_player_4bet_pre(self, player_id):
        """returns: (had_opportunity, 'raise'/'call'/'fold')"""
        player_opened = False
        someone_raised = False
        for a in self.all_actions(street=actions.PRE_FLOP):
            if a.is_aggro():
                if Player.names_eq(player_id, a.player_id):
                    if player_opened and someone_raised:
                        return True, actions.RAISE
                    elif someone_raised:
                        return False, None  # we're 3betting
                else:
                    if someone_raised:
                        return False, None  # two opponents took aggressive actions

    def did_player_raise(self, player_id, street=actions.ANY):
        for a in self.all_actions(player_id=self.hero_id, street=street):
            if Player.names_eq(player_id, a.player_id) and a.is_aggro():
                return True

    def did_hero_win(self):
        return self.did_player_win(None)

    def did_player_win(self, player_id):
        p = self.get_player(player_id)
        return p is not None and p.net() > 0

    def hero_got_to_street(self, street):
        return self.player_got_to_street(None, street)

    def player_got_to_street(self, player_id, street):
        for n in self.players_involved_at_street(street):
            if Player.names_eq(n, player_id or self.hero_id):
                return True
        return False

    def hand_got_to_street(self, street):
        return len(self.players_involved_at_street(street)) >= 2

    def is_multiway(self, street=actions.FLOP):
        return len(self.players_involved_at_street(street)) > 2

    def is_everyone_all_in(self, player_id=None, street=actions.RIVER):
        """
        Returns true if no more player actions can be taken because everyone is all-in
        or called an all-in (i.e. it's a cards-up "run-out" situation).
        :param player_id: Only count it if this player was involved (optional)
        :param street: Street by which the all-ins/calls occurred (optional).
        """
        all_in_players = set()
        active_players = set()
        folded_players = set()

        for a in self.all_actions(street=actions.street_range(None, street)):
            if a.is_fold():
                if player_id is not None and Player.names_eq(player_id, a.player_id):
                    return False  # player we care about folded, break early
                folded_players.add(a.player_id)
                if a.player_id in active_players:
                    active_players.remove(a.player_id)
            elif a.is_all_in():
                all_in_players.add(a.player_id)
                if a.player_id in active_players:
                    active_players.remove(a.player_id)
            elif a.player_id not in folded_players:
                active_players.add(a.player_id)

        if ((len(active_players) == 0 and len(all_in_players) > 1)
                or (len(active_players) == 1 and len(all_in_players) > 0)):
                    if player_id is not None:
                        for pid in active_players:
                            if Player.names_eq(player_id, pid):
                                return True
                        for pid in all_in_players:
                            if Player.names_eq(player_id, pid):
                                return True
                        return False
                    else:
                        return True
        return False

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
            res[actions.UTG_PLUS] = seen_players[3:len(seen_players) - 4]

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
        if name is None:
            return self.get_hero()
        for p in self.players:
            if p.matches_name(name):
                return p
        return None

    def get_hero(self) -> 'typing.Optional[Player]':
        return self.get_player(self.hero_id)

    def duration(self) -> float:
        """returns: wall-clock duration of hand in seconds"""
        return (self.end_timestamp - self.timestamp).total_seconds()


class Player:

    def __init__(self, name, stack, position, cards):
        self.name_and_id = name
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

        self.showed_cards = 0
        self.voluntarily_showed_cards = 0

    @staticmethod
    def names_eq(id1, id2) -> bool:
        if ' @ ' in id1 and ' @ ' in id2:
            return id1.split(' @ ')[1] == id2.split(' @ ')[1]  # Compare by IDs
        elif ' @ ' in id1:
            n1, n2 = id1.split(' @ ')
            return id2 == n1 or id2 == n2
        elif ' @ ' in id2:
            n1, n2 = id2.split(' @ ')
            return id1 == n1 or id1 == n2
        else:
            return id1 == id2

    def matches_name(self, name):
        return Player.names_eq(self.name_and_id, name)

    def known_cards(self) -> int:
        res = 0
        res += 1 if self.cards[0] is not None else 0
        res += 1 if self.cards[1] is not None else 0
        return res

    def net(self):
        return sum(self.street_nets.values()) + self.gain

    def get_id(self):
        if self.name_and_id is not None and ' @ ' in self.name_and_id:
            return self.name_and_id.split(' @ ')[1]
        else:
            return None

    def get_name(self):
        if self.name_and_id is not None and ' @ ' in self.name_and_id:
            return self.name_and_id.split(' @ ')[0]
        else:
            return None

    def summary_str(self) -> str:
        n = self.name_and_id.split(" @ ")[0]
        net = self.net()
        hand = str(self.cards[0] or "??") + str(self.cards[1] or "??")
        return f"{n} [{hand}] ({net:.2f})"

    def get_card_code(self) -> str:
        """returns: AKs, JTo style string"""
        return cardutils.to_card_code(self.cards)

    def get_cards_str(self) -> str:
        """returns: AdKd, JcTs style string"""
        return (f"{self.cards[0] if self.cards[0] is not None else '??'}"
                f"{self.cards[1] if self.cards[1] is not None else '??'}")

    def __repr__(self):
        return f"{type(self).__name__}({self.name_and_id=}, {self.stack=}, {self.position=}, {self.cards=}, {self.net=})"


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

    def __iter__(self) -> typing.Generator[Hand, None, None]:
        for h in sorted(self.hands, key=lambda x: x.timestamp):
            yield h

    def __getitem__(self, item):
        return self.hands[item]

    def dates(self) -> typing.List[str]:
        res = []
        for h in self.hands:
            datestr = h.timestamp.strftime("%Y-%m-%d")
            if len(res) == 0 or res[-1] != datestr:
                res.append(datestr)
        return res

    def players(self) -> typing.List[str]:
        """
        returns list of 'PlayerName @ PlayerID' found in this hand group, with PlayerName being
        the most commonly-used alias for that player.
        """
        ids = {}  # ids -> list of names used
        for h in self.hands:
            for p in h.players:
                p_id = p.get_id()
                p_name = p.get_name()
                if p_id not in ids:
                    ids[p_id] = collections.Counter()
                ids[p_id].update([p_name])

        return [f"{ids[p_id].most_common(1)[0][0]} @ {p_id}" for p_id in ids]

    def total_duration(self) -> float:
        """returns: total sum of the wall-clock durations of the hands in this group, in seconds"""
        res = 0
        for h in self.hands:
            res += h.duration()
        return res

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

    def vpip_pcnt(self, player_id=None, street=actions.PRE_FLOP):
        if len(self) == 0:
            return 0
        else:
            vpip_cnt = 0
            hand_cnt = 0
            for h in self.hands:
                if h.get_player(player_id) is not None:
                    hand_cnt += 1
                if h.did_player_vpip(player_id, street=street):
                    vpip_cnt += 1
            if hand_cnt == 0:
                return 0
            else:
                return vpip_cnt / hand_cnt

    def get_3bet_pcnt(self, player_id=None):
        """ returns: number of 3bets / number of opportunities to 3bet"""
        if self.hands_played(player_id) == 0:
            return 0
        else:
            had_opportunity = 0
            cnt = 0
            for h in self.hands:
                opp, res = h.did_player_3bet_pre(player_id or h.hero_id)
                if opp:
                    had_opportunity += 1
                    if res == actions.RAISE:
                        cnt += 1
            if had_opportunity == 0:
                return 0
            else:
                return cnt / had_opportunity

    def get_saw_street_pcnt(self, player_id=None, street=actions.FLOP):
        saw_street = 0
        played_hands = 0
        for h in self.hands:
            p = h.get_player(player_id)
            if p is not None:
                played_hands += 1
                if h.player_got_to_street(player_id, street=street):
                    saw_street += 1
        return saw_street / played_hands if played_hands > 0 else 0

    def get_voluntary_show_pcnt(self, player_id=None, after_vpip=True):
        had_opportunity = 0
        did_show = 0
        for h in self.hands:
            p = h.get_player(player_id)
            if p is not None:
                if not after_vpip or h.did_player_vpip(player_id, street=actions.ANY):
                    if p.showed_cards == 2 and p.voluntarily_showed_cards == 0:
                        pass  # player was compelled to show
                    else:
                        had_opportunity += 2
                        did_show += p.voluntarily_showed_cards
        if had_opportunity == 0:
            return 0
        else:
            return did_show / had_opportunity

    def net_gain(self, player_id=None):
        res = 0
        for h in self.hands:
            p = h.get_player(player_id)
            if p is not None:
                res += p.net()
        return res

    def total_flux(self, player_id=None):
        res = 0
        for h in self.hands:
            p = h.get_player(player_id)
            if p is not None:
                res += abs(p.net())
        return res

    def hands_played(self, player_id=None):
        if player_id is None:
            return len(self)
        else:
            return len([h for h in self.hands if h.get_player(player_id) is not None])

    def avg_gain_per_play(self, player_id=None):
        hands_played = self.hands_played(player_id=player_id)
        if hands_played == 0:
            return 0
        else:
            return self.net_gain(player_id=player_id) / hands_played

    def net_bbs(self, player_id=None):
        res = 0
        for h in self.hands:
            p = h.get_player(player_id)
            if p is not None:
                res += p.net() / h.get_bb_cost()
        return res

    def avg_bbs_per_play(self, player_id=None):
        hands_played = self.hands_played(player_id=player_id)
        if hands_played == 0:
            return 0
        else:
            return self.net_bbs(player_id=player_id) / hands_played

    def win_pcnt(self, player_id=None, after_vpip=True):
        wins = 0
        losses = 0
        for h in self.hands:
            p = h.get_player(player_id)
            if p is not None:
                if not after_vpip or h.did_player_vpip(player_id, street=actions.ANY):
                    if h.did_player_win(player_id):
                        wins += 1
                    else:
                        losses += 1
        if wins + losses == 0:
            return 0
        else:
            return wins / (wins + losses)

    def win_at_showdown_pcnt(self, player_id=None):
        wins = 0
        losses = 0
        for h in self.hands:
            if h.player_got_to_street(player_id, actions.SHOWDOWN):
                if h.did_player_win(player_id=player_id):
                    wins += 1
                else:
                    losses += 1
        if wins + losses == 0:
            return 0
        else:
            return wins / (wins + losses)

    def session_count(self) -> int:
        sessions = set()
        for h in self.hands:
            if 'logfile' in h.configs and h.configs['logfile'] is not None:
                sessions.add(h.configs['logfile'])
        return len(sessions)

    def most_recent_sessions(self, n, desc=None) -> 'HandGroup':
        if n < 0:
            return self
        desc = desc or f"{self.desc} (last {n} session(s))"
        if n == 0:
            return HandGroup([], desc=desc)
        else:
            all_sessions = {}
            for h in self.hands:
                if 'logfile' in h.configs and h.configs['logfile'] is not None:
                    logfile = h.configs['logfile']
                    if logfile not in all_sessions:
                        all_sessions[logfile] = h.timestamp
            sorted_sessions = [k for k in all_sessions.keys()]
            sorted_sessions.sort(key=lambda k: all_sessions[k], reverse=True)
            if len(sorted_sessions) <= n:
                return self
            else:
                sessions = sorted_sessions[:n]
                hands_to_keep = []
                for h in self.hands:
                    if 'logfile' in h.configs and h.configs['logfile'] in sessions:
                        hands_to_keep.append(h)
                return HandGroup(hands_to_keep, desc=desc)

    def summary(self, player_id=None):
        pid = ""
        if player_id is not None:
            p_name = player_id.split(' @ ')[0] if ' @ ' in player_id else player_id
            if len(p_name) > 18:
                p_name = p_name[:15] + "..."
            pid = f" ({p_name})"

        desc = f"{self.desc}{pid}: "
        avg_bbs = f"{self.avg_bbs_per_play(player_id=player_id):.1f}bb"
        total = f"{locale.currency(self.net_gain(player_id=player_id))}"
        in_x_hands = f"in {self.hands_played(player_id=player_id)} hand(s)"

        vpip_pcnt = cardutils.format_pcnt(self.vpip_pcnt(player_id=player_id))
        win_pcnt = cardutils.format_pcnt(self.win_pcnt(player_id=player_id))
        win_at_sd_pcnt = cardutils.format_pcnt(self.win_at_showdown_pcnt(player_id=player_id))
        three_bet_pcnt = cardutils.format_pcnt(self.get_3bet_pcnt(player_id=player_id))
        saw_flop = cardutils.format_pcnt(self.get_saw_street_pcnt(player_id=player_id, street=actions.FLOP))
        show_pcnt = cardutils.format_pcnt(self.get_voluntary_show_pcnt(player_id=player_id, after_vpip=True))

        return (f"{desc:<32}{avg_bbs:<12}{total:<12}{in_x_hands:<18}"
                f"[VPIP={vpip_pcnt:>5}, 3BET={three_bet_pcnt}, SAW_FLOP={saw_flop}, WIN={win_pcnt}, WaSD={win_at_sd_pcnt}, SHOW={show_pcnt}]")

    def get_hole_card_freqs(self, player_id=None):
        res = {}
        for h in self.hands:
            p = h.get_player(player_id)
            if p is not None and p.known_cards() == 2:
                cc = p.get_card_code()
                if cc not in res:
                    res[cc] = 0
                res[cc] += 1
        return res

    def get_player_stats(self, player_id):
        pass
