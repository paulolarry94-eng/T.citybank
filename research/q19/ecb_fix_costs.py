"""Q19 companion (declared in ecb_fix_eurusd_v1.py before the run): the same lab trades of all 4 configurations at other
cost levels, descriptive only (no selection). Periods 2011-19 and 2020-22 only: the lab rejected the rule at the development
gate, so the 2023-25 holdout was never opened and stays unopened here.
Cost levels (EURUSD round trip): gross 0; RoboForex Prime 0.55 pip (published, the lab's run); Exness Zero realistic 0.95 pip;
lab standard 1.5 pips. Output: research/results/q19/ecb_fix_costs.json
"""
import os, sys, json
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import protocol as P   # noqa: E402
from grid import year_index   # noqa: E402

LEVELS = {"gross": 0.0, "roboforex_prime": 5.5e-05, "exness_zero": 9.5e-05, "lab_standard": 1.5e-04}
PIP = 1e-4

if __name__ == "__main__":
    S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "ecb_fix_eurusd_v1.py"))
    M = P.market("EURUSD", S)
    out = dict(design=__doc__, configs={})
    for p in P.param_sets(S):
        tr = P.run_config(S, M, p, 0.0, 0.0, 0)                      # fills before 2023 (the lab's cut)
        y = year_index(tr[:, 0]); d = tr[:, 4]
        gross_r = tr[:, 3] + tr[:, 5] + tr[:, 7]
        key = f"{p['trade']}/{p['days']}"; out["configs"][key] = {}
        for per, m in (("2011-19", y <= 2019), ("2020-22", (y >= 2020) & (y <= 2022))):
            row = dict(n=int(m.sum()))
            for name, c in LEVELS.items():
                pips = (gross_r[m] * d[m] - c) / PIP
                row[name] = dict(pips=round(float(pips.mean()), 3), t=round(float(pips.mean() / pips.std(ddof=1) * np.sqrt(len(pips))), 2),
                                 win=round(float((pips > 0).mean()), 3))
            row["avg_abs_move_pips"] = round(float(np.abs(gross_r[m] * d[m]).mean() / PIP), 2)
            out["configs"][key][per] = row
            print(f"{key:16s} {per} n {row['n']:4d} |move| {row['avg_abs_move_pips']:5.2f} pips | " +
                  " | ".join(f"{k} {v['pips']:+.3f} (t {v['t']:+.2f}, win {v['win']:.0%})" for k, v in row.items() if isinstance(v, dict)))
    os.makedirs(os.path.join(ROOT, "research", "results", "q19"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "research", "results", "q19", "ecb_fix_costs.json"), "w"), indent=1)
