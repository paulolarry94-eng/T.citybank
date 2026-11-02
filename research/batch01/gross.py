"""Batch 01: each configuration's result before costs and swaps (is there a raw effect at all?).

    python3 research/batch01/gross.py      # writes research/results/batch01/gross.json

Per configuration (all markets pooled, fills before 2023, the lab's cut) and period 2011-19 / 2020-22: trades, net R (after
costs and swaps, as the lab scores it), gross R (cost and swap added back), t of the gross mean, and the mean cost in R.
(Written down 2026-11-02 when the batch was re-run on clock-fixed HistData; the first gross.json came from the same
calculation run inline.)
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import protocol as P          # noqa: E402
from grid import year_index   # noqa: E402
STRATS = ("us_close_flow_v1", "monthend_rebalance_v1")    # as in research/batch01/controls.py

PERIODS = (("2011-19", 0, 2019), ("2020-22", 2020, 2022))


def run():
    out = {}
    for name in STRATS:
        S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", f"{name}.py"))
        acc = {}
        for sym in S.MARKETS:
            M = P.market(sym, S)
            for p in P.param_sets(S):
                key = f"{name} " + json.dumps({k: p[k] for k in S.GRID})
                for tgt, trail, bias in P.mgmt_sets(S):
                    acc.setdefault(key, []).append(P.run_config(S, M, p, tgt, trail, bias))
        for key, parts in acc.items():
            T = np.vstack(parts); y = year_index(T[:, 0]) if len(T) else np.zeros(0)
            row = {}
            for per, a, b in PERIODS:
                m = (y >= a) & (y <= b)
                net = T[m, 3]; gross = T[m, 3] + T[m, 5] + T[m, 7]
                sd = gross.std(ddof=1) if m.sum() > 2 else 0
                row[per] = dict(n=int(m.sum()), net=round(float(net.mean()), 4) if m.any() else None,
                                gross_no_cost_no_swap=round(float(gross.mean()), 4) if m.any() else None,
                                t_gross=round(float(gross.mean() / sd * math.sqrt(m.sum())), 2) if sd > 0 else None,
                                cost_R=round(float(T[m, 5].mean()), 4) if m.any() else None)
            out[key] = row
    os.makedirs(os.path.join(ROOT, "research", "results", "batch01"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "research", "results", "batch01", "gross.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    for k, v in run().items():
        print(k, v)
