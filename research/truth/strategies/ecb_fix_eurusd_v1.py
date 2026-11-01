"""ECB euro reference rate (Q19), EURUSD at RoboForex Prime costs. Rules fixed 2026-11-01 BEFORE any result.

The fix: the ECB sets its euro reference rates from a daily concertation between central banks that "normally takes place
around 14:10 CET" (Frankfurt time, Europe/Berlin, so the UTC time moves with daylight saving) and publishes them around
16:00 CET on TARGET business days (ecb.europa.eu). The ECB says the rates are for information and that "using the rates for
transaction purposes is strongly discouraged". Some older documents give 14:15; this file uses the ECB's current 14:10.
Unlike the Tokyo fix there is no known payer DIRECTION, so the two testable shapes are the ones every fix study uses
(the same shapes as the London 4 pm tests, which failed: wmr_fix_reversion_v1, wmr_fix_postfade_v1):
  into   drift = close of the 13:55-14:00 Frankfurt M5 bar minus the open of the 13:40 bar; market order at 14:00 WITH the
         drift (orders worked into the fix keep pushing); exit at 14:10 (the concertation). No trade if drift = 0.
  after  drift = close of the 14:05-14:10 bar minus the open of the 13:40 bar; market order at 14:10 AGAINST the drift
         (the push fades once the fix orders are done); exit at 15:10 (one hour, as in the London post-fix test).
  stop   catastrophe 0.3% of price (R = 0.3% of price, about 35 pips; a pure time exit in practice). No target.
  days   all: every TARGET business day (the ECB publishes; weekends and TARGET holidays skipped);
         month_end: the last TARGET business day of the month (hedge rolls and rebalancing peak there).
  A missing M5 bar in the drift window: no trade. Trades never cross the 22:00 UTC rollover, so they pay no swap.
Grid: trade [into, after] x days [all, month_end] = 4 configurations; one market, EURUSD (the ECB's main rate; we have no
  EURGBP / EURJPY data). Known before running: month_end has about 108 trades in 2011-19 on one market, below the lab's
  200-trade gate, so it can only be reported, never selected.
Costs (owner, 2026-11-01): RoboForex Prime commission-plus-raw-spread model, research/truth/costs_roboforex_prime.json:
  published average spread 0.1 pip + commission 10 USD per million per side (0.25 pip round trip at 1.25) + 0.2 pip
  slippage = 0.55 pip round trip. Published, not measured. The lab's stress step adds 50% (0.83 pip).
  Reported afterwards from the same trades, descriptive only (no selection): gross (zero cost), Exness Zero realistic
  (0.95 pip) and the lab standard (1.5 pips).
Priors: fix family: Tokyo gotobi fix Tier B (a known payer and direction); London 4 pm fix rejected twice (no known
  direction); Hunt 2: the month-end London fix moved 1.4-1.9x costs, 12 trades a year.
"""
import os, sys, json, datetime as dt, calendar
from zoneinfo import ZoneInfo
import numpy as np

NAME = "ecb_fix_eurusd_v1"
HYPOTHESIS = ("Orders benchmarked to the ECB 14:10 CET concertation push EURUSD one way into the fix (continuation) "
              "and the push fades after it (reversal), by more than RoboForex Prime's round-trip cost.")
RULES = __doc__
FAMILY = ["calendar", "flow", "fix", "intraday", "eurusd", "reversal", "momentum", "payer", "owner-idea"]
MARKETS = ["EURUSD"]
TIMEFRAMES = ["M5"]
GRID = {"trade": ["into", "after"], "days": ["all", "month_end"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 50
STOP_CAP_ATR = 1e9
STOP_PCT = 0.003
_here = os.path.dirname(os.path.abspath(__file__))
_rf = json.load(open(os.path.join(_here, "..", "costs_roboforex_prime.json")))["realistic"]
COSTS = {"EURUSD": _rf["EURUSD"]}
sys.path.insert(0, os.path.join(_here, ".."))
import executors

FRA = ZoneInfo("Europe/Berlin")
DRIFT_FROM = (13, 40)
SIGNAL_BAR = {"into": (13, 55), "after": (14, 5)}       # Frankfurt bar start; the bar closes at the entry minute
EXIT_BAR = {"into": (14, 5), "after": (15, 5)}          # Frankfurt bar start; the bar closes at the exit minute
SIDE = {"into": +1, "after": -1}                        # +1 with the drift, -1 against it
_TARGET = None


def _utc(D, hm):
    return int(dt.datetime(D.year, D.month, D.day, hm[0], hm[1], tzinfo=FRA).timestamp())


def target_days(y0=2010, y1=2027):
    """TARGET business days: weekdays that are not TARGET holidays."""
    import holidays
    hol = holidays.financial_holidays("ECB", years=range(y0, y1 + 1))
    out = set()
    d = dt.date(y0, 1, 1)
    while d <= dt.date(y1, 12, 31):
        if d.weekday() < 5 and d not in hol:
            out.add(d)
        d += dt.timedelta(days=1)
    return out


def last_of_month(D, days):
    last = calendar.monthrange(D.year, D.month)[1]
    x = dt.date(D.year, D.month, last)
    while x not in days:
        x -= dt.timedelta(days=1)
    return x == D


def _days():
    global _TARGET
    if _TARGET is None:
        _TARGET = target_days()
    return _TARGET


def signals(B, p, M):
    days = _days()
    t = np.asarray(B["t"], np.int64); o = np.asarray(B["o"], float); c = np.asarray(B["c"], float)
    rows = []
    for d in np.unique(t // 86400):
        D = dt.datetime.utcfromtimestamp(int(d) * 86400).date()
        if D not in days or (p["days"] == "month_end" and not last_of_month(D, days)):
            continue
        t0, t1 = _utc(D, DRIFT_FROM), _utc(D, SIGNAL_BAR[p["trade"]])
        i0, i1 = np.searchsorted(t, t0), np.searchsorted(t, t1)
        if i1 >= len(t) or i0 >= len(t) or t[i0] != t0 or t[i1] != t1 or i1 - i0 != (t1 - t0) // 300:
            continue                                                  # a missing bar in the window: no trade
        drift = c[i1] - o[i0]
        if drift == 0:
            continue
        side = (1 if drift > 0 else -1) * SIDE[p["trade"]]
        stop = c[i1] * (1 - STOP_PCT) if side > 0 else c[i1] * (1 + STOP_PCT)
        rows.append((int(i1), side, float(stop)))
    return rows


def _exit_bars(B, p):
    t = np.asarray(B["t"], np.int64)
    hm = EXIT_BAR[p["trade"]]
    want = {_utc(dt.datetime.utcfromtimestamp(int(d) * 86400).date(), hm) for d in np.unique(t // 86400)}
    xb = np.flatnonzero(np.isin(t, np.fromiter(want, np.int64)))
    return xb, xb                                                     # longs and shorts leave at the same minute


EXECUTOR = executors.exit_when(_exit_bars)
