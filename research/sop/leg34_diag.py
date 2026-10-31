"""Leg 34 on gold M5, diagnostics for the owner (descriptive, nothing is selected from them), owner's configuration
(swing 3, perfect or slow engulfing, all hours, $0.35 buffer), 2011-2025:
  1. every exit at Exness Zero costs and at ZERO costs (is there a raw edge that costs eat?);
  2. how far filled trades go in their favour before the stop or 24 hours: share reaching +1R, +2R, +3R, +4R
     (the owner's loser "was in profit before the loss");
  3. cost as a share of the risk per trade, by year (gold was $1,100-1,800 in 2011-19, $3,000-4,500 in 2025).
  4. (python3 leg34_diag.py slope) results by how steeply the 10 EMA moved with the trade from Leg 4 to the entry.
Output: research/results/sop/leg34_diag.json
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
for p in (R, os.path.join(R, "northstar"), os.path.join(R, "truth"), os.path.join(R, "truth", "strategies")):
    sys.path.insert(0, p)
import engine as E
import protocol as P
import executors as X
import core


def stats(r):
    r = np.asarray(r, float)
    return dict(n=int(len(r)), E=round(float(r.mean()), 3), win=round(float((r > 0).mean()), 3)) if len(r) else dict(n=0)


def main():
    S = P.load_strategy(os.path.join(R, "truth", "strategies", "leg34_gold_v1.py"))
    p0 = dict(tf="M5", k=3, engulf="any", window="all", buffer="fixed")
    out = {"config": p0, "exits": {}}
    M = P.market("XAUUSD", S); cost = M.cost
    for ex in S.GRID["exit"]:
        p = dict(p0, exit=ex)
        tr = P.run_config(S, M, p, 0.0, 0.0, 0, cut=0)
        gross = tr[:, 3] + tr[:, 5]                          # add back the round-trip cost in R
        out["exits"][ex] = {"after_costs": stats(tr[:, 3]), "before_costs": stats(gross)}
        print(ex, out["exits"][ex], flush=True)
    # excursion: run with a far target and no breakeven, record the best favourable move before exit
    B = M.bars("M5"); C = P.to_candidates(B, S.signals(B, dict(p0, exit="t4"), M), M, S.STOP_CAP_ATR, S.FILL_SPREAD["XAUUSD"])
    o = np.argsort(C["k0"], kind="stable")
    k0 = C["k0"][o].astype(np.int64); sd = C["side"][o].astype(np.int64); en = C["entry"][o].astype(float); st = C["stop"][o].astype(float)
    res = X._managed(M.o, M.h, M.l, M.G.c, M.ts.astype(np.int64), M.gaps.astype(np.int64), k0, sd, en, st, 100.0, False, False,
                     np.zeros(0, np.int64), np.zeros(0, np.int64), False, cost, M.swap, 2 ** 62, 0, S.TIME_STOP * 5, core.BLOCK[0], core.BLOCK[1])
    ts = M.ts.astype(np.int64); mfe = []; risk = []; yrs = []
    pos = {int(t): i for i, t in enumerate(ts)}
    for row in res:
        i0, i1 = pos[int(row[0])], pos[int(row[1])]; d = row[4]; side = int(row[2])
        j = np.searchsorted(ts[k0], int(row[0]))
        e0 = en[j] if j < len(en) else np.nan
        if side > 0:
            best = (M.h[i0:i1 + 1].max() - e0) / d
        else:
            best = (e0 - (M.l[i0:i1 + 1].min() + cost)) / d
        mfe.append(best); risk.append(d); yrs.append(pd.Timestamp(int(row[0]), unit="s").year)
    mfe = np.array(mfe); risk = np.array(risk); yrs = np.array(yrs)
    out["reach"] = {f"+{x}R": round(float((mfe >= x).mean()), 3) for x in (1, 2, 3, 4)}
    out["n_filled"] = int(len(mfe))
    out["cost_share_of_R_by_year"] = {int(y): round(float(np.median(cost / risk[yrs == y])), 3) for y in np.unique(yrs)}
    out["median_risk_usd_by_year"] = {int(y): round(float(np.median(risk[yrs == y])), 2) for y in np.unique(yrs)}
    print(json.dumps({k: out[k] for k in ("reach", "n_filled", "cost_share_of_R_by_year", "median_risk_usd_by_year")}), flush=True)
    json.dump(out, open(os.path.join(R, "results", "sop", "leg34_diag.json"), "w"), indent=1)


if __name__ == "__main__" and len(sys.argv) == 1:
    main()


def slope_split():
    """Owner: 'especially when the 10 EMA slope supports the direction'. Every setup of the owner's configuration is
    simulated alone (exit t3, fixed buffer); EMA move from Leg 4 to the decision candle in the trade's direction, in
    units of the 14-candle average range, cut into thirds (cut points from 2011-19). Descriptive only."""
    S = P.load_strategy(os.path.join(R, "truth", "strategies", "leg34_gold_v1.py"))
    p = dict(tf="M5", k=3, engulf="any", window="all", buffer="fixed", exit="t3")
    out = {}
    for label, loader in (("2011-2025", None), ("Jan-Sep 2026", "2026")):
        if loader:
            hold = os.path.join(R, "..", "data", "holdout", "XAUUSD_M1_bid_2026.npz")
            def l26(sym, y0=2011, y1=2025, f=hold):
                d = np.load(f); return (d["ts"] // 1000).astype(np.int64), d["o"].astype(float), d["h"].astype(float), d["l"].astype(float), d["c"].astype(float)
            orig = E.load_m1; E.load_m1 = l26
        try:
            M = P.market("XAUUSD", S); B = M.bars("M5")
        finally:
            if loader:
                E.load_m1 = orig
        S._CACHE.clear()
        e = S.ema(np.asarray(B["c"], float)); atr = np.asarray(B["atr"], float); t = np.asarray(B["t"])
        rows = []
        for s in S.setups(B, p, M):
            row = [(s["d"], s["side"], S.stop_of(s, "fixed"), s["entry"], S.VALID)]
            C = P.to_candidates(B, row, M, S.STOP_CAP_ATR, S.FILL_SPREAD["XAUUSD"])
            if not len(C["k0"]):
                continue
            res = X._managed(M.o, M.h, M.l, M.G.c, M.ts.astype(np.int64), M.gaps.astype(np.int64), C["k0"][:1].astype(np.int64),
                             C["side"][:1].astype(np.int64), C["entry"][:1].astype(float), C["stop"][:1].astype(float), 3.0, False,
                             False, np.zeros(0, np.int64), np.zeros(0, np.int64), False, M.cost, M.swap, 2 ** 62, 0, S.TIME_STOP * 5,
                             core.BLOCK[0], core.BLOCK[1])
            if not len(res):
                continue
            s4 = s["legs"][0]; d = s["d"]
            slope = -s["side"] * (e[s4] - e[d]) / atr[d] if atr[d] > 0 else np.nan     # >0: EMA moved with the trade
            rows.append((int(t[d]), slope, float(res[0, 3])))
        out[label] = pd.DataFrame(rows, columns=["t", "slope", "R"])
    D = out["2011-2025"]; D["yr"] = pd.to_datetime(D.t, unit="s").dt.year
    q = D[D.yr <= 2019].slope.quantile([1 / 3, 2 / 3]).values
    res = {}
    for label, Df in out.items():
        cut = pd.cut(Df.slope, [-np.inf, q[0], q[1], np.inf], labels=["flattest third", "middle third", "steepest third"])
        res[label] = {str(k): stats(g.R) for k, g in Df.groupby(cut, observed=True)}
    res["cut_points_atr"] = [round(float(x), 2) for x in q]
    print(json.dumps(res), flush=True)
    return res


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "slope":
    r = slope_split()
    f = os.path.join(R, "results", "sop", "leg34_diag.json"); j = json.load(open(f)); j["ema_slope_split"] = r
    json.dump(j, open(f, "w"), indent=1)
