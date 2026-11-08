"""v4 study (pre-registered: research/body4/PREREGISTRATION_V4.md sections 2 and 3b): every configuration x market x
timeframe of body4_range_v4 on 2011-19 and 2020-22 (fills before 2023): trades, R per trade, edge quality, profit factor,
share of trades that reach the TARGET, win rate, swap-free R. Then: safe vs all window (paired), the configuration with the
highest target-hit rate for each target 2R-10R (learn 2011-19, check 2020-22), and the main settings before costs.
    python3 research/body4/study_v4.py  ->  research/results/body4/v4/study_v4.json + STUDY_V4.md
"""
import os, sys, json, math, itertools, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v4.py"))
OUT = os.path.join(ROOT, "research", "results", "body4", "v4")
Y20 = int(dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).timestamp())
NAMES = list(S.GRID)
CFGS = [dict(zip(NAMES, v)) for v in itertools.product(*S.GRID.values())]
PER = ("2011-19", "2020-22")


def ck(c):
    return "|".join(f"{k}={c[k]}" for k in NAMES)


def zeros():
    return dict(n=0, s=0.0, s2=0.0, hit=0, win=0, pos=0.0, neg=0.0, fin=0.0)


def add(a, R, why, fin):
    a["n"] += len(R); a["s"] += float(R.sum()); a["s2"] += float((R * R).sum()); a["hit"] += int((why == 2).sum())
    a["win"] += int((R > 0).sum()); a["pos"] += float(R[R > 0].sum()); a["neg"] += float(-R[R < 0].sum()); a["fin"] += float(fin.sum())


def fin_stats(a):
    n = a["n"]
    if n < 3:
        return dict(n=n)
    E = a["s"] / n; sd = math.sqrt(max(a["s2"] / n - E * E, 0.0))
    return dict(n=n, E=round(E, 4), t=round(E / sd * math.sqrt(n), 2) if sd > 0 else None, s=round(E / sd, 4) if sd > 0 else None,
                pf=round(a["pos"] / a["neg"], 3) if a["neg"] > 0 else None, hit=round(a["hit"] / n, 4), win=round(a["win"] / n, 4),
                E_swapfree=round((a["s"] + a["fin"]) / n, 4))


def worker(sym):
    """One market: every configuration's accumulators, and the main settings before costs."""
    M = P.market(sym, S)
    cell, gross = {}, {}
    for tf in S.TIMEFRAMES:
        B = M.bars(tf)
        for c in CFGS:
            D = S.detail(M, B, dict(c, tf=tf), cut=P.core.CUT)
            for per in PER:
                m = (D[:, 0] < Y20) if per == "2011-19" else (D[:, 0] >= Y20)
                add(cell.setdefault((sym, tf, ck(c), per), zeros()), D[m, 3], D[m, 9], D[m, 7])
    # before costs: main settings (entry 50%, buffer 0, lookback on), breakeven on and off, both windows, all targets
    S.SPLIT[sym] = dict(spread=0.0, commission=0.0, slippage=0.0)
    for tf in S.TIMEFRAMES:
        B = M.bars(tf)
        for w in ("safe", "all"):
            for T in S.GRID["target"]:
                for be in (1, 0):
                    D = S.detail(M, B, dict(tf=tf, target=T, window=w, entry=0.5, be=be, buffer=0.0, lookback=1), cut=P.core.CUT, swap=0.0)
                    for per in PER:
                        m = (D[:, 0] < Y20) if per == "2011-19" else (D[:, 0] >= Y20)
                        add(gross.setdefault((tf, w, T, be, per), zeros()), D[m, 3], D[m, 9], D[m, 7])
    print(sym, flush=True)
    return cell, gross


def main():
    from multiprocessing import Pool
    cell, gross = {}, {}
    with Pool(4) as pool:
        for c_, g_ in pool.imap_unordered(worker, S.MARKETS):
            cell.update(c_)
            for k, a in g_.items():
                b = gross.setdefault(k, zeros())
                for f in b:
                    b[f] += a[f]
    # pooled across markets
    pooled = {}
    for (sym, tf, k, per), a in cell.items():
        b = pooled.setdefault((tf, k, per), zeros())
        for f in b:
            b[f] += a[f]
    mkpos = {}
    for (sym, tf, k, per), a in cell.items():
        if a["n"] >= 3 and a["s"] > 0:
            mkpos[(tf, k, per)] = mkpos.get((tf, k, per), 0) + 1
    res = dict(configurations=len(CFGS) * len(S.TIMEFRAMES), markets=S.MARKETS, pooled={}, best_hit_by_target={}, best_E_by_target={},
               safe_vs_all={}, before_costs={})
    for (tf, k, per), a in pooled.items():
        res["pooled"].setdefault(f"{tf} | {k}", {})[per] = dict(fin_stats(a), markets_positive=mkpos.get((tf, k, per), 0))
    # best target-hit rate per target (learn 2011-19 with >= 200 trades, check 2020-22)
    for T in S.GRID["target"]:
        cands = [(key, v) for key, v in res["pooled"].items() if f"target={T}|" in key + "|" and v["2011-19"].get("n", 0) >= 200]
        if not cands:
            continue
        kh, vh = max(cands, key=lambda z: z[1]["2011-19"]["hit"])
        ke, ve = max(cands, key=lambda z: z[1]["2011-19"]["E"])
        res["best_hit_by_target"][f"{T}R"] = dict(config=kh, learn=vh["2011-19"], check=vh["2020-22"])
        res["best_E_by_target"][f"{T}R"] = dict(config=ke, learn=ve["2011-19"], check=ve["2020-22"])
    # paired: safe vs all, everything else equal
    for per in PER:
        wins = tot = 0; dE = []; dh = []
        for key, v in res["pooled"].items():
            if "window=safe" not in key:
                continue
            o = res["pooled"].get(key.replace("window=safe", "window=all"))
            a, b = v[per], (o or {}).get(per, {})
            if a.get("n", 0) < 100 or b.get("n", 0) < 100:
                continue
            tot += 1; wins += a["E"] > b["E"]; dE.append(a["E"] - b["E"]); dh.append(a["hit"] - b["hit"])
        res["safe_vs_all"][per] = dict(pairs=tot, safe_better_share=round(wins / tot, 3) if tot else None,
                                       mean_R_diff=round(float(np.mean(dE)), 4) if dE else None, mean_hit_diff=round(float(np.mean(dh)), 4) if dh else None)
    for (tf, w, T, be, per), a in gross.items():
        res["before_costs"].setdefault(f"{tf} | {w} | {T}R | breakeven {'on' if be else 'off'}", {})[per] = fin_stats(a)
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "study_v4.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["safe_vs_all"], indent=1))
    for T, v in r["best_hit_by_target"].items():
        print("best hit", T, v["config"], "learn", (v["learn"]["n"], v["learn"]["hit"], v["learn"]["E"]), "check", (v["check"].get("n"), v["check"].get("hit"), v["check"].get("E")))
    for T, v in r["best_E_by_target"].items():
        print("best E", T, v["config"], "learn", (v["learn"]["n"], v["learn"]["E"], v["learn"]["t"]), "check", (v["check"].get("n"), v["check"].get("E"), v["check"].get("t")))
