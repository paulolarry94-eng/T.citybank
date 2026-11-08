"""Gold body-engulf characteristics: learn on 2019, check everywhere else. Pre-registered (committed before any result):
research/body4/PREREGISTRATION_GOLD.md.
Every XAUUSD setup on M1-H4 (loose-engulf universe; "strict" is a characteristic), each traded ALONE with the lab's M1
engine (research/body4/body4_fast.py): limit at 50% of the range, stop at the range end, target 2R, no breakeven, no fills
20:30-23:00 UTC, everything flat at 20:30 UTC; RoboForex Prime gold costs. 20 characteristics known at candle 4's close.
Best single condition and best two-condition rule learned on 2019; checked on 2011-18 and 2020-25 (each year, pooled,
2,000 random selections); final logged look at unseen January-October 2026.
    python3 research/body4/gold_traits.py  ->  research/results/body4/gold/traits.json + TABLES.md
"""
import os, sys, json, math, time, datetime as dt
import numpy as np
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research")); sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import engine as E   # noqa: E402

_ORIG = E.load_m1
HOLD = os.path.join(ROOT, "data", "holdout")


def load_m1_2026(sym, y0=2011, y1=2025):
    """2011-2025 plus January-October 2026 (Exness ticks), as research/champion/regen_2026.py does."""
    ts, o, h, l, c = _ORIG(sym, y0, min(y1, 2025))
    f = os.path.join(HOLD, f"{sym}_M1_bid_2026.npz")
    if not os.path.exists(f):
        return ts, o, h, l, c
    d = np.load(f)
    t2 = (d["ts"] // 1000).astype(np.int64)
    ts = np.r_[ts, t2]; o = np.r_[o, d["o"]]; h = np.r_[h, d["h"]]; l = np.r_[l, d["l"]]; c = np.r_[c, d["c"]]
    order = np.argsort(ts, kind="stable"); ts, o, h, l, c = ts[order], o[order], h[order], l[order], c[order]
    keep = np.ones(len(ts), bool); keep[1:] = ts[1:] != ts[:-1]
    flat = (o == h) & (h == l) & (l == c); flat[1:] &= o[1:] == c[:-1]; flat[0] = False
    keep &= ~flat
    return ts[keep], o[keep], h[keep], l[keep], c[keep]


E.load_m1 = load_m1_2026
import protocol as P      # noqa: E402
import body4_scan as SC   # noqa: E402
import body4_fast as FA   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v5.py"))
SYM = "XAUUSD"
OUT = os.path.join(ROOT, "research", "results", "body4", "gold")
TFS = ["M1", "M5", "M15", "M30", "H1", "H4"]
MIN = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240}
TARGET = 2.0
LEARN = 2019
CHECK = [y for y in range(2011, 2026) if y != LEARN]
FINAL = 2026
MIN_N = 100
SEED = 20261108
SESS = ["Asia 23-07", "London 07-12", "overlap 12-16", "New York 16-20:30", "rollover 20:30-23"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@njit(cache=True)
def alone(ts, o, h, l, c, gaps, start, tconf, side, hi, lo, c4, spread, comm, slip, tgt):
    """Each setup traded on its own: the engine is called once per setup (one-element arrays)."""
    n = len(start)
    out = np.full((n, 16), np.nan)
    lb = np.full(1, 5, np.int64); allow = np.ones(1, np.int64)
    for j in range(n):
        rows, amb = FA.simulate(ts, o, h, l, c, gaps, start[j:j + 1], tconf[j:j + 1], side[j:j + 1], hi[j:j + 1], lo[j:j + 1],
                                c4[j:j + 1], lb, spread, comm, slip, 0.0, 0.5, 0.0, False, False, tgt, 0.75 * tgt,
                                4611686018427387904, allow, True)
        if rows.shape[0] > 0:
            for q in range(16):
                out[j, q] = rows[0, q]
    return out


@njit(cache=True)
def day_location(ts1, h1, l1, tconf, c4, side):
    """Where candle 4 closes in today's range so far (trading day from 22:00 UTC): 0 = at the day's low for buys / high
    for sells, 1 = at the other end."""
    n = len(tconf); out = np.full(n, np.nan)
    for j in range(n):
        t = tconf[j] - 1
        ds = ((t - 79200) // 86400) * 86400 + 79200
        i0 = np.searchsorted(ts1, ds); i1 = np.searchsorted(ts1, tconf[j])
        if i1 - i0 < 2:
            continue
        dh = h1[i0:i1].max(); dl = l1[i0:i1].min()
        if dh - dl <= 0:
            continue
        out[j] = (c4[j] - dl) / (dh - dl) if side[j] > 0 else (dh - c4[j]) / (dh - dl)
    return out


@njit(cache=True)
def rolling_ratio(atr, k, w):
    out = np.full(len(k), np.nan)
    for j in range(len(k)):
        a = k[j] - w + 1
        if a < 0 or atr[k[j]] <= 0:
            continue
        m = np.median(atr[a:k[j] + 1])
        if m > 0:
            out[j] = atr[k[j]] / m
    return out


@njit(cache=True)
def mfe_r(ts1, h1, l1, t_in, t_out, side, entry, risk, spread):
    """Furthest favourable move in R before the stop or the 20:30 close (fill and exit minutes left out)."""
    out = np.full(len(t_in), np.nan)
    for j in range(len(t_in)):
        if not (risk[j] > 0):
            continue
        i0 = np.searchsorted(ts1, t_in[j]); i1 = np.searchsorted(ts1, t_out[j])
        if i1 <= i0 + 1:
            out[j] = 0.0
            continue
        if side[j] > 0:
            out[j] = max(0.0, (h1[i0 + 1:i1].max() - entry[j]) / risk[j])
        else:
            out[j] = max(0.0, (entry[j] - (l1[i0 + 1:i1].min() + spread)) / risk[j])
    return out


def year_of(t):
    return np.array([dt.datetime.fromtimestamp(int(x), dt.timezone.utc).year for x in t])


def build():
    M = P.market(SYM, S)
    ts1, o1, h1, l1, c1 = (np.asarray(x) for x in (M.ts, M.o, M.h, M.l, M.G.c))
    gaps = np.asarray(M.gaps, np.int64)
    sp, cm, sl = S.SPLIT[SYM]["spread"], S.SPLIT[SYM]["commission"], S.SPLIT[SYM]["slippage"]
    H4 = M.bars("H4"); h4ema = E.ema(np.asarray(H4["c"], float), 50); h4close = np.asarray(H4["t"], np.int64) + 240 * 60
    Dt, Do, Dh, Dl, Dc, _ = E.resample(M.ts, M.o, M.h, M.l, M.G.c, 1440, 22 * 60)
    Dclose = np.asarray(Dt, np.int64) + 86400
    sma20 = np.convolve(Dc, np.ones(20) / 20, mode="full")[:len(Dc)]; sma20[:19] = np.nan
    adr20 = np.convolve(Dh - Dl, np.ones(20) / 20, mode="full")[:len(Dc)]; adr20[:19] = np.nan
    cols = {}
    for tf in TFS:
        B = M.bars(tf)
        o, h, l, c = (np.asarray(B[x], float) for x in "ohlc")
        X = SC.setups(B, MIN[tf], sample="flow", doji_bullish=True, engulf="loose")
        k, s = X["k"], X["side"]; hi, lo = X["hi"], X["lo"]; tconf = X["t_conf"]; c4 = X["c4"]
        start = np.searchsorted(ts1, tconf).astype(np.int64)
        r2 = alone(ts1, o1, h1, l1, c1, gaps, start, tconf.astype(np.int64), s.astype(np.int64), hi, lo, c4, sp, cm, sl, TARGET)
        rn = alone(ts1, o1, h1, l1, c1, gaps, start, tconf.astype(np.int64), s.astype(np.int64), hi, lo, c4, sp, cm, sl, 1000.0)
        mfe = mfe_r(ts1, h1, l1, np.nan_to_num(rn[:, 0], nan=0).astype(np.int64), np.nan_to_num(rn[:, 1], nan=0).astype(np.int64),
                    s.astype(np.int64), np.nan_to_num(rn[:, 10]), np.nan_to_num(rn[:, 4]), sp)
        mfe[np.isnan(rn[:, 0])] = np.nan
        atr = np.asarray(B["atr"], float)[k]; atr[atr <= 0] = np.nan
        rng = hi - lo; mid = (hi + lo) / 2
        body = np.abs(c - o); hl = h - l
        strict = np.ones(len(k), bool)
        for m in (2, 4):
            i = k - 4 + m; pv = i - 1
            strict &= np.where(s < 0, o[i] >= c[pv], o[i] <= c[pv])
        ema50 = E.ema(c, 50)
        kb = np.searchsorted(h4close, tconf, side="right") - 1
        h4atr = np.asarray(H4["atr"], float)
        kbc = np.clip(kb, 0, None)
        trend_h4 = np.where((kb >= 0) & (h4atr[kbc] > 0), s * (np.asarray(H4["c"], float)[kbc] - h4ema[kbc]) / np.where(h4atr[kbc] > 0, h4atr[kbc], 1), np.nan)
        kd = np.searchsorted(Dclose, tconf, side="right") - 1
        kdc = np.clip(kd, 0, None)
        daily = np.where(kd >= 0, s * (Dc[kdc] - sma20[kdc]) / adr20[kdc], np.nan)
        kk = np.maximum(k - 24, 0)
        d = dict(
            tf=np.full(len(k), TFS.index(tf)), side=s, strict=strict.astype(int),
            session=np.select([((tconf % 86400) >= 23 * 3600) | ((tconf % 86400) < 7 * 3600), (tconf % 86400) < 12 * 3600,
                               (tconf % 86400) < 16 * 3600, (tconf % 86400) < 20 * 3600 + 1800], [0, 1, 2, 3], 4),
            weekday=((((tconf - 1) - 79200) // 86400 + 1) + 3) % 7,
            news=np.array([dt.datetime.fromtimestamp(int(x) - 1, S._NY).date() in S.NEWS for x in tconf], int),
            lookback=X["lookback"],
            range_atr=rng / atr,
            cost_share=(sp + cm + sl) / (0.5 * rng),
            c2_vs_c1=np.minimum(body[k - 2] / np.maximum(body[k - 3], 1e-9), 50.0),
            c4_vs_c3=np.minimum(body[k] / np.maximum(body[k - 1], 1e-9), 50.0),
            c4_past_mid=s * (c[k] - mid) / rng,
            c4_past_c2=s * (c[k] - c[k - 2]) / atr,
            body_share=(body[k - 3] + body[k - 2] + body[k - 1] + body[k]) / np.maximum(hl[k - 3] + hl[k - 2] + hl[k - 1] + hl[k], 1e-9),
            trend_tf=s * (c[k] - ema50[k]) / atr,
            trend_h4=trend_h4,
            trend_daily=daily,
            vol_regime=rolling_ratio(np.asarray(B["atr"], float), k.astype(np.int64), 500),
            day_location=day_location(ts1, h1, l1, tconf.astype(np.int64), c4, s.astype(np.int64)),
            momentum=np.where(k >= 24, s * (c[k - 4] - c[kk]) / atr, np.nan),
            tconf=tconf, t_in=r2[:, 0], t_out=r2[:, 1], R=r2[:, 3], risk=r2[:, 4], reason=r2[:, 9], mfe=mfe,
        )
        filled = ~np.isnan(r2[:, 0])
        rs = np.nan_to_num(r2[:, 9]).astype(int)
        risk = np.where(filled, r2[:, 4], np.nan)
        d["gross"] = np.where(filled, r2[:, 3] + (sp + cm) / risk + np.where(np.isin(rs, [1, 3, 4, 5]), sl / risk, 0.0), np.nan)
        d["setup_year"] = year_of(tconf)
        for key, v in d.items():
            cols.setdefault(key, []).append(np.asarray(v))
        print(tf, "setups", len(k), "filled", int(filled.sum()), flush=True)
    T = {key: np.concatenate(v) for key, v in cols.items()}
    sy = T["setup_year"]
    setups = dict(by_year={int(y): int((sy == y).sum()) for y in sorted(set(sy.tolist()))},
                  y2019_by_tf={tf: int(((sy == LEARN) & (T["tf"] == i)).sum()) for i, tf in enumerate(TFS)})
    filled = ~np.isnan(T["t_in"])
    T = {key: v[filled] for key, v in T.items()}
    T["year"] = year_of(T["t_in"])
    return T, setups


NUMERIC = ["range_atr", "cost_share", "c2_vs_c1", "c4_vs_c3", "c4_past_mid", "c4_past_c2", "body_share", "trend_tf",
           "trend_h4", "trend_daily", "vol_regime", "day_location", "momentum"]
CATEG = {"tf": TFS, "side": {-1: "sell", 1: "buy"}, "strict": {0: "loose only", 1: "strict"}, "session": SESS,
         "weekday": DAYS, "news": {0: "no US news", 1: "US news day"}, "lookback": {i: f"{i}/5" for i in range(6)}}


def stats(R, gross=None, mfe=None):
    n = len(R)
    if n < 3:
        return dict(n=n)
    E_ = float(R.mean()); sd = float(R.std())
    d = dict(n=n, E=round(E_, 4), t=round(E_ / sd * math.sqrt(n), 2) if sd > 0 else None, win=round(float((R > 0).mean()), 3),
             hit2R=None)
    if gross is not None:
        d["E_before_costs"] = round(float(np.nanmean(gross)), 4)
    if mfe is not None and np.isfinite(mfe).any():
        d["mfe_median"] = round(float(np.nanmedian(mfe)), 3)
    return d


def conditions(T, learn):
    """Every third (cut points from the 2019 trades) of every numeric characteristic and every category."""
    out = []
    for f in NUMERIC:
        x = T[f]; xl = x[learn & np.isfinite(x)]
        q1, q2 = np.quantile(xl, [1 / 3, 2 / 3])
        out += [(f, f"{f} low (< {q1:.3g})", np.isfinite(x) & (x < q1)), (f, f"{f} middle ({q1:.3g}-{q2:.3g})", np.isfinite(x) & (x >= q1) & (x < q2)),
                (f, f"{f} high (>= {q2:.3g})", np.isfinite(x) & (x >= q2))]
    for f, labels in CATEG.items():
        items = labels.items() if isinstance(labels, dict) else enumerate(labels)
        for v, lab in items:
            m = T[f] == v
            if m.any():
                out.append((f, f"{f} = {lab}", m))
    return out


def main():
    t0 = time.time()
    T, setups = build()
    yr = T["year"]; R = T["R"]; G = T["gross"]; MF = T["mfe"]
    learn = yr == LEARN
    check = np.isin(yr, CHECK)
    final = yr == FINAL
    hit2 = T["reason"] == 2
    res = dict(prereg="research/body4/PREREGISTRATION_GOLD.md", target=TARGET, learn_year=LEARN, check_years=CHECK, final=FINAL)
    res["setups"] = setups
    res["trades_by_year"] = {int(y): int((yr == y).sum()) for y in sorted(set(yr.tolist()))}
    res["trades_2019_by_tf"] = {tf: int((learn & (T["tf"] == i)).sum()) for i, tf in enumerate(TFS)}
    def st(m):
        d = stats(R[m], G[m], MF[m]); d["hit2R"] = round(float(hit2[m].mean()), 3) if m.any() else None
        return d
    res["all"] = {"2019": st(learn), "check": st(check), "2026": st(final)}
    conds = conditions(T, learn)
    res["characteristics"] = [dict(feature=f, condition=lab, learn_2019=st(learn & m), check=st(check & m)) for f, lab, m in conds]
    # rule search on 2019
    cand = [(f, lab, m) for f, lab, m in conds if (learn & m).sum() >= MIN_N]
    ranked = sorted(cand, key=lambda z: -R[learn & z[2]].mean())
    first = ranked[0]
    second = []
    for f, lab, m in conds:
        if f == first[0]:
            continue
        mm = first[2] & m
        if (learn & mm).sum() >= MIN_N:
            second.append((f, lab, mm))
    best2 = max(second, key=lambda z: R[learn & z[2]].mean())
    rule = best2[2]
    res["search"] = dict(conditions=len(conds), tried_single=len(cand), tried_second=len(second), total_tried=len(cand) + len(second),
                         best_single=first[1], rule=f"{first[1]} AND {best2[1]}",
                         top5_single=[dict(condition=lab, learn_2019=st(learn & m)) for f, lab, m in ranked[:5]])
    # checking: each year, pooled, random selections
    def per_year(m):
        return {int(y): stats(R[(yr == y) & m], G[(yr == y) & m]) for y in CHECK}
    rows = [("all setups", np.ones(len(R), bool)), ("rule: " + res["search"]["rule"], rule)] + [("single: " + lab, m) for f, lab, m in ranked[:5]]
    res["check"] = []
    rng = np.random.default_rng(SEED)
    for name, m in rows:
        pooled = st(check & m)
        py = per_year(m)
        pos = sum(1 for v in py.values() if v.get("n", 0) >= 3 and v["E"] > 0)
        sel = R[check & m]; pool = R[check]
        if len(sel) >= 3 and len(sel) < len(pool):
            rnd = np.array([pool[rng.integers(0, len(pool), len(sel))].mean() for _ in range(2000)])   # random picks of the same size
            p_rand = float(((rnd >= sel.mean()).sum() + 1) / (len(rnd) + 1))
        else:
            p_rand = None
        res["check"].append(dict(what=name, learn_2019=st(learn & m), check_pooled=pooled, years_positive=pos, years=len(CHECK),
                                 p_random=None if p_rand is None else round(p_rand, 4), per_year=py, final_2026=st(final & m)))
    rc = res["check"][1]
    ok = (rc["check_pooled"].get("E", -1) > 0 and (rc["check_pooled"].get("t") or 0) >= 2 and rc["years_positive"] >= 9
          and (rc["p_random"] is not None and rc["p_random"] <= 0.05))
    f26 = rc["final_2026"]
    final_ok = None if f26.get("n", 0) < 30 else f26["E"] > 0
    res["verdict"] = ("PASS" if ok and final_ok else "INCONCLUSIVE (fewer than 30 trades in 2026)" if ok and final_ok is None else "REJECTED")
    res["seconds"] = round(time.time() - t0)
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "traits.json"), "w"), indent=1, default=float)
    tables(res)
    return res


def tables(res):
    f = lambda d, k="E": "-" if not d or d.get(k) is None else (f"{d[k]:+.3f}R" if k.startswith("E") else str(d[k]))
    L = ["# Gold body-engulf characteristics: learn on 2019, check everywhere else (built by research/body4/gold_traits.py)", "",
         f"Pre-registered: {res['prereg']}. Every XAUUSD setup M1-H4 traded alone: 50% limit, stop at the range end, "
         f"{res['target']:.0f}R, no breakeven, flat at 20:30 UTC; RoboForex Prime gold costs. R after costs unless marked.", "",
         "## Trades", "", "| Year | " + " | ".join(str(y) for y in res["trades_by_year"]) + " |", "|---|" + "---|" * len(res["trades_by_year"]),
         "| Trades | " + " | ".join(f"{v:,}" for v in res["trades_by_year"].values()) + " |", "",
         "2019 by timeframe (trades): " + ", ".join(f"{k} {v:,}" for k, v in res["trades_2019_by_tf"].items()) +
         "; setups found in 2019: " + ", ".join(f"{k} {v:,}" for k, v in res["setups"]["y2019_by_tf"].items()), "",
         "| All setups | Trades | R per trade | before costs | win rate | 2R hits | median MFE |", "|---|---|---|---|---|---|---|"]
    for k, d in res["all"].items():
        L.append(f"| {k} | {d.get('n', 0):,} | {f(d)} | {f(d, 'E_before_costs')} | {d.get('win', '-')} | {d.get('hit2R', '-')} | {d.get('mfe_median', '-')} |")
    L += ["", "## Every characteristic: 2019 (learning) vs the 14 check years", "",
          "| Condition | 2019 trades | 2019 R | 2019 before costs | Check trades | Check R | Check before costs |", "|---|---|---|---|---|---|---|"]
    for c in res["characteristics"]:
        a, b = c["learn_2019"], c["check"]
        L.append(f"| {c['condition']} | {a.get('n', 0):,} | {f(a)} | {f(a, 'E_before_costs')} | {b.get('n', 0):,} | {f(b)} | {f(b, 'E_before_costs')} |")
    s = res["search"]
    L += ["", "## The rule learned on 2019", "", f"Conditions: {s['conditions']}; tried {s['total_tried']} (single {s['tried_single']}, "
          f"second step {s['tried_second']}). Best single: {s['best_single']}. Rule: **{s['rule']}**.", "",
          "| Selection | 2019 | Check years pooled (t) | Years positive | Beats random | Jan-Oct 2026 |", "|---|---|---|---|---|---|"]
    for c in res["check"]:
        a, b, z = c["learn_2019"], c["check_pooled"], c["final_2026"]
        pr = "-" if c["p_random"] is None else f"p = {c['p_random']:.3f}"
        L.append(f"| {c['what']} | {a.get('n', 0):,}, {f(a)} | {b.get('n', 0):,}, {f(b)} (t {b.get('t')}) | {c['years_positive']} of {c['years']} | "
                 f"{pr} | {z.get('n', 0)}, {f(z)} |")
    L += ["", f"**Verdict: {res['verdict']}**", ""]
    L += ["## The rule, year by year (check years)", "", "| Year | Trades | R after costs | before costs |", "|---|---|---|---|"]
    for y, d in res["check"][1]["per_year"].items():
        L.append(f"| {y} | {d.get('n', 0)} | {f(d)} | {f(d, 'E_before_costs')} |")
    open(os.path.join(OUT, "TABLES.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("setups", "trades_by_year", "trades_2019_by_tf", "all", "search", "verdict", "seconds")}, indent=1, default=float)[:6000])
