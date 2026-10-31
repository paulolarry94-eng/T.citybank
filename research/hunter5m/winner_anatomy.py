"""5-minute hunter, step 1: the anatomy of Leg 34's biggest winners, learned on gold 2011-19, tested everywhere else.

Owner (2026-10-31): "out of the 700 trades ... study the 1 percent of the 1 percent winner attributes and run it again
through all the other markets ... build a 5-min hunter and survivor". Method fixed BEFORE running:

Universe: every Leg 34 setup (detector of truth/strategies/leg34_gold_v1.py: swing 3, perfect or slow engulfing, all hours,
  sell/buy limit 30% into the eaten Leg 4 candle, stop 0.032% of price beyond Leg 4, order valid 8 hours), both sides, on
  the 5-minute chart of 11 markets: XAUUSD, EURUSD, GBPUSD, USDJPY, XAGUSD, WTI, US500, NAS100, GER40, UK100, JP225.
  Each setup is simulated ALONE (no one-trade-at-a-time rule) with the lab's fills (limit through the measured spread, none
  in the 20:30-23:00 UTC rollover block) and the lab's exit engine (executors._managed), time stop 24 hours.
Outcomes per filled setup: MFE = the best favourable move in R before the stop or 24 hours ("how far it can run"); R after
  costs and swaps under exits t3 (3R target), t5, t10 and ladder (breakeven at +1R, then lock each completed R); the same
  before costs. PRIMARY exit for the rule search: ladder (the exit that keeps runners); the others are reported only.
Costs: Exness Zero realistic for XAUUSD, EURUSD, GBPUSD, USDJPY; the lab's conservative estimates for the other seven.
Features, all known when the order is placed (decision candle), signed so that + means "in the trade's direction":
  side, session (asia 22-07, london 07-12, overlap 12-16, ny 16-22 UTC), weekday, Leg 4 / Leg 2 engulfing type,
  legs distance (candles), stop size in ATR(14), cost as a share of R, structure size Leg 4->Leg 1 in ATR, Leg 1 break
  beyond Leg 3 in ATR, Leg 2 retrace ratio, volatility regime (ATR / its 500-candle median), 10-EMA move from Leg 4 to the
  decision in ATR, H1 EMA(20) slope over 3 hours in H1 ATR, H4 EMA(50) trend agreement, daily trend (yesterday's close vs
  the 20-day average, in average daily ranges), share of the average daily range already used today, today's move from
  the day's open, entry location in yesterday's range (premium for sells, discount for buys), 1-hour and 4-hour momentum,
  distance the price must travel back to the entry in ATR.
Learning set: XAUUSD 2011-2019 only. Anatomy: winners = top 10%, top 1% and top 0.1% by MFE; for each feature, the share
  of winners in each third (cut points from the learning set) against the share of all trades ("lift").
Rule search (as research/sop/winning_conditions.py): best single condition by mean R (primary exit, after costs) with at
  least 15% of learning trades, then the best second condition inside it (at least 300 trades); kept only if positive in
  BOTH halves (2011-14, 2015-19). Every condition tried is counted.
The frozen rule is then reported, without any change, on: gold 2020-22 and 2023-25; each of the other 10 markets 2011-25
  (never used for learning); January-September 2026 (gold, EUR, GBP, JPY; untouched); October 2026 separately (the month
  of the owner's screenshots).
Output: research/results/hunter5m/winner_anatomy.json, research/results/hunter5m/setups_m5.csv.gz
"""
import os, sys, json, time
import numpy as np
import pandas as pd
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
for p in (R, os.path.join(R, "northstar"), os.path.join(R, "truth"), os.path.join(R, "truth", "strategies")):
    sys.path.insert(0, p)
import engine as E
import core
import protocol as P
import executors as X
import leg34_gold_v1 as S

OUT = os.path.join(R, "results", "hunter5m"); os.makedirs(OUT, exist_ok=True)
MARKETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "XAGUSD", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
LEARN = "XAUUSD"
HOLD_MARKETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
JAN26, OCT26 = 1767225600, 1790812800
HOLD = os.path.join(R, "..", "data", "holdout")
ZERO = json.load(open(os.path.join(R, "truth", "costs_exness_zero.json")))["realistic"]
SPREADS = json.load(open(os.path.join(R, "results", "exness", "zero_spreads.json")))
SPREAD_NAME = {"GER40": "DE30", "WTI": "USOIL"}
EXITS = {"t3": (3.0, False, False, False), "t5": (5.0, False, False, False), "t10": (10.0, False, False, False),
         "ladder": (0.0, True, True, False)}
PRIMARY = "ladder"
SETUP = {"k": 3, "engulf": "any"}; BUFFER = "scaled"
NUMERIC = ["dist", "stop_atr", "cost_R", "struct_atr", "brk_atr", "leg2_retrace", "vol_regime", "ema_slope", "h1_slope",
           "d1_trend", "day_used", "from_open", "premium", "mom_1h", "mom_4h", "travel_atr"]
CATEG = ["side", "session", "weekday", "eg4", "eg2", "h4_agree"]
ORIG = E.load_m1
EMPTY = np.zeros(0, np.int64)


def load_2026(sym, y0=2011, y1=2025):
    d = np.load(os.path.join(HOLD, f"{sym}_M1_bid_2026.npz"))
    return (d["ts"] // 1000).astype(np.int64), d["o"].astype(float), d["h"].astype(float), d["l"].astype(float), d["c"].astype(float)


def fill_spread(sym):
    name = SPREAD_NAME.get(sym, sym)
    v = [x["mean"] for k, x in SPREADS.items() if k.split()[0] == name]
    return max(v) if v else None


def market(sym, y2026=False):
    S.COSTS = {sym: ZERO[sym]} if sym in ZERO else {}
    if y2026:
        E.load_m1 = load_2026
    try:
        return P.market(sym, S)
    finally:
        E.load_m1 = ORIG


@njit(cache=True)
def mfe_path(o, h, l, ts, k0, side, entry, stop, cost, max_min):
    """Best favourable move in R from the fill until the stop is hit or max_min minutes pass (same minute: stop first)."""
    d = entry - stop if side > 0 else stop - entry
    best = 0.0
    for i in range(k0, len(o)):
        if ts[i] - ts[k0] >= max_min * 60:
            break
        if side > 0:
            if l[i] <= stop:
                break
            f = (h[i] - entry) / d
        else:
            if h[i] + cost >= stop:
                break
            f = (entry - (l[i] + cost)) / d
        if f > best:
            best = f
    return best


def day_context(B):
    """Per 5-minute bar: today's open, high and low so far (UTC day), and for the last FULL day before today (>= 100
    bars): its high, low, close, the 20-day average range and the 20-day average close."""
    t = np.asarray(B["t"]); day = t // 86400
    df = pd.DataFrame(dict(day=day, o=B["o"], h=B["h"], l=B["l"], c=B["c"]))
    g = df.groupby("day", sort=True)
    dopen = g.o.transform("first").values; dhigh = g.h.cummax().values; dlow = g.l.cummin().values
    D = g.agg(h=("h", "max"), l=("l", "min"), c=("c", "last"), n=("c", "size"))
    full = D[D.n >= 100]
    fd = full.index.values
    rng = (full.h - full.l)
    adr = rng.rolling(20).mean().values; sma = full.c.rolling(20).mean().values
    k = np.searchsorted(fd, day, side="left") - 1                          # last full day strictly before today
    ok = k >= 0; kk = np.clip(k, 0, None)
    pick = lambda a: np.where(ok, a[kk], np.nan)
    return dict(dopen=dopen, dhigh=dhigh, dlow=dlow, pdh=pick(full.h.values), pdl=pick(full.l.values),
                pc=pick(full.c.values), adr=pick(adr), sma=pick(sma))


def session(hour):
    return "asia" if (hour >= 22 or hour < 7) else "london" if hour < 12 else "overlap" if hour < 16 else "ny"


def eg_kind(x):
    return "perfect" if x == ["perfect"] else ("slow" if "perfect" not in x else "mixed")


def features(M, B, Dc, H, s):
    d = s["d"]; side = s["side"]; s4, s3, s2, s1 = s["legs"]
    h, l, c = B["h"], B["l"], B["c"]; a = B["atr"][d]
    if not a > 0:
        return None
    e = B["_ema"]
    p4 = s["p4"]
    p3, p2, p1 = (l[s3], h[s2], l[s1]) if side < 0 else (h[s3], l[s2], h[s1])
    stop = S.stop_of(s, BUFFER); stop_d = abs(s["entry"] - stop)
    dec_t = int(B["t"][d] + B["minutes"] * 60)
    med = np.median(B["atr"][max(0, d - 500):d + 1][B["atr"][max(0, d - 500):d + 1] > 0])
    kH = np.searchsorted(H["t"] + 3600, dec_t, side="right") - 1
    h1 = side * (H["_ema"][kH] - H["_ema"][kH - 3]) / H["atr"][kH] if kH >= 3 and H["atr"][kH] > 0 else np.nan
    adr = Dc["adr"][d]
    rngp = Dc["pdh"][d] - Dc["pdl"][d]
    loc = (s["entry"] - Dc["pdl"][d]) / rngp if rngp > 0 else np.nan
    hour = (dec_t % 86400) // 3600
    return dict(side=side, session=session(hour), weekday=int(((dec_t // 86400) + 3) % 7), eg4=eg_kind(s["eg4"]),
                eg2=eg_kind(s["eg2"]), dist=s1 - s4, stop_atr=stop_d / a, cost_R=M.cost / stop_d,
                struct_atr=abs(p4 - p1) / a, brk_atr=abs(p3 - p1) / a,
                leg2_retrace=abs(p2 - p3) / abs(p4 - p3) if p4 != p3 else np.nan, vol_regime=a / med if med > 0 else np.nan,
                ema_slope=side * (e[d] - e[s4]) / a, h1_slope=h1, h4_agree=int(M.bias_at(np.array([dec_t]))[0] == side),
                d1_trend=side * (Dc["pc"][d] - Dc["sma"][d]) / adr if adr > 0 else np.nan,
                day_used=(Dc["dhigh"][d] - Dc["dlow"][d]) / adr if adr > 0 else np.nan,
                from_open=side * (c[d] - Dc["dopen"][d]) / adr if adr > 0 else np.nan,
                premium=(loc if side < 0 else 1 - loc), mom_1h=side * (c[d] - c[max(0, d - 12)]) / a,
                mom_4h=side * (c[d] - c[max(0, d - 48)]) / a, travel_atr=abs(s["entry"] - c[d]) / a, dec_t=dec_t)


def simulate(M, B, setups):
    rows = [(s["d"], s["side"], S.stop_of(s, BUFFER), s["entry"], S.VALID) for s in setups]
    C = P.to_candidates(B, rows, M, S.STOP_CAP_ATR, fill_spread(M.sym))
    ts = M.ts.astype(np.int64); gaps = M.gaps.astype(np.int64); out = {}
    for i in range(len(C["k0"])):
        k0 = C["k0"][i:i + 1].astype(np.int64); sd = C["side"][i:i + 1].astype(np.int64)
        en = C["entry"][i:i + 1].astype(np.float64); st = C["stop"][i:i + 1].astype(np.float64)
        rec = {}
        for name, (tgt, be, lad, ux) in EXITS.items():
            res = X._managed(M.o, M.h, M.l, M.G.c, ts, gaps, k0, sd, en, st, tgt, be, lad, EMPTY, EMPTY, ux, M.cost, M.swap,
                             2 ** 62, 0, S.TIME_STOP * 5, core.BLOCK[0], core.BLOCK[1])
            if not len(res):
                rec = None; break
            rec[name] = float(res[0, 3]); rec[name + "_gross"] = float(res[0, 3] + res[0, 5])
        if rec is None:
            continue
        rec["mfe"] = mfe_path(M.o, M.h, M.l, ts, int(k0[0]), int(sd[0]), float(en[0]), float(st[0]), M.cost, S.TIME_STOP * 5)
        rec["fill_t"] = int(ts[k0[0]])
        out[(int(C["dec_t"][i]), int(C["side"][i]))] = rec
    return out


def collect(sym, y2026=False):
    M = market(sym, y2026)
    B = M.bars("M5"); B["_ema"] = S.ema(np.asarray(B["c"], float))
    H = M.bars("H1"); H["_ema"] = S.ema(np.asarray(H["c"], float), 20)
    Dc = day_context(B)
    S._CACHE.clear()
    st = S._setups(B, SETUP)
    sims = simulate(M, B, st)
    recs = []
    for s in st:
        f = features(M, B, Dc, H, s)
        if f is None:
            continue
        r = sims.get((f["dec_t"], s["side"]))
        if r is None:
            continue
        f.update(r); f["sym"] = sym; recs.append(f)
    print(f"{sym}{' 2026' if y2026 else ''}: {len(st)} setups, {len(recs)} filled", flush=True)
    return pd.DataFrame(recs)


def stats(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 2:
        return dict(n=int(len(r)))
    return dict(n=int(len(r)), E=round(float(r.mean()), 3), t=round(float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))), 2),
                win=round(float((r > 0).mean()), 3))


def conditions(L):
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
    return (D[f] == v) if kind == "=" else ((D[f] > v[0]) & (D[f] <= v[1]))


def anatomy(L):
    res = {}
    cuts = {f: L[f].quantile([1 / 3, 2 / 3]).values for f in NUMERIC}
    for tier in (0.10, 0.01, 0.001):
        thr = float(L.mfe.quantile(1 - tier)); W = L[L.mfe >= thr]
        t = {"mfe_threshold_R": round(thr, 2), "n": int(len(W)), "numeric": {}, "categorical": {}}
        for f in NUMERIC:
            q = cuts[f]; bins = [-np.inf, q[0], q[1], np.inf]
            sa = pd.cut(L[f], bins).value_counts(normalize=True, sort=False).values
            sw = pd.cut(W[f], bins).value_counts(normalize=True, sort=False).values
            t["numeric"][f] = {"winners_low_mid_high": [round(float(x), 3) for x in sw],
                               "lift_low_mid_high": [round(float(x / y), 2) if y > 0 else None for x, y in zip(sw, sa)],
                               "median_all": round(float(L[f].median()), 3), "median_winners": round(float(W[f].median()), 3)}
        for f in CATEG:
            sa = L[f].value_counts(normalize=True); sw = W[f].value_counts(normalize=True)
            t["categorical"][f] = {str(k): {"winners": round(float(sw.get(k, 0)), 3), "lift": round(float(sw.get(k, 0) / v), 2)}
                                   for k, v in sa.items()}
        res[f"top_{tier:g}"] = t
    return res


def main():
    t0 = time.time()
    D = pd.concat([collect(m) for m in MARKETS], ignore_index=True)
    D["year"] = pd.to_datetime(D.dec_t, unit="s").dt.year
    D26 = pd.concat([collect(m, True) for m in HOLD_MARKETS], ignore_index=True)
    D26 = D26[D26.dec_t >= JAN26]
    D.to_csv(os.path.join(OUT, "setups_m5.csv.gz"), index=False); D26.to_csv(os.path.join(OUT, "setups_m5_2026.csv.gz"), index=False)
    L = D[(D.sym == LEARN) & (D.year <= 2019)]
    res = {"learning_set": {"market": LEARN, "years": "2011-2019", "n": int(len(L))}}
    res["mfe_distribution_learning"] = {f"p{q}": round(float(L.mfe.quantile(q / 100)), 2) for q in (50, 90, 99, 99.9)}
    res["share_reaching"] = {f"{x}R": round(float((L.mfe >= x).mean()), 4) for x in (1, 2, 3, 5, 10, 20)}
    res["anatomy"] = anatomy(L)
    # baseline per market and period, every exit, after and before costs
    base = {}
    for sym, g in D.groupby("sym"):
        for per, gg in (("2011-19", g[g.year <= 2019]), ("2020-22", g[(g.year >= 2020) & (g.year <= 2022)]), ("2023-25", g[g.year >= 2023])):
            base[f"{sym} {per}"] = {ex: stats(gg[ex]) for ex in EXITS} | {ex + "_gross": stats(gg[ex + "_gross"]) for ex in EXITS}
    for sym, g in D26.groupby("sym"):
        base[f"{sym} Jan-Sep 2026"] = {ex: stats(g[g.dec_t < OCT26][ex]) for ex in EXITS}
        base[f"{sym} Oct 2026"] = {ex: stats(g[g.dec_t >= OCT26][ex]) for ex in EXITS}
    res["baseline"] = base
    # rule search on the learning set, primary exit
    tried = 0; best = None
    for c1 in conditions(L):
        m1 = mask(L, c1); tried += 1
        if m1.sum() < 0.15 * len(L):
            continue
        e1 = L[PRIMARY][m1].mean()
        if best is None or e1 > best[1]:
            best = ([c1], e1)
    rule = best[0]; sub = L[mask(L, rule[0])]; best2 = None
    for c2 in conditions(sub):
        if c2[0] == rule[0][0]:
            continue
        m2 = mask(sub, c2); tried += 1
        if m2.sum() < 300:
            continue
        e2 = sub[PRIMARY][m2].mean()
        if best2 is None or e2 > best2[1]:
            best2 = (c2, e2)
    if best2 and best2[1] > best[1]:
        rule.append(best2[0])

    def apply(Df):
        m = pd.Series(True, index=Df.index)
        for c in rule:
            m &= mask(Df, c)
        return Df[m]

    halves = {"2011-14": stats(apply(L[L.year <= 2014])[PRIMARY]), "2015-19": stats(apply(L[L.year >= 2015])[PRIMARY])}
    res["rule"] = [dict(feature=c[0], kind=c[1], value=(list(c[2]) if c[1] != "=" else c[2])) for c in rule]
    res["conditions_tried"] = tried
    res["kept"] = all((halves[h].get("E") or -1) > 0 for h in halves)
    G = D[D.sym == LEARN]
    tests = {"gold 2011-19 (learned)": apply(L),
             "gold 2020-22": apply(G[(G.year >= 2020) & (G.year <= 2022)]), "gold 2023-25": apply(G[G.year >= 2023]),
             "other 10 markets 2011-25 (pooled)": apply(D[D.sym != LEARN])}
    for sym in MARKETS[1:]:
        tests[f"{sym} 2011-25"] = apply(D[D.sym == sym])
    tests["4 markets Jan-Sep 2026 (untouched)"] = apply(D26[D26.dec_t < OCT26])
    tests["gold Jan-Sep 2026 (untouched)"] = apply(D26[(D26.sym == LEARN) & (D26.dec_t < OCT26)])
    tests["4 markets Oct 2026"] = apply(D26[D26.dec_t >= OCT26])
    res["rule_halves"] = halves
    res["rule_results"] = {k: {ex: stats(v[ex]) for ex in EXITS} | {PRIMARY + "_gross": stats(v[PRIMARY + "_gross"])}
                           for k, v in tests.items()}
    res["runtime_s"] = round(time.time() - t0)
    json.dump(res, open(os.path.join(OUT, "winner_anatomy.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("learning_set", "mfe_distribution_learning", "share_reaching", "rule",
                                          "conditions_tried", "kept", "rule_halves")}, indent=1, default=str))
    for k, v in res["rule_results"].items():
        print(k, {ex: (x.get("n"), x.get("E")) for ex, x in v.items()})


if __name__ == "__main__":
    main()
