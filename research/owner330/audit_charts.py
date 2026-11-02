"""Audit charts: random 3:30 setups from 2011-2022, drawn like the owner's charts, so the owner can check the scanner by eye.

    python3 research/owner330/audit_charts.py      # writes research/results/owner330/audit/*.png and AUDIT.md

The days are drawn at random (fixed seed) from every TRADE the scanner made in 2011-2022 (fills before 2023), for the
owner's own anchor (15:30 Nigerian time) with entry A and a 3R target: 8 markets drawn at random, then one random trade in
each. Not chosen by result: winners and losers appear in the proportion the scanner produced them. The 2023-25 holdout is
not drawn from.
"""
import os, sys, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import replay                      # noqa: E402  (the strategy module S)
import charts                      # noqa: E402
import protocol as P               # noqa: E402

S = replay.S
P_CFG = dict(tf="M5", anchor="wat1530", entry="A", target=3, be=0)
N, SEED = 8, 330
OUT = os.path.join(ROOT, "research", "results", "owner330", "audit")
END = dt.date(2022, 12, 31).toordinal()


def main():
    os.makedirs(OUT, exist_ok=True)
    pool = {}
    for sym in S.MARKETS:
        M = P.market(sym, S); B = M.bars("M5")
        S._CACHE.clear()
        D = S.detail(M, B, P_CFG, cut=P.core.CUT)
        pool[sym] = sorted({dt.datetime.fromtimestamp(int(t), dt.timezone.utc).astimezone(S.NY).date().toordinal() for t in D[:, 0]})
    rng = np.random.default_rng(SEED)
    mk = sorted(rng.choice(sorted(pool), size=N, replace=False))
    pick = [(m, int(pool[m][rng.integers(len(pool[m]))])) for m in mk]
    n_all = sum(len(v) for v in pool.values())
    lines = ["# Audit charts: random 3:30 setups, 2011-2022", "",
             f"{N} trades drawn at random (seed {SEED}; 8 of the 12 markets, one trade each) from the {n_all} trades the scanner made in 2011-2022 "
             "(anchor 15:30 Nigerian time, entry A, 3R target, breakeven off). Times on the charts are Nigerian time (WAT). "
             "Top: M30 with the 10 EMA and the anchor candle's range. Bottom: M5 with the 10 EMA, the reference candle (black box) "
             "and the trade. Please check: is each one a setup you would have taken, with the same reference, entry and stop?", "",
             "| # | Market | Day | Chart |", "|---|---|---|---|"]
    for i, (sym, d) in enumerate(pick, 1):
        D = dt.date.fromordinal(d)
        M = P.market(sym, S)
        S._CACHE.clear()
        f = f"audit_{i:02d}_{sym}_{D}.png"
        charts.day_chart(M, D, P_CFG, S, os.path.join(OUT, f), note="random audit day (not chosen by result)")
        lines.append(f"| {i} | {sym} | {D} | `audit/{f}` |")
        print(i, sym, D, flush=True)
    open(os.path.join(ROOT, "research", "results", "owner330", "AUDIT.md"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
