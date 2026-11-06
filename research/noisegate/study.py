"""Noise gate on the 13 survivors (pre-registered: research/noisegate/PREREGISTRATION.md).

    python3 research/noisegate/study.py            # development + validation (2011-22), controls, selection
    python3 research/noisegate/study.py --look     # + the ONE logged 2023-25 look and Jan-Oct 2026 (book legs)

Gate: Kaufman efficiency ratio on H1 (24 bars) or D1 (20 bars, day from 21:00 UTC), threshold = rolling 1-year quantile,
hysteresis 0.10, hold 6 H1 / 5 D1 bars. A trade uses the state of the last bar closed at or before its entry.
Output: research/results/noisegate/{study.json, RESULT.md}
"""
import os, sys, json, glob, datetime as dt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "seesare"))
sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import daily_queue_study as DQ   # noqa: E402
import cyclegoal as G            # noqa: E402

OUT = os.path.join(ROOT, "research", "results", "noisegate")
HORIZON = {"fast": dict(minutes=60, offset=0, n=24, win=6000, hold=6),
           "slow": dict(minutes=1440, offset=21 * 60, n=20, win=250, hold=5)}
THETAS = (0.50, 0.67)
HYST = 0.10
TREND = ("VolBreakout", "Donchian", "EMA20-50", "WeeklySweep_FollowThrough")
REVERT = ("S1_reversion", "RSI2", "Bollinger", "close_beyond_reversal")
Y20, Y23, Y26 = (int(dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp()) for y in (2020, 2023, 2026))


def sym_of(name):
    for p, s in (("GBPJPY", "GBPJPY"), ("EURGBP", "EURGBP"), ("EUR_", "EURUSD"), ("eurusd", "EURUSD"), ("XAU", "XAUUSD"),
                 ("JPY_", "USDJPY"), ("tokyo", "USDJPY"), ("GBP_", "GBPUSD")):
        if name.startswith(p):
            return s
    raise KeyError(name)


def kind_of(name):
    if any(k in name for k in TREND):
        return "trend"
    if any(k in name for k in REVERT):
        return "revert"
    return "flow"


def m1_closes(sym, with2026):
    fs = sorted(glob.glob(os.path.join(ROOT, "data", f"{sym}_M1_bid_*.npz")))
    if with2026:
        fs += [os.path.join(ROOT, "data", "holdout", f"{sym}_M1_bid_2026.npz")]
    ts, c = [], []
    for f in fs:
        d = np.load(f); ts.append(d["ts"] // 1000); c.append(d["c"].astype(float))
    t = np.concatenate(ts).astype(np.int64); x = np.concatenate(c)
    o = np.argsort(t, kind="stable"); t, x = t[o], x[o]
    k = np.r_[True, t[1:] != t[:-1]]
    return t[k], x[k]


def bars(sym, h, with2026):
    """Bar close times (last minute + 60 s) and closes."""
    if sym == "GBPJPY":
        a = bars("GBPUSD", h, with2026); b = bars("USDJPY", h, with2026)
        s = pd.Series(a[1], index=a[0]); u = pd.Series(b[1], index=b[0])
        j = pd.concat([s, u], axis=1, join="inner")
        return j.index.to_numpy(np.int64), (j.iloc[:, 0] * j.iloc[:, 1]).to_numpy()
    t, c = m1_closes(sym, with2026)
    H = HORIZON[h]; sec = H["minutes"] * 60
    key = (t - H["offset"] * 60) // sec
    ends = np.r_[np.flatnonzero(key[1:] != key[:-1]), len(t) - 1]
    tc = key[ends] * sec + H["offset"] * 60 + sec          # nominal bar close time
    return tc.astype(np.int64), c[ends]


def gate_state(c, h, theta):
    H = HORIZON[h]; n = H["n"]
    s = pd.Series(c)
    er = (s - s.shift(n)).abs() / s.diff().abs().rolling(n).sum()
    q_open = er.rolling(H["win"], min_periods=H["win"] // 2).quantile(theta).shift(1)      # past year only
    q_close = er.rolling(H["win"], min_periods=H["win"] // 2).quantile(theta - HYST).shift(1)
    e, qo, qc = er.to_numpy(), q_open.to_numpy(), q_close.to_numpy()
    st = np.zeros(len(c), bool); is_open = False; held = 0
    for i in range(len(c)):
        if not (np.isfinite(e[i]) and np.isfinite(qo[i])):
            st[i] = False; continue
        if not is_open and e[i] >= qo[i]:
            is_open, held = True, 0
        elif is_open:
            held += 1
            if held >= H["hold"] and e[i] < qc[i]:
                is_open = False
        st[i] = is_open
    return st, e


_GATES = {}


def gate_at(sym, h, theta, t_in, with2026):
    k = (sym, h, theta, with2026)
    if k not in _GATES:
        tc, c = bars(sym, h, with2026)
        st, e = gate_state(c, h, theta)
        _GATES[k] = (tc, st)
    tc, st = _GATES[k]
    i = np.searchsorted(tc, np.asarray(t_in, np.int64), side="right") - 1
    return np.where(i >= 0, st[np.maximum(i, 0)], False)


def configs():
    return [dict(h=h, theta=th, policy=p) for h in HORIZON for th in THETAS for p in ("textbook", "by-type")]


def passes(name, open_, policy):
    if policy == "by-type" and kind_of(name) == "revert":
        return ~open_
    return open_


def s_of(r):
    r = np.asarray(r, float)
    return float(r.mean() / r.std(ddof=1)) if len(r) > 2 else float("nan")


def pool(legs, cfg, with2026=False):
    """Rows (t_in, r, leg index, passed) of all legs in time order."""
    rows = []
    for i, g in enumerate(legs):
        o = gate_at(sym_of(g["name"]), cfg["h"], cfg["theta"], g["t_in"], with2026) if cfg else np.ones(len(g["r"]), bool)
        p = passes(g["name"], o, cfg["policy"]) if cfg else o
        rows.append(np.c_[g["t_in"], g["r"], np.full(len(g["r"]), i), p])
    T = np.vstack(rows)
    return T[np.argsort(T[:, 0], kind="stable")]


def period_mask(t, per):
    return {"2011-19": t < Y20, "2020-22": (t >= Y20) & (t < Y23), "2023-25": (t >= Y23) & (t < Y26),
            "2026": t >= Y26}[per]


def summary(r, t):
    if len(r) < 3:
        return dict(trades=int(len(r)))
    sc = G.score(r, t)
    seq = sc.get("sequence") or {}
    return dict(trades=int(len(r)), E=round(float(np.mean(r)), 4), s=round(s_of(r), 4), win=round(float(np.mean(r > 0)), 3),
                cycle_at_3_6=sc.get("cycle_mean_pct_at_cap", {}).get("3.6"), trades_per_year=seq.get("trades_per_year"))


def random_control(T, m, s_gated, draws=2000, seed=7):
    """Random gates keeping the same number of passed trades per leg in the period."""
    rng = np.random.default_rng(seed)
    r, leg, p = T[m, 1], T[m, 2].astype(int), T[m, 3].astype(bool)
    idx = [np.flatnonzero(leg == k) for k in np.unique(leg)]
    keep_n = [int(p[ix].sum()) for ix in idx]
    out = np.empty(draws)
    for d in range(draws):
        sel = np.concatenate([rng.choice(ix, k, replace=False) for ix, k in zip(idx, keep_n) if k > 0])
        out[d] = s_of(r[np.sort(sel)])
    return dict(p_value=round(float(np.mean(out >= s_gated)), 4), random_s_median=round(float(np.median(out)), 4),
                random_s_95=round(float(np.quantile(out, 0.95)), 4))


def per_leg(legs, T, m):
    out = {}
    for i, g in enumerate(legs):
        k = m & (T[:, 2] == i)
        pa, bl = k & (T[:, 3] == 1), k & (T[:, 3] == 0)
        out[g["name"]] = dict(kind=kind_of(g["name"]), passed=int(pa.sum()), E_passed=round(float(T[pa, 1].mean()), 3) if pa.any() else None,
                              blocked=int(bl.sum()), E_blocked=round(float(T[bl, 1].mean()), 3) if bl.any() else None)
    return out


def study(look=False):
    legs = DQ.legs("zero_swaps")
    legs_sf = DQ.legs("zero_swapfree")
    base = pool(legs, None)
    res = dict(prereg="research/noisegate/PREREGISTRATION.md", configurations=len(configs()), ungated={}, configs=[])
    for per in ("2011-19", "2020-22"):
        m = period_mask(base[:, 0], per)
        res["ungated"][per] = summary(base[m, 1], base[m, 0])
    for cfg in configs():
        T = pool(legs, cfg); Tsf = pool(legs_sf, cfg)
        row = dict(config=cfg)
        for per in ("2011-19", "2020-22"):
            m = period_mask(T[:, 0], per); pa = m & (T[:, 3] == 1); bl = m & (T[:, 3] == 0)
            row[per] = dict(passed=summary(T[pa, 1], T[pa, 0]), blocked=summary(T[bl, 1], T[bl, 0]),
                            passed_swapfree=summary(Tsf[pa, 1], Tsf[pa, 0]), share_passed=round(float(pa.sum() / m.sum()), 3))
        m = period_mask(T[:, 0], "2011-19")
        row["control_2011_19"] = random_control(T, m, row["2011-19"]["passed"]["s"])
        row["per_leg_2011_19"] = per_leg(legs, T, m)
        row["beats_ungated_both"] = all(row[p]["passed"]["s"] > res["ungated"][p]["s"] for p in ("2011-19", "2020-22"))
        res["configs"].append(row)
        print(cfg, {p: (row[p]["passed"]["s"], row[p]["blocked"].get("s"), row[p]["share_passed"]) for p in ("2011-19", "2020-22")},
              "p", row["control_2011_19"]["p_value"], flush=True)
    ok = [r for r in res["configs"] if r["beats_ungated_both"]]
    sel = max(ok, key=lambda r: r["2011-19"]["passed"]["s"]) if ok else None
    res["selected"] = sel["config"] if sel else None
    if look and sel:
        cfg = sel["config"]
        T = pool(legs, cfg); Tsf = pool(legs_sf, cfg)
        m = period_mask(T[:, 0], "2023-25"); pa = m & (T[:, 3] == 1); bl = m & (T[:, 3] == 0)
        res["look_2023_25"] = dict(logged=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                                   ungated=summary(T[m, 1], T[m, 0]), passed=summary(T[pa, 1], T[pa, 0]),
                                   blocked=summary(T[bl, 1], T[bl, 0]), passed_swapfree=summary(Tsf[pa, 1], Tsf[pa, 0]),
                                   per_leg=per_leg(legs, T, m))
        L26 = DQ.legs("zero_swaps", y2026=True)
        T6 = pool(L26, cfg, with2026=True)
        m6 = period_mask(T6[:, 0], "2026"); pa6 = m6 & (T6[:, 3] == 1); bl6 = m6 & (T6[:, 3] == 0)
        res["forward_2026_book"] = dict(ungated=summary(T6[m6, 1], T6[m6, 0]), passed=summary(T6[pa6, 1], T6[pa6, 0]),
                                        blocked=summary(T6[bl6, 1], T6[bl6, 0]))
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "study.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = study(look="--look" in sys.argv)
    print("ungated", r["ungated"])
    print("selected", r["selected"])
    for k in ("look_2023_25", "forward_2026_book"):
        if k in r:
            print(k, {x: r[k][x] for x in ("ungated", "passed", "blocked")})
