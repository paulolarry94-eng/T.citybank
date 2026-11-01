"""Repo funnel: trustdan/trend-following-backtesting-strategies @ a34b7ba, all 48 Pine scripts (turtle-core-v2.2 and
alt1-alt47), translated line by line with the source's default inputs. Rules fixed 2026-11-01 BEFORE any result in
research/repofunnel/PREREG.md (sections A and B); translation in research/repofunnel/trustdan.py, engine in d1.py.

Why it might pay (the author's claim): Donchian breakouts catch trends; pyramiding, profit targets and filters
(their best: Alt10 3N/6N/9N targets, Alt45 RSI confirmation, Alt26 fractional pyramid) improve on the Turtle core.
Markets: our 11 CFDs, daily bars (Sunday stub merged into Monday), both sides (source default), one position per market
with its pyramid units; R = 1% equity per unit of the source's stop distance (stopN x ATR20 at entry).
Grid: rule = 48 configurations. Costs: research/truth/costs.json with overnight swaps (Wednesday x3).
Priors: Donchian trend rejected four times by the breadth gate (gold and USDJPY positive, the rest negative: P6).
"""
import os, sys
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..")); sys.path.insert(0, os.path.join(_here, "..", "..", "repofunnel"))
import d1
import trustdan as TD

NAME = "funnel_trustdan_v1"
HYPOTHESIS = "The trustdan Turtle/Seykota trend variants (Donchian breakouts with pyramiding, targets and filters) earn after costs on our markets."
RULES = __doc__
FAMILY = ["trend", "breakout", "donchian", "pyramiding", "daily", "breadth", "repo-funnel", "trustdan"]
MARKETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "US500", "NAS100", "GER40", "UK100", "JP225", "WTI", "XAGUSD"]
TIMEFRAMES = ["D1"]
GRID = {"rule": TD.NAMES}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 50
STOP_CAP_ATR = 1e9


def signals(B, p, M):
    return d1.signal_rows(B, TD.make_rule, p, M.sym, (1, -1))


EXECUTOR = d1.executor(TD.make_rule, lambda p: (1, -1))
