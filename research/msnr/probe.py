"""Robustness of the gold failed-engulfing-at-level finding: neighbours in every dimension."""
import os, sys, json, itertools, datetime as dt
import numpy as np
sys.path.insert(0, "..")
import msnr_lab as M, gold_search as GS


def j(tr, gy):
    v = GS.judge(tr, gy)
    if not v:
        return "n<30"
    R = v["regimes"]
    lo = tr["r"][tr["side"] > 0]; sh = tr["r"][tr["side"] < 0]
    return (f"{v['per_yr']:5.1f}/yr E {v['E']:+.3f} IS {v['E_is']:+.3f} OOS {v['E_oos']:+.3f} t {v['t']:+.2f} | eras "
            f"{R['bear_2011_15']:+.2f}/{R['range_2016_18']:+.2f}/{R['bull_2019_25']:+.2f} | long {lo.mean() if len(lo) else 0:+.2f} ({len(lo)}) short {sh.mean() if len(sh) else 0:+.2f} ({len(sh)})")


if __name__ == "__main__":
    L = M.Lab("XAUUSD")
    base = L.run("M15", 3, "failed", 3.0, story=True, htf="H1")
    print("BASE gold M15<H1 k3 failed tp3 story:", j(base, 0.53))
    y = np.array([dt.datetime.utcfromtimestamp(int(t)).year for t in base["t_in"]])
    print("  per year: " + " ".join(f"{q % 100:02d}:{base['r'][y == q].mean():+.2f}({(y == q).sum()})" for q in range(2011, 2026) if (y == q).any()))
    print("  win rate", round(float((base['r'] > 0).mean()), 3), "avg hold h", round(float(((base['t_out'] - base['t_in']) / 3600).mean()), 1))
    print("\npivot depth k (story, tp3):")
    for k in (1, 2, 3, 4, 5):
        print(f"  k{k}: ", j(L.run("M15", k, "failed", 3.0, story=True, htf="H1"), 0.53))
    print("\ntimeframe pairs (k3, story, tp3):")
    for tf, htf in (("M15", "H1"), ("M30", "H1"), ("M15", "H4"), ("M30", "H4"), ("H1", "H4"), ("M15", None), ("M30", None), ("H1", None), ("H1", "D1")):
        print(f"  {tf}<{htf}: ", j(L.run(tf, 3, "failed", 3.0, story=True, htf=htf), 0.53))
    print("\ntargets (M15<H1 k3 story):")
    for tg in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0):
        print(f"  tp{tg}: ", j(L.run("M15", 3, "failed", tg, story=True, htf="H1"), 0.53))
    print("\nother markets, same rule (M15<H1 k3 failed story tp3):")
    for sym in ("EURUSD", "GBPUSD", "USDJPY"):
        print(f"  {sym}: ", j(M.Lab(sym).run("M15", 3, "failed", 3.0, story=True, htf="H1"), 0.0))
