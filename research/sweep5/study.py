"""Pivot-sweep v2 study (pre-registered: research/sweep5/PREREGISTRATION.md). Every market x timeframe x configuration,
trades entered before 2023 only. Per cell and era: trades, win rate, average win / loss (R), expectancy, profit factor,
trades a month, before and after costs. Candidate legs = positive after costs in each of 2011-14, 2015-18, 2019-22 with
20+ trades in each. Loser study: stopped trades, did price reach TP1 / TP2 within a day, and how far past the stop first.
    python3 research/sweep5/study.py -> research/results/sweep5/study.json (+ legs pickle in the scratch path SWEEP5_PKL)
"""
import os, sys, json, math, itertools, pickle, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "sweep5_pivot_v2.py"))
OUT = os.path.join(ROOT, "research", "results", "sweep5")
UTC = dt.timezone.utc
T = lambda y: int(dt.datetime(y, 1, 1, tzinfo=UTC).timestamp())
ERAS = {"2011-14": (T(2011), T(2015)), "2015-18": (T(2015), T(2019)), "2019-22": (T(2019), T(2023)),
        "2011-19": (T(2011), T(2020)), "2020-22": (T(2020), T(2023))}
CUT = T(2023)
CFGS = [dict(zip(S.GRID, v)) for v in itertools.product(*S.GRID.values())]
ck = lambda c: "|".join(f"{k}={c[k]}" for k in S.GRID)


def stats(R, months):
    n = len(R)
    if n == 0:
        return dict(n=0)
    w, lo = R[R > 0], R[R <= 0]
    d = dict(n=n, per_month=round(n / months, 2), E=round(float(R.mean()), 4), win=round(float((R > 0).mean()), 3),
             avg_win=round(float(w.mean()), 2) if len(w) else None, avg_loss=round(float(lo.mean()), 2) if len(lo) else None,
             PF=round(float(w.sum() / -lo.sum()), 2) if len(lo) and lo.sum() < 0 else None)
    if n > 2 and R.std() > 0:
        d["s"] = round(float(R.mean() / R.std()), 4); d["t"] = round(float(R.mean() / R.std() * math.sqrt(n)), 2)
    return d


def loser_study(M, D):
    """Stopped trades (reason 1 or 5): within 1440 minutes after the stop, did price reach TP1 / TP2, and how far past the
    stop (in R) did it go before reaching TP1."""
    ts, h, l = M.ts, M.h, M.l
    rows = []
    for r in D[np.isin(D[:, 9], [1, 5])]:
        s, e, st, rk, tp1, tp2 = int(r[2]), r[10], r[12], r[4], r[13], r[14]
        i = int(np.searchsorted(ts, int(r[1]))); j = int(np.searchsorted(ts, int(r[1]) + 86400))
        if j <= i + 1:
            continue
        hh, ll = h[i + 1:j], l[i + 1:j]
        fav = ll if s < 0 else hh
        adv = hh if s < 0 else ll
        reach1 = np.flatnonzero((fav - tp1) * s >= 0)
        reach2 = np.flatnonzero((fav - tp2) * s >= 0)
        k1 = reach1[0] if len(reach1) else len(fav)
        worst = float(np.max((adv[:k1 + 1] - st) * -s) / rk) if k1 > 0 else 0.0     # R beyond the original stop before TP1
        rows.append((1.0 if len(reach1) else 0.0, 1.0 if len(reach2) else 0.0, max(worst, 0.0)))
    return np.array(rows) if rows else np.zeros((0, 3))


def worker(sym):
    M = P.market(sym, S)
    sp = S.SPLIT[sym]
    legs, losers = {}, {}
    for tf in S.TIMEFRAMES:
        B = M.bars(tf)
        for c in CFGS:
            D = S.detail(M, B, dict(c, tf=tf), cut=CUT)
            D = D[np.argsort(D[:, 0], kind="stable")]
            why = D[:, 9].astype(np.int8); R0 = D[:, 4]
            slip = np.where(np.isin(why, [1, 3, 4, 5, 6]), sp["slippage"] / R0, 0.0)
            Z = D[:, 3] + slip + (sp["spread"] + sp["commission"]) / R0 + D[:, 7]
            legs[(sym, tf, ck(c))] = dict(t_in=D[:, 0].astype(np.int64), t_out=D[:, 1].astype(np.int64), R=D[:, 3].astype(np.float32),
                                          Z=Z.astype(np.float32), why=why, tp1R=((D[:, 13] - D[:, 10]) * D[:, 2] / R0).astype(np.float32))
            if c["exit"] == "tp2" and c["stop"] == "range" and c["life"] == 96:
                losers[(sym, tf, c["sweep"])] = loser_study(M, D)
    print(sym, flush=True)
    return legs, losers


def main():
    from multiprocessing import Pool
    legs, losers = {}, {}
    with Pool(3) as pool:
        for a, b in pool.imap_unordered(worker, S.MARKETS):
            legs.update(a); losers.update(b)
    pickle.dump(legs, open(os.environ.get("SWEEP5_PKL", os.path.join(OUT, "_legs.pkl")), "wb"))
    res = dict(prereg="research/sweep5/PREREGISTRATION.md", cells=len(legs), cell_stats={}, candidates=[], by_tf={}, loser_study={})
    for key, v in legs.items():
        st = {}
        for era, (a, b) in ERAS.items():
            m = (v["t_in"] >= a) & (v["t_in"] < b); months = (b - a) / (86400 * 30.44)
            st[era] = dict(cost=stats(v["R"][m], months), zero=stats(v["Z"][m], months))
        res["cell_stats"][" | ".join(key)] = st
        if all(st[e]["cost"].get("n", 0) >= 20 and st[e]["cost"]["E"] > 0 for e in ("2011-14", "2015-18", "2019-22")):
            res["candidates"].append(" | ".join(key))
    for tf in S.TIMEFRAMES:
        for c in CFGS:
            parts = [v for (sym, t2, k), v in legs.items() if t2 == tf and k == ck(c)]
            for era in ("2011-19", "2020-22"):
                a, b = ERAS[era]
                R = np.concatenate([p["R"][(p["t_in"] >= a) & (p["t_in"] < b)] for p in parts])
                Z = np.concatenate([p["Z"][(p["t_in"] >= a) & (p["t_in"] < b)] for p in parts])
                res["by_tf"][f"{tf} | {ck(c)} | {era}"] = dict(cost=stats(R, (b - a) / (86400 * 30.44)), zero=stats(Z, (b - a) / (86400 * 30.44)))
    for tf in S.TIMEFRAMES:
        for sw in ("now", "recent"):
            A = np.concatenate([v for (sym, t2, s2), v in losers.items() if t2 == tf and s2 == sw] or [np.zeros((0, 3))])
            if len(A):
                res["loser_study"][f"{tf} | {sw}"] = dict(stopped=len(A), reached_TP1_within_a_day=round(float(A[:, 0].mean()), 3),
                    reached_TP2_within_a_day=round(float(A[:, 1].mean()), 3),
                    of_those_TP1_first_went_past_stop_by_R={q: round(float(np.quantile(A[A[:, 0] == 1, 2], q)), 2) for q in (0.25, 0.5, 0.75)} if (A[:, 0] == 1).any() else None,
                    would_survive_stop_wider_by={f"+{x}R": round(float(((A[:, 0] == 1) & (A[:, 2] <= x)).mean()), 3) for x in (0.5, 1, 2, 3)})
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "study.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    print("cells", r["cells"], "candidates", len(r["candidates"]))
    for c in r["candidates"]:
        print(c, {e: (r["cell_stats"][c][e]["cost"]["n"], r["cell_stats"][c][e]["cost"]["E"]) for e in ("2011-14", "2015-18", "2019-22")})
    print(json.dumps(r["loser_study"], indent=1))
