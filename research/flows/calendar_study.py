"""Calendar ideas from the awesome-systematic-trading list, drift-controlled (companion to the lab strategies
tom_indices_v1, opex_week_indices_v1, oil_equity_v1). Fixed 2026-11-01 BEFORE any result.

A long-only index window always looks good in a rising market. So every effect is measured AGAINST the other days:
  daily index return = 20:00 UTC close to the next trading day's 20:00 UTC close (trading day = weekday with a 19:00 bar);
  TOM days = the last trading day of a month and the first three of the next; OPEX days = the trading days from the day
  after entry to expiry day (see opex_week_indices_v1); everything else = "other days".
  Reported per market and period (2011-19, 2020-22, 2023-25): mean daily return on window days vs other days (bp), the
  difference and its t-statistic (Welch), and the number of window days.
Oil: next-month index return (month-end to month-end) after WTI fell vs after it rose, difference and t.
No costs here (the lab charges them); this answers only "is there an effect beyond drift?".
Output: research/results/flows/calendar_study.json
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
for _p in (R, os.path.join(R, "northstar"), os.path.join(R, "truth"), os.path.join(R, "truth", "strategies")):
    sys.path.insert(0, _p)
import engine as E
import tom_indices_v1 as TOM
import opex_week_indices_v1 as OPX
import oil_equity_v1 as OIL

MARKETS = TOM.MARKETS
PERIODS = {"2011-19": (2011, 2019), "2020-22": (2020, 2022), "2023-25": (2023, 2025)}
OUT = os.path.join(R, "results", "flows"); os.makedirs(OUT, exist_ok=True)


def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3:
        return dict(n_window=int(len(a)))
    d = a.mean() - b.mean(); se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return dict(n_window=int(len(a)), window_bp=round(float(a.mean() * 1e4), 2), other_bp=round(float(b.mean() * 1e4), 2),
                diff_bp=round(float(d * 1e4), 2), t=round(float(d / se), 2))


def market_days(sym):
    ts, o, h, l, c = E.load_m1(sym)
    bt, bo, bh, bl, bc, nxt = E.resample(ts, o, h, l, c, 60)
    B = dict(t=bt, c=bc)
    idx, day, mkey = TOM.trading_days(B)
    close = bc[idx]
    ret = np.r_[np.nan, close[1:] / close[:-1] - 1]
    year = (day.astype("datetime64[D]").astype("datetime64[Y]").astype(int) + 1970)
    return B, idx, day, mkey, close, ret, year


def main():
    res = {"tom": {}, "opex": {}, "oil": {}}
    sign = OIL.oil_month_sign()
    for sym in MARKETS:
        B, idx, day, mkey, close, ret, year = market_days(sym)
        n = len(idx)
        tom = np.zeros(n, bool)
        groups = TOM._month_groups(mkey)
        for g0, g1 in zip(groups[:-1], groups[1:]):
            tom[g0[1] - 1] = True                              # last trading day of the month
            tom[g1[0]:min(g1[0] + 3, g1[1])] = True            # first three of the next month
        opx = np.zeros(n, bool)
        pos = {int(b): k for k, b in enumerate(idx)}
        for a, b in OPX._plan(B, sym):
            ka, kb = pos[a], pos[b]
            opx[ka + 1:kb + 1] = True
        ok = np.isfinite(ret)
        res["tom"][sym] = {}; res["opex"][sym] = {}
        for pn, (y0, y1) in PERIODS.items():
            m = ok & (year >= y0) & (year <= y1)
            res["tom"][sym][pn] = welch(ret[m & tom], ret[m & ~tom])
            res["opex"][sym][pn] = welch(ret[m & opx], ret[m & ~opx])
        # oil: month-end to month-end index returns, by the sign of the previous month's oil return
        me = {}
        for a, b in groups:
            me[int(mkey[b - 1])] = float(close[b - 1])
        ks = sorted(me); rows = []
        for k0, k1 in zip(ks[:-1], ks[1:]):
            if k1 == k0 + 1 and k0 in sign:
                rows.append((k1, sign[k0], me[k1] / me[k0] - 1))
        M = pd.DataFrame(rows, columns=["mkey", "oil_sign_prev", "ret"])
        M["year"] = M.mkey // 12 + 1970
        res["oil"][sym] = {}
        for pn, (y0, y1) in PERIODS.items():
            g = M[(M.year >= y0) & (M.year <= y1)]
            res["oil"][sym][pn] = welch(g[g.oil_sign_prev < 0].ret, g[g.oil_sign_prev > 0].ret) | {"n_months": int(len(g))}
        print(sym, "done", flush=True)
    json.dump(res, open(os.path.join(OUT, "calendar_study.json"), "w"), indent=1)
    for fam in ("tom", "opex"):
        print(f"\n== {fam}: window-day minus other-day daily return (bp), t")
        for sym, v in res[fam].items():
            print(f"  {sym:7s}", {p: (x.get("diff_bp"), x.get("t"), x.get("n_window")) for p, x in v.items()})
    print("\n== oil: next-month index return after oil FELL minus after it ROSE (bp), t")
    for sym, v in res["oil"].items():
        print(f"  {sym:7s}", {p: (x.get("diff_bp"), x.get("t"), x.get("n_months")) for p, x in v.items()})


if __name__ == "__main__":
    main()
