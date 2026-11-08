"""Owner's questions on the body-engulf 4-candle range, answered on 2011-19 (development) and 2020-22 (validation) only
(fills before 2023, the lab's cut; the 2023-25 holdout stays closed). Pre-registered: research/body4/PREREGISTRATION.md.

    python3 research/body4/study.py      ->  research/results/body4/study.json and STUDY.md

  1. every configuration x market x timeframe: trades, R per trade, edge quality s, profit factor, R a year, win rate,
     swap-free R per trade, share of unclear minutes;
  2. paired comparisons (all else equal): breakeven on vs off, 50% vs 70% entry, buffers, lookback on vs off;
  3. candle size terciles (average body of candles 1-4 / ATR(14) at candle 4; cut points from 2011-19 setups only);
  4. best market x timeframe: learn on 2011-19 (best s, >= 100 trades), check on 2020-22.
"""
import os, sys, json, math, itertools, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P              # noqa: E402

OUT = os.path.join(ROOT, "research", "results", "body4")
NAME = next((a for a in sys.argv[1:] if a.startswith("body4_")), "body4_range_v1")
S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", f"{NAME}.py"))
SUB = "" if NAME == "body4_range_v1" else NAME.split("_")[-1]
Y20 = int(dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).timestamp())
Y11 = int(dt.datetime(2011, 1, 1, tzinfo=dt.timezone.utc).timestamp())
YEARS = {"2011-19": 9.0, "2020-22": 3.0}
MAIN_T = S.GRID.get("target", [4])[0]
CFGS = [dict(zip(S.GRID, v)) for v in itertools.product(*S.GRID.values())]


def metrics(R, fin=None):
    R = np.asarray(R, float)
    n = len(R)
    if n < 3:
        return dict(n=n)
    sd = R.std(ddof=1)
    win, loss = R[R > 0].sum(), -R[R < 0].sum()
    out = dict(n=n, E=round(float(R.mean()), 4), t=round(float(R.mean() / sd * math.sqrt(n)), 2) if sd > 0 else None,
               s=round(float(R.mean() / sd), 4) if sd > 0 else None, pf=round(float(win / loss), 3) if loss > 0 else None,
               win=round(float((R > 0).mean()), 3), total=round(float(R.sum()), 1))
    if fin is not None:
        out["E_swapfree"] = round(float((R + np.asarray(fin)).mean()), 4)
    return out


def key(c):
    return (f"target {c['target']}R | " if "target" in c else "") + f"entry {int(c['entry'] * 100)}% | breakeven {'on' if c['be'] else 'off'} | buffer {int(c['buffer'] * 100)}% | lookback {'on' if c['lookback'] else 'off'}"


def main():
    rows = []                          # one per market x tf x config: metrics per period
    size_acc = {}                      # tf -> period -> tercile -> list of R (main configuration only)
    size_acc_all = {}                  # tf -> period -> tercile -> list of R (every configuration)
    amb = {}
    for sym in S.MARKETS:
        M = P.market(sym, S)
        for tf in S.TIMEFRAMES:
            B = M.bars(tf)
            Sx = S.setups(B, dict(sample="flow"), M)
            k = Sx["k"]
            body = np.mean([np.abs(B["c"][k - j] - B["o"][k - j]) for j in range(4)], axis=0)
            atr = np.asarray(B["atr"], float)[k]
            size = np.where(atr > 0, body / np.where(atr > 0, atr, 1), np.nan)
            dev = (Sx["t_conf"] < Y20) & np.isfinite(size)
            q1, q2 = (np.quantile(size[dev], [1 / 3, 2 / 3]) if dev.sum() > 10 else (np.nan, np.nan))
            terc = np.where(size < q1, 0, np.where(size < q2, 1, 2))
            for c in CFGS:
                p = dict(c, tf=tf)
                D = S.detail(M, B, p, cut=P.core.CUT)
                t_in, R, fin = D[:, 0], D[:, 3], D[:, 7]
                rec = dict(market=sym, tf=tf, config=key(c), cfg=c, n_unclear=int(D[:, 15].sum()) if len(D) else 0)
                for per, m in (("2011-19", (t_in >= Y11) & (t_in < Y20)), ("2020-22", t_in >= Y20)):
                    rec[per] = metrics(R[m], fin[m])
                    if rec[per].get("n", 0) >= 3:
                        rec[per]["per_year"] = round(rec[per]["total"] / YEARS[per], 1)
                    j = D[m, 8].astype(int)
                    for z in range(3):
                        sel = terc[j] == z
                        size_acc_all.setdefault(tf, {}).setdefault(per, {}).setdefault(z, []).extend(R[m][sel].tolist())
                        if {k: v for k, v in c.items() if k != "target"} == dict(entry=0.5, be=1, buffer=0.0, lookback=1) and c.get("target", 4) == MAIN_T:
                            size_acc.setdefault(tf, {}).setdefault(per, {}).setdefault(z, []).extend(R[m][sel].tolist())
                rows.append(rec)
                amb.setdefault(tf, [0, 0]); amb[tf][0] += rec["n_unclear"]; amb[tf][1] += len(D)
            print(sym, tf, "setups", len(k), flush=True)
    res = dict(prereg="research/body4/PREREGISTRATION.md", configurations=len(CFGS) * len(S.TIMEFRAMES), rows=rows)
    # 2. paired comparisons
    def pairs(var, a, b):
        out = {}
        for per in ("2011-19", "2020-22"):
            dpf, dE, wins, tot = [], [], 0, 0
            for r in rows:
                if r["cfg"][var] != a:
                    continue
                c2 = dict(r["cfg"], **{var: b})
                o = next(x for x in rows if x["market"] == r["market"] and x["tf"] == r["tf"] and x["cfg"] == c2)
                A, Bq = r[per], o[per]
                if A.get("n", 0) < 30 or Bq.get("n", 0) < 30 or A.get("pf") is None or Bq.get("pf") is None:
                    continue
                tot += 1; wins += A["pf"] > Bq["pf"]; dpf.append(A["pf"] - Bq["pf"]); dE.append(A["E"] - Bq["E"])
            out[per] = dict(pairs=tot, share_a_better_pf=round(wins / tot, 3) if tot else None,
                            mean_pf_diff=round(float(np.mean(dpf)), 3) if dpf else None,
                            mean_R_diff=round(float(np.mean(dE)), 4) if dE else None)
        return out
    res["paired"] = {"breakeven on vs off": pairs("be", 1, 0), "entry 50% vs 70%": pairs("entry", 0.5, 0.7),
                     "lookback on vs off": pairs("lookback", 1, 0),
                     "buffer 0% vs 5%": pairs("buffer", 0.0, 0.05), "buffer 0% vs 10%": pairs("buffer", 0.0, 0.1),
                     "buffer 0% vs 20%": pairs("buffer", 0.0, 0.2)}
    if "target" in S.GRID:
        res["paired"]["target 2R vs 1R"] = pairs("target", 2, 1)
    # 3. size terciles
    res["size_terciles_main"] = {tf: {per: {["small", "medium", "large"][z]: metrics(v) for z, v in d.items()} for per, d in pp.items()}
                                 for tf, pp in size_acc.items()}
    res["size_terciles_all_configs"] = {tf: {per: {["small", "medium", "large"][z]: metrics(v) for z, v in d.items()} for per, d in pp.items()}
                                        for tf, pp in size_acc_all.items()}
    res["unclear_share"] = {tf: round(a / b, 4) if b else None for tf, (a, b) in amb.items()}
    # 4. best market x timeframe: learn 2011-19, check 2020-22
    picks = []
    for sym in S.MARKETS:
        for tf in S.TIMEFRAMES:
            cand = [r for r in rows if r["market"] == sym and r["tf"] == tf and r["2011-19"].get("n", 0) >= 100 and r["2011-19"].get("s") is not None]
            if not cand:
                continue
            b = max(cand, key=lambda r: r["2011-19"]["s"])
            picks.append(dict(market=sym, tf=tf, config=b["config"], learn=b["2011-19"], check=b["2020-22"]))
    res["learn_then_check"] = picks
    # pooled per timeframe, main configuration and best-by-volume
    pooled = {}
    for tf in S.TIMEFRAMES:
        for c in CFGS:
            rs = [r for r in rows if r["tf"] == tf and r["cfg"] == c]
            pooled.setdefault(tf, {})[key(c)] = {per: dict(n=sum(r[per].get("n", 0) for r in rs),
                                                            total=round(sum(r[per].get("total", 0.0) for r in rs), 1),
                                                            markets_positive=sum(1 for r in rs if r[per].get("E", -1) > 0))
                                                 for per in ("2011-19", "2020-22")}
    res["pooled_by_tf"] = pooled
    out = os.path.join(OUT, SUB) if SUB else OUT
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "study.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["paired"], indent=1))
    print(json.dumps(r["unclear_share"]))
