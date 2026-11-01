"""Turn of the Month in equity indexes (awesome-systematic-trading: "Turn of the Month in Equity Indexes", paper Sharpe
0.305; Ariel 1987, Lakonishok & Smidt 1988). Owner chose it 2026-11-01 ("3 ... the best ideas"). Rules fixed BEFORE any
result.
Why it might pay: money arrives at month end and month start (salaries and pension contributions invested, fund flows and
rebalancing), so index returns cluster on the last trading day and the first three trading days of the month.
Trade: long the index from 20:00 UTC on the second-to-last trading day of the month to 20:00 UTC on the third trading day
  of the next month (holds day -1, +1, +2, +3). 20:00 UTC is one fixed daily anchor for every market (US cash close in
  summer; a simplification for Europe and Japan). Trading day = weekday with a 19:00 UTC hourly bar in that market's data.
  Market orders at the 20:00 bar's open; catastrophe stop 5% below entry (R = 5% of price, for reporting).
Grid: one configuration (the paper's window). Markets US500, NAS100, GER40, UK100, JP225; timeframe H1.
Costs: lab estimates for index CFDs (research/truth/costs.json) including overnight financing for every night held
  (about 1.3-1.7 bp a night). No 2026 data for indices yet (data/holdout holds FX and gold only).
Priors: index trend and RSI(2) rejected (different families); the only calendar idea so far (Tokyo fix) is Tier B.
Companion drift-controlled study: research/flows/calendar_study.py.
"""
import os, sys
import numpy as np

NAME = "tom_indices_v1"
HYPOTHESIS = "Month-end and month-start money flows lift equity indexes on the last trading day and the first three."
RULES = __doc__
FAMILY = ["calendar", "flow", "seasonal", "index", "turn-of-month", "awesome-list"]
MARKETS = ["US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["H1"]
GRID = {"window": ["d-1_d+3"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 50
STOP_CAP_ATR = 1e9
STOP_PCT = 0.05
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import executors


def trading_days(B):
    """(bar index of the 19:00 UTC bar, UTC day number, month key) for every weekday that has that bar."""
    t = np.asarray(B["t"], np.int64)
    idx = np.flatnonzero((t % 86400) // 3600 == 19)
    day = t[idx] // 86400
    keep = ((day + 3) % 7) < 5
    idx, day = idx[keep], day[keep]
    dt = day.astype("datetime64[D]")
    mkey = dt.astype("datetime64[M]").astype(np.int64)
    return idx, day, mkey


def _month_groups(mkey):
    starts = np.r_[0, np.flatnonzero(np.diff(mkey)) + 1]
    ends = np.r_[starts[1:], len(mkey)]
    return list(zip(starts, ends))


def signals(B, p, M):
    idx, day, mkey = trading_days(B); c = np.asarray(B["c"], float)
    rows = []
    for a, b in _month_groups(mkey):
        if b - a >= 3:
            i = idx[b - 2]                                    # second-to-last trading day of the month
            rows.append((int(i), 1, float(c[i] * (1 - STOP_PCT))))
    return rows


def _exit_bars(B, p):
    idx, day, mkey = trading_days(B)
    xb = np.array([idx[a + 2] for a, b in _month_groups(mkey) if b - a >= 3], np.int64)   # third trading day
    return xb, xb


EXECUTOR = executors.exit_when(_exit_bars)
