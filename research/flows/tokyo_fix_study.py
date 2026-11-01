"""Tokyo fix study (companion to truth/strategies/tokyo_fix_gotobi_v1.py), fixed 2026-11-01 BEFORE any result.

For every Tokyo business-day fix (00:55 UTC) 2011-2025 and 2026, USDJPY move in pips (1 pip = 0.01) from the 1-minute opens:
  pre2300  23:00 UTC (evening before) -> 00:55;  pre0000  00:00 -> 00:55;  post0055  00:55 -> 02:00 (sign: + = dollar up).
Gotobi days (the hypothesis) vs every other Tokyo business day (the control). Reported by period (2011-19, 2020-22, 2023-25,
Jan-Sep 2026, Oct 2026): mean pips, t, share of up moves; and the trade result after the Exness Zero realistic cost
(1.35 pips round trip; long for pre*, short for post0055). No stop, no selection: one number per cell.
Output: research/results/flows/tokyo_fix.json
"""
import os, sys, json, datetime as dt
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(R, "truth", "strategies"))
import tokyo_fix_gotobi_v1 as T

DATA = os.path.join(R, "..", "data"); OUT = os.path.join(R, "results", "flows"); os.makedirs(OUT, exist_ok=True)
COST_PIPS = T.COSTS["USDJPY"] / 0.01
OCT26 = dt.date(2026, 10, 1)


def load():
    parts = []
    for y in range(2010, 2026):
        f = os.path.join(DATA, f"USDJPY_M1_bid_{y}.npz")
        if os.path.exists(f):
            d = np.load(f); parts.append(pd.Series(d["o"], index=pd.to_datetime(d["ts"] // 1000, unit="s")))
    d = np.load(os.path.join(DATA, "holdout", "USDJPY_M1_bid_2026.npz"))
    parts.append(pd.Series(d["o"], index=pd.to_datetime(d["ts"] // 1000, unit="s")))
    s = pd.concat(parts); return s[~s.index.duplicated()].sort_index()


def px_at(s, ts):
    """Open of the minute at ts, or of the first minute within 5 minutes after it (data gaps)."""
    i = s.index.searchsorted(ts)
    if i < len(s) and s.index[i] - ts <= pd.Timedelta(minutes=5):
        return float(s.iloc[i])
    return np.nan


def stats(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    if len(x) < 2:
        return dict(n=int(len(x)))
    return dict(n=int(len(x)), mean_pips=round(float(x.mean()), 2), t=round(float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))), 2),
                up_share=round(float((x > 0).mean()), 3))


def main():
    import holidays
    s = load()
    jp = holidays.Japan(years=range(2010, 2028))
    gotobi = T.gotobi_days()
    rows = []
    d = dt.date(2011, 1, 1)
    while d <= dt.date(2026, 10, 30):
        if T._business(d, jp):
            f = pd.Timestamp(d) + pd.Timedelta(minutes=55)
            p23 = px_at(s, f - pd.Timedelta(minutes=115)); p00 = px_at(s, f - pd.Timedelta(minutes=55))
            p55 = px_at(s, f); p02 = px_at(s, f + pd.Timedelta(minutes=65))
            rows.append(dict(date=d, gotobi=d in gotobi, pre2300=(p55 - p23) / 0.01, pre0000=(p55 - p00) / 0.01,
                             post0055=(p02 - p55) / 0.01))
        d += dt.timedelta(days=1)
    D = pd.DataFrame(rows); D["year"] = [x.year for x in D.date]
    per = {"2011-19": D.year <= 2019, "2020-22": D.year.between(2020, 2022), "2023-25": D.year.between(2023, 2025),
           "Jan-Sep 2026": (D.year == 2026) & (D.date < OCT26), "Oct 2026": D.date >= OCT26}
    res = {"cost_pips_round_trip": round(COST_PIPS, 2), "days": int(len(D)), "gotobi_days": int(D.gotobi.sum()), "moves": {}, "trades_after_cost": {}}
    for leg, sign in (("pre2300", 1), ("pre0000", 1), ("post0055", -1)):
        res["moves"][leg] = {p: {"gotobi": stats(D[m & D.gotobi][leg]), "other days": stats(D[m & ~D.gotobi][leg])} for p, m in per.items()}
        res["trades_after_cost"][leg] = {p: stats(sign * D[m & D.gotobi][leg] - COST_PIPS) for p, m in per.items()}
    json.dump(res, open(os.path.join(OUT, "tokyo_fix.json"), "w"), indent=1, default=str)
    for leg in res["moves"]:
        print(f"\n{leg}  (pips, + = dollar up)")
        for p, v in res["moves"][leg].items():
            a = res["trades_after_cost"][leg][p]
            print(f"  {p:13s} gotobi {v['gotobi']}  | other {v['other days']}  | trade after cost {a.get('mean_pips')} (t {a.get('t')})")


if __name__ == "__main__":
    main()
