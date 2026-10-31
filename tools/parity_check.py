"""Parity: does the MT5 implementation trade like the research?

    python3 tools/parity_check.py RESEARCH.csv EA.csv [--tf-minutes 240] [--from 2023-01-01] [--market XAUUSD]

RESEARCH.csv: a lab parity list (results/truth/<NAME>/parity_trades.csv: t_in, side, r, market) or a North Star
parity list (t_in_utc, side, r_after_costs). EA.csv: the TruthEA / governor log (t_in_utc, side, r).
A research trade is matched by an EA trade on the same side whose entry is within one signal bar.
PASS when >= 95% of research trades are matched and the median |R difference| of matched trades <= 0.10.
"""
import sys, argparse
import numpy as np
import pandas as pd


def load(path, market=None):
    d = pd.read_csv(path)
    if market and "market" in d:
        d = d[d.market == market]
    t = pd.to_datetime(d["t_in_utc"] if "t_in_utc" in d else d["t_in"])
    r = d["r"] if "r" in d else d["r_after_costs"]
    return pd.DataFrame(dict(t=t, side=d["side"].astype(int), r=r.astype(float))).sort_values("t").reset_index(drop=True)


def check(res, ea, tf_minutes):
    tol = pd.Timedelta(minutes=tf_minutes)
    used = np.zeros(len(ea), bool); matched = []
    for _, x in res.iterrows():
        cand = ea[(ea.side == x.side) & ((ea.t - x.t).abs() <= tol) & ~used]
        if len(cand):
            j = (cand.t - x.t).abs().idxmin(); used[j] = True; matched.append((x.r, ea.r[j]))
    m = len(matched); share = m / len(res) if len(res) else 0.0
    dr = np.abs(np.array([a - b for a, b in matched])) if m else np.array([np.nan])
    return dict(research=len(res), ea=len(ea), matched=m, share=share, extra_ea_trades=int((~used).sum()),
                median_abs_dR=float(np.nanmedian(dr)), passed=bool(share >= 0.95 and np.nanmedian(dr) <= 0.10))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("research"); ap.add_argument("ea"); ap.add_argument("--tf-minutes", type=int, default=240)
    ap.add_argument("--from", dest="start"); ap.add_argument("--market")
    a = ap.parse_args()
    R, X = load(a.research, a.market), load(a.ea)
    if a.start:
        R, X = R[R.t >= a.start], X[X.t >= a.start]
    lo, hi = X.t.min(), X.t.max()
    R = R[(R.t >= lo - pd.Timedelta(days=1)) & (R.t <= hi + pd.Timedelta(days=1))]
    out = check(R.reset_index(drop=True), X.reset_index(drop=True), a.tf_minutes)
    print(out)
    sys.exit(0 if out["passed"] else 1)
