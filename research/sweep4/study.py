"""Pivot-sweep body-engulf range: the cycle-centric study (pre-registered: research/sweep4/PREREGISTRATION.md).
Every market x timeframe x configuration, plus the no-sweep control ("none": the same 60%-body patterns with no sweep near),
2011-19 and 2020-22 only (trades entered before 2023; 2023-25 and 2026 are not opened here).
    python3 research/sweep4/study.py  ->  research/results/sweep4/study.json
"""
import os, sys, json, math, itertools, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "sweep4_pivot_v1.py"))
OUT = os.path.join(ROOT, "research", "results", "sweep4")
UTC = dt.timezone.utc
ts_ = lambda y: int(dt.datetime(y, 1, 1, tzinfo=UTC).timestamp())
PERIODS = {"2011-19": (ts_(2011), ts_(2020)), "2020-22": (ts_(2020), ts_(2023))}
CUT = ts_(2023)
GRID = dict(S.GRID, sweep=["c12", "near", "none"])
NAMES = list(GRID)
CFGS = [dict(zip(NAMES, v)) for v in itertools.product(*GRID.values())]


def ck(c):
    return "|".join(f"{k}={c[k]}" for k in NAMES)


def cycles(R, size=10):
    m = len(R) // size
    if m == 0:
        return dict(cycles=0)
    C = R[:m * size].reshape(m, size).sum(axis=1)
    return dict(cycles=m, pos=round(float((C > 0).mean()), 3), mean=round(float(C.mean()), 2),
                hit4R=round(float((C >= 4).mean()), 3), worst=round(float(C.min()), 1))


def stats(R, why=None):
    n = len(R)
    if n < 3:
        return dict(n=n, E=round(float(R.mean()), 3) if n else None)
    E = float(R.mean()); sd = float(R.std())
    d = dict(n=n, E=round(E, 4), s=round(E / sd, 4) if sd > 0 else None, t=round(E / sd * math.sqrt(n), 2) if sd > 0 else None,
             win=round(float((R > 0).mean()), 3))
    if why is not None:
        d["target_hit"] = round(float((why == 2).mean()), 3)
    d.update({"c10_" + k: v for k, v in cycles(R).items()})
    return d


def worker(sym):
    M = P.market(sym, S)
    sp = S.SPLIT[sym]
    out = {}
    for tf in S.TIMEFRAMES:
        B = M.bars(tf)
        for c in CFGS:
            D = S.detail(M, B, dict(c, tf=tf), cut=CUT)
            o = np.argsort(D[:, 0], kind="stable"); D = D[o]
            why = D[:, 9].astype(np.int8); R0 = D[:, 4]
            slip = np.where(np.isin(why, [1, 3, 4, 5]), sp["slippage"] / R0, 0.0)
            zero = D[:, 3] + slip + (sp["spread"] + sp["commission"]) / R0 + D[:, 7]
            out[(sym, tf, ck(c))] = dict(t_in=D[:, 0].astype(np.int64), t_out=D[:, 1].astype(np.int64), why=why,
                                         R=D[:, 3].astype(np.float32), Z=zero.astype(np.float32), mfe=D[:, 16].astype(np.float32))
    print(sym, flush=True)
    return out


def sel(p, per):
    lo, hi = PERIODS[per]
    m = (p["t_in"] >= lo) & (p["t_in"] < hi)
    return {k: v[m] for k, v in p.items()}


def merged(parts):
    if not parts:
        return dict(t_in=np.zeros(0, np.int64), R=np.zeros(0), Z=np.zeros(0), why=np.zeros(0, np.int8))
    t = np.concatenate([p["t_in"] for p in parts]); o = np.argsort(t, kind="stable")
    return {k: np.concatenate([p[k] for p in parts])[o] for k in ("t_in", "R", "Z", "why")}


def main():
    from multiprocessing import Pool
    legs = {}
    with Pool(4) as pool:
        for o in pool.imap_unordered(worker, S.MARKETS):
            legs.update(o)
    res = dict(prereg="research/sweep4/PREREGISTRATION.md", configurations=len(CFGS), cells=len(legs), pooled={}, cells_top={},
               sweep_vs_none={}, stop_styles={}, timeframes={})
    # pooled over markets: configuration x timeframe
    for c in CFGS:
        for tf in S.TIMEFRAMES:
            parts = [v for (sym, t2, k), v in legs.items() if t2 == tf and k == ck(c)]
            res["pooled"][f"{tf} | {ck(c)}"] = {per: dict(cost=stats(merged([sel(p, per) for p in parts])["R"],
                                                                     merged([sel(p, per) for p in parts])["why"]),
                                                         zero=stats(merged([sel(p, per) for p in parts])["Z"]))
                                                for per in PERIODS}
    PO = res["pooled"]
    # sweep vs the no-sweep control (same timeframe, pivot N, stop, target)
    for sw in ("c12", "near"):
        for per in PERIODS:
            better = tot = 0; dE = []; dZ = []
            for c in CFGS:
                if c["sweep"] != sw:
                    continue
                for tf in S.TIMEFRAMES:
                    a = PO[f"{tf} | {ck(c)}"][per]; b = PO[f"{tf} | {ck(dict(c, sweep='none'))}"][per]
                    if a["cost"].get("n", 0) >= 30 and b["cost"].get("n", 0) >= 30:
                        tot += 1; better += a["cost"]["E"] > b["cost"]["E"]
                        dE.append(a["cost"]["E"] - b["cost"]["E"]); dZ.append(a["zero"]["E"] - b["zero"]["E"])
            res["sweep_vs_none"][f"{sw} | {per}"] = dict(pairs=tot, sweep_better=round(better / tot, 3) if tot else None,
                                                        mean_R_diff=round(float(np.mean(dE)), 4) if dE else None,
                                                        mean_R_diff_zero_cost=round(float(np.mean(dZ)), 4) if dZ else None)
    # stop styles and timeframes (median over the other settings, c12 and near)
    for per in PERIODS:
        for st in GRID["stop"]:
            v = [PO[f"{tf} | {ck(c)}"][per]["cost"] for c in CFGS for tf in S.TIMEFRAMES if c["stop"] == st and c["sweep"] != "none"]
            v = [x for x in v if x.get("n", 0) >= 30]
            res["stop_styles"][f"{st} | {per}"] = dict(cells=len(v), median_E=round(float(np.median([x["E"] for x in v])), 3) if v else None,
                                                       positive=round(float(np.mean([x["E"] > 0 for x in v])), 3) if v else None)
        for tf in S.TIMEFRAMES:
            for sw in ("c12", "near", "none"):
                v = [PO[f"{tf} | {ck(c)}"][per] for c in CFGS if c["sweep"] == sw]
                v = [x for x in v if x["cost"].get("n", 0) >= 30]
                res["timeframes"][f"{tf} | {sw} | {per}"] = dict(
                    cells=len(v), trades_median=int(np.median([x["cost"]["n"] for x in v])) if v else 0,
                    median_E=round(float(np.median([x["cost"]["E"] for x in v])), 3) if v else None,
                    median_E_zero=round(float(np.median([x["zero"]["E"] for x in v])), 3) if v else None,
                    best_E=round(float(max(x["cost"]["E"] for x in v)), 3) if v else None,
                    positive=round(float(np.mean([x["cost"]["E"] > 0 for x in v])), 3) if v else None)
    # best market x timeframe x configuration cells chosen on 2011-19, then 2020-22 unchanged
    cand = []
    for (sym, tf, k), v in legs.items():
        if "sweep=none" in k:
            continue
        a = sel(v, "2011-19")
        if len(a["R"]) >= 60 and a["R"].std() > 0:
            cand.append((float(a["R"].mean() / a["R"].std()), sym, tf, k))
    cand.sort(reverse=True)
    res["cells_considered"] = len(cand)
    res["cells_positive_2011_19"] = int(sum(x[0] > 0 for x in cand))
    top = []
    for s_, sym, tf, k in cand[:10]:
        v = legs[(sym, tf, k)]
        top.append(dict(cell=f"{sym} {tf} | {k}", **{per: stats(sel(v, per)["R"], sel(v, per)["why"]) for per in PERIODS}))
    res["cells_top"] = top
    later = [x for x in cand if x[0] > 0]
    res["positive_2011_19_then_2020_22"] = dict(
        cells=len(later),
        positive_later=int(sum(float(sel(legs[(sym, tf, k)], "2020-22")["R"].mean()) > 0 for _, sym, tf, k in later
                               if len(sel(legs[(sym, tf, k)], "2020-22")["R"]))))
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "study.json"), "w"), indent=1, default=float)
    import pickle
    pickle.dump(legs, open(os.environ.get("SWEEP4_PKL", os.path.join(OUT, "_legs.pkl")), "wb"))
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(dict(sweep_vs_none=r["sweep_vs_none"], stop_styles=r["stop_styles"], cells_considered=r["cells_considered"],
                          cells_positive=r["cells_positive_2011_19"], later=r["positive_2011_19_then_2020_22"]), indent=1))
