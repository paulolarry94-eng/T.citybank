"""Batch 01, candidate 11: leveraged / vol-target fund rebalancing into the US cash close. Rules fixed 2026-11-02 BEFORE any result.

Payer: daily-leveraged and inverse ETPs must rebalance at the close in the direction of the day's move (buy after up days,
sell after down days), and short-gamma dealers hedge the same way; the size grows with the size of the move. Direction is
known before the close. Coded:
  move    price at the entry minute minus the anchor: prev_close = the 16:00 New York close of the previous NYSE session
          (close of the 15:55 M5 bar); open = the 09:30 open today (open of the 09:30 M5 bar). New York time, DST-aware.
  entry   market order at 15:30 or 15:45 New York WITH the move; no trade if move = 0.
  filter  flow days only: |move| >= the median |move| of the previous 60 sessions (same anchor and entry time; prior days
          only). The CONTROL is the same rule on the below-median days (research/batch01/controls.py, never selected).
  stop    0.5 x the average daily range of the previous 20 New York sessions (the batch's R); exit at 16:00 New York
          (the open of the 16:00 bar) if not stopped. No overnight hold, no swap.
  days    NYSE sessions only (holidays from the NYSE calendar); early closes skipped (day after Thanksgiving, 24 Dec, 3 Jul).
Grid: anchor [prev_close, open] x entry [15:30, 15:45] = 4 configurations; US500 and NAS100 (both pre-chosen: the US cash
  indices with leveraged ETPs; GER40 / UK100 close at other hours).
Costs: RoboForex Prime published (US500 0.5, NAS100 0.97 points round trip; research/truth/costs_roboforex_prime.json); the
  lab's cost ladder adds gross, Exness (n/a for indices) and lab standard (0.6 / 2.0 points, estimates).
Priors (told to the owner): every index calendar idea so far was rejected (turn of month, option-expiry week, payday,
  oil->equity); intraday shapes rejected after costs (P1, P21). This one differs: a named payer with a known direction (P22).
"""
import os, sys, json, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np

NAME = "us_close_flow_v1"
HYPOTHESIS = ("Leveraged and vol-target funds rebalance into the US cash close in the direction of the day's move, so the last "
              "15-30 minutes continue big moves by more than RoboForex Prime's cost.")
RULES = __doc__
FAMILY = ["calendar", "flow", "payer", "intraday", "index", "close", "rebalancing", "momentum", "batch01"]
MARKETS = ["US500", "NAS100"]
TIMEFRAMES = ["M5"]
GRID = {"anchor": ["prev_close", "open"], "entry": ["15:30", "15:45"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 50
STOP_CAP_ATR = 1e9
LOOKBACK, ATR_DAYS, STOP_MULT = 60, 20, 0.5
_here = os.path.dirname(os.path.abspath(__file__))
_rf = json.load(open(os.path.join(_here, "..", "costs_roboforex_prime.json")))["realistic"]
COSTS = {m: _rf[m] for m in MARKETS}
sys.path.insert(0, os.path.join(_here, ".."))
import executors

NY = ZoneInfo("America/New_York")
_CAL = {}


def _utc(D, h, m):
    return int(dt.datetime(D.year, D.month, D.day, h, m, tzinfo=NY).timestamp())


def sessions(y0=2010, y1=2027):
    """NYSE full sessions: weekdays, not NYSE holidays, not the usual early closes."""
    if "nyse" not in _CAL:
        import holidays
        hol = holidays.financial_holidays("NYSE", years=range(y0, y1 + 1))
        early = set()
        for y in range(y0, y1 + 1):
            th = [d for d, n in holidays.financial_holidays("NYSE", years=y).items() if "Thanksgiving" in n]
            early |= {t + dt.timedelta(days=1) for t in th}
            early |= {dt.date(y, 12, 24), dt.date(y, 7, 3)}
        out, d = [], dt.date(y0, 1, 1)
        while d <= dt.date(y1, 12, 31):
            if d.weekday() < 5 and d not in hol and d not in early:
                out.append(d)
            d += dt.timedelta(days=1)
        _CAL["nyse"] = out
    return _CAL["nyse"]


def _ny_days(t):
    """New York calendar date (ordinal of days since 1970) of each UTC timestamp, DST-aware."""
    ud, inv = np.unique(t // 86400, return_inverse=True)
    off = np.array([int(dt.datetime.fromtimestamp(int(d) * 86400 + 43200, tz=NY).utcoffset().total_seconds()) for d in ud])[inv]
    return (t + off) // 86400


def _day_ranges(t, h, l):
    """Average range of the previous ATR_DAYS New York weekdays, keyed by NY date ordinal (prior days only)."""
    days = _ny_days(t)
    u, inv = np.unique(days, return_inverse=True)
    hi = np.full(len(u), -np.inf); lo = np.full(len(u), np.inf)
    np.maximum.at(hi, inv, h); np.minimum.at(lo, inv, l)
    wk = ((u + 3) % 7) < 5                                       # 1970-01-01 was a Thursday
    u, rng = u[wk], (hi - lo)[wk]
    out = {}
    for i in range(ATR_DAYS, len(u)):
        out[int(u[i]) + 719163] = float(rng[i - ATR_DAYS:i].mean())   # 719163 = date(1970, 1, 1).toordinal()
    return out


def signals(B, p, M):
    t = np.asarray(B["t"], np.int64); o = np.asarray(B["o"], float); c = np.asarray(B["c"], float)
    h = np.asarray(B["h"], float); l = np.asarray(B["l"], float)
    if len(t) == 0:
        return []
    idx = {int(x): i for i, x in enumerate(t)}
    atr = _day_ranges(t, h, l)
    eh, em = (int(x) for x in p["entry"].split(":"))
    first = dt.datetime.utcfromtimestamp(int(t[0])).date(); last = dt.datetime.utcfromtimestamp(int(t[-1])).date()
    days = [d for d in sessions() if first <= d <= last]
    hist, rows = [], []
    for k, D in enumerate(days):
        sb = idx.get(_utc(D, eh, em) - 300)                          # M5 bar that closes at the entry minute
        if sb is None:
            continue
        if p["anchor"] == "open":
            ab = idx.get(_utc(D, 9, 30)); anchor = o[ab] if ab is not None else None
        else:
            if k == 0:
                continue
            ab = idx.get(_utc(days[k - 1], 15, 55)); anchor = c[ab] if ab is not None else None
        if anchor is None:
            continue
        move = c[sb] - anchor
        a = atr.get(D.toordinal())
        prior = hist[-LOOKBACK:]
        hist.append(abs(move))
        if move == 0 or a is None or len(prior) < LOOKBACK:
            continue
        big = abs(move) >= float(np.median(prior))
        if big != (p.get("sample", "flow") == "flow"):
            continue
        side = 1 if move > 0 else -1
        stop = c[sb] - side * STOP_MULT * a
        rows.append((int(sb), side, float(stop)))
    return rows


def _exit_bars(B, p):
    t = np.asarray(B["t"], np.int64)
    first = dt.datetime.utcfromtimestamp(int(t[0])).date(); last = dt.datetime.utcfromtimestamp(int(t[-1])).date()
    want = np.array([_utc(D, 15, 55) for D in sessions() if first <= D <= last], np.int64)
    xb = np.flatnonzero(np.isin(t, want))
    return xb, xb


EXECUTOR = executors.exit_when(_exit_bars)
