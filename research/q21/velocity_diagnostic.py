"""Q21 diagnostic: does a tick-volume surge on an opening-range breakout predict range expansion, and does it predict
direction? Descriptive only (no strategy is selected). Fixed 2026-11-01 before any result.

Markets: the only ones with tick volume every year: USDJPY 2011-2025; GER40 2020-2025 (no tick volume before 2020).
Sessions (local time, daylight saving handled): Tokyo 09:00, London 08:00, New York 08:00 (inside the London-New York overlap);
GER40: London and New York only.
Event: the 15-minute opening range; the first M1 close beyond its high (up) or low (down) within 180 minutes; one per session day.
Activity ("velocity surge"): tick volume of the breakout minute / mean tick volume of the 60 minutes before it.
Outcomes over the next 60 minutes, in units of the 14-day average daily range (ATR_D, prior days only):
  expansion      = (highest high - lowest low) / ATR_D        (range expansion, either direction)
  follow_through = (close after 60 min - breakout close) x direction / ATR_D   (direction: does it keep going?)
  mfe, mae       = largest move with / against the breakout / ATR_D
Reported for 2011-2019 and 2020-2025 separately: Spearman rank correlation of activity with each outcome, and the mean of each
outcome by activity quintile (quintile edges from the same period). Cost for scale: Exness Zero all-in round trip
(USDJPY 0.013465), shown in ATR_D units.
Output: research/results/q21/velocity_diagnostic.json
"""
import os
import sys
import json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import seesare_verify as S   # noqa: E402  (DST-aware venue clocks)

OUT = os.path.join(ROOT, "research", "results", "q21")
SESSIONS = {"tokyo_0900": (S.TOKYO, 9, 0), "london_0800": (S.LONDON, 8, 0), "newyork_0800": (S.NEW_YORK, 8, 0)}
PLAN = {"USDJPY": (2011, 2025, ("tokyo_0900", "london_0800", "newyork_0800")), "GER40": (2020, 2025, ("london_0800", "newyork_0800"))}
COST = {"USDJPY": 0.013465, "GER40": None}
OR_MIN, WAIT_MIN, HORIZON, PRE = 15, 180, 60, 60


def load(sym, y0, y1):
    parts = [np.load(os.path.join(ROOT, "data", f"{sym}_M1_bid_{y}.npz")) for y in range(y0, y1 + 1)]
    ts = np.concatenate([p["ts"] // 1000 for p in parts]).astype(np.int64)
    o, h, l, c, v = (np.concatenate([p[k] for p in parts]).astype(float) for k in ("o", "h", "l", "c", "v"))
    idx = np.argsort(ts, kind="stable")
    ts, o, h, l, c, v = ts[idx], o[idx], h[idx], l[idx], c[idx], v[idx]
    keep = np.r_[True, ts[1:] != ts[:-1]]
    return ts[keep], o[keep], h[keep], l[keep], c[keep], v[keep]


def atr_d(ts, h, l):
    day = ts // 86400
    df = pd.DataFrame(dict(day=day, h=h, l=l)).groupby("day").agg(h=("h", "max"), l=("l", "min"))
    rng = (df.h - df.l)
    return (rng.rolling(14).mean().shift(1)).to_dict()


def events(sym, ts, o, h, l, c, v, atr, sess):
    venue, hh, mm = SESSIONS[sess]
    out = []
    d0, d1 = int(ts[0] // 86400), int(ts[-1] // 86400)
    for day in range(d0, d1 + 1):
        if S.day_of_week(day * 86400) >= 5:
            continue
        t_open = S.venue_to_utc(venue, day * 86400 + hh * 3600 + mm * 60)
        a = np.searchsorted(ts, t_open)
        b = np.searchsorted(ts, t_open + OR_MIN * 60)
        if b - a < int(OR_MIN * 0.8) or b >= len(ts):
            continue
        orh, orl = h[a:b].max(), l[a:b].min()
        e = np.searchsorted(ts, t_open + (OR_MIN + WAIT_MIN) * 60)
        A = atr.get(int(t_open // 86400))
        if A is None or not np.isfinite(A) or A <= 0:
            continue
        for i in range(b, min(e, len(ts) - 1)):
            side = 1 if c[i] > orh else (-1 if c[i] < orl else 0)
            if side == 0:
                continue
            j = np.searchsorted(ts, ts[i] + HORIZON * 60)
            p = np.searchsorted(ts, ts[i] - PRE * 60)
            if j >= len(ts) or j - i < HORIZON * 0.8 or i - p < PRE * 0.8:
                break
            pre = v[p:i].mean()
            if pre <= 0:
                break
            hi, lo = h[i + 1:j + 1].max(), l[i + 1:j + 1].min()
            ft = (c[j] - c[i]) * side
            mfe = (hi - c[i]) if side > 0 else (c[i] - lo)
            mae = (c[i] - lo) if side > 0 else (hi - c[i])
            out.append(dict(year=int(pd.Timestamp(ts[i], unit="s").year), session=sess, activity=v[i] / pre,
                            expansion=(hi - lo) / A, follow_through=ft / A, mfe=mfe / A, mae=mae / A, atr=A))
            break
    return out


def summarize(df):
    res = {}
    for name, a, b in (("2011-2019", 2011, 2019), ("2020-2025", 2020, 2025)):
        x = df[(df.year >= a) & (df.year <= b)]
        if len(x) < 50:
            continue
        q = pd.qcut(x.activity.rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
        res[name] = dict(n=len(x),
                         spearman={k: round(float(x.activity.corr(x[k], method="spearman")), 3)
                                   for k in ("expansion", "follow_through", "mfe", "mae")},
                         by_quintile={int(k): {m: round(float(g[m].mean()), 4) for m in ("activity", "expansion", "follow_through",
                                                                                           "mfe", "mae")} | {"n": len(g)}
                                      for k, g in x.groupby(q, observed=True)},
                         follow_through_t={int(k): round(float(g.follow_through.mean() / g.follow_through.std(ddof=1)
                                                               * np.sqrt(len(g))), 2) for k, g in x.groupby(q, observed=True)})
    return res


if __name__ == "__main__":
    out = dict(design=__doc__, results={})
    for sym, (y0, y1, sessions) in PLAN.items():
        ts, o, h, l, c, v = load(sym, y0, y1)
        atr = atr_d(ts, h, l)
        rows = []
        for sess in sessions:
            rows += events(sym, ts, o, h, l, c, v, atr, sess)
        df = pd.DataFrame(rows)
        cost_atr = round(COST[sym] / float(df.atr.median()), 4) if COST[sym] else None
        out["results"][sym] = dict(cost_in_atr_d=cost_atr, all_sessions=summarize(df),
                                   by_session={s: summarize(df[df.session == s]) for s in sessions})
        print(sym, "events", len(df), "cost in ATR_D units", cost_atr)
        for per, r in out["results"][sym]["all_sessions"].items():
            print(" ", per, r["n"], "spearman", r["spearman"])
            for k, g in r["by_quintile"].items():
                print(f"    Q{k}: activity {g['activity']:.2f} expansion {g['expansion']:.3f} follow {g['follow_through']:+.4f} "
                      f"(t {r['follow_through_t'][k]}) mfe {g['mfe']:.3f} mae {g['mae']:.3f} n {g['n']}")
        for s, rr in out["results"][sym]["by_session"].items():
            for per, r in rr.items():
                print(f"  {s:13s} {per}: n {r['n']} spearman {r['spearman']}")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "velocity_diagnostic.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
