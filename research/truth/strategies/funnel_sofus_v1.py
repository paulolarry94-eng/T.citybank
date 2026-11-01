"""Repo funnel: sofus-nl/swing-trading-strategies @ 1b7cf1c, the 18 setups that can be expressed with prices.
Rules fixed 2026-11-01 BEFORE any result in research/repofunnel/PREREG.md (sections A and C); translation in
research/repofunnel/sofus.py, engine in d1.py.

Why it might pay (the source's claim): published swing setups (Minervini, O'Neil, Weinstein, Connors, Wilder, Bulkowski,
Kullamagi, Turtles) with walk-forward-validated profit factors of 1.7-4.5 on US stocks.
Translation: price only (volume, RS rank, earnings, news, sector baselines and grades dropped); stock percentages as
ATR(14) multiples at 2% per ATR; swing points = 3-bar fractals known one bar later; s01, s02, s08, s10, s11 are
mechanical approximations of discretionary patterns. Markets: our 11 CFDs, daily bars (Sunday stub merged into Monday).
Grid: 18 rules x side [long (as written), both (mirror image for shorts)] = 36 configurations.
Costs: research/truth/costs.json with overnight swaps. R = entry minus the initial stop (1% risk).
Priors: chart patterns rejected (P14); index RSI(2) rejected after costs; Donchian trend rejected by the breadth gate (P6).
"""
import os, sys
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..")); sys.path.insert(0, os.path.join(_here, "..", "..", "repofunnel"))
import d1
import sofus as SF

NAME = "funnel_sofus_v1"
HYPOTHESIS = "The sofus-nl swing setups (breakouts, pullbacks, momentum, RSI reversion, patterns) earn after costs on our markets."
RULES = __doc__
FAMILY = ["swing", "breakout", "pullback", "momentum", "pattern", "mean-reversion", "daily", "breadth", "repo-funnel", "sofus"]
MARKETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "US500", "NAS100", "GER40", "UK100", "JP225", "WTI", "XAGUSD"]
TIMEFRAMES = ["D1"]
GRID = {"rule": SF.NAMES, "side": ["long", "both"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 50
STOP_CAP_ATR = 1e9


def signals(B, p, M):
    return d1.signal_rows(B, SF.make_rule, p, M.sym, SF.sides_of(p))


EXECUTOR = d1.executor(SF.make_rule, SF.sides_of)
