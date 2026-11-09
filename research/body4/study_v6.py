"""v6 study (pre-registered: research/body4/PREREGISTRATION_V6.md, step 3). Learn 2011-19, check 2020-22, seen 2023-25.
(1) 60% body vs 2-candle lookback: the four combinations side by side and paired comparisons (pooled over the 12 markets,
    per timeframe and target).
(2) Target hit rates against what each target needs.
(3) The best two-week mix: for each of the 12 configurations, legs = market x timeframe cells with >= 50 trades and R per
    trade after costs > 0 in 2011-19; every trade at 1R; the best mix = highest fortnight Sharpe in 2011-19. Fortnights =
    14-day blocks from Monday 2011-01-03 00:00 UTC; a trade counts in the fortnight it closes; empty fortnights count as 0.
    Also every leg of each configuration ("everywhere"). The chosen mix is saved for the one 2026 look (look_v6.py).
    python3 research/body4/study_v6.py  ->  research/results/body4/v6/study_v6.json + STUDY_V6.md
"""
import os, sys, json, math, itertools, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v6.py"))
OUT = os.path.join(ROOT, "research", "results", "body4", "v6")
NAMES = list(S.GRID)
CFGS = [dict(zip(NAMES, v)) for v in itertools.product(*S.GRID.values())]
UTC = dt.timezone.utc
ts_ = lambda y: int(dt.datetime(y, 1, 1, tzinfo=UTC).timestamp())
PERIODS = {"2011-19": (ts_(2011), ts_(2020)), "2020-22": (ts_(2020), ts_(2023)), "2023-25": (ts_(2023), ts_(2026))}
F0 = int(dt.datetime(2011, 1, 3, tzinfo=UTC).timestamp()); FN = 14 * 86400
MIN_LEG = 50


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
            gross = D[:, 3] + (sp + cm) / R0 + np.where(np.isin(why, [1, 3, 4, 5]), sl / R0, 0.0)
            out[(sym, tf, ck(c))] = dict(t_in=D[:, 0].astype(np.int64), t_out=D[:, 1].astype(np.int64), R=D[:, 3].copy(),
                                         gross=gross, cost=D[:, 5].copy(), why=why)
    print(sym, flush=True)
    return out


def stats(R, gross=None, why=None, cost=None):
    n = len(R)
    if n < 3:
        return dict(n=n)
    E = float(R.mean()); sd = float(R.std())
    d = dict(n=n, E=round(E, 4), t=round(E / sd * math.sqrt(n), 2) if sd > 0 else None, s=round(E / sd, 4) if sd > 0 else None,
             pf=round(float(R[R > 0].sum() / -R[R < 0].sum()), 3) if (R < 0).any() else None, win=round(float((R > 0).mean()), 4))
    if gross is not None:
        d["E_before_costs"] = round(float(gross.mean()), 4)
    if why is not None:
        d["hit"] = round(float((why == 2).mean()), 4)
    if cost is not None:
        d["cost_R"] = round(float(cost.mean()), 4)
    return d


def cat(parts, key):
    return np.concatenate([p[key] for p in parts]) if parts else np.zeros(0)


def fortnights(parts, lo, hi):
    """Fortnight series of a mix in [lo, hi): R sum, trades and target hits per fortnight (empty fortnights = 0)."""
    f_lo, f_hi = (lo - F0) // FN, (hi - F0) // FN
    nf = int(f_hi - f_lo)
    R = np.zeros(nf); n = np.zeros(nf); w = np.zeros(nf)
    for p in parts:
        m = (p["t_out"] >= lo) & (p["t_out"] < hi)
        f = ((p["t_out"][m] - F0) // FN - f_lo).astype(int)
        f = np.clip(f, 0, nf - 1)
        np.add.at(R, f, p["R"][m]); np.add.at(n, f, 1); np.add.at(w, f, (p["why"][m] == 2).astype(float))
    return R, n, w


def fstats(R, n, w):
    if len(R) < 3:
        return dict(fortnights=len(R))
    sd = float(R.std())
    return dict(fortnights=len(R), trades_per_fortnight=round(float(n.mean()), 2), wins_per_fortnight=round(float(w.mean()), 2),
                share_2_wins=round(float((w >= 2).mean()), 3), share_positive=round(float((R > 0).mean()), 3),
                mean_R=round(float(R.mean()), 3), sharpe=round(float(R.mean()) / sd, 3) if sd > 0 else None,
                t=round(float(R.mean()) / sd * math.sqrt(len(R)), 2) if sd > 0 else None, worst_R=round(float(R.min()), 2),
                best_R=round(float(R.max()), 2), R_per_year=round(float(R.mean()) * 365.25 / 14, 1))


def main():
    from multiprocessing import Pool
    legs = {}
    with Pool(4) as pool:
        for o in pool.imap_unordered(worker, S.MARKETS):
            legs.update(o)
    res = dict(prereg="research/body4/PREREGISTRATION_V6.md", configurations=len(CFGS) * len(S.TIMEFRAMES), pooled={}, by_tf={},
               paired={}, hits={}, mix={}, everywhere={})
    def period_parts(parts, per):
        lo, hi = PERIODS[per]
        out = []
        for p in parts:
            m = (p["t_in"] >= lo) & (p["t_in"] < hi)
            out.append({k: v[m] for k, v in p.items()})
        return out
    # (1) pooled per configuration and per configuration x timeframe
    for c in CFGS:
        k = ck(c)
        allp = [v for (sym, tf, kk), v in legs.items() if kk == k]
        res["pooled"][k] = {per: stats(*(cat(period_parts(allp, per), x) for x in ("R", "gross", "why", "cost"))) for per in PERIODS}
        for tf in S.TIMEFRAMES:
            tp = [v for (sym, t2, kk), v in legs.items() if kk == k and t2 == tf]
            res["by_tf"][f"{tf} | {k}"] = {per: stats(*(cat(period_parts(tp, per), x) for x in ("R", "gross", "why", "cost"))) for per in PERIODS}
    # paired: body60 on vs off, lb2 on vs off, body60 alone vs lb2 alone (pooled over markets, per timeframe x target)
    comps = {"60% body on vs off": [], "2-candle lookback on vs off": [], "60% body alone vs 2-candle lookback alone": []}
    for tf in S.TIMEFRAMES:
        for T in S.GRID["target"]:
            for other in (1, 0):
                comps["60% body on vs off"].append((f"{tf} | body60=1|lb2={other}|target={T}", f"{tf} | body60=0|lb2={other}|target={T}"))
                comps["2-candle lookback on vs off"].append((f"{tf} | body60={other}|lb2=1|target={T}", f"{tf} | body60={other}|lb2=0|target={T}"))
            comps["60% body alone vs 2-candle lookback alone"].append((f"{tf} | body60=1|lb2=0|target={T}", f"{tf} | body60=0|lb2=1|target={T}"))
    for name, prs in comps.items():
        for per in PERIODS:
            wins = tot = 0; dE = []
            for a, b in prs:
                x, y = res["by_tf"][a][per], res["by_tf"][b][per]
                if x.get("n", 0) < 100 or y.get("n", 0) < 100:
                    continue
                tot += 1; wins += x["E"] > y["E"]; dE.append(x["E"] - y["E"])
            res["paired"].setdefault(name, {})[per] = dict(pairs=tot, first_better_share=round(wins / tot, 3) if tot else None,
                                                           mean_R_diff=round(float(np.mean(dE)), 4) if dE else None)
    # (2) target hit rates vs needed
    for c in CFGS:
        k = ck(c); T = c["target"]
        for per in PERIODS:
            d = res["pooled"][k][per]
            if d.get("n", 0) >= 3:
                res["hits"].setdefault(k, {})[per] = dict(hit=d["hit"], needed_before_costs=round(1 / (1 + T), 4),
                                                          needed_after_costs=round((1 + d["cost_R"]) / (1 + T), 4))
    # (3) mixes
    best = None
    for c in CFGS:
        k = ck(c)
        cells = {(sym, tf): v for (sym, tf, kk), v in legs.items() if kk == k}
        chosen = []
        for (sym, tf), v in cells.items():
            lo, hi = PERIODS["2011-19"]
            m = (v["t_in"] >= lo) & (v["t_in"] < hi)
            if m.sum() >= MIN_LEG and v["R"][m].mean() > 0:
                chosen.append(dict(market=sym, tf=tf, trades_2011_19=int(m.sum()), E_2011_19=round(float(v["R"][m].mean()), 4)))
        parts = [cells[(x["market"], x["tf"])] for x in chosen]
        rec = dict(legs=chosen)
        for per, (lo, hi) in PERIODS.items():
            rec[per] = fstats(*fortnights(parts, lo, hi)) if parts else dict(fortnights=0)
        res["mix"][k] = rec
        allparts = list(cells.values())
        res["everywhere"][k] = {per: fstats(*fortnights(allparts, lo, hi)) for per, (lo, hi) in PERIODS.items()}
        sh = rec["2011-19"].get("sharpe")
        if chosen and sh is not None and (best is None or sh > res["mix"][best]["2011-19"]["sharpe"]):
            best = k
    res["best_mix"] = dict(config=best, rule="highest 2011-19 fortnight Sharpe among configurations with at least one leg",
                           legs=res["mix"][best]["legs"] if best else [])
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "study_v6.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["paired"], indent=1))
    print("best mix:", r["best_mix"]["config"], len(r["best_mix"]["legs"]), "legs")
