"""Hunt 2, step 1: where in the day (and month) do these markets move for structural reasons?

For every instrument: mean move of each UTC hour and each London-local hour on weekdays,
in multiples of the all-in round-trip cost, with t-statistics in 2011-2018 (in-sample) and
2019-2025 (out-of-sample) and the number of years with the same sign. Then two pre-declared
flow hypotheses from the literature:
  gotobi  USDJPY rises into the 09:55 JST Tokyo fix on 5/10/15/20/25/month-end business days
          (Japanese importers' dollar buying; Bessho et al., Ito & Yamada)
  wmr     moves into the 16:00 London WM/R fix reverse in the following hour (Evans 2018;
          Melvin & Prins 2015), strongest at month-end
"""
import os, sys, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "orb"))
import core

LDN = ZoneInfo("Europe/London"); TOK = ZoneInfo("Asia/Tokyo")


def hourly(M, tz=None):
    """One row per (day, hour): move from the first minute's open to the last minute's close."""
    ts = M.ts
    if tz is None:
        loc = ts
    else:   # local clock time via a per-day UTC offset
        days = np.unique(ts // 86400)
        off = {int(d): int(dt.datetime.fromtimestamp(int(d) * 86400 + 43200, tz).utcoffset().total_seconds()) for d in days}
        loc = ts + np.array([off[int(d)] for d in ts // 86400])
    key = loc // 3600
    st = np.flatnonzero(np.r_[True, key[1:] != key[:-1]]); en = np.r_[st[1:], len(ts)] - 1
    mv = M.c[en] - M.o[st]
    hr = (key[st] % 24).astype(int)
    day = loc[st] // 86400
    wd = ((day + 3) % 7) < 5
    yr = np.array([dt.datetime.utcfromtimestamp(int(t)).year for t in ts[st]])
    full = (en - st + 1) >= 45          # hour mostly present
    return dict(mv=mv[wd & full], hr=hr[wd & full], yr=yr[wd & full], day=day[wd & full])


def table(H, cost):
    out = []
    for h in range(24):
        k = H["hr"] == h
        x = H["mv"][k] / cost; y = H["yr"][k]
        a, b = x[y <= 2018], x[y >= 2019]
        ys = [x[y == yy].mean() for yy in range(2011, 2026) if (y == yy).sum() > 50]
        sgn = np.sign(x.mean())
        out.append((h, x.mean(), a.mean() / a.std() * np.sqrt(len(a)), b.mean() / b.std() * np.sqrt(len(b)),
                    sum(np.sign(v) == sgn for v in ys), len(ys)))
    return out


def main():
    for sym in core.SYMS:
        M = core.Market(sym)
        for name, tz in (("UTC", None), ("London", LDN)):
            H = hourly(M, tz)
            print(f"\n{sym} by {name} hour: mean move in cost units | t 2011-18 | t 2019-25 | years same sign")
            rows = table(H, M.cost)
            for h, m, t1, t2, ny, n in rows:
                flag = " <==" if abs(t1) > 2.5 and np.sign(t1) == np.sign(t2) and abs(t2) > 1.5 else ""
                print(f"  {h:02d}  {m:+.3f}  {t1:+5.2f}  {t2:+5.2f}  {ny:2d}/{n}{flag}")


if __name__ == "__main__":
    main()
