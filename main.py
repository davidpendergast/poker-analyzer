# -*- coding: utf-8 -*-

import typing
import locale

from poker import filters, actions, hands, scraping, preflop_db

import const

if __name__ == "__main__":
    preflop_db.load_from_disk()
    all_hands = scraping.scrape_directory(const.HERO_ID, const.LOG_DOWNLOADER_ID, const.LOG_DIR)

    if const.N_MOST_RECENT_SESSIONS_TO_SCRAPE > 0:
        all_hands = all_hands.most_recent_sessions(const.N_MOST_RECENT_SESSIONS_TO_SCRAPE, desc=all_hands.desc)
        print(f"** Analyzing last {all_hands.session_count()} session(s) **\n")

    if all_hands.session_count() == 1:
        for h in all_hands:
            print(f"  {h}")
        print()

    hero_hands = all_hands.filter(filters.HeroPlayed())

    print(f"-- Summary of {const.HERO_ID} --")
    print(f"Hands:        {len(hero_hands)} (in {hero_hands.session_count()} sessions)")

    # When analyzing another player as the hero, a good chunk of their cards will be unknown.
    unknown_card_hands = hero_hands.filter(filters.HeroCardsKnown(counts=0))
    one_known_card_hands = hero_hands.filter(filters.HeroCardsKnown(counts=1))
    if len(unknown_card_hands) > 0 or len(one_known_card_hands) > 0:
        pcnt = (len(hero_hands) - len(unknown_card_hands) - len(one_known_card_hands) / 2) / len(hero_hands)
        print(f"Known Cards:  {pcnt * 100.:.2f}%")

    saw_flop_filter = filters.HeroSawStreet(actions.FLOP)
    saw_flop_hands = hero_hands.filter(saw_flop_filter, desc="Saw Flop")
    sign = '+' if hero_hands.net_gain() > 0 else ''
    print(f"Saw Flop:     {len(saw_flop_hands)} time(s) ({len(saw_flop_hands) / len(hero_hands) * 100.:.2f}%)")
    print(f"VPIP:         {hero_hands.vpip_pcnt() * 100:.2f}%")
    print(f"3BET%:        {hero_hands.get_3bet_pcnt() * 100:.2f}%")
    print(f"Net Gain:     {locale.currency(hero_hands.net_gain())}")
    print(f"Edge:         {sign}{hero_hands.net_bbs() / len(hero_hands):.2f}bb per hand, "
                        f"{sign}{locale.currency(hero_hands.net_gain() / hero_hands.total_duration() * 3600.)} "
                        f"per hour (in {round(hero_hands.total_duration() / 3600.)} hours)")
    print()

    sess_dates = all_hands.dates(first_hand_per_sess_only=True)
    if len(sess_dates) > 0:
        daterange_str = f"{sess_dates[0]} to {sess_dates[-1]}" if len(sess_dates) > 1 else f"{sess_dates[0]}"
    else:
        daterange_str = "---"

    print(f"-- Player Breakdowns ({all_hands.session_count()} session(s): {daterange_str}) --")
    known_players = all_hands.players()
    known_players.sort(key=lambda pid: all_hands.net_gain(player_id=pid), reverse=True)
    for pid in known_players:
        print(all_hands.summary(player_id=pid))
    print()

    print(f"-- Situational Breakdowns for {const.HERO_ID} --")

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

        "Best 15%": filters.HeroCardFilter("15%"),
        "Best 33%": filters.HeroCardFilter("33%"),
        "Middle 33%": filters.HeroCardFilter("66-33%"),
        "Worst 33%": filters.HeroCardFilter("100-66%"),

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
        "Doesn't get to Showdown": filters.HeroVPIP() & ~filters.HeroSawStreet(actions.SHOWDOWN),

        "All-in Pre-Flop": filters.EveryoneAndHeroAllInBy(actions.PRE_FLOP),
        "All-in Before River": filters.EveryoneAndHeroAllInBy(actions.TURN),
    }

    custom_results = [hero_hands.filter(custom_filters[f], desc=f) for f in custom_filters]
    custom_results.sort(key=lambda x: x.avg_bbs_per_play(), reverse=True)

    for res in custom_results:
        if len(res) > 0:  # skip categories with zero hands
            print(res.summary())
            # if res.desc == "Middle 33%":
            #     for h in res:
            #         print(f"  {h}")
    print()

    print(f"-- Per-Hand Stats for {const.HERO_ID} --")
    my_per_hand_stats: typing.Dict[str, hands.HandGroup] = {}
    for h in hero_hands:
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
