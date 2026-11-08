"""Main settings (50% entry, stop at the range end, breakeven at 50% of the target, lookback on) at 4R (v1), 2R and 1R
(v2), 12 markets pooled, 2011-19 and 2020-22 (fills before 2023). Win rate next to the win rate each target needs after
costs: about (1 + cost) / (target + 1), cost = average round-trip cost in R for these trades.

    python3 research/body4/compare_targets.py  ->  research/results/body4/v2/TARGETS.md + targets.json
"""
import os, json
import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
R1 = os.path.join(ROOT, "research", "results")
TF = ["M1", "M5", "M15", "M30", "H1", "H4"]
MAIN = dict(entry=0.5, be=1, buffer=0.0, lookback=1)
VARIANTS = ((1, "on"), (0, "off"))


def pooled(study, tf, target, per, be=1):
    want = dict(MAIN, be=be)
    rs = [x for x in study["rows"] if x["tf"] == tf and {k: v for k, v in x["cfg"].items() if k != "target"} == want
          and x["cfg"].get("target", 4) == target]
    n = sum(x[per].get("n", 0) for x in rs)
    tot = sum(x[per].get("total", 0.0) for x in rs)
    win = sum(x[per].get("n", 0) * x[per].get("win", 0.0) for x in rs)
    mk = sum(1 for x in rs if x[per].get("E", -1) > 0)
    return dict(n=n, E=round(tot / n, 3) if n else None, win=round(win / n, 3) if n else None, markets_positive=mk)


def cost_r(grid, tf, target, be=1):
    q = grid[(grid.tf == tf) & (grid.entry == 0.5) & (grid.be == be) & (grid.buffer == 0) & (grid.lookback == 1)]
    if "target" in grid.columns:
        q = q[q.target == target]
    n = sum(q[f"n_{y}"].sum() for y in range(2011, 2020)); c = sum(q[f"c_{y}"].sum() for y in range(2011, 2020))
    return c / n if n else np.nan


def main():
    s1 = json.load(open(os.path.join(R1, "body4", "study.json")))
    s2 = json.load(open(os.path.join(R1, "body4", "v2", "study.json")))
    g1 = json.load(open(os.path.join(R1, "body4", "gross.json")))
    g2 = json.load(open(os.path.join(R1, "body4", "v2", "gross.json")))
    G1 = pd.read_csv(os.path.join(R1, "truth", "body4_range_v1", "grid.csv.gz"))
    G2 = pd.read_csv(os.path.join(R1, "truth", "body4_range_v2", "grid.csv.gz"))
    out = {}
    L = ["# Body-engulf range: 4R vs 2R vs 1R (12 markets pooled)", "",
         "Entry 50%, stop at the range end, lookback on; breakeven at 50% of the target ON (owner's main) and OFF. "
         "2011-19 (2020-22 in brackets). 'Needed' = the win rate that breaks even after costs, about "
         "(1 + cost) / (target + 1); it is exact only with breakeven OFF (every trade is then a full win or a full loss, "
         "apart from Friday closes). With breakeven ON many trades end near 0 (minus commission), so their win rate "
         "looks lower.", ""]
    for be, word in VARIANTS:
        L += [f"## Breakeven {word}", "",
              "| Timeframe | Target | Trades 2011-19 | Win rate | Needed | R per trade after costs | Before costs | Markets positive |",
              "|---|---|---|---|---|---|---|---|"]
        for tf in TF:
            for T, st, gr, G in ((4, s1, g1, G1), (2, s2, g2, G2), (1, s2, g2, G2)):
                a, b = pooled(st, tf, T, "2011-19", be), pooled(st, tf, T, "2020-22", be)
                c = cost_r(G, tf, T, be)
                need = (1 + c) / (T + 1)
                gk = f"{tf} | " + ("" if T == 4 else f"target {T}R | ") + f"entry 50% | be {word} | buffer 0% | lookback on"
                ga, gb = gr[gk]["2011-19"]["E"], gr[gk]["2020-22"]["E"]
                out[f"{tf} {T}R be {word}"] = dict(dev=a, val=b, cost_r=round(float(c), 3), needed=round(float(need), 3), gross=(ga, gb))
                L.append(f"| {tf} | {T}R | {a['n']:,} | {a['win']:.0%} ({b['win']:.0%}) | {need:.0%} | {a['E']:+.2f} ({b['E']:+.2f}) | "
                         f"{ga:+.2f} ({gb:+.2f}) | {a['markets_positive']} of 12 |")
        L.append("")
    d = os.path.join(R1, "body4", "v2")
    json.dump(out, open(os.path.join(d, "targets.json"), "w"), indent=1)
    open(os.path.join(d, "TARGETS.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
