"""The owner's "Wealth Game" (2026-11-08): risk 25% of the balance on each 1:4 trade; when the balance reaches 4x the
level's start (two wins in a row: $100 -> $200 -> $400), withdraw half and start the next level with the other half;
12 levels. What happens at realistic win rates?
Each trade wins with probability p (+4R) or loses (-1R); costs in R are taken from both (win +4R - c, loss -1R - c).
100 trades (about a year at 2 a week), 200,000 simulated players per row.
    python3 research/goal/wealth_game.py  ->  research/results/goal/WEALTH_GAME.md
"""
import os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "results", "goal", "WEALTH_GAME.md")


def run(p, risk=0.25, rr=4.0, cost=0.0, n_trades=100, runs=200_000, seed=1):
    rng = np.random.default_rng(seed)
    B = np.full(runs, 100.0); start = B.copy(); wd = np.zeros(runs); lvl = np.ones(runs, int)
    peak = B.copy(); maxdd = np.zeros(runs)
    for _ in range(n_trades):
        win = rng.random(runs) < p
        r = risk * B
        B = np.where(win, B + (rr - cost) * r, B - (1 + cost) * r)
        peak = np.maximum(peak, B); maxdd = np.maximum(maxdd, 1 - B / peak)
        up = B >= 4 * start - 1e-9                        # level done: withdraw half, the rest starts the next level
        wd = np.where(up, wd + B / 2, wd); B = np.where(up, B / 2, B); start = np.where(up, B, start)
        peak = np.where(up, B, peak); lvl = lvl + up
    total = wd + B
    return dict(pass1=float((lvl >= 2).mean()), lvl5=float((lvl >= 5).mean()), finish=float((lvl >= 13).mean()),
                median=float(np.median(total)), below100=float((total < 100).mean()), dd50=float((maxdd >= 0.5).mean()),
                wiped=float(((wd == 0) & (B < 10)).mean()))


def main():
    L = ["# The Wealth Game at 25% risk a trade (owner, 2026-11-08)", "",
         "Rules as given: risk 25% of the balance on a 1:4 trade; at 4x the level's start, withdraw half; 12 levels.",
         "Simulated: 100 trades (about a year at 2 a week), 200,000 players per row. Built by research/goal/wealth_game.py.", "",
         "Arithmetic check: level 1's second target is $400 (200 + 200), not $408; every later number in the plan is 2% too",
         "high (level 12 withdrawal $409,600, not $417,792; all 12 withdrawals $819,000, not $835,380).", "",
         "## 1. Which win rate the plan needs (no costs)", "",
         "| Win rate at 1:4 | Edge a trade | Account growth a trade at 25% risk | Best risk (Kelly) |", "|---|---|---|---|"]
    for p in (0.18, 0.20, 0.25, 0.293, 0.30, 0.40):
        g = p * math.log(2) + (1 - p) * math.log(0.75)
        L.append(f"| {p:.1%} | {5 * p - 1:+.2f}R | {math.expm1(g):+.1%} | {max(0.0, (5 * p - 1) / 4):.1%} |")
    L += ["", "Growth turns positive only above a 29.3% win rate; 25% risk is the best size only at 40% (+1R a trade).",
          "As written (no losses), the 12 levels need 24 wins in a row: 1 in 6e16 at 20%, 1 in 17 million at 50%.", ""]
    for cost in (0.0, 0.2):
        L += [f"## 2. 100 trades at 25% risk, costs {cost}R a trade", "",
              "| Win rate | Pass level 1 (bank $200) | Reach level 5 | Finish level 12 | Median money after 100 trades | End below $100 | Fall of 50%+ at some point |",
              "|---|---|---|---|---|---|---|"]
        for p in (0.18, 0.20, 0.25, 0.30, 0.40):
            r = run(p, cost=cost)
            L.append(f"| {p:.0%} | {r['pass1']:.0%} | {r['lvl5']:.1%} | {r['finish']:.2%} | ${r['median']:,.2f} | {r['below100']:.0%} | {r['dd50']:.0%} |")
        L.append("")
    L += ["## 3. Same edge, smaller risk (win rate 25% at 1:4, costs 0.2R: +0.05R a trade, like our best strategies)", "",
          "| Risk a trade | Pass level 1 within 100 trades | Median money after 100 trades | End below $100 | Lose 90% |", "|---|---|---|---|---|"]
    for risk in (0.25, 0.10, 0.05, 0.02, 0.01):
        r = run(0.25, risk=risk, cost=0.2)
        L.append(f"| {risk:.0%} | {r['pass1']:.1%} | ${r['median']:,.2f} | {r['below100']:.0%} | {r['wiped']:.1%} |")
    L += ["", "Kelly for this edge (mean / variance of R) is about 1% a trade; 25% is about 23 times that."]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write("\n".join(L) + "\n")
    return "\n".join(L)


if __name__ == "__main__":
    print(main())
