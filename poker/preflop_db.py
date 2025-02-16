
import json
import itertools
import poker.cardutils as cardutils
import const

_DB = {}


def load_from_disk():
    global _DB
    with open(const.EQUITY_DB) as f:
        _DB = json.load(f)


def save_to_disk():
    if _DB is not None:
        with open(const.EQUITY_DB, 'w') as f:
            json.dump(_DB, f)


def get_equities(h_list, board=()):
    pass


if __name__ == "__main__":
    load_from_disk()
    all_cards = list(cardutils.all_cards())
    n_combos = 52 * 51 * 50 * 49 / (2 * 2)
    limit = 10_000
    n = 0
    for i0 in range(len(all_cards)):
        for i1 in range(i0 + 1, len(all_cards)):
            for i2 in range(i1 + 1, len(all_cards)):
                for i3 in range(i2 + 1, len(all_cards)):
                    c1 = all_cards[i0]
                    c2 = all_cards[i1]
                    c3 = all_cards[i2]
                    c4 = all_cards[i3]
                    n += 1

                    h1 = cardutils.sort_by_rank((c1, c2))
                    h2 = cardutils.sort_by_rank((c3, c4))
                    h1_str = "".join(h1)
                    h2_str = "".join(h2)

                    if h1_str not in _DB:
                        _DB[h1_str] = {}
                    if h2_str not in _DB:
                        _DB[h2_str] = {}

                    if h2_str not in _DB[h1_str]:
                        _DB[h1_str][h2_str] = {'equity': None}
                    if h1_str not in _DB[h2_str]:
                        _DB[h2_str][h1_str] = {'equity': None}

                    pcnt_done = f"{n / n_combos * 100:.2f}% DONE"

                    if _DB[h1_str][h2_str]['equity'] is None:
                        h1_eq, h2_eq = cardutils.calc_equities([h1, h2], [], limit=limit)
                        _DB[h1_str][h2_str]['equity'] = h1_eq
                        _DB[h2_str][h1_str]['equity'] = h2_eq
                        print(f"{pcnt_done} {h1_str} vs {h2_str}: {h1_eq * 100.:.2f}% | {h2_eq * 100.:.2f}%")
                        save_to_disk()
                    else:
                        print(f"{pcnt_done} {h1_str} vs {h2_str}: Already Calc'd")

