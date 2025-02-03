# -*- coding: utf-8 -*-

import hands
import filters
import actions

import typing
import os
import locale
import scraping

HERO_ID = 'Ghast @ k-xm91OpZ6'              # ID of the player to track.
# HERO_ID = 'M1sf1re @ TNLfj8hFbJ'            # (for debug) M1sf1re
# HERO_ID = 'Ravi @ B8jVhFGWIY'               # (for debug) Ravi
# HERO_ID = 'Flow @ pvi7lGaAqX'               # (for debug) Flow
# HERO_ID = 'Freky @ rnl8dHxqtf'              # (for debug) Freky

LOG_DOWNLOADER_ID = 'k-xm91OpZ6'    # ID of the player who downloaded the logs.

LOG_DIR = "C:\\Users\\david\\Desktop\\Poker Notes\\logs"
# LOG_DIR = "testdata"

if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')
    filenames = os.listdir(LOG_DIR)
    all_hands = hands.HandGroup([], desc="All Hands")
    all_groups = []
    for f in filenames:
        hl = scraping.scrape(HERO_ID, LOG_DOWNLOADER_ID, os.path.join(LOG_DIR, f))
        group = hands.HandGroup(hl)
        all_groups.append((group, f))
        all_hands.extend(hl)
    for group, fname in sorted(all_groups, key=lambda x: x[0].dates()):
        dates = group.dates()

        print(f"Scraped {len(group):<4} hand(s) from: {fname} {locale.currency(group.net_gain()):<9} "
              f"({dates[0] if len(dates) > 0 else "?/?/????"})")
    print()

    if len(all_hands) == 0:
        print(f"No hands found for HERO_ID={HERO_ID}")
        raise SystemExit

    # for debugging
    if len(all_groups) == 1:
        next_stack_should_be = None
        for h in all_hands:
            if next_stack_should_be is not None and abs(h.get_hero().stack - next_stack_should_be) > 0.005:
                print(f"*** Unexpected stack (expect={locale.currency(next_stack_should_be)}, actual={h.get_hero().stack})")
            print(h)
            next_stack_should_be = h.get_hero().stack + h.get_hero().net()

    print(f"-- Summary of {HERO_ID} --")
    print(f"Hands:        {len(all_hands)} (in {all_hands.session_count()} sessions)")

    # When analyzing another player, a good chunk of their cards will be unknown.
    unknown_card_hands = all_hands.filter(filters.HeroCardsKnown(counts=0))
    one_known_card_hands = all_hands.filter(filters.HeroCardsKnown(counts=1))
    if len(unknown_card_hands) > 0 or len(one_known_card_hands) > 0:
        pcnt = (len(all_hands) - len(unknown_card_hands) - len(one_known_card_hands) / 2) / len(all_hands)
        print(f"Known Cards:  {pcnt * 100.:.2f}%")

    saw_flop_filter = filters.HeroSawStreet(actions.FLOP)
    saw_flop_hands = all_hands.filter(saw_flop_filter, desc="Saw Flop")
    print(f"Saw Flop:     {len(saw_flop_hands)} time(s) ({len(saw_flop_hands) / len(all_hands) * 100.:.2f}%)")
    print(f"VPIP:         {all_hands.vpip_pcnt() * 100:.1f}%")
    print(f"3BET%:        {all_hands.get_3bet_pcnt() * 100:.1f}%")
    print(f"Net Gain:     {locale.currency(all_hands.net_gain())}")
    print()

    print("-- Situational Breakdowns --")

    custom_filters = {
        "All Hands": filters.Filter(),
        "AA": filters.HeroCardFilter("AA"),
        "KK": filters.HeroCardFilter("KK"),
        "AK": filters.HeroCardFilter("AK"),
        "QQ": filters.HeroCardFilter("QQ"),
        "??": filters.HeroCardsKnown(counts=0),
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
        "Doesn't get to Showdown": filters.HeroVPIP() & ~filters.HeroSawStreet(actions.SHOWDOWN)
    }

    custom_results = [all_hands.filter(custom_filters[f], desc=f) for f in custom_filters]
    custom_results.sort(key=lambda x: x.avg_bbs_per_play(), reverse=True)

    for res in custom_results:
        if len(res) > 0:  # skip categories with zero hands
            print(res.summary())
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
