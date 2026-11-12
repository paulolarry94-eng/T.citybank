"""Pivot-sweep range v2, the owner's chart reading (2026-11-12). Pre-registration: research/sweep5/PREREGISTRATION.md.
SELL (BUY mirror): candle 1 bullish (doji = bullish), candle 2 bearish closing below candle 1's open, candle 3 bullish, candle
4 bearish closing below candle 3's open; candles 2 and 4 bodies >= 50%; a live Pivot Points High Low (10/10) high swept by
the candle before candle 1, candle 1 or 2 (now) or by any candle from 6 before candle 1 through candle 2 (recent); range =
candle 4's low to the highest high of the four; sell limit at 60% up; the order waits up to `life` candles (cancelled if
price reaches the stop first); stop at the range high (range) or + 0.5 x range (wide); at the fill TP1 / TP2 = the nearest /
next live pivot low; exit partial (60% at TP1, rest to TP2 with the stop at entry - spread - commission), tp1 or tp2.
Friday close; RoboForex Prime costs + swaps.
"""
import os, sys, json
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "sweep5"))
import sweep5_scan as SW   # noqa: E402
import sweep5_fast as FA   # noqa: E402

NAME = "sweep5_pivot_v2"
HYPOTHESIS = ("After a pivot is swept, a two-step engulfing reversal traps breakout traders; a 60% pull-back limit with the stop "
              "beyond the four candles reaches the next pivots (TP1, TP2) often enough to pay, taking 60% at TP1.")
RULES = __doc__
FAMILY = ["engulfing", "owner-idea", "limit-entry", "multi-market", "multi-timeframe", "range", "candle-body", "liquidity",
          "sweep", "pivot", "reversal", "structure", "partial-exit", "breakeven"]
MARKETS = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1"]
GRID = {"sweep": ["now", "recent"], "stop": ["range", "wide"], "life": [24, 96], "exit": ["partial", "tp1", "tp2"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 10 ** 6
STOP_CAP_ATR = 1e9
SELECT_BY = "s"

_rf = json.load(open(os.path.join(_here, "..", "costs_roboforex_prime.json")))
_lab = json.load(open(os.path.join(_here, "..", "costs.json")))
COSTS = {m: _rf["realistic"][m] for m in MARKETS if m in _rf["realistic"]}


def _split(sym):
    c = _rf["components"].get(sym)
    if c is None:
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
    t = np.asarray(B["t"], np.int64)
    key = (M.sym, int(B["minutes"]), len(t), int(t[-1]) if len(t) else 0)
    if key not in _CACHE:
        _CACHE.clear() if len(_CACHE) > 3 else None
        _CACHE[key] = SW.setups(B, int(B["minutes"]))
    return _CACHE[key]


def signals(B, p, M):
    S_ = setups(B, p, M)
    O = SW.orders(S_, p["stop"], p["life"])
    a = S_[p["sweep"]]
    return [(int(k), int(s), float(x)) for k, s, x in zip(S_["k"][a], S_["side"][a], O["stop"][a])]


def detail(M, B, p, cut=2 ** 62, swap=None, split=None):
    S_ = setups(B, p, M)
    O = SW.orders(S_, p["stop"], p["life"])
    costs = dict(split or SPLIT[M.sym], swap=M.swap if swap is None else swap)
    M1 = dict(ts=M.ts, o=M.o, h=M.h, l=M.l, c=M.G.c)
    return FA.run(M1, O, S_, costs, p["exit"], allow=S_[p["sweep"]], cut=cut if cut else 2 ** 62, gaps=M.gaps)


def EXECUTOR(M, B, C, p, cut=2 ** 62, cost_mult=1.0, swap_mult=1.0, delay=0):
    res = detail(M, B, p, cut=cut)[:, :8].copy()
    if cost_mult != 1.0 or swap_mult != 1.0:
        res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
    return res
