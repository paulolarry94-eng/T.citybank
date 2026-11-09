"""v7 study (pre-registered: research/body4/PREREGISTRATION_V7.md, step 3). The curated version at three cost views of the
SAME trades: Prime as modelled (R after spread, commission, slippage on stop and time exits); low cost (the same without
slippage, the owner's pasted figures); zero cost (the price move alone). 2011-19, 2020-22, 2023-25 (seen).
PRIMARY: lbbody on, the target with the best 2011-19 edge quality at Prime costs (10 markets, M5 + M15 pooled).
    python3 research/body4/study_v7.py  ->  research/results/body4/v7/study_v7.json
"""
import os, sys, json, math, itertools, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v7.py"))
OUT = os.path.join(ROOT, "research", "results", "body4", "v7")
NAMES = list(S.GRID)
CFGS = [dict(zip(NAMES, v)) for v in itertools.product(*S.GRID.values())]
UTC = dt.timezone.utc
ts_ = lambda y: int(dt.datetime(y, 1, 1, tzinfo=UTC).timestamp())
PERIODS = {"2011-19": (ts_(2011), ts_(2020)), "2020-22": (ts_(2020), ts_(2023)), "2023-25": (ts_(2023), ts_(2026))}
F0 = int(dt.datetime(2011, 1, 3, tzinfo=UTC).timestamp()); FN = 14 * 86400
VIEWS = ("prime", "low", "zero")


def ck(c):
    return "|".join(f"{k}={c[k]}" for k in NAMES)


def worker(sym):
    M = P.market(sym, S)
    sp, cm, sl = S.SPLIT[sym]["spread"], S.SPLIT[sym]["commission"], S.SPLIT[sym]["slippage"]
    out = {}
    for tf in S.TIMEFRAMES:
        B = M.bars(tf)
        for c in CFGS:
            D = S.detail(M, B, dict(c, tf=tf))
            why = D[:, 9].astype(np.int8); R0 = D[:, 4]
            slip = np.where(np.isin(why, [1, 3, 4, 5]), sl / R0, 0.0)
            out[(sym, tf, ck(c))] = dict(t_in=D[:, 0].astype(np.int64), t_out=D[:, 1].astype(np.int64), why=why,
                                         prime=D[:, 3].copy(), low=D[:, 3] + slip, zero=D[:, 3] + slip + (sp + cm) / R0)
    print(sym, flush=True)
    return out


def stats(R, why=None):
    n = len(R)
    if n < 3:
        return dict(n=n)
    E = float(R.mean()); sd = float(R.std())
    d = dict(n=n, E=round(E, 4), t=round(E / sd * math.sqrt(n), 2) if sd > 0 else None, s=round(E / sd, 4) if sd > 0 else None,
             win=round(float((R > 0).mean()), 4))
    if why is not None:
        d["hit"] = round(float((why == 2).mean()), 4)
    return d


def sel(parts, per):
    lo, hi = PERIODS[per]
    out = []
    for p in parts:
        m = (p["t_in"] >= lo) & (p["t_in"] < hi)
        out.append({k: v[m] for k, v in p.items()})
    return out


def cat(parts, key):
    return np.concatenate([p[key] for p in parts]) if parts else np.zeros(0)


def fortnights(parts, lo, hi, view):
    f_lo, f_hi = (lo - F0) // FN, (hi - F0) // FN
    nf = int(f_hi - f_lo)
    R = np.zeros(nf); n = np.zeros(nf); w = np.zeros(nf)
    for p in parts:
        m = (p["t_out"] >= lo) & (p["t_out"] < hi)
        f = np.clip(((p["t_out"][m] - F0) // FN - f_lo).astype(int), 0, nf - 1)
        np.add.at(R, f, p[view][m]); np.add.at(n, f, 1); np.add.at(w, f, (p["why"][m] == 2).astype(float))
    sd = float(R.std())
    return dict(fortnights=nf, trades_per_fortnight=round(float(n.mean()), 2), wins_per_fortnight=round(float(w.mean()), 2),
                share_2_wins=round(float((w >= 2).mean()), 3), share_positive=round(float((R > 0).mean()), 3),
                share_with_a_trade=round(float((n > 0).mean()), 3), mean_R=round(float(R.mean()), 3),
                R_per_year=round(float(R.mean()) * 365.25 / 14, 1), sharpe=round(float(R.mean()) / sd, 3) if sd > 0 else None)


def main():
    from multiprocessing import Pool
    legs = {}
    with Pool(4) as pool:
        for o in pool.imap_unordered(worker, S.MARKETS):
            legs.update(o)
    res = dict(prereg="research/body4/PREREGISTRATION_V7.md", configurations=len(CFGS) * len(S.TIMEFRAMES), pooled={}, by_market={},
               by_tf={}, paired={}, hits={})
    for c in CFGS:
        k = ck(c); T = c["target"]
        allp = [v for (sym, tf, kk), v in legs.items() if kk == k]
        res["pooled"][k] = {per: {vw: stats(cat(sel(allp, per), vw), cat(sel(allp, per), "why")) for vw in VIEWS} for per in PERIODS}
        res["hits"][k] = {per: dict(hit=res["pooled"][k][per]["prime"].get("hit"), needed_zero_cost=round(1 / (1 + T), 4)) for per in PERIODS}
        for tf in S.TIMEFRAMES:
            tp = [v for (sym, t2, kk), v in legs.items() if kk == k and t2 == tf]
            res["by_tf"][f"{tf} | {k}"] = {per: {vw: stats(cat(sel(tp, per), vw)) for vw in VIEWS} for per in PERIODS}
        for sym in S.MARKETS:
            mp = [v for (s2, tf, kk), v in legs.items() if kk == k and s2 == sym]
            res["by_market"][f"{sym} | {k}"] = {per: {vw: stats(cat(sel(mp, per), vw)) for vw in VIEWS} for per in PERIODS}
    for per in PERIODS:                                      # lookback-body rule on vs off (pooled per timeframe x target)
        wins = tot = 0; dE = []
        for tf in S.TIMEFRAMES:
            for T in S.GRID["target"]:
                a = res["by_tf"][f"{tf} | lbbody=1|target={T}"][per]["prime"]; b = res["by_tf"][f"{tf} | lbbody=0|target={T}"][per]["prime"]
                if a.get("n", 0) >= 30 and b.get("n", 0) >= 30:
                    tot += 1; wins += a["E"] > b["E"]; dE.append(a["E"] - b["E"])
        res["paired"][per] = dict(pairs=tot, lbbody_better_share=round(wins / tot, 3) if tot else None,
                                  mean_R_diff=round(float(np.mean(dE)), 4) if dE else None)
    cands = [c for c in CFGS if c["lbbody"] == 1 and res["pooled"][ck(c)]["2011-19"]["prime"].get("s") is not None]
    prim = max(cands, key=lambda c: res["pooled"][ck(c)]["2011-19"]["prime"]["s"])
    kp = ck(prim)
    parts = [v for (sym, tf, kk), v in legs.items() if kk == kp]
    later = cat(sel(parts, "2020-22"), "prime"); later = np.concatenate([later, cat(sel(parts, "2023-25"), "prime")])
    pooled_later = stats(later)
    ok = all(res["pooled"][kp][per]["prime"].get("E", -1) > 0 for per in PERIODS) and (pooled_later.get("t") or 0) >= 2
    res["primary"] = dict(config=kp, chosen_on="best 2011-19 edge quality at Prime costs, lbbody on", periods=res["pooled"][kp],
                          later_2020_25=pooled_later, passes_development=ok,
                          fortnights={per: {vw: fortnights(parts, *PERIODS[per], vw) for vw in VIEWS} for per in PERIODS})
    res["verdict"] = ("development passed: the Jan-Oct 2026 look waits for the owner's confirmation" if ok else
                      "REJECTED on 2011-25: the Jan-Oct 2026 look is not needed (it cannot change the verdict)")
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "study_v7.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(dict(primary=r["primary"]["config"], periods=r["primary"]["periods"], later=r["primary"]["later_2020_25"],
                          paired=r["paired"], verdict=r["verdict"]), indent=1))
