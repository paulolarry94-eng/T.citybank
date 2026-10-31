"""TEMPLATE — copy this file, rename it, fill it in, then run:
    python3 research/truth/run.py research/truth/strategies/<your_file>.py

Rules of the lab (do not fight them, they are what makes the answer true):
- signals() may only use bars up to and including the signal bar (the lab checks this automatically).
- Fix the GRID before running. Once the 2023-25 look is logged, changing this file requires a new NAME.
- Keep the grid small and meaningful: every extra setting is another lottery ticket the deflated Sharpe charges for.
"""
import numpy as np

NAME = "my_idea_v1"                       # results go to research/results/truth/<NAME>/
HYPOTHESIS = "Why should this make money? Who is on the other side?"
RULES = "Plain-language rules, used for the EA specification."
MARKETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]   # any symbol with data/<SYM>_M1_bid_<YEAR>.npz and an entry in costs.json
TIMEFRAMES = ["H1", "H4"]                  # M5 M15 M30 H1 H4 D1 (H4 / D1 on the broker clock, 22:00 UTC)
GRID = {"n": [20, 55]}                     # ordered lists: neighbours = one step either side
# Optional:
# MANAGEMENT = {"tgt": [2.0, 3.0, 0.0], "trail": [0.0, 3.0], "bias": [0, 1]}   # target in R (0 = none), chandelier trail in ATR, H4 EMA50 filter
# TIME_STOP = 50                           # bars on the strategy's timeframe
# STOP_CAP_ATR = 5.0                       # stops wider than this x ATR are skipped


def signals(B, p, M):
    """B: closed bars of p['tf'] — arrays t (bar open, UTC s), o, h, l, c, atr (14-bar SMA true range), nxt, minutes.
    p: one parameter set, e.g. {'tf': 'H4', 'n': 20}. M: the market (M.cost, M.sym).
    Return rows (bar, side, stop) -> market order at the next bar's open, stop at `stop`;
    or (bar, side, stop, limit_price, valid_bars) -> limit order from the next bar, valid that many bars."""
    rows = []
    return rows
