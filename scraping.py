import datetime

import hands
import actions

import typing
import os
import csv
import re


def scrape(hero_id, log_downloader_id, logfilepath) -> typing.List[hands.Hand]:
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
        started_first = False
        for i in range(len(lines)):
            _update_configs(configs, lines[i])
            if lines[i][0].startswith("-- starting hand #"):
                started_first = True
                cur_hand_configs = configs.copy()
                cur_hand_lines.clear()
            cur_hand_lines.append(lines[i])
            if i >= len(lines) - 1 or (started_first and lines[i + 1][0].startswith("-- starting hand #")):
                hand = _create_hand_from_lines(hero_id, log_downloader_id, cur_hand_configs, cur_hand_lines)
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

def _create_hand_from_lines(hero_id, log_downloader_id, configs, lines) -> typing.Optional[hands.Hand]:
    intro_line = _pop_line_matching(lines, r'-- starting hand #(\d+).*')
    timestamp = parse_utc_timestamp(intro_line[1])
    hand_idx = int(_find_text(intro_line[0], r'-- starting hand #(\d+).*')[0])

    players_line = _pop_line_matching(lines, r'Player stacks: (.*)')
    player_list = []
    raw_players = _find_text(players_line[0], r'Player stacks: (.*)')[0].split(" | ")
    for p in raw_players:
        pname, pstack = _find_text(p, r'"(.*)" \((.*)\)')
        player_list.append(hands.Player(pname, float(pstack), -1, (None, None)))

    hand = hands.Hand(timestamp, configs, hand_idx, hero_id, player_list)

    hero = hand.get_hero()
    your_hand_line = _pop_line_matching(lines, r'Your hand is.*', allow_fail=True)
    if hero is not None and hands.Player.names_eq(log_downloader_id, hero_id) and your_hand_line is not None:
        c1, c2 = _find_text(your_hand_line[0], "Your hand is (.+), (.+)")
        hero.cards = _convert_card(c1), _convert_card(c2)

    # Pre-Flop
    pos = 0
    while len(lines) > 0:
        line = lines[0]
        if fields := _find_text(line[0], r'"(.*)" posts a small blind of ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.SB, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] -=amt
        elif fields := _find_text(line[0], r'"(.*)" posts a big blind of ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.BB, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] -=amt
        elif fields := _find_text(line[0], r'"(.*)" posts a miss(?:.*) of ([\d\.]+)( and go all in)?', allow_fail=True):
            # if you sit out during your blind(s) and then rejoin, it compels you to post a missing SB/BB at your current position.
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            _get_player(player_list, name).street_nets[actions.PRE_FLOP] -= amt
        elif fields := _find_text(line[0], r'"(.*)" calls ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.CALL, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif fields := _find_text(line[0], r'"(.*)" bets ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.OPEN, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif name := _find_text(line[0], r'"(.*)" checks', allow_fail=True):
            name = name[0]
            hand.pre_flop_actions.append(actions.Action(name, 0, actions.CHECK, actions.PRE_FLOP))
        elif name := _find_text(line[0], r'"(.*)" folds', allow_fail=True):
            name = name[0]
            hand.pre_flop_actions.append(actions.Action(name, 0, actions.FOLD, actions.PRE_FLOP))
        elif fields := _find_text(line[0], r'"(.*)" raises to ([\d\.]+)( and go all in)?', allow_fail=True):
            name, amt, all_in = fields[0], float(fields[1]), fields[2] is not None
            hand.pre_flop_actions.append(actions.Action(name, amt, actions.RAISE, actions.PRE_FLOP, all_in=all_in))
            _get_player(player_list, name).street_nets['pre-flop'] = -amt
        elif name_amt := _find_text(line[0], r'Uncalled bet of (.*) returned to "(.*)"', allow_fail=True):
            amt, name = float(name_amt[0]), name_amt[1]
            _get_player(player_list, name).gain += amt
        elif name_amt := _find_text(line[0], r'"(.*)" collected ([\d\.]+) from pot.*', allow_fail=True):
            name, amt = name_amt[0], float(name_amt[1])
            _get_player(player_list, name).gain += amt
            return hand if hand.get_hero() is not None else None
        elif name_shows := _find_text(line[0], r'"(.*)" shows a (.*)\.', allow_fail=True):
            name, shows = name_shows[0], name_shows[1]
            _handle_player_shows_a_card(player_list, name, shows)
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
        return hand if hand.get_hero() is not None else None

    hand.flop_actions = _process_post_flop_actions(hand, lines, player_list, actions.FLOP)

    turn_line = _pop_line_matching(lines, r'Turn:[ ]+.*', allow_fail=True)
    if turn_line is not None:
        turn_raw = _find_text(turn_line[0], r'Turn:[ ]+.* \[(.*)\]')[0]
        hand.board[3] = _convert_card(turn_raw)
    else:
        return hand if hand.get_hero() is not None else None

    hand.turn_actions = _process_post_flop_actions(hand, lines, player_list, actions.TURN)

    river_line = _pop_line_matching(lines, r'River:[ ]+.*', allow_fail=True)
    if river_line is not None:
        river_raw = _find_text(river_line[0], r'River:[ ]+.* \[(.*)\]')[0]
        hand.board[4] = _convert_card(river_raw)
    else:
        return hand if hand.get_hero() is not None else None

    hand.river_actions = _process_post_flop_actions(hand, lines, player_list, actions.RIVER)

    return hand if hand.get_hero() is not None else None

def _process_post_flop_actions(hand, lines, player_list, street):
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
        elif name_amt := _find_text(line[0], r'"(.*)" collected ([\d\.]+) from pot.*', allow_fail=True):
            name, amt = name_amt[0], float(name_amt[1])
            _get_player(hand.players, name).gain += amt
        elif name_shows := _find_text(line[0], r'"(.*)" shows a (.*)\.', allow_fail=True):
            name, shows = name_shows[0], name_shows[1]
            _handle_player_shows_a_card(player_list, name, shows)
        elif street == actions.FLOP and _find_text(line[0], r'Turn:[ ]+.*', allow_fail=True) is not None:
            break
        elif street == actions.TURN and _find_text(line[0], r'River:[ ]+.*', allow_fail=True) is not None:
            break
        elif street == actions.RIVER and _find_text(line[0], r'-- ending hand .*', allow_fail=True) is not None:
            break
        lines.pop(0)
    return acts

def _handle_player_shows_a_card(player_list, name, shows):
    cards = [_convert_card(shows)] if ", " not in shows else [_convert_card(shows.split(", ")[0]),
                                                              _convert_card(shows.split(", ")[1])]
    if len(cards) == 2:
        # player showed both cards at the same time
        _get_player(player_list, name).cards = tuple(cards)
    else:
        # player only showed one card
        old_cards = _get_player(player_list, name).cards
        if old_cards == (None, None):
            _get_player(player_list, name).cards = (cards[0], None)
        elif old_cards[1] is None:
            _get_player(player_list, name).cards = (old_cards[0], cards[0])
        elif cards[0] not in old_cards:
            raise ValueError(f"Player's current cards are {old_cards} and showed {cards}?")

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