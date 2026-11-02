"""Where did the 2026 profit come from? The 3:30 trades split by US daylight-saving season.

    python3 research/owner330/season_split.py      # writes research/results/owner330/season_split.json

15:30 Nigerian time (WAT) = 14:30 UTC = 09:30 New York in US winter time but 10:30 New York in US summer time (mid-March to
early November). So the owner's anchor (wat1530) and the New York open anchor (ny0930) are the SAME candle in winter and an
hour apart in summer. For both anchors, entries A and B3, 3R target, no breakeven: trades in 2011-2022 (lab data, fills
before 2023; the 2023-25 holdout is not opened) and Jan-Oct 2026 (the five markets with 2026 data, Exness ticks + HistData
EURGBP), split by season at the entry time. Net R after RoboForex Prime published costs; gross = before costs.
"""
import os, sys, json, datetime as dt
import numpy as np
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import check_2026 as C            # noqa: E402
import protocol as P              # noqa: E402
from grid import year_index       # noqa: E402

S = C.S
NY = ZoneInfo("America/New_York")
CFGS = [dict(tf="M5", anchor=a, entry=e, target=3, be=0) for a in ("wat1530", "ny0930") for e in ("A", "B3")]
OUT = os.path.join(ROOT, "research", "results", "owner330")


def summer(t):
    return np.array([1 if dt.datetime.fromtimestamp(int(x), NY).dst() else 0 for x in t], int)


def stats(R, c):
    if len(R) < 3:
        return dict(n=int(len(R)))
    sd = R.std(ddof=1)
    return dict(n=int(len(R)), net_R=round(float(R.mean()), 4), gross_R=round(float((R + c).mean()), 4),
                t=round(float(R.mean() / sd * np.sqrt(len(R))), 2), s=round(float(R.mean() / sd), 4))


def main():
    m26 = {s: C.replay.Market2026(s, S.COSTS[s]) for s in C.MKTS}
    acc = {}
    for sym in S.MARKETS:
        M = P.market(sym, S); B = M.bars("M5")
        for p in CFGS:
            name = f"{p['anchor']}/{p['entry']}/3R"
            S._CACHE.clear()
            D = S.detail(M, B, p, cut=P.core.CUT)
            D = D[year_index(D[:, 0]) <= 2022] if len(D) else D
            acc.setdefault(("2011-22", "12 markets", name), []).append(np.c_[D[:, [3, 5]], summer(D[:, 0])])
            if sym in m26:
                acc.setdefault(("2011-22", "5 markets", name), []).append(np.c_[D[:, [3, 5]], summer(D[:, 0])])
                S._CACHE.clear()
                E = S.detail(m26[sym], m26[sym].bars("M5"), p); E = E[E[:, 0] >= C.T2026]
                acc.setdefault(("2026", "5 markets", name), []).append(np.c_[E[:, [3, 5]], summer(E[:, 0])])
    out = []
    for (per, mk, name), parts in sorted(acc.items()):
        T = np.vstack(parts)
        for season, m in (("winter (anchors identical)", T[:, 2] == 0), ("summer (wat1530 = 10:30 New York)", T[:, 2] == 1)):
            out.append(dict(period=per, markets=mk, config=name, season=season, **stats(T[m, 0], T[m, 1])))
            print(per, mk, name, season, out[-1], flush=True)
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(note=__doc__, rows=out), open(os.path.join(OUT, "season_split.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
