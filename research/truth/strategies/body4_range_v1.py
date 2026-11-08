"""Owner's body-engulf 4-candle range (Q30), rules as corrected by the owner on 2026-11-08. Fixed BEFORE any backtest
result. Pre-registration: research/body4/PREREGISTRATION.md. Specification: research/body4/body4_orders.py (reference
engine); this file runs the identical fast engine research/body4/body4_fast.py (tests: research/truth/tests/test_body4.py).

PATTERN (SELL; BUY is the mirror), four consecutive candles of one timeframe:
  1 bullish, 2 bearish whose BODY engulfs candle 1's body (opens at/above 1's close, closes below 1's open),
  3 bullish, 4 bearish whose BODY engulfs candle 3's body. Wicks do not count for the engulfing. Dojis are neither.
  Range = highest high to lowest low of the four candles (wicks count here).
  lookback (option): at least 3 of the 5 candles before candle 1 bearish (bullish for a buy); dojis count for neither.
  intent: candle 4 must close on the trade's side of the midpoint; otherwise the setup is skipped (owner: "price above
  the midpoint shows no intent").
TRADE
  entry  limit at 50% of the range (the midpoint) or at a 70% pull-back (sell: low + 0.7 x range; buy: high - 0.7 x range);
         skipped if price is already through that level when the order would be placed.
  stop   far end of the range + buffer 0 / 5 / 10 / 20% of the range. 1R = entry to stop. Target 4R.
  breakeven (option): at +2R the stop moves to the entry price.
  orders same direction: every valid setup waits as a limit order; the first to fill removes the others. Opposite
         direction: replaces all waiting orders only if its range is wider than every one of them. An order is
         cancelled if price reaches its target before it fills. While a trade is open new setups are ignored.
  week   no setup from Friday 20:30 UTC to Sunday 23:00 UTC (Monday 00:00 Lagos); everything closes Friday 20:30 UTC.
         Trades may be held overnight Monday-Thursday: they pay swaps (the lab's swap; swap-free reported separately).
COSTS  RoboForex Prime published (spread, commission, slippage kept apart: the spread decides whether a price is reached,
       commission is charged per trade, slippage on stop and market exits); XAGUSD and UK100: the lab's all-in estimate
       split 50% spread, 25% commission, 25% slippage.
SEARCH timeframes M1 M5 (stage 1, owner) and M15 M30 H1 H4 (stage 2) x entry 2 x breakeven 2 x buffer 4 x lookback 2
       = 192 configurations, 12 markets. Selection by edge quality (cycle-centric), the lab's gate and one 2023-25 look.
CONTROL (controls.py): the same order logic on the same four alternating candles WITHOUT the engulfing.
Priors (told to the owner): every earlier four-candle / engulfing idea was rejected (about 6,200 settings, P14);
resting limit entries suffer adverse selection (P2); breakeven stops added nothing out of sample (P4).
"""
import os, sys, json
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "body4"))
import body4_scan as SC    # noqa: E402
import body4_fast as FA    # noqa: E402

NAME = "body4_range_v1"
HYPOTHESIS = ("Four alternating candles whose 2nd and 4th bodies engulf the 1st and 3rd mark a range whose midpoint (or 70% "
              "pull-back) is a good place to join the 4th candle's direction for a 4R move, after costs and swaps.")
RULES = __doc__
FAMILY = ["engulfing", "owner-idea", "limit-entry", "breakeven", "intraday", "multi-market", "multi-timeframe", "range"]
MARKETS = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4"]
GRID = {"entry": [0.5, 0.7], "be": [1, 0], "buffer": [0.0, 0.05, 0.1, 0.2], "lookback": [1, 0]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 10 ** 6
STOP_CAP_ATR = 1e9
SELECT_BY = "s"

_rf = json.load(open(os.path.join(_here, "..", "costs_roboforex_prime.json")))
_lab = json.load(open(os.path.join(_here, "..", "costs.json")))
COSTS = {m: _rf["realistic"][m] for m in MARKETS if m in _rf["realistic"]}


def _split(sym):
    c = _rf["components"].get(sym)
    if c is None:                                        # not on RoboForex Prime: the lab's all-in estimate
        tot = _lab[sym]["cost"]
        return dict(spread=0.5 * tot, commission=0.25 * tot, slippage=0.25 * tot)
    pip = c.get("pip", 1.0)
    g = lambda *ks: next(c[k] for k in ks if k in c)
    return dict(spread=g("spread", "spread_pips", "spread_points") * (pip if "spread_pips" in c else 1.0),
                commission=g("commission_round_trip", "commission_pips_round_trip", "commission_points_round_trip")
                * (pip if "commission_pips_round_trip" in c else 1.0),
                slippage=g("slippage", "slippage_pips", "slippage_points") * (pip if "slippage_pips" in c else 1.0))


SPLIT = {m: _split(m) for m in MARKETS}
_CACHE = {}


def setups(B, p, M):
    sample = p.get("sample", "flow")
    t = np.asarray(B["t"], np.int64)
    key = (M.sym, int(B["minutes"]), sample, len(t), int(t[-1]) if len(t) else 0)
    if key not in _CACHE:
        _CACHE[key] = SC.setups(B, int(B["minutes"]), sample=sample)
    return _CACHE[key]


def signals(B, p, M):
    """What the lab's look-ahead check sees: every setup that passes the pattern, lookback and intent rules at candle 4,
    with its stop. The orders themselves are run by EXECUTOR on M1 data."""
    S_ = setups(B, p, M)
    mid = (S_["hi"] + S_["lo"]) / 2
    ok = np.where(S_["side"] > 0, S_["c4"] > mid, S_["c4"] < mid)
    if p["lookback"]:
        ok &= S_["lookback"] >= 3
    w = S_["hi"] - S_["lo"]
    stop = np.where(S_["side"] > 0, S_["lo"] - p["buffer"] * w, S_["hi"] + p["buffer"] * w)
    return [(int(k), int(s), float(x)) for k, s, x in zip(S_["k"][ok], S_["side"][ok], stop[ok])]


def detail(M, B, p, cut=2 ** 62, delay=0, swap=None):
    """All 16 columns of body4_fast.simulate for one market and configuration (see that file)."""
    S_ = setups(B, p, M)
    costs = dict(SPLIT[M.sym], swap=M.swap if swap is None else swap)
    M1 = dict(ts=M.ts, o=M.o, h=M.h, l=M.l, c=M.G.c)
    rows, amb = FA.run(M1, S_, costs, dict(entry=p["entry"], buffer=p["buffer"], be=p["be"], lookback=p["lookback"]),
                       cut=cut if cut else 2 ** 62, delay=delay, gaps=M.gaps)
    return rows


def EXECUTOR(M, B, C, p, cut=2 ** 62, cost_mult=1.0, swap_mult=1.0, delay=0):
    res = detail(M, B, p, cut=cut, delay=delay)[:, :8].copy()
    if cost_mult != 1.0 or swap_mult != 1.0:
        res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
    return res
