"""v5 study on 2011-19 and 2020-22 only (pre-registered: research/body4/PREREGISTRATION_V5.md, step 2), and the choice of
the 4 PRIMARY configurations for the owner's 2023-25 look (best edge quality on 2011-22 pooled, >= 300 trades, per
engulf x layer), made here BEFORE any 2023-25 number exists.
    python3 research/body4/study_v5.py  ->  research/results/body4/v5/study_v5.json
"""
import os, sys, json, math, itertools, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v5.py"))
OUT = os.path.join(ROOT, "research", "results", "body4", "v5")
Y20 = int(dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).timestamp())
NAMES = list(S.GRID)
CFGS = [dict(zip(NAMES, v)) for v in itertools.product(*S.GRID.values())]
PER = ("2011-19", "2020-22")


def ck(tf, c):
    return tf + " | " + "|".join(f"{k}={c[k]}" for k in NAMES)


def zeros():
    return dict(n=0, s=0.0, s2=0.0, hit=0, win=0, pos=0.0, neg=0.0, fin=0.0)


def add(a, R, why, fin):
    a["n"] += len(R); a["s"] += float(R.sum()); a["s2"] += float((R * R).sum()); a["hit"] += int((why == 2).sum())
    a["win"] += int((R > 0).sum()); a["pos"] += float(R[R > 0].sum()); a["neg"] += float(-R[R < 0].sum()); a["fin"] += float(fin.sum())


def stats(a):
    n = a["n"]
    if n < 3:
        return dict(n=n)
    E = a["s"] / n; sd = math.sqrt(max(a["s2"] / n - E * E, 0.0))
    return dict(n=n, E=round(E, 4), t=round(E / sd * math.sqrt(n), 2) if sd > 0 else None, s=round(E / sd, 4) if sd > 0 else None,
                pf=round(a["pos"] / a["neg"], 3) if a["neg"] > 0 else None, hit=round(a["hit"] / n, 4), win=round(a["win"] / n, 4),
                E_swapfree=round((a["s"] + a["fin"]) / n, 4))


def worker(sym):
    M = P.market(sym, S)
    cell, gross = {}, {}
    for tf in S.TIMEFRAMES:
        B = M.bars(tf)
        for c in CFGS:
            D = S.detail(M, B, dict(c, tf=tf), cut=P.core.CUT)
            for per in PER:
                m = (D[:, 0] < Y20) if per == "2011-19" else (D[:, 0] >= Y20)
                add(cell.setdefault((sym, ck(tf, c), per), zeros()), D[m, 3], D[m, 9], D[m, 7])
    S.SPLIT[sym] = dict(spread=0.0, commission=0.0, slippage=0.0)          # before costs: main settings
    for tf in S.TIMEFRAMES:
        B = M.bars(tf)
        for e in ("body", "loose"):
            for ly in ("none", "on"):
                for T in S.GRID["target"]:
                    D = S.detail(M, B, dict(tf=tf, engulf=e, layer=ly, target=T, be=1, buffer=0.0, lookback=1), cut=P.core.CUT, swap=0.0)
                    for per in PER:
                        m = (D[:, 0] < Y20) if per == "2011-19" else (D[:, 0] >= Y20)
                        add(gross.setdefault((f"{tf} | engulf={e}|layer={ly}|target={T}", per), zeros()), D[m, 3], D[m, 9], D[m, 7])
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
    pooled, mk = {}, {}
    for (sym, k, per), a in cell.items():
        b = pooled.setdefault((k, per), zeros())
        for f in b:
            b[f] += a[f]
        if a["n"] >= 3 and a["s"] > 0:
            mk[(k, per)] = mk.get((k, per), 0) + 1
    res = dict(configurations=len(CFGS) * len(S.TIMEFRAMES), pooled={}, paired={}, before_costs={}, primary_for_look={})
    keys = sorted({k for k, _ in pooled})
    for k in keys:
        res["pooled"][k] = {per: dict(stats(pooled[(k, per)]), markets_positive=mk.get((k, per), 0)) for per in PER}
        both = zeros()
        for per in PER:
            for f in both:
                both[f] += pooled[(k, per)][f]
        res["pooled"][k]["2011-22"] = stats(both)
    for var, a, b in (("engulf", "loose", "body"), ("layer", "on", "none")):
        for per in PER:
            wins = tot = 0; dE = []
            for k, v in res["pooled"].items():
                if f"{var}={a}" not in k:
                    continue
                o = res["pooled"].get(k.replace(f"{var}={a}", f"{var}={b}"))
                x, y = v[per], (o or {}).get(per, {})
                if x.get("n", 0) < 100 or y.get("n", 0) < 100:
                    continue
                tot += 1; wins += x["E"] > y["E"]; dE.append(x["E"] - y["E"])
            res["paired"].setdefault(f"{var} {a} vs {b}", {})[per] = dict(pairs=tot, first_better_share=round(wins / tot, 3) if tot else None,
                                                                          mean_R_diff=round(float(np.mean(dE)), 4) if dE else None)
    for (k, per), a in gross.items():
        res["before_costs"].setdefault(k, {})[per] = stats(a)
    for e in ("body", "loose"):
        for ly in ("none", "on"):
            cands = [(k, v) for k, v in res["pooled"].items() if f"engulf={e}|layer={ly}|" in k and v["2011-22"].get("n", 0) >= 300 and v["2011-22"].get("s") is not None]
            if not cands:                                    # pre-registered minimum not met: no primary for this combination
                res["primary_for_look"][f"engulf={e} layer={ly}"] = dict(config=None, chosen_on="no setting has 300 trades in 2011-22")
                continue
            k, v = max(cands, key=lambda z: z[1]["2011-22"]["s"])
            res["primary_for_look"][f"engulf={e} layer={ly}"] = dict(config=k, chosen_on="2011-22 pooled edge quality, >= 300 trades",
                                                                     dev=v["2011-19"], val=v["2020-22"], dev_val=v["2011-22"])
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "study_v5.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["paired"], indent=1))
    print(json.dumps(r["primary_for_look"], indent=1))
