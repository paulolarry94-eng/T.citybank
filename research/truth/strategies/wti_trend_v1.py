"""HINDSIGHT, called out: WTI was picked AFTER breadth_trend_v1 showed it was the only one of its four markets with a
positive trend edge in 2011-2022 (net +0.14R; before costs +0.21R). The rules and grid are breadth_trend_v1's, unchanged.
The only clean evidence this run can add is the 2023-25 look, which no test has seen for these rules on WTI.
Economic prior (stated before this session's tests too): energy futures trend (research/multiasset futures study)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from breadth_trend_v1 import signals, GRID, MANAGEMENT, TIMEFRAMES, TIME_STOP, RULES   # identical rules

NAME = "wti_trend_v1"
HYPOTHESIS = ("Oil trends (inventory cycles, OPEC decisions and hedging flows diffuse slowly). Chosen after "
              "breadth_trend_v1 (hindsight); only 2023-25 is clean.")
FAMILY = ["trend", "breakout", "energy", "hindsight-market-choice"]
MARKETS = ["WTI"]
