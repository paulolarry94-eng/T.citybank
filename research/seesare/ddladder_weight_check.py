"""Drawdown-keyed ladder: what the router can trade today, and a "maximised" Tokyo weight (owner, 2026-11-01).
Fixed before any result of this check.

Rule throughout: the drawdown-keyed ladder exactly as it goes into CycleLedger.mqh: 16 levels of 0.225% (2.25 USD on the
$1,000 baseline), level = floor(drawdown / 0.225%), risk = 0.30 x weight x (3.6% - (level+1) x 0.225%), pre-trade guard,
lifecycle = 360 real trades then reset, stopped lifecycles counted (research/seesare/universe_lifecycle_study.py).
Costs: Exness Zero + swaps (primary) and lab costs + swaps (higher-cost proxy; ProCent USDJPY is 1.9 pips, lab 1.35).
Checks (none selected; all reported; 2011-22 and 2023-25 reported separately; both periods were already seen for these legs,
so this is descriptive, not a holdout):
  A  Tokyo fix alone, weight 1.00 (the only module the SEESARE router can trade live today)
  B  book + Tokyo fix + EURUSD reversal with the Tokyo weight at 0.5732 (the book's inverse-volatility rule), 1.00 (the
     largest weight any leg has: the "maximised" weight the code will allow) and 2.00 (beyond anything tested)
Output: research/results/seesare/ddladder_weight_check.json
"""
import os
import sys
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import universe_cap_study as U        # noqa: E402
import universe_lifecycle_study as L  # noqa: E402

M = 0.30


def merge(legs):
    t_in = np.concatenate([g["t_in"] for g in legs]); t_out = np.concatenate([g["t_out"] for g in legs])
    r = np.concatenate([g["r"] for g in legs]); w = np.concatenate([np.full(len(g["r"]), g["w"]) for g in legs])
    leg = np.concatenate([np.full(len(g["r"]), i) for i, g in enumerate(legs)])
    o = np.lexsort((leg, t_in))
    return dict(t_in=t_in[o], t_out=np.maximum(t_out[o], t_in[o]), r=r[o], w=w[o])


def universe(profile, tokyo_w, tokyo_only=False):
    book, max_iv = U.book_legs(profile)
    tokyo = U.lab_leg("tokyo_fix_gotobi_v1", "USDJPY", profile, max_iv)
    tokyo["w"] = tokyo_w
    if tokyo_only:
        return merge([tokyo])
    eur = U.lab_leg("eurusd_close_beyond_reversal_v1", "EURUSD", profile, max_iv)
    return merge(book + [tokyo, eur])


def run(T):
    out = {}
    for name, a, b in (("2011-22", 0, U.Y23), ("2023-25", U.Y23, U.JAN26)):
        W = U.window(T, a, b)
        sc = L.score(L.simulate(W, "DDLADDER", M))
        sc["trades_per_year"] = round(len(W["r"]) / (12 if name == "2011-22" else 3), 1)
        sc.pop("each", None)
        out[name] = sc
    return out


if __name__ == "__main__":
    res = {}
    for pf in ("zero_swaps", "lab_swaps"):
        res[f"A_tokyo_only_w1.00/{pf}"] = run(universe(pf, 1.0, tokyo_only=True))
        for w in (0.5732, 1.0, 2.0):
            res[f"B_universe_tokyo_w{w}/{pf}"] = run(universe(pf, w))
    os.makedirs(U.OUT, exist_ok=True)
    with open(os.path.join(U.OUT, "ddladder_weight_check.json"), "w") as f:
        json.dump(dict(design=__doc__, results=res), f, indent=1, default=float)
    for k, v in res.items():
        for era, s in v.items():
            print(f"{k:38s} {era}: {s['completed']}c+{s['stopped']}s mean/life {s.get('mean_ret_pct')}% median {s.get('median_ret_pct')}% "
                  f"worst {s.get('worst_ret_pct')}% dd {s['worst_dd_pct']}% days/life {s.get('mean_days')} trades/yr {s['trades_per_year']} "
                  f"partial {[(p['taken'], p['ret_pct'], p['dd_pct']) for p in s['partial']]}")
