"""Turn of the Month in equity indexes, v2 (same idea and window as tom_indices_v1, which FAILED the lab's look-ahead
check: v1 found "the last trading day of the month" from the data, i.e. from bars that come later). v2 uses only the
calendar, which a live robot knows in advance. Fixed 2026-11-01 before any lab result; the companion study
research/flows/calendar_study.py had already shown the drift-controlled effect for 2011-2025 (disclosed).
Trade: long from 20:00 UTC on the second-to-last WEEKDAY of the month to 20:00 UTC on the third weekday of the next month
  (exit at the first 20:00 UTC bar on or after that weekday). No trade that month if the entry weekday has no 19:00 UTC
  hourly bar (an exchange holiday). Market orders; catastrophe stop 5% (R = 5% of price). One configuration.
Markets US500, NAS100, GER40, UK100, JP225; H1. Costs: lab estimates with overnight financing. No 2026 index data yet.
"""
import os, sys
import numpy as np

NAME = "tom_indices_v2"
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


def weekdays_by_month(y0=2010, y1=2027):
    d = np.arange(np.datetime64(f"{y0}-01-01"), np.datetime64(f"{y1 + 1}-01-01"), dtype="datetime64[D]")
    d = d[((d.astype(np.int64) + 3) % 7) < 5]
    m = d.astype("datetime64[M]").astype(np.int64)
    out = {}
    for k in np.unique(m):
        out[int(k)] = d[m == k].astype(np.int64)                # day numbers (days since 1970-01-01)
    return out


def anchor_bars(B):
    """{day number: index of that day's 19:00 UTC hourly bar} (the bar that closes at 20:00 UTC)."""
    t = np.asarray(B["t"], np.int64)
    idx = np.flatnonzero((t % 86400) // 3600 == 19)
    return dict(zip((t[idx] // 86400).tolist(), idx.tolist()))


def first_bar_on_or_after(anchor, day):
    keys = np.array(sorted(anchor)); k = np.searchsorted(keys, day, side="left")
    return anchor[int(keys[k])] if k < len(keys) else None


_WD = weekdays_by_month()
_ENTRY_DAYS = {int(v[-2]) for v in _WD.values()}                 # second-to-last weekday of each month
_EXIT_DAYS = sorted(int(v[2]) for v in _WD.values())             # third weekday of each month


def signals(B, p, M):
    t = np.asarray(B["t"], np.int64); c = np.asarray(B["c"], float)
    idx = np.flatnonzero(((t % 86400) // 3600 == 19) & np.isin(t // 86400, list(_ENTRY_DAYS)))
    return [(int(i), 1, float(c[i] * (1 - STOP_PCT))) for i in idx]


def _exit_bars(B, p):
    anchor = anchor_bars(B)
    xb = {first_bar_on_or_after(anchor, d) for d in _EXIT_DAYS}
    return (np.array(sorted(x for x in xb if x is not None), np.int64),) * 2


EXECUTOR = executors.exit_when(_exit_bars)
