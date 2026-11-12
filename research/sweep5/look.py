"""The one logged look for pivot-sweep v2 candidate legs (research/sweep5/PREREGISTRATION.md): the 20 cells that were
positive after costs in each of 2011-14, 2015-18 and 2019-22 (20+ trades each; research/results/sweep5/study.json).
PASS (fixed here, before the look): R a trade after costs above 0 in 2023-25 AND in Jan-Oct 2026 where 2026 data exists
(GBPUSD, EURGBP; WTI and NAS100 have none: 2023-25 only). Passing cells become portfolio legs (v2_legs.pkl) for pareto.py,
one leg per market x timeframe (the cell with the best 2011-22 edge quality among the passing ones), weight set so its R
volatility matches the survivors' average (w x sd, 2011-19).
    python3 research/sweep5/look.py -> research/results/sweep5/LOOK.json (+ v2_legs.pkl)
"""
import os, sys, json, math, pickle, time, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p_ in ("research", "research/truth", "research/body4", "research/goal"):
    sys.path.insert(0, os.path.join(ROOT, p_))
import gold_traits   # noqa: E402,F401  (adds data/holdout/<SYM>_M1_bid_2026.npz to the loader)
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "sweep5_pivot_v2.py"))
OUT = os.path.join(ROOT, "research", "results", "sweep5")
T = lambda y: int(dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp())
PER = {"2011-22": (T(2011), T(2023)), "2023-25": (T(2023), T(2026)), "2026": (T(2026), T(2027))}
WITH_2026 = {"EURUSD", "GBPUSD", "USDJPY", "EURGBP", "XAUUSD", "GER40"}


def st(R):
    if not len(R):
        return dict(n=0)
    w, l = R[R > 0], R[R <= 0]
    d = dict(n=int(len(R)), E=round(float(R.mean()), 3), win=round(float((R > 0).mean()), 3),
             PF=round(float(w.sum() / -l.sum()), 2) if l.sum() < 0 else None)
    if len(R) > 2 and R.std() > 0:
        d["t"] = round(float(R.mean() / R.std() * math.sqrt(len(R))), 2)
    return d


def main():
    path = os.path.join(OUT, "LOOK.json")
    if os.path.exists(path):
        raise SystemExit("the look was already made: " + path)
    cands = json.load(open(os.path.join(OUT, "study.json")))["candidates"]
    rec = dict(prereg="research/sweep5/PREREGISTRATION.md", candidates=cands, started=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    json.dump(rec, open(path, "w"), indent=1)
    res, data = {}, {}
    for c in cands:
        sym, tf, cfg = [x.strip() for x in c.split("|", 2)]
        p = dict(kv.split("=") for kv in cfg.split("|")); p["life"] = int(p["life"]); p["tf"] = tf
        M = P.market(sym, S)
        D = S.detail(M, M.bars(tf), p)
        D = D[np.argsort(D[:, 0], kind="stable")]
        r = {k: st(D[(D[:, 0] >= a) & (D[:, 0] < b), 3]) for k, (a, b) in PER.items()}
        dev = D[D[:, 0] < T(2023), 3]
        r["s_2011_22"] = round(float(dev.mean() / dev.std()), 4)
        ok = r["2023-25"].get("E", -1) > 0 and (sym not in WITH_2026 or r["2026"].get("E", -1) > 0)
        r["passes"] = bool(ok); r["has_2026_data"] = sym in WITH_2026
        res[c] = r; data[c] = D
        print(c, {k: (r[k].get("n"), r[k].get("E")) for k in PER}, "PASS" if ok else "fail", flush=True)
    rec["results"] = res
    passing = [c for c in cands if res[c]["passes"]]
    best = {}
    for c in passing:
        sym, tf = [x.strip() for x in c.split("|")[:2]]
        if (sym, tf) not in best or res[c]["s_2011_22"] > res[best[(sym, tf)]]["s_2011_22"]:
            best[(sym, tf)] = c
    rec["legs"] = list(best.values())
    rec["verdict"] = (f"{len(passing)} of {len(cands)} candidate cells pass; legs: {rec['legs']}" if passing
                      else f"0 of {len(cands)} candidate cells pass: v2 adds no portfolio leg")
    if best:
        sys.path.insert(0, os.path.join(ROOT, "research", "seesare"))
        import daily_queue_study as DQ
        Lb = DQ.legs("zero_swaps")
        target = float(np.mean([g["w"] * g["r"][g["t_in"] < T(2020)].std() for g in Lb]))
        legs = []
        for (sym, tf), c in best.items():
            D = data[c]; old = D[D[:, 0] < T(2026)]; new = D[D[:, 0] >= T(2026)]
            sd = old[old[:, 0] < T(2020), 3].std()
            legs.append(dict(name=f"v2_{sym}_{tf}", market=sym, tf=tf, w=target / sd, t_in=old[:, 0].astype(np.int64),
                             t_out=old[:, 1].astype(np.int64), r=old[:, 3], t_in26=new[:, 0].astype(np.int64),
                             t_out26=new[:, 1].astype(np.int64), r26=new[:, 3], cell=c))
        pickle.dump(legs, open(os.path.join(OUT, "v2_legs.pkl"), "wb"))
    rec["finished"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    json.dump(rec, open(path, "w"), indent=1)
    return rec


if __name__ == "__main__":
    print(main()["verdict"])
