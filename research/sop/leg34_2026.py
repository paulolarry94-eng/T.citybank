"""Leg 34 on gold, the final check: 2026 Exness Zero prices (data/holdout/), split as fixed BEFORE running (2026-10-31):
  - January-September 2026: untouched (no test, calibration or owner screenshot comes from these months);
  - October 2026: the month of the owner's screenshots (in-sample for the owner's eye), reported separately.
Runs, with the lab's own fills, costs, swaps and exits:
  1. the configuration the lab selected (if any);
  2. the owner's own configuration, for information: swing 3, perfect or slow engulfing, all hours, both stop
     buffers, every exit (t3, t4, t3be, t4be, ladder, ema). Also shown on 2011-19 / 2020-22 / 2023-25 for context
     (descriptive only: nothing is selected from these rows).
Output: research/results/sop/leg34_2026.json
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
for p in (R, os.path.join(R, "northstar"), os.path.join(R, "truth"), os.path.join(R, "truth", "strategies")):
    sys.path.insert(0, p)
import engine as E
import protocol as P

JAN26, OCT26 = 1767225600, 1790812800                       # 2026-01-01, 2026-10-01 00:00 UTC
HOLD = os.path.join(R, "..", "data", "holdout")
_orig = E.load_m1


def load_2026(sym, y0=2011, y1=2025):
    d = np.load(os.path.join(HOLD, f"{sym}_M1_bid_2026.npz"))
    ts = (d["ts"] // 1000).astype(np.int64)
    return ts, d["o"].astype(float), d["h"].astype(float), d["l"].astype(float), d["c"].astype(float)


def stats(r):
    r = np.asarray(r, float)
    if len(r) == 0:
        return dict(n=0)
    pf = r[r > 0].sum() / max(1e-9, -r[r < 0].sum())
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 and r.std() > 0 else None
    return dict(n=int(len(r)), E=round(float(r.mean()), 3), t=round(float(t), 2) if t is not None else None,
                PF=round(float(pf), 2), win=round(float((r > 0).mean()), 3), sum_R=round(float(r.sum()), 1))


def run(S, p, sym, y2026):
    if y2026:
        E.load_m1 = load_2026
    try:
        M = P.market(sym, S)
        tr = P.run_config(S, M, p, 0.0, 0.0, 0, cut=0)
    finally:
        E.load_m1 = _orig
    return tr


def split(tr, y2026):
    if not len(tr):
        return {}
    t, r = tr[:, 0], tr[:, 3]
    if y2026:
        return {"Jan-Sep 2026 (untouched)": stats(r[(t >= JAN26) & (t < OCT26)]), "Oct 2026 (owner's month)": stats(r[t >= OCT26])}
    yr = np.asarray(pd.to_datetime(t.astype(np.int64), unit="s").year)
    return {"2011-19": stats(r[yr <= 2019]), "2020-22": stats(r[(yr >= 2020) & (yr <= 2022)]), "2023-25": stats(r[yr >= 2023])}


def main():
    S = P.load_strategy(os.path.join(R, "truth", "strategies", "leg34_gold_v1.py"))
    out = {}
    summ = os.path.join(R, "results", "truth", S.NAME, "summary.json")
    cand = (json.load(open(summ)).get("selection") or {}).get("candidate") if os.path.exists(summ) else None
    if cand:
        p = {k: v for k, v in cand.items() if k not in ("tgt", "trail", "bias")}
        out["lab_candidate"] = dict(config=p, **split(run(S, p, "XAUUSD", True), True))
    rows = []
    for buf in S.GRID["buffer"]:
        for ex in S.GRID["exit"]:
            p = dict(tf="M5", k=3, engulf="any", window="all", buffer=buf, exit=ex)
            row = dict(config=p, **split(run(S, p, "XAUUSD", False), False), **split(run(S, p, "XAUUSD", True), True))
            rows.append(row)
            print(buf, ex, {k: (v.get("n"), v.get("E")) for k, v in row.items() if k != "config"}, flush=True)
    out["owner_config"] = rows
    os.makedirs(os.path.join(R, "results", "sop"), exist_ok=True)
    json.dump(out, open(os.path.join(R, "results", "sop", "leg34_2026.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
