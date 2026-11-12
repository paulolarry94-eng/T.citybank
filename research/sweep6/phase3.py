"""Phase 3-4 of the deep M1 study (research/sweep6/PREREGISTRATION.md): the scanner (sweep6_scanner_v1) on every
timeframe and market, trades entered before 2023 only; frictionless table, then RoboForex Prime costs + swaps; candidate
cells (with costs, R a trade > 0 in each of 2011-14, 2015-18, 2019-22 with >= 20 trades each); Monte Carlo for candidates
(10,000 one-year paths at 1% risk: survive if P(losing year) <= 20% and the median worst drawdown within a year <= 10%).
    python3 research/sweep6/phase3.py -> research/results/sweep6/phase3.json
"""
import os, sys, json, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "sweep6_scanner_v1.py"))
OUT = os.path.join(ROOT, "research", "results", "sweep6")
T = lambda y: int(dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp())
PER = {"2011-19": (T(2011), T(2020)), "2020-22": (T(2020), T(2023)), "2011-14": (T(2011), T(2015)), "2015-18": (T(2015), T(2019)),
       "2019-22": (T(2019), T(2023))}
CUT = T(2023)


def st(R):
    if not len(R):
        return dict(n=0)
    w, l = R[R > 0], R[R <= 0]
    return dict(n=int(len(R)), win=round(float((R > 0).mean()), 4), avg_win=round(float(w.mean()), 2) if len(w) else None,
                avg_loss=round(float(l.mean()), 3) if len(l) else None, E=round(float(R.mean()), 4),
                PF=round(float(w.sum() / -l.sum()), 3) if l.sum() < 0 else None,
                t=round(float(R.mean() / R.std() * np.sqrt(len(R))), 2) if len(R) > 2 and R.std() > 0 else None)


def mc(R, per_year, seed=7, n=10000):
    rng = np.random.default_rng(seed)
    k = max(int(round(per_year)), 1)
    X = R[rng.integers(0, len(R), (n, k))] * 0.01
    eq = np.cumsum(X, axis=1)
    dd = np.max(np.maximum.accumulate(np.concatenate([np.zeros((n, 1)), eq], axis=1), axis=1)[:, None] * 0 + 0, axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.zeros((n, 1)), eq], axis=1), axis=1)[:, 1:]
    mdd = np.max(peak - eq, axis=1)
    yr = eq[:, -1]
    return dict(trades_per_year=k, p_losing_year=round(float((yr < 0).mean()), 4), median_year_pct=round(float(np.median(yr)) * 100, 2),
                p5_year_pct=round(float(np.quantile(yr, 0.05)) * 100, 2), median_maxdd_pct=round(float(np.median(mdd)) * 100, 2),
                p95_maxdd_pct=round(float(np.quantile(mdd, 0.95)) * 100, 2))


def worker(sym):
    M = P.market(sym, S)
    out = {}
    for tf in S.TIMEFRAMES:
        B = M.bars(tf); p = dict(tf=tf, rule="scanner")
        Dc = S.detail(M, B, p, cut=CUT)
        Dz = S.detail(M, B, p, cut=CUT, swap=0.0, split=S.ZERO)
        out[f"{sym} {tf}"] = dict(cost={k: st(Dc[(Dc[:, 0] >= a) & (Dc[:, 0] < b), 3]) for k, (a, b) in PER.items()},
                                  zero={k: st(Dz[(Dz[:, 0] >= a) & (Dz[:, 0] < b), 3]) for k, (a, b) in PER.items()},
                                  _R=Dc[:, 3].tolist(), _t=Dc[:, 0].tolist())
    print(sym, flush=True)
    return out


def main():
    from multiprocessing import Pool
    cells = {}
    with Pool(3) as pool:
        for o in pool.imap_unordered(worker, S.MARKETS):
            cells.update(o)
    res = dict(prereg="research/sweep6/PREREGISTRATION.md", strategy=S.NAME, cells={}, candidates=[], mc={}, survivors=[])
    for key, v in cells.items():
        R = np.array(v.pop("_R")); t = np.array(v.pop("_t"))
        res["cells"][key] = v
        ok = all(v["cost"][e].get("n", 0) >= 20 and v["cost"][e]["E"] > 0 for e in ("2011-14", "2015-18", "2019-22"))
        if ok:
            res["candidates"].append(key)
            m = R[t < CUT]
            res["mc"][key] = mc(m, len(m) / 12.0)
            if res["mc"][key]["p_losing_year"] <= 0.20 and res["mc"][key]["median_maxdd_pct"] <= 10:
                res["survivors"].append(key)
    pooled = {}
    for tf in S.TIMEFRAMES:
        for view in ("zero", "cost"):
            for per in ("2011-19", "2020-22"):
                rows = [res["cells"][f"{m} {tf}"][view][per] for m in S.MARKETS]
                n = sum(r.get("n", 0) for r in rows)
                pooled[f"{tf} | {view} | {per}"] = dict(n=n, E=round(sum((r.get("E") or 0) * r.get("n", 0) for r in rows) / n, 4) if n else None,
                                                        positive_cells=int(sum((r.get("E") or -1) > 0 for r in rows if r.get("n", 0) >= 20)))
    res["pooled"] = pooled
    json.dump(res, open(os.path.join(OUT, "phase3.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    for k, v in r["pooled"].items():
        print(k, v)
    print("candidates", r["candidates"]); print("mc", json.dumps(r["mc"], indent=1)); print("survivors", r["survivors"])
