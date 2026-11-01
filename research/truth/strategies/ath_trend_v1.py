"""Repo funnel: awesome-systematic-trading "Trend-following effect in stocks" (Wilcox & Crittenden), applied to our
11 CFDs. Rules fixed 2026-11-01 BEFORE any result in research/repofunnel/PREREG.md (sections A and D); code in
research/repofunnel/awesome_cfd.py.

Why it might pay: a close at a multi-year high marks a trend that keeps going; a tight trailing stop cuts the losers.
Entry at the next open when the daily close >= the highest close of the prior 2,520 bars (10 years; all history before
2021); stop = close - 1 x ATR(10), raised daily, never lowered, intrabar. Sides: long (source) and both (mirror image:
a 10-year closing low -> short). Daily bars (Sunday stub merged into Monday). Grid: side = 2 configurations.
Costs: research/truth/costs.json with overnight swaps. Priors: Donchian trend rejected by the breadth gate (P6).
"""
import os, sys
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..")); sys.path.insert(0, os.path.join(_here, "..", "..", "repofunnel"))
import d1
import awesome_cfd as AC

NAME = "ath_trend_v1"
HYPOTHESIS = "Buying a 10-year closing high with a 1-ATR trailing stop earns after costs on our markets."
RULES = __doc__
FAMILY = ["trend", "breakout", "all-time-high", "daily", "breadth", "repo-funnel", "awesome-list"]
MARKETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "US500", "NAS100", "GER40", "UK100", "JP225", "WTI", "XAGUSD"]
TIMEFRAMES = ["D1"]
GRID = {"side": ["long", "both"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 50
STOP_CAP_ATR = 1e9


def signals(B, p, M):
    return d1.signal_rows(B, AC.make_rule, p, M.sym, AC.sides_of(p))


EXECUTOR = d1.executor(AC.make_rule, AC.sides_of)
