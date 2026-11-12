"""Phase 1 of the deep M1 study: the payout structure (research/sweep6/PREREGISTRATION.md). Phase 1 base = the owner's
current rule (bodies >= 50%, a stop-side sweep by a candle from 6 before candle 1 through candle 2), M1, 12 markets pooled,
frictionless. Same trade set for every structure (filled, every structure resolved). Choice: the best R a trade on LEARN.
    python3 research/sweep6/phase1.py -> research/results/sweep6/phase1.json, PHASE1.md
"""
import os, sys, json, glob, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import sweep6_outcomes as OC   # noqa: E402

DIR = os.environ.get("SWEEP6_DIR", os.path.join(ROOT, "research", "results", "sweep6", "_cells"))
OUT = os.path.join(ROOT, "research", "results", "sweep6")
T = lambda y: int(dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp())
PER = {"LEARN 2011-15": (T(2011), T(2016)), "CONFIRM 2016-19": (T(2016), T(2020)), "VALIDATE 2020-22": (T(2020), T(2023))}
RECENT = sum(1 << d for d in range(2, 10))


def load(base=True):
    rows = []
    for f in sorted(glob.glob(os.path.join(DIR, "*_M1.npz"))):
        z = dict(np.load(f))
        sym = os.path.basename(f).split("_")[0]
        m = (z["o_status"] == 3) & np.all(np.isfinite(z["o_R"]), axis=1)
        if base:
            m &= (z["body_min"] >= 0.5) & ((z["swmask"] & RECENT) > 0)
        rows.append(dict(sym=np.full(m.sum(), sym), t=z["o_tfill"][m], R=z["o_R"][m].astype(float), Ro=z["o_R_opt"][m].astype(float),
                         amb=z["o_amb"][m], tp2R=z["o_tp2R"][m], tp1R=z["o_tp1R"][m]))
    return {k: np.concatenate([r[k] for r in rows]) for k in rows[0]}


def streak(x):
    best = cur = 0
    for v in x:
        cur = cur + 1 if v <= 0 else 0; best = max(best, cur)
    return best


def stats(R):
    n = len(R)
    w, l = R[R > 0], R[R <= 0]
    m = n // 10
    B = R[:m * 10].reshape(m, 10).sum(axis=1) if m else np.zeros(0)
    return dict(n=n, win=round(float((R > 0).mean()), 4), wins_per_10=round(float((R > 0).mean()) * 10, 2),
                avg_win=round(float(w.mean()), 2) if len(w) else None, avg_loss=round(float(l.mean()), 3) if len(l) else None,
                E=round(float(R.mean()), 4), t=round(float(R.mean() / R.std() * np.sqrt(n)), 2) if R.std() > 0 else None,
                R_per_10=round(float(R.mean()) * 10, 2), blocks=m, block_median=round(float(np.median(B)), 2) if m else None,
                block_pos=round(float((B > 0).mean()), 3) if m else None, block_p10=round(float(np.quantile(B, 0.1)), 1) if m else None,
                block_worst=round(float(B.min()), 1) if m else None, longest_losing_streak=streak(R),
                PF=round(float(w.sum() / -l.sum()), 3) if l.sum() < 0 else None)


def main():
    D = load(base=True)
    o = np.argsort(D["t"], kind="stable"); D = {k: v[o] for k, v in D.items()}
    res = dict(prereg="research/sweep6/PREREGISTRATION.md", base="bodies >= 50%, sweep 6 before candle 1 .. candle 2", periods={}, by_market={})
    for pn, (a, b) in PER.items():
        m = (D["t"] >= a) & (D["t"] < b)
        res["periods"][pn] = {}
        for q, name in enumerate(OC.NAMES):
            st = stats(D["R"][m, q])
            st["E_optimistic"] = round(float(D["Ro"][m, q].mean()), 4)
            st["ambiguous_share"] = round(float(D["amb"][m, q].mean()), 4)
            res["periods"][pn][name] = st
        res["periods"][pn]["_tp2_distance_R"] = {str(qq): round(float(np.quantile(D["tp2R"][m], qq)), 2) for qq in (0.1, 0.25, 0.5, 0.75, 0.9)}
        res["periods"][pn]["_tp1_distance_R"] = {str(qq): round(float(np.quantile(D["tp1R"][m], qq)), 2) for qq in (0.1, 0.25, 0.5, 0.75, 0.9)}
    a, b = PER["LEARN 2011-15"]
    for sym in np.unique(D["sym"]):
        m = (D["sym"] == sym) & (D["t"] >= a) & (D["t"] < b)
        res["by_market"][sym] = {name: round(float(D["R"][m, q].mean()), 3) for q, name in enumerate(OC.NAMES)}
    L = res["periods"]["LEARN 2011-15"]
    res["choice"] = max(OC.NAMES, key=lambda nm: L[nm]["E"])
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "phase1.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    for pn, P_ in r["periods"].items():
        print("\n==", pn, "TP2 distance quantiles", P_["_tp2_distance_R"], "TP1", P_["_tp1_distance_R"])
        for nm in OC.NAMES:
            s = P_[nm]
            print(f"{nm:9} n {s['n']:6} win {s['win']:.3f} ({s['wins_per_10']:.2f}/10) avgW {s['avg_win']} avgL {s['avg_loss']} E {s['E']:+.4f} t {s['t']} R/10 {s['R_per_10']:+.2f} blk med {s['block_median']} pos {s['block_pos']} p10 {s['block_p10']} streak {s['longest_losing_streak']} PF {s['PF']} | opt {s['E_optimistic']:+.4f} amb {s['ambiguous_share']}")
    print("\nchoice:", r["choice"])
