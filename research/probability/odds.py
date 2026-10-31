"""How do we raise the probability of a profitable fortnight / month / year? Measured on the 11-leg book's own trades.

Levers compared (same trades, P&L booked at exit, 1% risk per trade x leg weight):
  costs: lab costs + swaps vs Exness Zero realistic + swaps vs Exness Zero swap-free;
  breadth: each leg alone vs all 11 together;
  time: share of positive fortnights (10 business days), months, quarters and years.
Also the textbook view: with a per-period Sharpe s the chance of a positive period is about Phi(s); it rises with the
square root of time and of the number of independent edges.
Output: research/results/probability/odds.json
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
for p in (R, os.path.join(R, "northstar"), os.path.join(R, "exness")):
    sys.path.insert(0, p)
import core
import ns_portfolio as PF
import rescore_book as RB
from rescore import COST, SWAP

OUT = os.path.join(R, "results", "probability"); os.makedirs(OUT, exist_ok=True)


def leg_frames(cost, swap, w):
    out = []
    for i, (name, sym, x) in enumerate(PF.legs("BOOK")):
        nights = np.array([core.nights_held(int(a), int(b)) for a, b in zip(x["t_in"], x["t_out"])])
        r = x["r"] + COST[sym] / x["dist"] - cost[sym] / x["dist"] - nights * swap[sym] / x["dist"]
        out.append((name, pd.DataFrame(dict(t_out=x["t_out"].astype(np.int64), r=r, w=w[i]))))
    return out


def odds(p):
    res = {}
    for lab, rule in (("fortnight", "2W"), ("month", "ME"), ("quarter", "QE"), ("year", "YE")):
        g = p.resample(rule).sum()
        g = g[g.index >= "2011-02-01"]
        res[lab] = round(float((g > 0).mean()), 3)
    res["worst_month_pct"] = round(float(p.resample("ME").sum().min() * 100), 1)
    return res


def main():
    _, names = PF.build("BOOK"); w = np.array([n["weight"] for n in names])
    profiles = {"lab costs + swaps": (COST, SWAP), "Exness Zero + swaps": (RB.zero_costs(1.0), SWAP),
                "Exness Zero swap-free": (RB.zero_costs(1.0), {k: 0.0 for k in SWAP})}
    out = {}
    for lab, (cost, swap) in profiles.items():
        legs = leg_frames(cost, swap, w)
        allD = pd.concat([d for _, d in legs])
        book = RB.daily(allD, allD["w"].to_numpy())
        single = {}
        for name, d in legs:
            s = RB.daily(d, np.ones(len(d)))                     # one leg alone at full 1% risk
            single[name] = odds(s)
        avg_single = {k: round(float(np.mean([v[k] for v in single.values()])), 3) for k in ("fortnight", "month", "quarter", "year")}
        r = allD["r"].to_numpy()
        out[lab] = dict(book=odds(book), one_leg_average=avg_single, per_trade_mean_R=round(float(r.mean()), 3),
                        per_trade_sd_R=round(float(r.std()), 3), trades=int(len(r)),
                        trades_for_90pct_profit=int(np.ceil((1.2816 * r.std() / r.mean()) ** 2)) if r.mean() > 0 else None)
        print(lab, json.dumps(out[lab]), flush=True)
    json.dump(out, open(os.path.join(OUT, "odds.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
