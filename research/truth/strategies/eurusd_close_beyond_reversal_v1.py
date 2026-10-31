"""Owner's spec (2026-10-31): no-indicator daily reversal on EUR/USD.
Long: a RED daily candle whose close is below the previous day's low -> buy stop at that candle's high, valid for the
next session only. Short: a GREEN candle whose close is above the previous day's high -> sell stop at its low, next
session only. Only when flat. Exit: in profit between 16:45 and 16:55 New York time -> close; otherwise a fixed stop
(250 pips in the spec; 150 and 350 are the declared neighbours). Costs: 4 pips round trip per the spec ($40 per lot)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import executors

NAME = "eurusd_close_beyond_reversal_v1"
HYPOTHESIS = ("A daily close beyond the prior day's range is an exhaustion move; a stop entry back through the bar's "
              "far extreme catches the snap-back, and banking the first profitable New York close harvests it.")
RULES = __doc__
FAMILY = ["reversal", "daily", "stop-entry", "eurusd", "bailout-exit"]
MARKETS = ["EURUSD"]
TIMEFRAMES = ["D1"]
GRID = {"stop_pips": [150, 250, 350]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}      # not used: the exit is the bailout executor
COSTS = {"EURUSD": 0.0004}
STOP_CAP_ATR = 1e9
EXECUTOR = executors.bailout("stop_pips", "pips")


def signals(B, p, M):
    o, h, l, c = B["o"], B["h"], B["l"], B["c"]
    pip = 0.01 if M.sym.endswith("JPY") else 0.0001; d = p["stop_pips"] * pip
    rows = []
    for i in range(1, len(c)):
        if c[i] < o[i] and c[i] < l[i - 1]:
            rows.append((i, 1, h[i] - d, h[i], 1, "stop"))
        elif c[i] > o[i] and c[i] > h[i - 1]:
            rows.append((i, -1, l[i] + d, l[i], 1, "stop"))
    return rows
