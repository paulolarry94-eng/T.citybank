"""Repo funnel: awesome-systematic-trading "Payday anomaly" (S&P 500 earns more on the day after the 15th, when US
salaries arrive and are invested). Rules fixed 2026-11-01 BEFORE any result in research/repofunnel/PREREG.md section D.

Payday = the 15th; Saturday -> Friday 14th, Sunday -> Friday 13th (the source's rule). Long from the 20:00 UTC H1 bar of
payday to the 20:00 UTC bar of the next trading day (the source buys one minute before the close on payday and sells one
minute before the next day's close). If payday has no 19:00 UTC bar in our data (an exchange holiday) there is no trade
that month, as in the source; PREREG said "or the last trading day before it", which would need future data to know,
so it is not used (changed before any result). Market orders; catastrophe stop 5% (R = 5% of price). One configuration.
Markets US500, NAS100, GER40, UK100, JP225 (the source uses only the S&P 500; the others are breadth, as for TOM/OPEX).
Costs: lab estimates with overnight financing. Companion priors: TOM and option-expiry week rejected (no effect beyond
drift, 2026-11-01).
"""
import os, sys, datetime as dt
import numpy as np

NAME = "payday_indices_v1"
HYPOTHESIS = "Salary money arriving around the 15th lifts equity indexes on the next trading day."
RULES = __doc__
FAMILY = ["calendar", "flow", "seasonal", "index", "payday", "repo-funnel", "awesome-list"]
MARKETS = ["US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["H1"]
GRID = {"day": ["payday"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 50
STOP_CAP_ATR = 1e9
STOP_PCT = 0.05
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..")); sys.path.insert(0, _here)
import executors
from tom_indices_v2 import anchor_bars, first_bar_on_or_after


def paydays(y0=2010, y1=2027):
    out = []
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            d = dt.date(y, m, 15)
            if d.weekday() == 5:
                d -= dt.timedelta(days=1)
            elif d.weekday() == 6:
                d -= dt.timedelta(days=2)
            out.append((d - dt.date(1970, 1, 1)).days)
    return out


_PAY = paydays()
_PAYSET = set(_PAY)


def signals(B, p, M):
    t = np.asarray(B["t"], np.int64); c = np.asarray(B["c"], float)
    idx = np.flatnonzero(((t % 86400) // 3600 == 19) & np.isin(t // 86400, list(_PAYSET)))
    return [(int(i), 1, float(c[i] * (1 - STOP_PCT))) for i in idx]


def _exit_bars(B, p):
    anchor = anchor_bars(B)
    xb = {first_bar_on_or_after(anchor, d + 1) for d in _PAY}
    return (np.array(sorted(x for x in xb if x is not None), np.int64),) * 2


EXECUTOR = executors.exit_when(_exit_bars)
