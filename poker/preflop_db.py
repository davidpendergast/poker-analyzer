import typing

import poker.cardutils as cardutils
import const

_DB = {}

# Looks like:
# {
#     'AhKh': {
#         'AdAd': 0.5,
#         'AcKc': 0.5,
#         ...
#     },
#     ...
# }


def load_from_disk():
    global _DB
    with open(const.EQUITY_DB) as f:
        n = 0
        for line in f:
            line = line.rstrip()
            if len(line) == 0:
                continue
            cards1, cards2, eq = line.split(" ")
            eq = float(eq)

            if cards1 not in _DB:
                _DB[cards1] = {}
            _DB[cards1][cards2] = eq
            n += 1
        print(f"INFO: loaded {n} pre-flop hand equities from {const.EQUITY_DB}")


def save_to_disk():
    if _DB is not None:
        with open(const.EQUITY_DB, 'w') as f:
            for cards1 in _DB:
                for cards2 in _DB[cards1]:
                    equity = _DB[cards1][cards2]
                    f.write(f"{cards1} {cards2} {equity:.5f}\n")


def add_line_to_disk(cards1, cards2, equity):
    with open(const.EQUITY_DB, 'a') as f:
        f.write(f"{cards1} {cards2} {equity:.5f}\n")


def get_equity(h1, h2, no_fail=False):
    if len(_DB) == 0:
        load_from_disk()
    orig_h1c1 = h1[0]
    h1, h2, key1, key2 = _normalize(h1, h2)
    if key1 in _DB and key2 in _DB[key1]:
        return _DB[key1][key2] if orig_h1c1 in h1 else 1 - _DB[key1][key2]
    elif no_fail:
        return None
    else:
        raise ValueError(f"Failed to find pre-flop equity for: {h1} vs {h2}")


def get_avg_equity_by_cardcode(cc1, cc2) -> typing.Tuple[float, int]:
    combos1 = cardutils.all_combos_of_card_code(cc1)
    combos2 = cardutils.all_combos_of_card_code(cc2)

    n = 0
    sum1, sum2 = 0, 0

    for h1 in combos1:
        for h2 in combos2:
            if cardutils.are_unique(h1 + h2):
                eq = get_equity(h1, h2)
                sum1 += eq
                sum2 += 1 - eq
                n += 1

    return sum1 / (sum1 + sum2), n


def get_avg_equity_vs_all(cc):
    total_eq = 0
    total_n = 0
    for cc2 in cardutils.all_card_codes():
        eq, n = get_avg_equity_by_cardcode(cc, cc2)
        total_eq += eq * n
        total_n += n
    return total_eq / total_n


def _normalize(h1, h2):
    """
    ('Kh', '9c'), ('Kd', 'Ac') -> ('Ac', 'Kd'), ('Kh', '9c'), 'AaKb', 'Kc9a'
    """
    h1 = cardutils.sort_by_rank(h1)
    h2 = cardutils.sort_by_rank(h2)

    cmp = cardutils.compare_by_ranks(h1, h2)
    if cmp < 0:
        h2, h1 = h1, h2
    elif cmp == 0:
        if h2[0][1] == h2[1][1]:
            h2, h1 = h1, h2  # put self-suited hand first
        elif h2[0][1] == h1[1][1]:
            h2, h1 = h1, h2  # put dominating hand first

    if h2[0][0] == h2[1][0]:
        if h2[1][1] == h1[0][1] or (h2[0][1] != h1[0][1] and h2[1][1] == h1[1][1]):
            h2 = (h2[1], h2[0])  # for pocket pairs, put shared suit first

    suit_mapping = {}
    for c in [h1[0], h1[1], h2[0], h2[1]]:
        if c[1] not in suit_mapping:
            suit_mapping[c[1]] = "abcd"[len(suit_mapping)]

    key1 = f"{h1[0][0]}{suit_mapping[h1[0][1]]}{h1[1][0]}{suit_mapping[h1[1][1]]}"
    key2 = f"{h2[0][0]}{suit_mapping[h2[0][1]]}{h2[1][0]}{suit_mapping[h2[1][1]]}"

    return h1, h2, key1, key2


if __name__ == "__main__":
    all_codes = list(cardutils.all_card_codes())
    avg_equities = {}
    for cc in all_codes:
        total_eq1, total_eq2 = 0, 0
        total_n = 0
        for cc2 in all_codes:
            eq, n = get_avg_equity_by_cardcode(cc, cc2)
            total_eq1 += eq * n
            total_eq2 += (1 - eq) * n
            total_n += n
        avg_equities[cc] = total_eq1 / total_n

    for cc in sorted(all_codes, key=lambda _cc: avg_equities[_cc], reverse=True):
        print(f"{cc:<3} vs All: {avg_equities[cc] * 100:.2f}%")


if __name__ == "__main__" and False:
    cards = ['9s', '9d', '9c', '9h', 'As', 'Ad', 'Ac', 'Ah']
    uniques = {}
    for i0 in range(len(cards)):
        for i1 in range(len(cards)):
            for i2 in range(len(cards)):
                for i3 in range(len(cards)):
                    if len(set((i0, i1, i2, i3))) < 4:
                        continue
                    h1 = (cards[i0], cards[i1])
                    h2 = (cards[i2], cards[i3])
                    h1, h2, key1, key2 = _normalize(h1, h2)
                    key = f"{key1} {key2}"
                    if key not in uniques:
                        uniques[key] = []
                    uniques[key].append((h1, h2))
    for key in uniques:
        print(f"{key}: ({len(uniques[key])}) {uniques[key]}")


if __name__ == "__main__" and False:
    load_from_disk()
    all_cards = list(cardutils.all_cards())
    n_iters = 270725
    n = 0
    last_pcnt = 0

    for i0 in range(len(all_cards)):
        for i1 in range(i0 + 1, len(all_cards)):
            for i2 in range(i1 + 1, len(all_cards)):
                for i3 in range(i2 + 1, len(all_cards)):
                    c1 = all_cards[i0]
                    c2 = all_cards[i1]
                    c3 = all_cards[i2]
                    c4 = all_cards[i3]
                    n += 1

                    combos = [((c1, c2), (c3, c4)),
                              ((c1, c3), (c2, c4)),
                              ((c1, c4), (c2, c3))]

                    for (h1, h2) in combos:
                        h1, h2, key1, key2 = _normalize(h1, h2)
                        if key1 in _DB and key2 in _DB[key1]:
                            continue

                        if key1 not in _DB:
                            _DB[key1] = {}
                        if key2 not in _DB[key1]:
                            _DB[key1][key2] = None

                        h1_eq, h2_eq = cardutils.calc_equities([h1, h2], [], limit=const.EQUITY_CALC_N_ITERS)
                        _DB[key1][key2] = h1_eq
                        add_line_to_disk(key1, key2, h1_eq)

                        pcnt = n / n_iters * 100
                        if int(last_pcnt * 100) < int(pcnt * 100):
                            last_pcnt = pcnt
                            pcnt_done = f"{pcnt:.2f}% DONE"
                            print(f"{pcnt_done} {key1} vs {key2}: {h1_eq * 100.:.5f}%")
