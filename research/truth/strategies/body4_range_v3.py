"""Owner's body-engulf 4-candle range, version 3 (owner, 2026-11-08: "a doji counts ... that doji was bullish ... test it
with the doji ... at 1:2 ... 1:10R at breakeven at 75% of the journey"). Fixed BEFORE any v3 result.
Pre-registration: research/body4/PREREGISTRATION_V3.md (v1 4R and v2 2R/1R were rejected).

Changes from v2: (1) lookback colours: a doji (open = close) is BULLISH (close >= open), so it counts for a buy's lookback
and not for a sell's; the four pattern candles still need real bodies. (2) targets 2R and 10R. (3) breakeven at 75% of
the way to the target (+1.5R for 2R, +7.5R for 10R), on or off.
Unchanged: pattern (candles 2 and 4 body-engulf 1 and 3), range = high-low of the four, lookback >= 3 of the 5 candles
before candle 1 (on/off), skip when candle 4 closes beyond the midpoint, entry 50% / 70%, stop at the range end + buffer
0/5/10/20% of the range, waiting orders (first fill removes the others), wider opposite range wins, cancel when price
reaches the target before the fill, no new setups Friday 20:30 - Sunday 23:00 UTC, Friday 20:30 UTC close, RoboForex
Prime costs (spread decides fills, commission per trade, slippage on stops), the lab's swaps (swap-free reported apart).
SEARCH 6 timeframes (M1-H4) x target 2 x entry 2 x breakeven 2 x buffer 4 x lookback 2 = 384 configurations, 12 markets.
Priors (told to the owner): v1 (4R) and v2 (2R, 1R) rejected, 576 settings, about 0 before costs; P4 breakeven; P14.
"""
import os, sys, json
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "body4"))
import body4_scan as SC    # noqa: E402
import body4_fast as FA    # noqa: E402

NAME = "body4_range_v3"
HYPOTHESIS = ("With dojis counted as bullish in the lookback, the body-engulf range entries reach a 10R (or 2R) target "
              "often enough to pay costs and swaps (10R needs about 1 win in 10 before costs).")
RULES = __doc__
FAMILY = ["engulfing", "owner-idea", "limit-entry", "breakeven", "intraday", "multi-market", "multi-timeframe", "range", "large-target"]
MARKETS = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4"]
GRID = {"target": [10, 2], "entry": [0.5, 0.7], "be": [1, 0], "buffer": [0.0, 0.05, 0.1, 0.2], "lookback": [1, 0]}
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
BE_FRAC = 0.75             # breakeven at 75% of the way to the target
DOJI_BULLISH = True        # a doji counts as bullish in the lookback
_CACHE = {}


def setups(B, p, M):
    sample = p.get("sample", "flow")
    t = np.asarray(B["t"], np.int64)
    key = (M.sym, int(B["minutes"]), sample, len(t), int(t[-1]) if len(t) else 0, DOJI_BULLISH)
    if key not in _CACHE:
        _CACHE[key] = SC.setups(B, int(B["minutes"]), sample=sample, doji_bullish=DOJI_BULLISH)
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
    rows, amb = FA.run(M1, S_, costs, dict(entry=p["entry"], buffer=p["buffer"], be=p["be"], lookback=p["lookback"],
                                           target=p["target"], be_frac=BE_FRAC),
                       cut=cut if cut else 2 ** 62, delay=delay, gaps=M.gaps)
    return rows


def EXECUTOR(M, B, C, p, cut=2 ** 62, cost_mult=1.0, swap_mult=1.0, delay=0):
    res = detail(M, B, p, cut=cut, delay=delay)[:, :8].copy()
    if cost_mult != 1.0 or swap_mult != 1.0:
        res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
    return res
