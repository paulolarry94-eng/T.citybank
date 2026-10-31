"""The clean final check for the owner's 4-leg SOP: February-October 2026 (Exness Zero ticks -> M1, data/holdout/).
No test, calibration or case study has touched these months (the case studies end on 30 January 2026).

Runs, with the lab's own execution (limit fills at the real spread, costs, swaps, breakeven executor):
  1. the configuration the lab selected (if any) for each strategy;
  2. the owner's own configuration, for information: swing 3, perfect or slow engulfing, the owner's window,
     retest within 10 candles, with and without breakeven, on every timeframe.
Output: research/results/sop/holdout_2026.json
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
for p in (R, os.path.join(R, "northstar"), os.path.join(R, "truth"), os.path.join(R, "truth", "strategies")):
    sys.path.insert(0, p)
import engine as E
import protocol as P

FEB = 1769904000                                             # 2026-02-01 00:00 UTC
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
                PF=round(float(pf), 2), win=round(float((r > 0).mean()), 3))


def run(S, p, sym):
    E.load_m1 = load_2026
    try:
        M = P.market(sym, S)
        tr = P.run_config(S, M, p, 2.0, 0.0, 0, cut=0)
    finally:
        E.load_m1 = _orig
    return tr[tr[:, 0] >= FEB][:, 3] if len(tr) else np.zeros(0)


def main():
    out = {}
    for name in ("sop_4leg_v1", "sop_4leg_gold_v1"):
        S = P.load_strategy(os.path.join(R, "truth", "strategies", f"{name}.py"))
        summ = os.path.join(R, "results", "truth", name, "summary.json")
        res = {}
        cand = None
        if os.path.exists(summ):
            sj = json.load(open(summ))
            cand = (sj.get("selection") or {}).get("candidate")
        if cand:
            p = {k: v for k, v in cand.items() if k not in ("tgt", "trail", "bias")}
            res["lab_candidate"] = dict(config=p, **{m: stats(run(S, p, m)) for m in S.MARKETS if os.path.exists(os.path.join(HOLD, f"{m}_M1_bid_2026.npz"))})
        owner = []
        for tf in S.TIMEFRAMES:
            for be in (0, 1):
                p = dict(tf=tf, k=3, engulf="any", window="owner" if "owner" in S.GRID["window"] else "all",
                         valid=10 if 10 in S.GRID["valid"] else S.GRID["valid"][0], be=be)
                row = dict(config=p)
                allr = []
                for m in S.MARKETS:
                    if not os.path.exists(os.path.join(HOLD, f"{m}_M1_bid_2026.npz")):
                        continue
                    r = run(S, p, m); row[m] = stats(r); allr += list(r)
                row["pooled"] = stats(allr)
                owner.append(row)
                print(name, p, row["pooled"], flush=True)
        res["owner_config"] = owner
        out[name] = res
    os.makedirs(os.path.join(R, "results", "sop"), exist_ok=True)
    json.dump(out, open(os.path.join(R, "results", "sop", "holdout_2026.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
