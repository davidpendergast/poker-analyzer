import datetime

import const
from poker import hands, actions

import typing
import os
import csv
import re
import locale


def scrape_directory(hero_id, log_downloader_id, dirpath, desc="All Hands", aliases=()) -> hands.HandGroup:
    locale.setlocale(locale.LC_ALL, '')
    all_hands = hands.HandGroup([], desc=desc)
    all_groups = []
    filenames = os.listdir(dirpath)
    for f in filenames:
        hl = scrape(hero_id, log_downloader_id, os.path.join(dirpath, f),
                    alias_lookup=_invert_alias_map(hero_id, aliases))
        group = hands.HandGroup(hl)
        all_groups.append((group, f))
        all_hands.extend(hl)

    for group, fname in sorted(all_groups, key=lambda x: x[0].dates()):
        dates = group.dates()
        print(f"Scraped {len(group):<4} hand(s) from: {fname} {locale.currency(group.net_gain()):<9} "
              f"({dates[0] if len(dates) > 0 else '?/?/????'})")
    print()

    # for debugging
    # if len(all_groups) == 1:
    #     next_stack_should_be = None
    #     for h in all_hands:
    #         print(h)
    #         if h.get_hero() is None:
    #             continue
    #         if next_stack_should_be is not None and abs(h.get_hero().stack - next_stack_should_be) > 0.005:
    #             print(f"*** Unexpected stack (expect={locale.currency(next_stack_should_be)}, actual={h.get_hero().stack})")
    #         next_stack_should_be = h.get_hero().stack + h.get_hero().net()

    return all_hands


def _invert_alias_map(hero_id, aliases):
    res = {}  # player_id -> 'AliasName @ alias_id'
    for pname in aliases:
        codes = aliases[pname]
        if len(codes) == 0:
            continue
        elif hero_id in codes:
            alias = f"{pname} @ {hero_id}"
        else:
            alias = f"{pname} @ {codes[0]}"
        for code in codes:
            if code in res:
                raise ValueError(f"Player code \"{code}\" is pointing at two aliases: {res[code]}, {alias}")
            res[code] = alias
    return res


def scrape(hero_id, log_downloader_id, logfilepath, alias_lookup=()) -> typing.List[hands.Hand]:
    res = []
    with open(logfilepath, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        lines = [l for l in reader if (len(l) == 3 and l != ["entry", "at", "order"])]
        lines.sort(key=lambda l: int(l[2]))  # sort lines by "order" field

        configs = {
            "logfile": os.path.basename(logfilepath),
            "sb_cost": 0.10,
            "bb_cost": 0.20,
            "ante_cost": 0.0,
        }

        cur_hand_lines = []
        cur_hand_configs = configs.copy()
        started_first = False
        for i in range(len(lines)):
            _update_configs(configs, lines[i])
            if lines[i][0].startswith("-- starting hand #"):
                started_first = True
                cur_hand_configs = configs.copy()
                cur_hand_lines.clear()
            cur_hand_lines.append(lines[i])
            if i >= len(lines) - 1 or (started_first and lines[i + 1][0].startswith("-- starting hand #")):
                hand = _create_hand_from_lines(
                        hero_id,
                        log_downloader_id,
                        cur_hand_configs,
                        cur_hand_lines,
                        alias_lookup=alias_lookup,
                        must_include_hero=False)
                if hand is not None:
                    hand.calc_advanced_stats(limit=const.EQUITY_CALC_N_ITERS)
                    res.append(hand)
    return res


def _update_configs(configs, line):
    if old_new := _find_text(line[0], r'The game\'s small blind was changed from (.*) to (.*)\.', allow_fail=True):
        configs['sb_cost'] = float(old_new[1])
    elif old_new := _find_text(line[0], r'The game\'s big blind was changed from (.*) to (.*)\.', allow_fail=True):
        configs['bb_cost'] = float(old_new[1])
    elif old_new := _find_text(line[0], r'The game\'s ante was changed from (.*) to (.*)\.', allow_fail=True):
        configs['ante_cost'] = float(old_new[1])


def _create_hand_from_lines(hero_id, log_downloader_id, configs, lines, alias_lookup=(), must_include_hero=True) -> typing.Optional[hands.Hand]:
    pid_switches = _get_pid_switches(lines)

    intro_line = _pop_line_matching(lines, r'-- starting hand #(\d+).*')
    hand_idx = int(_find_text(intro_line[0], r'-- starting hand #(\d+).*')[0])
    timestamp = parse_utc_timestamp(intro_line[1])

    _alias_mappings = {}

    def clean_pname(_pname: str):
        name, pid = _pname.split(' @ ')
        if pid in pid_switches:
            pid = pid_switches[pid]
        if pid not in _alias_mappings:
            alias = alias_lookup[pid] if pid in alias_lookup else f'{name} @ {pid}'
            if alias in _alias_mappings.values():
                # this can happen if people join a table with two alts at once
                # we need to give them unique IDs
                alias += "(dupe)"
            _alias_mappings[pid] = alias
        return _alias_mappings[pid]

    end_line = _find_line_matching(lines, r'-- ending hand #(\d+).*')
    if end_line is None:
        # Incomplete hand, probably due to log-truncation (after 20k lines)
        # or the game ending while paused. Not much we can do.
        return None
    end_timestamp = parse_utc_timestamp(end_line[1])

    # this sometimes gets logged before final hand-shows, just move it to the end for simplicity
    lines.sort(key=lambda l: 1 if "-- ending hand #" in l[0] else 0)

    final_collect_line_order = int(_find_line_matching(lines, r'"(.*)" collected ([\d\.]+) from pot.*', first=False)[2])

    players_line = _pop_line_matching(lines, r'Player stacks: (.*)')
    player_list = []
    raw_players = _find_text(players_line[0], r'Player stacks: (.*)')[0].split(" | ")
    for p in raw_players:
        pname, pstack = _find_text(p, r'"(.*)" \((.*)\)')
        player_list.append(hands.Player(clean_pname(pname), float(pstack), -1, (None, None)))

    hand = hands.Hand(timestamp, end_timestamp, configs, hand_idx, hero_id, player_list)

    hero = hand.get_hero()
    if hero is None and must_include_hero:
        return None

    if log_downloader_id in alias_lookup:
        log_downloader_id = alias_lookup[log_downloader_id]

    your_hand_line = _pop_line_matching(lines, r'Your hand is.*', allow_fail=True)
    if hero is not None and hands.Player.names_eq(log_downloader_id, hero_id) and your_hand_line is not None:
        c1, c2 = _find_text(your_hand_line[0], "Your hand is (.+), (.+)")
        hero.cards = _convert_card(c1), _convert_card(c2)

    # Pre-Flop
    pos = 0
    while len(lines) > 0:
        line = lines[0]
        if fields := _find_text(line[0], r'"(.*)" posts a small blind of ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = clean_pname(fields[0]), float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.SB, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif fields := _find_text(line[0], r'"(.*)" posts a big blind of ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = clean_pname(fields[0]), float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.BB, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif fields := _find_text(line[0], r'"(.*)" posts a straddle of ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = clean_pname(fields[0]), float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.STRADDLE, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif fields := _find_text(line[0], r'"(.*)" posts a miss(.*) of ([\d\.]+)( and go all in)?', allow_fail=True):
            # if you sit out during your blind(s) and then rejoin, it compels you to post a missing SB/BB.
            # note: a missing small blind is treated like an ante, whereas a missing bb is treated like a bet.
            name, bet_type, amt, all_in = clean_pname(fields[0]), fields[1], float(fields[2]), fields[3] is not None
            if "small blind" in bet_type:
                _get_player(player_list, name).street_nets['ante'] -= amt
            elif "big blind" in bet_type:
                _get_player(player_list, name).street_nets['pre-flop'] = -amt
            else:
                raise ValueError(f"Unrecognized missing bet type: {bet_type} (value={amt})")
        elif fields := _find_text(line[0], r'"(.*)" calls ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = clean_pname(fields[0]), float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.CALL, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif fields := _find_text(line[0], r'"(.*)" bets ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = clean_pname(fields[0]), float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.OPEN, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif name := _find_text(line[0], r'"(.*)" checks', allow_fail=True):
            name = clean_pname(name[0])
            hand.pre_flop_actions.append(actions.Action(name, 0, actions.CHECK, actions.PRE_FLOP))
        elif name := _find_text(line[0], r'"(.*)" folds', allow_fail=True):
            name = clean_pname(name[0])
            hand.pre_flop_actions.append(actions.Action(name, 0, actions.FOLD, actions.PRE_FLOP))
        elif fields := _find_text(line[0], r'"(.*)" raises to ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = clean_pname(fields[0]), float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.RAISE, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif name_amt := _find_text(line[0], r'Uncalled bet of (.*) returned to "(.*)"', allow_fail=True):
            amt, name = float(name_amt[0]), clean_pname(name_amt[1])
            _get_player(player_list, name).gain += amt
        elif name_amt := _find_text(line[0], r'"(.*)" collected ([\d\.]+) from pot.*', allow_fail=True):
            name, amt = clean_pname(name_amt[0]), float(name_amt[1])
            _get_player(player_list, name).gain += amt
        elif name_shows := _find_text(line[0], r'"(.*)" shows a (.*)\.', allow_fail=True):
            name, shows = clean_pname(name_shows[0]), name_shows[1]
            _handle_player_shows_a_card(player_list, name, shows, voluntary=int(line[2]) > final_collect_line_order)
        elif _find_text(line[0], r'Flop:[ ]+.*', allow_fail=True) is not None:
            break

        p = _get_player(player_list, name)
        if p is not None and p.position == -1:
            p.position = pos
            pos += 1
        lines.pop(0)

    flop_line = _pop_line_matching(lines, r'Flop:[ ]+.*', allow_fail=True)
    if flop_line is not None:
        flop_raw = _find_text(flop_line[0], r'Flop:[ ]+\[(.*)\]')[0].split(", ")
        hand.board = [_convert_card(c) for c in flop_raw] + [None, None]
    else:
        return hand

    hand.flop_actions = _process_post_flop_actions(hand, lines, player_list, actions.FLOP, final_collect_line_order, clean_pname)

    turn_line = _pop_line_matching(lines, r'Turn:[ ]+.*', allow_fail=True)
    if turn_line is not None:
        turn_raw = _find_text(turn_line[0], r'Turn:[ ]+.* \[(.*)\]')[0]
        hand.board[3] = _convert_card(turn_raw)
    else:
        return hand

    hand.turn_actions = _process_post_flop_actions(hand, lines, player_list, actions.TURN, final_collect_line_order, clean_pname)

    river_line = _pop_line_matching(lines, r'River:[ ]+.*', allow_fail=True)
    if river_line is not None:
        river_raw = _find_text(river_line[0], r'River:[ ]+.* \[(.*)\]')[0]
        hand.board[4] = _convert_card(river_raw)
    else:
        return hand

    # find 2nd run-out if there was one.
    river2_line = _pop_line_matching(lines, r'River \(second run\):.*', allow_fail=True)
    if river2_line is not None:
        river2_cards = _find_text(river2_line[0], r'River \(second run\):[ ]+([^,]*), ([^,]*), ([^,]*), ([^,]*) \[(.*)\].*')
        hand.board2 = [_convert_card(c) for c in river2_cards]

    hand.river_actions = _process_post_flop_actions(hand, lines, player_list, actions.RIVER, final_collect_line_order, clean_pname)
    return hand


def _process_post_flop_actions(hand, lines, player_list, street, final_collect_line_order, clean_pname):
    acts = []

    while len(lines) > 0:
        line = lines[0]
        if fields := _find_text(line[0], r'"(.*)" calls ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = clean_pname(fields[0]), float(fields[1]), fields[2] is not None
            acts.append(actions.Action(name, amt, actions.CALL, street, all_in=all_in))
            _get_player(hand.players, name).street_nets[street] = -amt
        elif fields := _find_text(line[0], r'"(.*)" bets ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = clean_pname(fields[0]), float(fields[1]), fields[2] is not None
            acts.append(actions.Action(name, amt, actions.OPEN, street, all_in=all_in))
            _get_player(hand.players, name).street_nets[street] = -amt
        elif name := _find_text(line[0], r'"(.*)" checks', allow_fail=True):
            name = clean_pname(name[0])
            acts.append(actions.Action(name, 0, actions.CHECK, street))
        elif name := _find_text(line[0], r'"(.*)" folds', allow_fail=True):
            name = clean_pname(name[0])
            acts.append(actions.Action(name, 0, actions.FOLD, street))
        elif fields := _find_text(line[0], r'"(.*)" raises to ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = clean_pname(fields[0]), float(fields[1]), fields[2] is not None
            acts.append(actions.Action(name, amt, actions.RAISE, street, all_in=all_in))
            _get_player(hand.players, name).street_nets[street] = -amt
        elif name_amt := _find_text(line[0], r'Uncalled bet of (.*) returned to "(.*)"', allow_fail=True):
            amt, name = float(name_amt[0]), clean_pname(name_amt[1])
            _get_player(hand.players, name).gain += amt
        elif name_amt := _find_text(line[0], r'"(.*)" collected ([\d\.]+) from pot.*', allow_fail=True):
            name, amt = clean_pname(name_amt[0]), float(name_amt[1])
            _get_player(hand.players, name).gain += amt
        elif name_shows := _find_text(line[0], r'"(.*)" shows a (.*)\.', allow_fail=True):
            name, shows = clean_pname(name_shows[0]), name_shows[1]
            _handle_player_shows_a_card(player_list, name, shows, voluntary=int(line[2]) > final_collect_line_order)
        elif street == actions.FLOP and _find_text(line[0], r'Turn:[ ]+.*', allow_fail=True) is not None:
            break
        elif street == actions.TURN and _find_text(line[0], r'River:[ ]+.*', allow_fail=True) is not None:
            break
        elif street == actions.RIVER and _find_text(line[0], r'-- ending hand .*', allow_fail=True) is not None:
            break
        lines.pop(0)
    return acts


def _handle_player_shows_a_card(player_list, name, shows, voluntary=False):
    cards = [_convert_card(shows)] if ", " not in shows else [_convert_card(shows.split(", ")[0]),
                                                              _convert_card(shows.split(", ")[1])]
    player = _get_player(player_list, name)
    if len(cards) == 2:
        # player showed both cards at the same time
        player.cards = tuple(cards)
        player.showed_cards = 2
        if voluntary:
            player.voluntarily_showed_cards = 2
    else:
        # player only showed one card
        old_cards = player.cards
        if old_cards == (None, None):
            player.cards = (cards[0], None)
            player.showed_cards = 1
            if voluntary:
                player.voluntarily_showed_cards = 1
        elif old_cards[1] is None:
            player.cards = (old_cards[0], cards[0])
            player.showed_cards = 2
            if voluntary:
                player.voluntarily_showed_cards = 2
        elif cards[0] not in old_cards:
            raise ValueError(f"Player's current cards are {old_cards} and showed {cards}?")


def _get_pid_switches(lines) -> typing.Dict[str, str]:
    # deals with lines like: "The player ""Nick @ pvi7lGaAqX"" changed the ID from -MJHz7DZc1 to pvi7lGaAqX
    # because authenticated login."
    switches = {}
    for line in lines:
        fields = _find_text(line[0], r'The player "(.*)" changed the ID from (.*) to (.*) because.*', allow_fail=True)
        if fields is not None:
            pid, old_id, new_id = fields

            if old_id in switches.values():
                # same player switched IDs multiple time in same hand...?
                ks_to_remap = []
                for k, v in switches:
                    if v == old_id:
                        ks_to_remap.append(k)
                for k in ks_to_remap:
                    switches[k] = new_id

            switches[old_id] = new_id
    return switches


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


def _get_player(players, player_name) -> typing.Optional[hands.Player]:
    for p in players:
        if p.name_and_id == player_name:
            return p
    return None


def _assign_player_positions(players, sb_player_name, bb_player_name):
    pnames = [p.name_and_id for p in players]
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
        msg_lines = '\n  '.join(list(str(s) for s in discarded))
        raise ValueError(f"Failed to find line matching pattern: {pattern}\n  {msg_lines}")


def _find_line_matching(lines, pattern, line_idx=0, first=True):
    ordered_lines = lines if first else reversed(lines)
    for cur in ordered_lines:
        if line_idx < len(cur):
            res = _find_text(cur[line_idx], pattern, allow_fail=True)
            if res is not None:
                return cur
    return None


def _find_text(search_domain, pattern, allow_fail=False):
    """
    :param pattern: "Plain text {1} with more plain text {2}"
    """
    result = re.search(pattern, search_domain)
    if result is None:
        if not allow_fail:
            raise ValueError(f"Failed to find pattern '{pattern}' in: '{search_domain}'")
        else:
            return None
    return result.groups()


def parse_utc_timestamp(timestamp: str) -> datetime.datetime:
    """2025-01-28T03:22:32.149Z -> datetime"""
    date, time = timestamp.split("T")
    time = time.split(".")[0]
    yyyy, mm, dd = date.split("-")
    hh, minute, ss = time.split(":")
    return datetime.datetime(int(yyyy), int(mm), int(dd), int(hh), int(minute), int(ss), tzinfo=datetime.timezone.utc).astimezone()


if __name__ == "__main__":
    print(parse_utc_timestamp("2025-01-28T03:22:32.149Z").astimezone().strftime("%Y-%m-%d"))