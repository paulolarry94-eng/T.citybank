"""Month-end FX hedge rebalancing into the London 4 pm fix (a flow with a payer AND a known direction). Rules fixed
2026-11-03 BEFORE any result (owner's last push: "look for flows that have a payer ... run final test").

Why it might pay (published research, e.g. Melvin & Prins 2015, "Equity hedging and exchange rates at the London 4 p.m.
fix"; nothing taken from our data): investors who hold foreign stocks and hedge the currency must resize the hedge at the
month-end WM/Reuters 4 pm London fix. When US stocks beat a foreign market over the month, foreign holders of US stocks
must SELL more dollars (and US holders of foreign stocks buy back less), so the dollar tends to weaken into the fix; when
the foreign market beat the US, the dollar tends to strengthen. Payer: hedgers who must trade at the fix; direction known
from public month-to-date index returns before the trade.
RULE (last London business day of each month; weekdays that are not England bank holidays):
  diff = month-to-date return of US500 minus that of the foreign index (EURUSD: GER40, GBPUSD: UK100, USDJPY: JP225),
         from the last price before the month began to the last price at or before the entry minute (causal).
  diff > 0 -> sell dollars: buy EURUSD / buy GBPUSD / sell USDJPY; diff < 0 -> the opposite.
  entry 12:00 / 14:00 / 15:00 London time (market order), exit 16:00 London (the fix). filter all / strong (|diff| >= 2%).
  Protective stop 0.3% of price (R = 0.3% of price; rarely touched in 1-4 hours). No overnight hold, no swap.
GRID entry 3 x filter 2 = 6 configurations; 3 markets. Costs: RoboForex Prime published.
CONTROL (controls.py, never selected): the same rule and direction on the 10th London business day of the month (no
month-end hedge flow).
Priors (told to the owner): London-fix fades without a direction were rejected (wmr_fix_*), month-end index rebalancing
was rejected, the US close flow was rejected; P22: a payer needs a known direction - this rule supplies one.
"""
import os, json, sys, glob, calendar, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np

NAME = "monthend_hedge_fix_v1"
HYPOTHESIS = ("Month-end currency-hedge rebalancing at the London 4 pm fix moves the dollar against the month's relative "
              "US-vs-foreign equity performance, by more than RoboForex Prime's cost.")
RULES = __doc__
FAMILY = ["calendar", "flow", "fix", "month-end", "payer", "hedging", "fx", "intraday"]
MARKETS = ["EURUSD", "GBPUSD", "USDJPY"]
TIMEFRAMES = ["M5"]
GRID = {"entry": ["1200", "1400", "1500"], "filter": ["all", "strong"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 60
STOP_CAP_ATR = 1e9
STOP_PCT, STRONG = 0.003, 0.02
FOREIGN = {"EURUSD": "GER40", "GBPUSD": "UK100", "USDJPY": "JP225"}
USD_IS_BASE = {"EURUSD": False, "GBPUSD": False, "USDJPY": True}
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, "..", "..", ".."))
_rf = json.load(open(os.path.join(_here, "..", "costs_roboforex_prime.json")))["realistic"]
COSTS = {m: _rf[m] for m in MARKETS}
sys.path.insert(0, os.path.join(_here, ".."))
import executors   # noqa: E402

LDN = ZoneInfo("Europe/London")
_IDX = {}


def _index(sym):
    """Index M1 closes (ts seconds, close), all years in data/ (2026 holdout not loaded)."""
    if sym not in _IDX:
        ts, c = [], []
        for f in sorted(glob.glob(os.path.join(_root, "data", f"{sym}_M1_bid_*.npz"))):
            d = np.load(f); ts.append(d["ts"] // 1000); c.append(d["c"].astype(float))
        t = np.concatenate(ts); x = np.concatenate(c); o = np.argsort(t, kind="stable")
        _IDX[sym] = (t[o], x[o])
    return _IDX[sym]


def _px(sym, t):
    ts, c = _index(sym)
    i = np.searchsorted(ts, t, side="right") - 1
    return c[i] if i >= 0 else np.nan


def _days(sample):
    import holidays
    uk = holidays.UK(subdiv="England", years=range(2010, 2028))
    out = []
    for y in range(2010, 2028):
        for m in range(1, 13):
            bd = [dt.date(y, m, d) for d in range(1, calendar.monthrange(y, m)[1] + 1)
                  if dt.date(y, m, d).weekday() < 5 and dt.date(y, m, d) not in uk]
            if len(bd) >= 10:
                out.append(bd[-1] if sample != "control" else bd[9])
    return out


def _utc(d, hhmm):
    return int(dt.datetime(d.year, d.month, d.day, hhmm // 100, hhmm % 100, tzinfo=LDN).timestamp())


def signals(B, p, M):
    t = np.asarray(B["t"], np.int64); c = np.asarray(B["c"], float)
    pos = {int(x): i for i, x in enumerate(t)}
    hh = int(p["entry"]); fsym = FOREIGN[M.sym]; rows = []
    for d in _days(p.get("sample", "flow")):
        te = _utc(d, hh)
        i = pos.get(te - 300)                                       # the bar that CLOSES at the entry minute
        if i is None or te > int(t[-1]) + 300:
            continue
        m0 = int(dt.datetime(d.year, d.month, 1, tzinfo=dt.timezone.utc).timestamp())
        r_us = _px("US500", te) / _px("US500", m0) - 1
        r_fx = _px(fsym, te) / _px(fsym, m0) - 1
        diff = r_us - r_fx
        if not np.isfinite(diff) or (p["filter"] == "strong" and abs(diff) < STRONG):
            continue
        sell_usd = diff > 0
        side = (-1 if sell_usd else 1) if USD_IS_BASE[M.sym] else (1 if sell_usd else -1)
        stop = c[i] * (1 - STOP_PCT) if side > 0 else c[i] * (1 + STOP_PCT)
        rows.append((int(i), int(side), float(stop)))
    return rows


def _exit_bars(B, p):
    t = np.asarray(B["t"], np.int64)
    want = {_utc(d, 1600) - 300 for d in _days(p.get("sample", "flow"))}   # bar closing at 16:00 London
    xb = np.flatnonzero(np.isin(t, np.fromiter(want, np.int64)))
    return xb, xb


EXECUTOR = executors.exit_when(_exit_bars)
