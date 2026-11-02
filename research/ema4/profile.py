"""Descriptive profile of the 4-flip pattern (no selection): one fixed, typical setting per timeframe and grade
(entry at the 4th candle's close, stop 4th candle + 0.25 ATR, 2R target), 12 markets, fills before 2023.

    python3 research/ema4/profile.py      # writes research/results/ema4/profile.json and PROFILE.md

Per timeframe x grade: trades, win rate, R per trade after costs and before costs, cost per trade; for each timeframe also by
market and by hour of the 4th candle's close (UTC+1, the owner's clock). 2011-19 and 2020-22 side by side.
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import protocol as P             # noqa: E402
from grid import year_index      # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "ema4_flip_v1.py"))
BASE = dict(entry="close", stop="c4", buffer=0.25, target=2)
OUT = os.path.join(ROOT, "research", "results", "ema4")


def st(R, c):
    if len(R) < 5:
        return dict(n=int(len(R)))
    return dict(n=int(len(R)), win=round(float((R > 0).mean()), 3), net=round(float(R.mean()), 4), gross=round(float((R + c).mean()), 4),
                cost=round(float(c.mean()), 3), t=round(float(R.mean() / R.std(ddof=1) * np.sqrt(len(R))), 2))


def main():
    res = {}
    mk = {s: P.market(s, S) for s in S.MARKETS}
    for tf in S.TIMEFRAMES:
        for grade in ("A", "AB"):
            p = dict(tf=tf, grade=grade, **BASE); rows = []
            for i, s in enumerate(S.MARKETS):
                B = mk[s].bars(tf); D = S.detail(mk[s], B, p, cut=P.core.CUT)
                if len(D):
                    t4 = S.select(S.setups(B, p, mk[s]), p)["t4"][D[:, 13].astype(int)]
                    rows.append(np.c_[D[:, [0, 3, 5]], np.full(len(D), i), ((t4 + 3600) % 86400) // 3600])
            T = np.vstack(rows); y = year_index(T[:, 0])
            r = {}
            for per, m in (("2011-19", y <= 2019), ("2020-22", (y >= 2020) & (y <= 2022))):
                r[per] = dict(all=st(T[m, 1], T[m, 2]),
                              by_market={s: st(T[m & (T[:, 3] == i), 1], T[m & (T[:, 3] == i), 2]) for i, s in enumerate(S.MARKETS)},
                              by_hour_utc1={int(h): st(T[m & (T[:, 4] == h), 1], T[m & (T[:, 4] == h), 2]) for h in range(24)})
            res[f"{tf} {grade}"] = r
            a, b = r["2011-19"]["all"], r["2020-22"]["all"]
            print(tf, grade, "2011-19", a, "| 2020-22", b, flush=True)
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(note=__doc__, setting=BASE, results=res), open(os.path.join(OUT, "profile.json"), "w"), indent=1)
    f = lambda d, k, fm: fm.format(d[k]) if k in d else "-"
    L = ["# 4-flip pattern: descriptive profile (entry at close, stop 4th candle + 0.25 ATR, 2R; 12 markets)", "",
         "| Timeframe | Grade | 2011-19 trades | Win rate | R/trade | Before costs | Cost/trade | 2020-22 trades | Win rate | R/trade | Before costs |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in res.items():
        a, b = r["2011-19"]["all"], r["2020-22"]["all"]
        L.append(f"| {k.split()[0]} | {'A+' if k.endswith('A') else 'A+ and B+'} | {a['n']} | {f(a, 'win', '{:.0%}')} | {f(a, 'net', '{:+.3f}')} | "
                 f"{f(a, 'gross', '{:+.3f}')} | {f(a, 'cost', '{:.2f}R')} | {b['n']} | {f(b, 'win', '{:.0%}')} | {f(b, 'net', '{:+.3f}')} | {f(b, 'gross', '{:+.3f}')} |")
    open(os.path.join(OUT, "PROFILE.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
