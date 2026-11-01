"""Option-Expiration Week effect in equity indexes (awesome-systematic-trading: "Option-Expiration Week Effect", paper
Sharpe 0.452). Owner chose it 2026-11-01. Rules fixed BEFORE any result.
Why it might pay: in the week of the monthly option expiry, option dealers' hedging flows (and the unwinding of hedges)
push large-cap stocks and their indexes up on average.
Expiry day: the third Friday of the month for US500, NAS100, GER40 and UK100; the second Friday for JP225 (Japan's SQ);
  if that Friday is not a trading day in the data, the trading day before it.
Trade: long from 20:00 UTC on the last trading day before the Monday of expiry week to 20:00 UTC on expiry day
  (Friday close to Friday close, as the paper's weekly return). Market orders at the 20:00 bar's open; catastrophe stop
  5% below entry (R = 5% of price). Trading day = weekday with a 19:00 UTC hourly bar (see tom_indices_v1).
Grid: one configuration. Markets US500, NAS100, GER40, UK100, JP225; timeframe H1.
Costs: lab estimates for index CFDs with overnight financing for each night (a week = 7 nights incl. the weekend).
  No 2026 index data yet.
Companion drift-controlled study: research/flows/calendar_study.py.
"""
import os, sys, datetime as dt
import numpy as np

NAME = "opex_week_indices_v1"
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
sys.path.insert(0, os.path.join(_here, "..")); sys.path.insert(0, _here)
import executors
from tom_indices_v1 import trading_days


def expiry_dates(sym, y0=2010, y1=2027):
    nth = 2 if sym == "JP225" else 3
    out = []
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            d = dt.date(y, m, 1)
            fr = [d + dt.timedelta(days=k) for k in range(31) if (d + dt.timedelta(days=k)).month == m and (d + dt.timedelta(days=k)).weekday() == 4]
            out.append(fr[nth - 1])
    return out


def _plan(B, sym):
    """[(entry bar, exit bar)] for every expiry: exit = the expiry day's 19:00 bar (or the trading day before),
    entry = the last trading day before that week's Monday."""
    idx, day, _ = trading_days(B)
    epoch = dt.date(1970, 1, 1); plan = []
    for e in expiry_dates(sym):
        en = (e - epoch).days
        k = np.searchsorted(day, en, side="right") - 1          # expiry day or the trading day before it
        if k < 1 or day[k] < en - 4:
            continue
        monday = en - 4
        j = np.searchsorted(day, monday, side="left") - 1       # last trading day before Monday
        if j < 0 or j >= k:
            continue
        plan.append((int(idx[j]), int(idx[k])))
    return plan


def signals(B, p, M):
    c = np.asarray(B["c"], float)
    return [(a, 1, float(c[a] * (1 - STOP_PCT))) for a, b in _plan(B, M.sym)]


_SYM = {}


def _exit_bars(B, p):
    xb = np.array(sorted({b for a, b in _plan(B, _SYM.get("sym", ""))}), np.int64)
    return xb, xb


def _executor():
    inner = executors.exit_when(_exit_bars)
    def run(M, B, C, p, **kw):
        _SYM["sym"] = M.sym                                      # JP225 expires on the second Friday
        return inner(M, B, C, p, **kw)
    return run


EXECUTOR = _executor()
