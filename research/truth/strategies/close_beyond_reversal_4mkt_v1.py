"""Breadth check declared before any result (2026-10-31): the owner's EUR/USD daily reversal on all four research
markets, with the fixed stop expressed as % of price (2.25% ~ 250 pips on EUR/USD at 1.11; neighbours 1.35% / 3.15%).
Lab standard costs (costs.json) and swaps."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import executors

NAME = "close_beyond_reversal_4mkt_v1"
HYPOTHESIS = "Same as eurusd_close_beyond_reversal_v1: an exhaustion close beyond the prior range snaps back."
RULES = __doc__
FAMILY = ["reversal", "daily", "stop-entry", "bailout-exit", "breadth"]
MARKETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
TIMEFRAMES = ["D1"]
GRID = {"stop_pct": [1.35, 2.25, 3.15]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
STOP_CAP_ATR = 1e9
EXECUTOR = executors.bailout("stop_pct", "pct")


def signals(B, p, M):
    o, h, l, c = B["o"], B["h"], B["l"], B["c"]
    rows = []
    for i in range(1, len(c)):
        if c[i] < o[i] and c[i] < l[i - 1]:
            rows.append((i, 1, h[i] * (1 - p["stop_pct"] / 100), h[i], 1, "stop"))
        elif c[i] > o[i] and c[i] > h[i - 1]:
            rows.append((i, -1, l[i] * (1 + p["stop_pct"] / 100), l[i], 1, "stop"))
    return rows
