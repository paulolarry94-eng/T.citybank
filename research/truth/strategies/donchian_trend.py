"""Example: classic Donchian close breakout (the family behind TimelessCity S2/S3)."""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as sw

NAME = "donchian_trend_v1"
HYPOTHESIS = "Breakouts of an N-bar range persist (trend following: slow information diffusion, hedging flows)."
RULES = ("Long when a bar closes above the highest high of the previous n bars; short when it closes below the lowest low. "
         "Stop = atr_stop x ATR(14) from the signal close. One position per market.")
TIMEFRAMES = ["H4", "D1"]
GRID = {"n": [20, 55], "atr_stop": [2.0, 3.0]}


def signals(B, p, M):
    h, l, c, a = B["h"], B["l"], B["c"], B["atr"]; n = int(p["n"])
    if len(c) <= n + 1:
        return []
    hh = np.full(len(c), np.nan); ll = np.full(len(c), np.nan)
    hh[n:] = sw(h, n).max(axis=1)[:-1]; ll[n:] = sw(l, n).min(axis=1)[:-1]       # previous n bars only
    up = (c > hh) & (a > 0); dn = (c < ll) & (a > 0)
    rows = [(i, 1, c[i] - p["atr_stop"] * a[i]) for i in np.flatnonzero(up)]
    rows += [(i, -1, c[i] + p["atr_stop"] * a[i]) for i in np.flatnonzero(dn)]
    return rows
