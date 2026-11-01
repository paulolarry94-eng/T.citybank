"""Crude oil predicts equity returns (awesome-systematic-trading: "Crude Oil Predicts Equity Returns", paper Sharpe 0.599;
Driesprong, Jacobsen & Maat 2008, "Striking oil"). Owner chose it 2026-11-01. Rules fixed BEFORE any result.
Why it might pay: investors under-react to oil price news, so a rise in oil this month is followed by weaker equity
  returns next month (a behavioural lag, not a forced flow: lower prior than the calendar flows).
Signal: WTI's return over calendar month m, from its 20:00 UTC close on the last trading day of month m-1 to that of
  month m (sign only; WTI data from data/ as in Q4, the April 2020 negative-price episode included).
Trade: hold the index for month m+1, from 20:00 UTC on the index's last trading day of month m to 20:00 UTC on its last
  trading day of month m+1. Modes: long_cash = long when oil fell, flat when it rose; long_short = long when oil fell,
  short when it rose. Market orders; catastrophe stop 10% (R = 10% of price).
Grid: mode [long_cash, long_short] = 2 configurations. Markets US500, NAS100, GER40, UK100, JP225; timeframe H1.
Costs: lab estimates for index CFDs with overnight financing every night, charged to shorts too (conservative: the
  owner's Exness US500 specification shows 0 swap for shorts). No 2026 index data yet.
"""
import os, sys
import numpy as np

NAME = "oil_equity_v1"
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
sys.path.insert(0, os.path.join(_here, "..")); sys.path.insert(0, _here); sys.path.insert(0, os.path.join(_here, "..", ".."))
import executors
from tom_indices_v1 import trading_days, _month_groups
_OIL = {}


def oil_month_sign():
    """{month key: sign of WTI's return over that month} from WTI's own 20:00 UTC month-end closes."""
    if "sign" in _OIL:
        return _OIL["sign"]
    import engine as E
    ts, o, h, l, c = E.load_m1("WTI")
    bt, bo, bh, bl, bc, nxt = E.resample(ts, o, h, l, c, 60)
    B = dict(t=bt, c=bc)
    idx, day, mkey = trading_days(B)
    closes = {}
    for a, b in _month_groups(mkey):
        closes[int(mkey[b - 1])] = float(bc[idx[b - 1]])
    ks = sorted(closes); sign = {}
    for k0, k1 in zip(ks[:-1], ks[1:]):
        if k1 == k0 + 1 and closes[k0] > 0 and closes[k1] > 0:
            sign[k1] = np.sign(closes[k1] / closes[k0] - 1)
    _OIL["sign"] = sign
    return sign


def signals(B, p, M):
    sign = oil_month_sign()
    idx, day, mkey = trading_days(B); c = np.asarray(B["c"], float)
    rows = []
    for a, b in _month_groups(mkey):
        m = int(mkey[b - 1]); s = sign.get(m, 0)
        i = int(idx[b - 1])                                   # last trading day of month m
        if s < 0:
            rows.append((i, 1, float(c[i] * (1 - STOP_PCT))))
        elif s > 0 and p["mode"] == "long_short":
            rows.append((i, -1, float(c[i] * (1 + STOP_PCT))))
    return rows


def _exit_bars(B, p):
    idx, day, mkey = trading_days(B)
    xb = np.array([idx[b - 1] for a, b in _month_groups(mkey)], np.int64)
    return xb, xb


EXECUTOR = executors.exit_when(_exit_bars)
