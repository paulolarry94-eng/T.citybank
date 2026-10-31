"""The owner's 4-leg engulfing SOP on GOLD, H4 and daily (owner, 2026-10-31: "see this in gold daily too", with a daily
XAUUSD chart: Leg 4 high -> Leg 3 low -> Leg 2 lower high -> Leg 1 lower low, then a retest of the Leg 4 zone many
candles later). Detector, entry, stop and target identical to sop_4leg_v1 (calibrated on the owner's FX case studies
before any result); only the market, timeframes, pip size and the retest limits differ (the daily example retested
after ~45 candles, so 50 is added). Gold pip = $0.10, so the stop buffer is $0.35. No time window on H4/D1.
Costs: Exness Zero realistic for XAUUSD; limit fills use the measured Zero spread; swaps as the lab standard."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import sop_4leg_v1 as base

NAME = "sop_4leg_gold_v1"
HYPOTHESIS = base.HYPOTHESIS + " On gold's higher timeframes (owner's daily example)."
RULES = __doc__ + "\n" + base.RULES
FAMILY = ["engulfing", "structure", "retest", "limit-entry", "ema", "owner-idea", "gold", "daily"]
MARKETS = ["XAUUSD"]
TIMEFRAMES = ["H4", "D1"]
GRID = {"k": [3, 4, 5], "engulf": ["perfect", "any"], "window": ["all"], "valid": [10, 20, 50], "be": [0, 1]}
MANAGEMENT = base.MANAGEMENT
TIME_STOP = 200
STOP_CAP_ATR = 1e9
COSTS = {"XAUUSD": base._cz["XAUUSD"]}
FILL_SPREAD = {"XAUUSD": max(v["mean"] for k, v in base._sp.items() if k.startswith("XAUUSD"))}
EXECUTOR = base.executors.bracket(tgt=2.0, be_key="be", time_stop_bars=TIME_STOP)


def signals(B, p, M):
    old = (base.PIP, base.TOL)
    base.PIP, base.TOL = 0.1, 0.3 * 0.1                       # gold: pip $0.10, tolerance $0.03
    try:
        base._CACHE.clear() if len(base._CACHE) > 64 else None
        return base.signals(B, p, M)
    finally:
        base.PIP, base.TOL = old
