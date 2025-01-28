# -*- coding: utf-8 -*-

import hands
import filters
import actions

import typing
import os
import csv
import re
import locale

HERO_ID = 'k-xm91OpZ6'              # ID of the player to track.
LOG_DOWNLOADER_ID = 'k-xm91OpZ6'    # ID of the player who downloaded the logs.

def scrape(hero, logfilepath) -> typing.List[hands.Hand]:
    res = []
    with open(logfilepath, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        lines = [l for l in reader if len(l) > 0]
        lines.reverse()  # pokernow logs go from newest to oldest

        configs = {
            "logfile": os.path.basename(logfilepath),
            "sb_cost": 0.10,
            "bb_cost": 0.20,
            "ante_cost": 0.0,
        }

        cur_hand_lines = []
        cur_hand_configs = configs.copy()
        for i in range(len(lines)):
            _update_configs(configs, lines[i])
            if lines[i][0].startswith("-- starting hand #"):
                cur_hand_configs = configs.copy()
                cur_hand_lines.clear()
            cur_hand_lines.append(lines[i])
            if lines[i][0].startswith("-- ending hand #"):
                hand = _create_hand_from_lines(hero, cur_hand_configs, cur_hand_lines)
                if hand is not None:
                    res.append(hand)
    return res

def _update_configs(configs, line):
    if old_new := _find_text(line[0], r'The game\'s small blind was changed from (.*) to (.*)\.', allow_fail=True):
        configs['sb_cost'] = float(old_new[1])
    elif old_new := _find_text(line[0], r'The game\'s big blind was changed from (.*) to (.*)\.', allow_fail=True):
        configs['bb_cost'] = float(old_new[1])
    elif old_new := _find_text(line[0], r'The game\'s ante was changed from (.*) to (.*)\.', allow_fail=True):
        configs['ante_cost'] = float(old_new[1])

def _create_hand_from_lines(hero_id, configs, lines) -> typing.Optional[hands.Hand]:
    intro_line = _pop_line_matching(lines, r'-- starting hand #(\d+).*')
    datetime = intro_line[1]
    hand_idx = int(_find_text(intro_line[0], r'-- starting hand #(\d+).*')[0])

    players_line = _pop_line_matching(lines, r'Player stacks: (.*)')
    player_list = []
    raw_players = _find_text(players_line[0], r'Player stacks: (.*)')[0].split(" | ")
    for p in raw_players:
        pname, pstack = _find_text(p, r'"(.*)" \((.*)\)')
        player_list.append(hands.Player(pname, pstack, -1, (None, None)))

    hand = hands.Hand(datetime, configs, hand_idx, hero_id, player_list)

    hero = hand.get_hero()
    your_hand_line = _pop_line_matching(lines, r'Your hand is.*', allow_fail=True)
    if hero is not None and LOG_DOWNLOADER_ID == HERO_ID and your_hand_line is not None:
        c1, c2 = _find_text(your_hand_line[0], "Your hand is (.+), (.+)")
        hero.cards = _convert_card(c1), _convert_card(c2)

    # Pre-Flop
    pos = 0
    while len(lines) > 0:
        line = lines[0]
        if fields := _find_text(line[0], r'"(.*)" posts a small blind of ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.SB, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif fields := _find_text(line[0], r'"(.*)" posts a big blind of ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.BB, actions.PRE_FLOP))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif fields := _find_text(line[0], r'"(.*)" calls ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.CALL, actions.PRE_FLOP))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif fields := _find_text(line[0], r'"(.*)" bets ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.OPEN, actions.PRE_FLOP))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif name := _find_text(line[0], r'"(.*)" checks', allow_fail=True):
            name = name[0]
            hand.pre_flop_actions.append(actions.Action(name, 0, actions.CHECK, actions.PRE_FLOP))
        elif name := _find_text(line[0], r'"(.*)" folds', allow_fail=True):
            name = name[0]
            hand.pre_flop_actions.append(actions.Action(name, 0, actions.FOLD, actions.PRE_FLOP))
        elif fields := _find_text(line[0], r'"(.*)" raises to ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.RAISE, actions.PRE_FLOP))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif name_amt := _find_text(line[0], r'Uncalled bet of (.*) returned to "(.*)"', allow_fail=True):
            amt, name = float(name_amt[0]), name_amt[1]
            _get_player(player_list, name).gain += amt
        elif name_amt := _find_text(line[0], r'"(.*)" collected ([\d\.]+) from pot', allow_fail=True):
            name, amt = name_amt[0], float(name_amt[1])
            _get_player(player_list, name).gain += amt
            return hand if hand.get_hero() is not None else None
        elif name_shows := _find_text(line[0], r'"(.*)" shows a (.*)\.', allow_fail=True):
            if " ," in name_shows[1]:
                _get_player(player_list, name_shows[0]).cards = [
                    name_shows[1].split(", ")
                ]
        elif _find_text(line[0], r'Flop: .*', allow_fail=True):
            break

        p = _get_player(player_list, name)
        if p is not None and p.position == -1:
            p.position = pos
            pos += 1
        lines.pop(0)

    flop_line = _pop_line_matching(lines, r'Flop: .*', allow_fail=True)
    if flop_line is not None:
        flop_raw = _find_text(flop_line[0], "Flop: [(.*)]")[0].split(", ")
        hand.board = [_convert_card(c) for c in flop_raw] + [None, None]
    else:
        return hand if hand.get_hero() is not None else None

    hand.flop_actions = _process_post_flop_actions(hand, lines, actions.FLOP)

    turn_line = _pop_line_matching(lines, r'Turn: .*', allow_fail=True)
    if turn_line is not None:
        turn_raw = _find_text(flop_line[0], "Turn: [.*, [(.*)]]")[0]
        hand.board[3] = _convert_card(turn_raw)
    else:
        return hand if hand.get_hero() is not None else None

    hand.turn_actions = _process_post_flop_actions(hand, lines, actions.TURN)

    river_line = _pop_line_matching(lines, r'River: .*', allow_fail=True)
    if river_line is not None:
        river_raw = _find_text(flop_line[0], "River: [.*, [(.*)]]")[0]
        hand.board[4] = _convert_card(river_raw)
    else:
        return hand if hand.get_hero() is not None else None

    hand.river_actions = _process_post_flop_actions(hand, lines, actions.RIVER)

    return hand if hand.get_hero() is not None else None

def _process_post_flop_actions(hand, lines, street):
    acts = []

    while len(lines) > 0:
        line = lines[0]
        if fields := _find_text(line[0], r'"(.*)" calls ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            acts.append(actions.Action(name, amt, actions.CALL, street, all_in=all_in))
            _get_player(hand.players, name).street_nets[street] = -amt
        elif fields := _find_text(line[0], r'"(.*)" bets ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            acts.append(actions.Action(name, amt, actions.OPEN, street, all_in=all_in))
            _get_player(hand.players, name).street_nets[street] = -amt
        elif name := _find_text(line[0], r'"(.*)" checks', allow_fail=True):
            name = name[0]
            acts.append(actions.Action(name, 0, actions.CHECK, street))
        elif name := _find_text(line[0], r'"(.*)" folds', allow_fail=True):
            name = name[0]
            acts.append(actions.Action(name, 0, actions.FOLD, street))
        elif fields := _find_text(line[0], r'"(.*)" raises to ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            acts.append(actions.Action(name, amt, actions.RAISE, street, all_in=all_in))
            _get_player(hand.players, name).street_nets[street] = -amt
        elif name_amt := _find_text(line[0], r'Uncalled bet of (.*) returned to "(.*)"', allow_fail=True):
            amt, name = float(name_amt[0]), name_amt[1]
            _get_player(hand.players, name).gain += amt
        elif name_amt := _find_text(line[0], r'"(.*)" collected ([\d\.]+) from pot .*', allow_fail=True):
            name, amt = name_amt[0], float(name_amt[1])
            _get_player(hand.players, name).gain += amt
        elif street == "flop" and _find_text(line[0], r'Turn:  .*', allow_fail=True):
            break
        elif street == "turn" and _find_text(line[0], r'River:  .*', allow_fail=True):
            break
        elif street == "river" and _find_text(line[0], r'-- ending hand .*', allow_fail=True):
            break
        lines.pop(0)
    return acts

def _convert_card(c: str):
    if c is None:
        return None
    else:
        return (
            c.replace("10", "T")
                .replace('â™¦', 'd')
                .replace('â™\xa0', 's')
                .replace('â™¥', 'h')
                .replace('â™£', 'c'))

def _get_player(players, player_name):
    for p in players:
        if p.name == player_name:
            return p
    return None

def _assign_player_positions(players, sb_player_name, bb_player_name):
    pnames = [p.name for p in players]
    sb_index = pnames.index(sb_player_name)
    bb_index = pnames.index(bb_player_name)
    players[sb_index].position = 0
    players[bb_index].position = 1
    for i in range(len(players) - 2):
        players[(bb_index + i + 1) % len(players)].position = 2 + i

def _pop_line_matching(lines, pattern, line_idx=0, allow_fail=False):
    discarded = []
    while len(lines) > 0:
        cur = lines.pop(0)
        if line_idx < len(cur) and _find_text(cur[line_idx], pattern, allow_fail=True) is not None:
            return cur
        else:
            discarded.append(cur)
    if allow_fail:
        lines.extend(discarded)
        return None
    else:
        raise ValueError(f"Failed to find line matching pattern: {pattern}\n  "
                        f"{'\n  '.join(list(str(s) for s in discarded))}")

def _find_text(search_domain, pattern, allow_fail=False):
    """
    :param pattern: "Plain text {1} with more plain text {2}"
    """
    result = re.search(pattern, search_domain)
    if result is None:
        if not allow_fail:
            raise ValueError(f"Failed to find pattern '{pattern}' in: {search_domain}")
        else:
            return None
    return result.groups()

if __name__ == "__main__":
    logdir = "C:\\Users\\david\\Desktop\\Poker Notes\\logs"
    filenames = os.listdir(logdir)
    all_hands = hands.HandGroup([], desc="All Hands")
    for f in filenames:
        hl = scrape(HERO_ID, os.path.join(logdir, f))
        print(f"Scraped {len(hl)} hand(s) from: {f}")
        all_hands.extend(hl)
    print()

    locale.setlocale(locale.LC_ALL, '')

    print("-- Summary --")
    print(f"Hands:      {len(all_hands)} (in {all_hands.session_count()} sessions)")
    # print(f"Total Flux:     {locale.currency(all_hands.total_flux())}")
    saw_flop_filter = filters.HeroSawStreet(actions.FLOP)
    saw_flop_hands = all_hands.filter(saw_flop_filter, desc="Saw Flop")
    print(f"Saw Flop:   {len(saw_flop_hands)} time(s) ({len(saw_flop_hands) / len(all_hands) * 100.:.2f}%)")
    print(f"Net Gain:   {locale.currency(all_hands.net_gain())}")
    print()

    print("-- Situational Breakdowns --")

    custom_filters = {
        "All Hands": filters.Filter(),
        "Early Position": filters.HeroAtSpecificPosition(actions.EARLY_POS),
        "Mid Position": filters.HeroAtSpecificPosition(actions.MID_POS),
        "Late Position": filters.HeroAtSpecificPosition(actions.LATE_POS),
        "UTG": filters.HeroAtSpecificPosition(actions.UTG),
        "BTN": filters.HeroAtSpecificPosition(actions.BTN),
        "as BB": filters.HeroAtSpecificPosition(actions.BB),
        "as SB": filters.HeroAtSpecificPosition(actions.SB),
        "from Blinds": filters.HeroAtSpecificPosition(actions.BLINDS),
        "IP Post-Flop": filters.HeroInPosition(),
        "OoP Post-Flop": filters.HeroOutOfPosition(),
        "Premiums (JJ+, AQ+)": filters.HeroCardFilter("JJ+, AQ+"),
        "Mid Pairs (TT-77)": filters.HeroCardFilter("77-TT"),
        "Low Pairs (66-22)": filters.HeroCardFilter("22-66"),

        "Broadways (KQ KJ QJ)": filters.HeroCardFilter("KQ, KJ, QJ"),

        "High S Connectors (AK-JTs)": filters.HeroCardFilter("AK-JTs"),
        "Mid S Connectors (T9-76s)": filters.HeroCardFilter("T9-76s"),
        "Low S Connectors (32-65s)": filters.HeroCardFilter("32-65s"),

        "High S Gappers (AQ-J9s)": filters.HeroCardFilter("AQ-J9s"),

        "Mid oS Ax (AJ-A6o)": filters.HeroCardFilter("AJ-A6o"),
        "Mid S Ax (AJ-A6s)": filters.HeroCardFilter("AJ-A6s"),
        "Low oS Ax (A5-A2o)": filters.HeroCardFilter("A5-A2o"),
        "Low S Ax (A5-A2s)": filters.HeroCardFilter("A5-A2s"),

        "Junky oS Kx (KT-K2o)": filters.HeroCardFilter("KT-K2o"),
        "Suited Kx (KT-K2s)": filters.HeroCardFilter("KT-K2s"),
        "Junky oS Qx (QT-Q2o)": filters.HeroCardFilter("QT-Q2o"),
        "Suited Qx (QT-Q2s)": filters.HeroCardFilter("QT-Q2s"),

        "2-way Flops": filters.HeroSawStreet(actions.FLOP) & filters.Multiway(actions.FLOP, at_most=2),
        "3-way Flops": filters.HeroSawStreet(actions.FLOP) & filters.Multiway(actions.FLOP, at_least=3, at_most=3),
        "4-way+ Flops": filters.HeroSawStreet(actions.FLOP) & filters.Multiway(actions.FLOP, at_least=4),

        "Gets to Showdown": filters.HeroSawStreet(actions.SHOWDOWN),
        "Doesn't get to Showdown": filters.HeroVPIP(street=actions.ANY) & ~filters.HeroSawStreet(actions.SHOWDOWN)
    }

    custom_results = [all_hands.filter(custom_filters[f], desc=f) for f in custom_filters]
    custom_results.sort(key=lambda x: x.avg_gain_per_play(), reverse=True)

    for res in custom_results:
        print(res.summary())
        # print(f"Hands: {filtered_hands.get_hole_card_freqs()}")
    print()

    print("-- Per-Hand Stats --")
    my_per_hand_stats: typing.Dict[str, hands.HandGroup] = {}
    for h in all_hands:
        p = h.get_hero()
        if p.net() != 0:
            cc = p.get_card_code()
            if cc is not None:
                if cc not in my_per_hand_stats:
                    my_per_hand_stats[cc] = hands.HandGroup([], desc=cc)
                my_per_hand_stats[cc].append(h)

    ents = [v for v in my_per_hand_stats.values() if len(v) >= 3]
    ents.sort(key=lambda x: x.avg_gain_per_play(), reverse=True)

    for ent in ents:
        avg = f"{ent.avg_bbs_per_play():.1f}bb"
        tot = locale.currency(ent.net_gain())
        print(f"{ent.desc:<12}{avg:<12}{tot: <10} in {len(ent)} hand(s)")
    print()

    print("-- Per-Hand Profit Table --")
    cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
    print(" " * 12 + "".join(f"{c:<12}" for c in cards))
    for c1 in cards:
        line = f"{c1:<12}"
        for c2 in cards:
            if c1 == c2:
                hand = c1 + c2
            elif cards.index(c1) < cards.index(c2):
                hand = c1 + c2 + "s"
            else:
                hand = c2 + c1 + "o"
            cnt = len(my_per_hand_stats[hand]) if hand in my_per_hand_stats else 0
            avg = my_per_hand_stats[hand].avg_bbs_per_play() if hand in my_per_hand_stats else 0
            text = f"{avg:.1f} ({cnt})"
            line += f"{text:<12}"
        print(line)
