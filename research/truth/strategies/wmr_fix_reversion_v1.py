"""London 4 pm WM/R fix reversion, EURUSD and GBPUSD (owner's Module 3 spec, 2026-11-01). Rules fixed BEFORE any result.

Owner's spec: measure the pre-fix drift into the 16:00 London fix, enter against it before the fix with a 5:1 payoff
structure, exit by the clock at 16:05 London. Coded literally:
  drift   close of the 15:50-15:55 London M5 bar minus the open of the 15:30 bar (25 minutes into the fix);
  entry   market order at 15:55 London against the drift (sell after a rise, buy after a fall); no trade if drift = 0;
  stop    catastrophe: 0.3% of price (R = 0.3% of price; the 5R target is then out of reach: a pure time exit);
          structure:   1 pip beyond the drift window's extreme (15:30-15:55 high for a sell, low for a buy); R = that
                       distance; the lab skips trades whose R is under 3 x cost (its standard rule);
  target  5R (the owner's 5:1 payoff structure); exit at 16:05 London (time stop 2 M5 bars) if neither boundary is hit;
  days    all: every weekday; month_end: the last weekday of the month only (hedge rolls and rebalancing peak there).
London times come from the IANA zone Europe/London, so the UTC entry moves with daylight saving.
Grid: stop [catastrophe, structure] x days [all, month_end] = 4 configurations; markets EURUSD, GBPUSD (owner's choice).
Costs: Exness Zero realistic (EURUSD 0.95, GBPUSD 0.98 pips round trip). RoboForex costs are not measured yet.
Priors: Hunt 2 measured the fade AFTER the fix (enter 16:00 against 15:30-16:00, exit 17:00): gross +0.45 / +0.38 of a
  1.5 / 1.8-pip cost on all days (negative after costs), +1.4 / +1.9 costs on month-ends (t 1.2-1.6, 12 a year). Published work
  (Evans 2018; Krohn and Sushko 2020) finds the pre-fix move continues into the fix and reverses after it, so entering
  against it at 15:55 bets against the documented pattern for half of the 10 minutes. Companion file wmr_fix_postfade_v1
  tests the documented timing with the same stops, target and days.
"""
import os, sys, json, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np

NAME = "wmr_fix_reversion_v1"
HYPOTHESIS = ("Hedge and rebalancing orders worked into the 16:00 London fix push EURUSD and GBPUSD one way; fading that push "
              "from 15:55 to 16:05 London earns more than the round-trip cost.")
RULES = __doc__
FAMILY = ["calendar", "flow", "fix", "intraday", "eurusd", "gbpusd", "reversal", "owner-idea"]
MARKETS = ["EURUSD", "GBPUSD"]
TIMEFRAMES = ["M5"]
GRID = {"stop": ["catastrophe", "structure"], "days": ["all", "month_end"]}
MANAGEMENT = {"tgt": [5.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 2
STOP_CAP_ATR = 1e9
STOP_PCT = 0.003
PIP = 0.0001
DRIFT_FROM, SIGNAL_BAR = (15, 30), (15, 50)          # London wall time: drift start, signal bar start (closes 15:55)
_here = os.path.dirname(os.path.abspath(__file__))
_cz = json.load(open(os.path.join(_here, "..", "costs_exness_zero.json")))["realistic"]
COSTS = {m: _cz[m] for m in MARKETS}
LDN = ZoneInfo("Europe/London")


def _utc(D, hm):
    return int(dt.datetime(D.year, D.month, D.day, hm[0], hm[1], tzinfo=LDN).timestamp())


def last_weekday(D):
    nxt = D + dt.timedelta(days=1)
    while nxt.weekday() >= 5:
        nxt += dt.timedelta(days=1)
    return nxt.month != D.month


def fix_signals(B, p, drift_from, signal_bar):
    t = np.asarray(B["t"], np.int64); o = np.asarray(B["o"], float); h = np.asarray(B["h"], float)
    l = np.asarray(B["l"], float); c = np.asarray(B["c"], float)
    rows = []
    for d in np.unique(t // 86400):
        D = dt.datetime.utcfromtimestamp(int(d) * 86400).date()
        if D.weekday() >= 5 or (p["days"] == "month_end" and not last_weekday(D)):
            continue
        t0, t1 = _utc(D, drift_from), _utc(D, signal_bar)
        i0, i1 = np.searchsorted(t, t0), np.searchsorted(t, t1)
        if i1 >= len(t) or i0 >= len(t) or t[i0] != t0 or t[i1] != t1 or i1 - i0 != (t1 - t0) // 300:
            continue                                                  # a missing bar in the window: no trade
        drift = c[i1] - o[i0]
        if drift == 0:
            continue
        side = -1 if drift > 0 else 1
        if p["stop"] == "catastrophe":
            stop = c[i1] * (1 + STOP_PCT) if side < 0 else c[i1] * (1 - STOP_PCT)
        else:
            stop = h[i0:i1 + 1].max() + PIP if side < 0 else l[i0:i1 + 1].min() - PIP
        rows.append((int(i1), side, float(stop)))
    return rows


def signals(B, p, M):
    return fix_signals(B, p, DRIFT_FROM, SIGNAL_BAR)
