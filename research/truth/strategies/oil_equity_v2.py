"""Crude oil predicts equity returns, v2 (same idea as oil_equity_v1, which FAILED the lab's look-ahead check by finding
month-end trading days from later bars). v2 uses only the calendar, and reads WTI only up to the decision time.
Fixed 2026-11-01 before any lab result; the companion study research/flows/calendar_study.py had already shown the
next-month effect for 2011-2025 (disclosed).
Decision time: 20:00 UTC on the last WEEKDAY of each month (no trade that month if the index has no 19:00 UTC bar then).
Signal: WTI's return between consecutive decision times (WTI close of the last hourly bar that closed by then; sign only).
Trade: hold the index until the next month's decision time (or the last 20:00 UTC bar before it if that weekday has no
  bar). Modes: long_cash = long after oil fell, flat after it rose; long_short = long after oil fell, short after it rose.
  Market orders; catastrophe stop 10% (R = 10% of price). Grid: mode = 2 configurations.
Markets US500, NAS100, GER40, UK100, JP225; H1. Costs: lab estimates with overnight financing, charged to shorts too
  (conservative: the owner's Exness US500 specification shows 0 swap for shorts). No 2026 index data yet.
"""
import os, sys
import numpy as np

NAME = "oil_equity_v2"
HYPOTHESIS = "A falling oil price this month predicts higher equity index returns next month, a rising one lower returns."
RULES = __doc__
FAMILY = ["macro", "cross-asset", "oil", "index", "monthly", "awesome-list"]
MARKETS = ["US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["H1"]
GRID = {"mode": ["long_cash", "long_short"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 50
STOP_CAP_ATR = 1e9
STOP_PCT = 0.10
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..")); sys.path.insert(0, os.path.join(_here, "..", ".."))
import executors
_OIL = {}


def decision_days(y0=2010, y1=2027):
    d = np.arange(np.datetime64(f"{y0}-01-01"), np.datetime64(f"{y1 + 1}-01-01"), dtype="datetime64[D]")
    d = d[((d.astype(np.int64) + 3) % 7) < 5]
    m = d.astype("datetime64[M]").astype(np.int64)
    last = np.r_[m[1:] != m[:-1], True]
    return d[last].astype(np.int64)                                   # last weekday of each month


DAYS = decision_days()


def oil_sign_at():
    """{decision day: sign of WTI's return since the previous decision day}, using WTI hourly bars closed by 20:00 UTC."""
    if "s" in _OIL:
        return _OIL["s"]
    import engine as E
    ts, o, h, l, c = E.load_m1("WTI")
    bt, bo, bh, bl, bc, nxt = E.resample(ts, o, h, l, c, 60)
    close_t = bt + 3600
    px = {}
    for d in DAYS:
        T = int(d) * 86400 + 20 * 3600
        k = np.searchsorted(close_t, T, side="right") - 1
        if k >= 0 and T - close_t[k] < 3 * 86400 and bc[k] > 0:
            px[int(d)] = float(bc[k])
    s = {}
    for d0, d1 in zip(DAYS[:-1], DAYS[1:]):
        if int(d0) in px and int(d1) in px:
            s[int(d1)] = float(np.sign(px[int(d1)] / px[int(d0)] - 1))
    _OIL["s"] = s
    return s


def signals(B, p, M):
    s = oil_sign_at()
    t = np.asarray(B["t"], np.int64); c = np.asarray(B["c"], float)
    idx = np.flatnonzero(((t % 86400) // 3600 == 19) & np.isin(t // 86400, DAYS))
    rows = []
    for i in idx:
        g = s.get(int(t[i] // 86400), 0.0)
        if g < 0:
            rows.append((int(i), 1, float(c[i] * (1 - STOP_PCT))))
        elif g > 0 and p["mode"] == "long_short":
            rows.append((int(i), -1, float(c[i] * (1 + STOP_PCT))))
    return rows


def _exit_bars(B, p):
    t = np.asarray(B["t"], np.int64)
    idx = np.flatnonzero((t % 86400) // 3600 == 19); day = t[idx] // 86400
    xb = []
    for d in DAYS:
        k = np.searchsorted(day, d, side="right") - 1                  # that weekday, or the last trading day before it
        if k >= 0 and day[k] > d - 7:
            xb.append(int(idx[k]))
    xb = np.array(sorted(set(xb)), np.int64)
    return xb, xb


EXECUTOR = executors.exit_when(_exit_bars)
