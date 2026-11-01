"""Option-Expiration Week effect in equity indexes, v2 (same idea and window as opex_week_indices_v1, which FAILED the
lab's look-ahead check by finding trading days from later bars). v2 uses only the calendar. Fixed 2026-11-01 before any
lab result; the companion study research/flows/calendar_study.py had already shown the drift-controlled effect (disclosed).
Expiry: third Friday (US500, NAS100, GER40, UK100), second Friday (JP225). Trade: long from 20:00 UTC on the Friday
  before expiry week to 20:00 UTC on expiry Friday (if that Friday has no 19:00 UTC bar, the last trading day before it).
  No trade if the entry Friday has no 19:00 UTC bar. Market orders; catastrophe stop 5% (R = 5% of price).
One configuration. Markets US500, NAS100, GER40, UK100, JP225; H1. Costs: lab estimates with overnight financing.
"""
import os, sys, datetime as dt
import numpy as np

NAME = "opex_week_indices_v2"
HYPOTHESIS = "Option dealers' hedging flows lift equity indexes in the week of the monthly option expiry."
RULES = __doc__
FAMILY = ["calendar", "flow", "seasonal", "index", "options-expiry", "awesome-list"]
MARKETS = ["US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["H1"]
GRID = {"week": ["opex"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 50
STOP_CAP_ATR = 1e9
STOP_PCT = 0.05
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, ".."))
import executors


def expiry_days(sym, y0=2010, y1=2027):
    nth = 2 if sym == "JP225" else 3; ep = dt.date(1970, 1, 1); out = []
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            fr = [d for d in (dt.date(y, m, 1) + dt.timedelta(days=k) for k in range(31)) if d.month == m and d.weekday() == 4]
            out.append((fr[nth - 1] - ep).days)
    return out


def signals(B, p, M):
    t = np.asarray(B["t"], np.int64); c = np.asarray(B["c"], float)
    entry_days = [e - 7 for e in expiry_days(M.sym)]                   # the Friday before expiry week
    idx = np.flatnonzero(((t % 86400) // 3600 == 19) & np.isin(t // 86400, entry_days))
    return [(int(i), 1, float(c[i] * (1 - STOP_PCT))) for i in idx]


_SYM = {}


def _exit_bars(B, p):
    t = np.asarray(B["t"], np.int64)
    idx = np.flatnonzero((t % 86400) // 3600 == 19); day = t[idx] // 86400
    xb = []
    for e in expiry_days(_SYM.get("sym", "")):
        k = np.searchsorted(day, e, side="right") - 1                  # expiry Friday or the trading day before it
        if k >= 0 and day[k] > e - 7:
            xb.append(int(idx[k]))
    xb = np.array(sorted(set(xb)), np.int64)
    return xb, xb


def _executor():
    inner = executors.exit_when(_exit_bars)
    def run(M, B, C, p, **kw):
        _SYM["sym"] = M.sym
        return inner(M, B, C, p, **kw)
    return run


EXECUTOR = _executor()
