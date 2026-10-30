"""Buy gold 18:00-20:00 Nigeria time (WAT = UTC+1, no daylight saving) = 17:00-19:00 UTC.
Each weekday: buy at the open of the entry minute (ask), sell at the open of the exit minute
(bid), all-in cost $0.45. Neighbouring windows and splits shown; values per trade in dollars
and in multiples of the cost."""
import os, sys, datetime as dt
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "orb"))
import core

M = core.Market("XAUUSD")
ts, o = M.ts, M.o
days = np.unique(ts // 86400)
yr_of = {int(d): dt.datetime.utcfromtimestamp(int(d) * 86400).year for d in days}


def window(h0, m0, h1, m1, side=1, dows=(0, 1, 2, 3, 4), us_dst=None):
    rows = []
    for d in days:
        wd = (d + 3) % 7
        if wd not in dows:
            continue
        t0 = d * 86400 + h0 * 3600 + m0 * 60; t1 = d * 86400 + h1 * 3600 + m1 * 60
        i0, i1 = np.searchsorted(ts, t0), np.searchsorted(ts, t1)
        if i1 >= len(ts) or ts[i0] - t0 > 120 or ts[i1] - t1 > 120:
            continue
        if us_dst is not None:
            D = dt.datetime.utcfromtimestamp(int(d) * 86400)
            from zoneinfo import ZoneInfo
            is_dst = bool(dt.datetime(D.year, D.month, D.day, 12, tzinfo=ZoneInfo("America/New_York")).dst())
            if is_dst != us_dst:
                continue
        mv = side * (o[i1] - o[i0]) - M.cost
        rows.append((yr_of[int(d)], mv, wd))
    return np.array(rows)


def show(label, A):
    y, x = A[:, 0], A[:, 1]
    i, s = x[y <= 2018], x[y >= 2019]
    t = lambda v: v.mean() / v.std() * np.sqrt(len(v))
    per = [x[y == q].mean() for q in range(2011, 2026) if (y == q).any()]
    print(f"{label:38s} n={len(x):4d} net ${x.mean():+.3f} ({x.mean()/M.cost:+.2f} cost) gross {(x.mean()+M.cost)/M.cost:+.2f} cost | "
          f"IS {i.mean():+.3f} t {t(i):+.2f} | OOS {s.mean():+.3f} t {t(s):+.2f} | yrs+ {sum(p > 0 for p in per)}/{len(per)}")
    return per


if __name__ == "__main__":
    per = show("BUY 18:00-20:00 WAT (17-19 UTC)", window(17, 0, 19, 0))
    print("   per year net $: " + " ".join(f"{11+i:02d}:{p:+.2f}" for i, p in enumerate(per)))
    for lab, args in (("BUY 18:00-19:00 WAT", (17, 0, 18, 0)), ("BUY 19:00-20:00 WAT", (18, 0, 19, 0)),
                      ("BUY 17:00-20:00 WAT", (16, 0, 19, 0)), ("BUY 18:00-21:00 WAT", (17, 0, 20, 0)),
                      ("BUY 18:00-22:00 WAT (before rollover)", (17, 0, 21, 0)), ("BUY 18:30-20:00 WAT", (17, 30, 19, 0))):
        show(lab, window(*args))
    for lab, kw in (("  US summer time (NY 13-15h)", dict(us_dst=True)), ("  US winter time (NY 12-14h)", dict(us_dst=False))):
        show(lab, window(17, 0, 19, 0, **kw))
    for wd, nm in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri")):
        show(f"  only {nm}", window(17, 0, 19, 0, dows=(wd,)))
