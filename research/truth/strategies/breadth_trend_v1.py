"""Breadth test (OPEN_QUESTIONS Q4): the trend family that works on gold and USDJPY, on four NEW markets.
Rules are donchian_trend_v2_room_to_run unchanged (gold +0.14-0.21R, JPY +0.15-0.28R there); only the markets differ.
Markets were declared on 2026-10-31 before any data existed here; this file was written before any strategy was run on
them (only data-quality checks had been done). Costs and swaps: the lab's conservative estimates in costs.json for these
markets (CFD financing included); Exness Zero spreads for them were measured at near zero (research/exness/), but their
commissions are unknown, so no low-cost profile is assumed."""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as sw

NAME = "breadth_trend_v1"
HYPOTHESIS = ("Trend persistence (slow information diffusion, hedging and momentum flows) exists in equity indices, oil "
              "and silver as it does in gold and USDJPY; futures evidence (research/multiasset) says indices and energy trend.")
FAMILY = ["trend", "breakout", "breadth", "index", "energy", "metals"]
RULES = ("Long when a bar closes above the highest high of the previous n bars; short when it closes below the lowest low. "
         "Stop = atr_stop x ATR(14) from the signal close (1R). No target or a 3R target; chandelier trail 3 x ATR or none; "
         "optional H4 EMA50 direction filter; time stop 300 bars. One position per market.")
MARKETS = ["US500", "GER40", "WTI", "XAGUSD"]
TIMEFRAMES = ["H4", "D1"]
GRID = {"n": [20, 55], "atr_stop": [2.0, 3.0]}
MANAGEMENT = {"tgt": [0.0, 3.0], "trail": [3.0, 0.0], "bias": [0, 1]}
TIME_STOP = 300


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
