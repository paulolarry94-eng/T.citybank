"""Deep M1 study scanner (research/sweep6/PREREGISTRATION.md, Phase 2 greedy result, 2026-11-12): the owner's four-candle
reversal (v2 reading: loose engulf, doji = bullish, candles 2 and 4 bodies >= 40%; with or without a pivot sweep), candle 4
closing 12:00-16:00 UTC (London-New York overlap), not on a Monday; sell limit at 60% of the range (buy mirror), stop at the
range end, a fixed 20R target; the order waits up to 60 candles (cancelled if price reaches the stop first); one trade at a
time per market and timeframe; Friday close. RoboForex Prime costs + swaps (lab standard where Prime has no price).
Chosen on M1 2011-15; on M1 it was +0.024R a trade before costs in 2011-15 and negative in 2016-19 (-0.039R) and 2020-22
(-0.037R). Phase 3 runs it on every timeframe and market as pre-registered.
"""
import os, sys, json
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "sweep6")); sys.path.insert(0, os.path.join(_here, "..", "..", "sweep5"))
import sweep6_scan as SW   # noqa: E402
import sweep5_fast as FA   # noqa: E402

NAME = "sweep6_scanner_v1"
HYPOTHESIS = ("The four-candle reversal formed in the London-New York overlap (not Mondays), entered on a 60% pull-back with a "
              "20R target, has enough raw edge to pay costs on some timeframe and market.")
RULES = __doc__
FAMILY = ["engulfing", "owner-idea", "limit-entry", "multi-market", "multi-timeframe", "range", "large-target", "session",
          "liquidity", "sweep", "pivot", "reversal", "filter-mining", "winner-anatomy"]
MARKETS = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4"]
GRID = {"rule": ["scanner"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 10 ** 6
STOP_CAP_ATR = 1e9
SELECT_BY = "s"
TARGET_R, LIFE = 20.0, 60

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
ZERO = dict(spread=0.0, commission=0.0, slippage=0.0)
_CACHE = {}


def setups(B, p, M):
    t = np.asarray(B["t"], np.int64)
    key = (M.sym, int(B["minutes"]), len(t), int(t[-1]) if len(t) else 0)
    if key not in _CACHE:
        if len(_CACHE) > 3:
            _CACHE.clear()
        S_, L_ = SW.setups(B, int(B["minutes"]), M.sym)
        S_["allow"] = (S_["hour"] >= 12) & (S_["hour"] < 16) & (S_["weekday"] != 0)
        _CACHE[key] = (S_, L_)
    return _CACHE[key]


def signals(B, p, M):
    S_, L_ = setups(B, p, M)
    a = S_["allow"]
    return [(int(k), int(s), float(x)) for k, s, x in zip(S_["k"][a], S_["side"][a], S_["stop"][a])]


def detail(M, B, p, cut=2 ** 62, swap=None, split=None):
    S_, L_ = setups(B, p, M)
    O = dict(t_conf=S_["t_conf"], side=S_["side"], level=S_["level"], stop=S_["stop"], width=S_["hi"] - S_["lo"],
             t_exp=S_["t_conf"] + LIFE * int(B["minutes"]) * 60)
    costs = dict(split or SPLIT[M.sym], swap=M.swap if swap is None else swap)
    M1 = dict(ts=M.ts, o=M.o, h=M.h, l=M.l, c=M.G.c)
    return FA.run(M1, O, L_, costs, "fixed", allow=S_["allow"], cut=cut if cut else 2 ** 62, gaps=M.gaps, tgt_r=TARGET_R)


def EXECUTOR(M, B, C, p, cut=2 ** 62, cost_mult=1.0, swap_mult=1.0, delay=0):
    res = detail(M, B, p, cut=cut)[:, :8].copy()
    if cost_mult != 1.0 or swap_mult != 1.0:
        res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
    return res
