"""What conditions make the owner's 4-leg SOP win? Learn them on 2011-2019 ONLY, freeze them, then check later years.

Method (fixed before running, 2026-10-31):
  Setups: the calibrated detector (research/truth/strategies/sop_4leg_v1.py), owner's settings: swing 3, perfect or slow
  engulfing, ANY hour (the hour is a feature), limit order valid 10 candles, stop 3.5 pips beyond Leg 4, target 2R, no
  breakeven; EURUSD and GBPUSD; M5, M15, M30. Every setup is simulated on its own (no one-at-a-time rule) with the lab's
  fill and exit code (real-spread limit fills, Exness Zero costs, swaps).
  Features, all known when the order is placed:
    tf, sym, side, hour (UTC), weekday, Leg-4 and Leg-2 engulfing type, entry 30/70%, legs distance (candles),
    stop size in ATR and in pips, cost as a share of R, travel to the entry in ATR, structure size (Leg 4 to Leg 1) in ATR,
    Leg-1 break beyond Leg 3 in ATR, Leg-2 retrace ratio, volatility regime (ATR / its 500-bar median), H4 EMA50 trend
    agreement, EMA(10) slope over 10 candles in ATR (in the trade's direction).
  Learning on 2011-19: each numeric feature is cut into terciles (cut points from 2011-19); categorical features by value.
  Rule search: the best single condition (mean R, at least 15% of the learning trades), then the best second condition
  inside it (at least 300 learning trades). A rule is kept only if it is positive in BOTH halves (2011-14 and 2015-19).
  Every condition tried is counted. The frozen rule is then reported on 2020-22, 2023-25 and Feb-Oct 2026, and written
  into a new lab strategy (sop_4leg_filtered_v1) for the lab's own verdict.
Output: research/results/sop/winning_conditions.json, research/results/sop/setups_features.csv.gz
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
for p in (R, os.path.join(R, "northstar"), os.path.join(R, "truth"), os.path.join(R, "truth", "strategies")):
    sys.path.insert(0, p)
import engine as E
import core
import protocol as P
import executors as X
import sop_4leg_v1 as S

OUT = os.path.join(R, "results", "sop"); os.makedirs(OUT, exist_ok=True)
HOLD = os.path.join(R, "..", "data", "holdout")
PARAMS = {"k": 3, "engulf": "any"}
VALID = 10
TFS = ["M5", "M15", "M30"]
SYMS = ["EURUSD", "GBPUSD"]
NUMERIC = ["hour", "dist", "stop_atr", "stop_pips", "cost_R", "travel_atr", "struct_atr", "leg1_break_atr",
           "leg2_retrace", "vol_regime", "ema_slope_atr"]
CATEG = ["tf", "sym", "side", "weekday", "eg4", "eg2", "pct", "htf_agree"]


def features(M, B, tf, s):
    d = s["d"]; side = s["side"]; s4, s3, s2, s1 = s["legs"]
    h, l, c = B["h"], B["l"], B["c"]; atr = B["atr"]
    a = atr[d] if atr[d] > 0 else np.nan
    e = S.ema(c[max(0, d - 300):d + 1])
    if side < 0:
        p4, p3, p2, p1 = h[s4], l[s3], h[s2], l[s1]
        struct = p4 - p1; brk = p3 - p1; retr = (p2 - p3) / (p4 - p3) if p4 > p3 else np.nan
    else:
        p4, p3, p2, p1 = l[s4], h[s3], l[s2], h[s1]
        struct = p1 - p4; brk = p1 - p3; retr = (p3 - p2) / (p3 - p4) if p3 > p4 else np.nan
    dec_t = int(B["t"][d] + B["minutes"] * 60)
    med = np.median(atr[max(0, d - 500):d + 1][atr[max(0, d - 500):d + 1] > 0]) if d > 20 else np.nan
    stop_d = abs(s["entry"] - s["stop"])
    return dict(tf=tf, sym=M.sym, side=side, dec_t=dec_t, hour=(dec_t % 86400) // 3600, weekday=((dec_t // 86400) + 3) % 7,
                eg4="perfect" if s["eg4"] == ["perfect"] else ("slow" if "perfect" not in s["eg4"] else "mixed"),
                eg2="perfect" if s["eg2"] == ["perfect"] else ("slow" if "perfect" not in s["eg2"] else "mixed"),
                pct=s["pct"], dist=s1 - s4, stop_atr=stop_d / a, stop_pips=stop_d / S.PIP, cost_R=M.cost / stop_d,
                travel_atr=abs(s["entry"] - c[d]) / a, struct_atr=struct / a, leg1_break_atr=brk / a, leg2_retrace=retr,
                vol_regime=a / med if med else np.nan, htf_agree=int(M.bias_at(np.array([dec_t]))[0] == side),
                ema_slope_atr=side * (e[-1] - e[-11]) / a if len(e) > 11 else np.nan)


def simulate(M, B, setups):
    """Each setup alone: lab limit fill (real spread) within VALID candles, then the lab's bracket exit (2R, no BE)."""
    rows = [(s["d"], s["side"], s["stop"], s["entry"], VALID) for s in setups]
    C = P.to_candidates(B, rows, M, S.STOP_CAP_ATR, S.FILL_SPREAD[M.sym])
    fills = {}
    for i in range(len(C["k0"])):
        key = (int(C["dec_t"][i]), int(C["side"][i]))
        res = X._bracket(M.o, M.h, M.l, M.G.c, M.ts.astype(np.int64), M.gaps.astype(np.int64),
                         C["k0"][i:i + 1].astype(np.int64), C["side"][i:i + 1].astype(np.int64),
                         C["entry"][i:i + 1].astype(np.float64), C["stop"][i:i + 1].astype(np.float64), 2.0, False,
                         M.cost, M.swap, 2 ** 62, 0, 200 * B["minutes"], core.BLOCK[0], core.BLOCK[1])
        if len(res):
            fills[key] = float(res[0, 3])
    return fills


def collect(load=None):
    recs = []
    for sym in SYMS:
        if load:
            E.load_m1 = load
        try:
            M = P.market(sym, S)
        finally:
            E.load_m1 = ORIG
        for tf in TFS:
            B = M.bars(tf)
            st = S._setups(B, PARAMS)
            fills = simulate(M, B, st)
            for s in st:
                f = features(M, B, tf, s)
                r = fills.get((f["dec_t"], s["side"]))
                if r is None:
                    continue
                f["R"] = r; recs.append(f)
            print(sym, tf, len(st), "setups,", sum(1 for s in st if (int(B["t"][s["d"]] + B["minutes"] * 60), s["side"]) in fills), "filled", flush=True)
    return pd.DataFrame(recs)


ORIG = E.load_m1


def load_2026(sym, y0=2011, y1=2025):
    d = np.load(os.path.join(HOLD, f"{sym}_M1_bid_2026.npz"))
    return (d["ts"] // 1000).astype(np.int64), d["o"].astype(float), d["h"].astype(float), d["l"].astype(float), d["c"].astype(float)


def year(t):
    return pd.to_datetime(t, unit="s").dt.year


def stats(r):
    r = np.asarray(r, float)
    if len(r) < 2:
        return dict(n=int(len(r)))
    return dict(n=int(len(r)), E=round(float(r.mean()), 3), t=round(float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))), 2),
                win=round(float((r > 0).mean()), 3), PF=round(float(r[r > 0].sum() / max(1e-9, -r[r < 0].sum())), 2))


def conditions(L):
    """All single conditions: numeric terciles (cut points from the learning set) and categorical values."""
    out = []
    for f in NUMERIC:
        q = L[f].quantile([1 / 3, 2 / 3]).values
        out += [(f, "low", (-np.inf, q[0])), (f, "mid", (q[0], q[1])), (f, "high", (q[1], np.inf))]
    for f in CATEG:
        for v in sorted(L[f].dropna().unique(), key=str):
            out.append((f, "=", v))
    return out


def mask(D, cond):
    f, kind, v = cond
    if kind == "=":
        return D[f] == v
    return (D[f] > v[0]) & (D[f] <= v[1])


def main():
    D = collect()
    D26 = collect(load_2026); D26 = D26[D26.dec_t >= 1769904000]                # Feb-Oct 2026 only
    D["year"] = year(D.dec_t)
    D.to_csv(os.path.join(OUT, "setups_features.csv.gz"), index=False)
    L = D[D.year <= 2019]; V = D[(D.year >= 2020) & (D.year <= 2022)]; O = D[D.year >= 2023]
    res = {"all_setups": {"2011-19": stats(L.R), "2020-22": stats(V.R), "2023-25": stats(O.R), "Feb-Oct 2026": stats(D26.R)}}
    # univariate table (learning set only decides; later years shown for honesty)
    uni = []
    for cond in conditions(L):
        mL = mask(L, cond)
        uni.append(dict(feature=cond[0], bin=cond[1] if cond[1] != "=" else str(cond[2]),
                        learn=stats(L.R[mL]), val=stats(V.R[mask(V, cond)]), oos=stats(O.R[mask(O, cond)])))
    res["univariate"] = uni
    tried = 0
    best = None
    for c1 in conditions(L):
        m1 = mask(L, c1); tried += 1
        if m1.sum() < 0.15 * len(L):
            continue
        e1 = L.R[m1].mean()
        if best is None or e1 > best[1]:
            best = ([c1], e1)
    rule = best[0]
    m1 = mask(L, rule[0]); sub = L[m1]
    best2 = None
    for c2 in conditions(sub):
        if c2[0] == rule[0][0]:
            continue
        m2 = mask(sub, c2); tried += 1
        if m2.sum() < 300:
            continue
        e2 = sub.R[m2].mean()
        if best2 is None or e2 > best2[1]:
            best2 = (c2, e2)
    if best2 and best2[1] > best[1]:
        rule.append(best2[0])

    def apply(Df):
        m = pd.Series(True, index=Df.index)
        for c in rule:
            if c[1] == "=":
                m &= Df[c[0]] == c[2]
            else:
                lo, hi = c[2]; m &= (Df[c[0]] > lo) & (Df[c[0]] <= hi)
        return Df[m]

    halves = {"2011-14": stats(apply(L[L.year <= 2014]).R), "2015-19": stats(apply(L[L.year >= 2015]).R)}
    res["rule"] = [dict(feature=c[0], kind=c[1], value=(list(c[2]) if c[1] != "=" else c[2])) for c in rule]
    res["conditions_tried"] = tried
    res["rule_results"] = {"2011-19 (learned)": stats(apply(L).R), **halves, "2020-22": stats(apply(V).R),
                           "2023-25": stats(apply(O).R), "Feb-Oct 2026": stats(apply(D26).R)}
    res["kept"] = all((halves[h].get("E") or -1) > 0 for h in halves)
    json.dump(res, open(os.path.join(OUT, "winning_conditions.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("all_setups", "rule", "conditions_tried", "rule_results", "kept")}, indent=1, default=str))


if __name__ == "__main__":
    main()
