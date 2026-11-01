"""Tokyo fix on "Gotobi" days, USDJPY (Q10/Q15: a flow with a payer). Rules fixed 2026-11-01 BEFORE any result.

Why it might pay: Japanese importers buy dollars at the Tokyo fixing (09:55 JST = 00:55 UTC; Japan has no daylight
saving) and settle most on gotobi days: the 5th, 10th, 15th, 20th, 25th and the last day of the month, moved to the previous
Tokyo business day when it falls on a weekend, a Japanese holiday or the bank year-end (31 Dec - 3 Jan). Published research
reports the dollar rising into the fix on those days and easing after it. Nothing here was taken from our own data.
Trades (market orders at the open of the minute named, exits at the open of the minute named):
  pre2300   buy 23:00 UTC (08:00 JST) on the evening before a gotobi fix, sell 00:55 UTC (the fix);
  pre0000   buy 00:00 UTC (09:00 JST, Tokyo open), sell 00:55 UTC;
  post0055  sell 00:55 UTC (after the fix), buy back 02:00 UTC.
  Protective stop 0.3% of price (a catastrophe stop, rarely touched in an hour or two; R = 0.3% of price). No overnight
  swap (no 22:00 UTC rollover inside the trade).
Grid: trade [pre2300, pre0000, post0055] = 3 configurations, gotobi days only (other days are the control, reported by
  research/flows/tokyo_fix_study.py, not traded).
Costs: Exness Zero realistic USDJPY (1.35 pips round trip: commission is charged in dollars, so it costs more in yen).
Priors: no earlier idea shares the calendar/fix/flow tags; Hunt 2 found the London 4 pm fix reversal real but worth half a
  cost, and month-end flows 1.4-1.9 costs but only 12 trades a year.
"""
import os, json, sys, datetime as dt
import numpy as np

NAME = "tokyo_fix_gotobi_v1"
HYPOTHESIS = ("Japanese importers' dollar buying at the 09:55 JST Tokyo fix on gotobi days lifts USDJPY into the fix "
              "(and it eases after), by more than the round-trip cost.")
RULES = __doc__
FAMILY = ["calendar", "flow", "fix", "intraday", "usdjpy", "seasonal"]
MARKETS = ["USDJPY"]
TIMEFRAMES = ["M5"]
GRID = {"trade": ["pre2300", "pre0000", "post0055"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 50
STOP_CAP_ATR = 1e9
STOP_PCT = 0.003
_here = os.path.dirname(os.path.abspath(__file__))
_cz = json.load(open(os.path.join(_here, "..", "costs_exness_zero.json")))["realistic"]
COSTS = {"USDJPY": _cz["USDJPY"]}
sys.path.insert(0, os.path.join(_here, ".."))
import executors

# entry bar = the 5-minute bar that CLOSES at the entry minute (the lab enters at the next bar's open)
ENTRY = {"pre2300": (22 * 60 + 55, 1, +1), "pre0000": (23 * 60 + 55, 1, +1), "post0055": (50, 0, -1)}  # (bar start min, days to fix, side)
EXIT_BAR = {"pre2300": 50, "pre0000": 50, "post0055": 115}                 # bar start minute whose close is the exit minute


def _business(d, jp):
    return d.weekday() < 5 and d not in jp and not (d.month == 12 and d.day == 31) and not (d.month == 1 and d.day <= 3)


def gotobi_days(y0=2010, y1=2027):
    import holidays, calendar
    jp = holidays.Japan(years=range(y0, y1 + 1))
    out = set()
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            last = calendar.monthrange(y, m)[1]
            for day in (5, 10, 15, 20, 25, last):
                d = dt.date(y, m, day)
                while not _business(d, jp):
                    d -= dt.timedelta(days=1)
                out.add(d)
    return out


_GOTOBI = None


def signals(B, p, M):
    global _GOTOBI
    if _GOTOBI is None:
        _GOTOBI = gotobi_days()
    start_min, days_ahead, side = ENTRY[p["trade"]]
    t = np.asarray(B["t"]); c = np.asarray(B["c"], float)
    mins = (t % 86400) // 60
    rows = []
    for i in np.flatnonzero(mins == start_min):
        fix = dt.datetime.utcfromtimestamp(int(t[i])).date() + dt.timedelta(days=days_ahead)
        if fix in _GOTOBI:
            stop = c[i] * (1 - STOP_PCT) if side > 0 else c[i] * (1 + STOP_PCT)
            rows.append((int(i), side, float(stop)))
    return rows


def _exit_bars(B, p):
    t = np.asarray(B["t"]); mins = (t % 86400) // 60
    xb = np.flatnonzero(mins == EXIT_BAR[p["trade"]])
    return xb, xb                                                     # longs and shorts leave at the same minute


EXECUTOR = executors.exit_when(_exit_bars)
