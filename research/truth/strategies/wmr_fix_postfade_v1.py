"""London 4 pm WM/R fix: fade the pre-fix move AFTER the fix, EURUSD and GBPUSD (companion to wmr_fix_reversion_v1).
Rules fixed 2026-11-01 BEFORE any result of either file.

The documented timing (Evans 2018; Krohn and Sushko 2020; our Hunt 2 study): the move into the fix continues until the fix
and reverses after it. Same stops, target, days and costs as wmr_fix_reversion_v1; only the clock differs:
  drift   close of the 15:55-16:00 London M5 bar minus the open of the 15:30 bar;
  entry   market order at 16:00 London against the drift; no trade if drift = 0;
  stop    catastrophe 0.3% of price, or structure 1 pip beyond the 15:30-16:00 extreme;
  target  5R; exit at 17:00 London (time stop 12 M5 bars) if neither boundary is hit (Hunt 2's one-hour window);
  days    all weekdays, or the last weekday of the month.
Grid: stop [catastrophe, structure] x days [all, month_end] = 4 configurations; EURUSD, GBPUSD.
Priors: Hunt 2 (gross, no stops): all days +0.45 / +0.38 costs (negative after costs); month-end +1.4 / +1.9 costs, t 1.2-1.6.
"""
import os, sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import wmr_fix_reversion_v1 as W

NAME = "wmr_fix_postfade_v1"
HYPOTHESIS = ("The push into the 16:00 London fix reverses once the fix orders are filled: fading it from 16:00 to 17:00 "
              "London earns more than the round-trip cost.")
RULES = __doc__
FAMILY = ["calendar", "flow", "fix", "intraday", "eurusd", "gbpusd", "reversal"]
MARKETS = W.MARKETS
TIMEFRAMES = ["M5"]
GRID = dict(W.GRID)
MANAGEMENT = dict(W.MANAGEMENT)
TIME_STOP = 12
STOP_CAP_ATR = 1e9
COSTS = dict(W.COSTS)


def signals(B, p, M):
    return W.fix_signals(B, p, (15, 30), (15, 55))
