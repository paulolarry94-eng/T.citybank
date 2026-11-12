"""Owner's pivot-sweep body-engulf range (2026-11-12). Pre-registration: research/sweep4/PREREGISTRATION.md.

SELL (BUY is the mirror): a live TradingView-style pivot high (left = right = N) is swept by candle 1 or 2 (c12) or by the
bar before candle 1 or any of the four (near); candles 1-4 alternate with strict body engulfing on candles 2 and 4, each
>= 60% body; range = candle 4's low to the highest high of the four; sell limit at 60% of the range up from candle 4's
low; stop at the range high (range), + 20% of the range (buf20), or trailed to new pivot highs (trail); target 3-15R or
the nearest (p1) / second (p2) live pivot low at least 3R away. Friday close; RoboForex Prime costs + swaps.
"""
import os, sys, json
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "sweep4"))
import sweep4_scan as SW   # noqa: E402
import sweep4_fast as FA   # noqa: E402
import pivots as PV        # noqa: E402

NAME = "sweep4_pivot_v1"
HYPOTHESIS = ("Right after a pivot level is swept, a strong two-step body-engulf reversal marks trapped breakout traders; "
              "a 60% pull-back entry with the stop beyond the sweep reaches 3R-15R or the next pivot often enough to pay.")
RULES = __doc__
FAMILY = ["engulfing", "owner-idea", "limit-entry", "multi-market", "multi-timeframe", "range", "large-target", "candle-body",
          "liquidity", "sweep", "pivot", "reversal", "structure", "trailing"]
MARKETS = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4"]
GRID = {"piv": [10, 5], "sweep": ["c12", "near"], "stop": ["range", "buf20", "trail"], "target": [3, 5, 8, 10, 15, "p1", "p2"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 10 ** 6
STOP_CAP_ATR = 1e9
SELECT_BY = "s"
ENTRY = 0.6

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
    t = np.asarray(B["t"], np.int64)
    key = (M.sym, int(B["minutes"]), int(p["piv"]), len(t), int(t[-1]) if len(t) else 0)
    if key not in _CACHE:
        S_ = SW.setups(B, int(B["minutes"]), piv=int(p["piv"]))
        S_["conf_hi"], S_["conf_lo"] = PV.confirmations(B["t"], B["h"], B["l"], S_["ph"], S_["pl"], int(p["piv"]), int(B["minutes"]))
        S_["none"] = ~S_["near"]
        _CACHE[key] = S_
    return _CACHE[key]


def orders(S_, p):
    """Entry level, stop, target (R), width and the allow mask for one configuration."""
    lvl, stp, risk, w = SW.levels(S_, buffer=0.2 if p["stop"] == "buf20" else 0.0, entry=ENTRY)
    if p["target"] in ("p1", "p2"):
        tgt = SW.structural_r(S_, lvl, risk, which=1 if p["target"] == "p1" else 2)
    else:
        tgt = np.full(len(lvl), float(p["target"]))
    allow = S_[p["sweep"]] & np.isfinite(tgt)
    return dict(t_conf=S_["t_conf"], side=S_["side"], level=lvl, stop=stp, tgt=np.where(np.isfinite(tgt), tgt, 0.0),
                width=w), allow


def signals(B, p, M):
    """What the lab's look-ahead check sees: every setup that passes the pattern and sweep rules at candle 4, with its stop.
    The orders themselves are run by EXECUTOR on M1 data."""
    S_ = setups(B, p, M)
    O, allow = orders(S_, p)
    return [(int(k), int(s), float(x)) for k, s, x in zip(S_["k"][allow], S_["side"][allow], O["stop"][allow])]


def detail(M, B, p, cut=2 ** 62, delay=0, swap=None):
    """All 17 columns of sweep4_fast.simulate for one market and configuration (see that file)."""
    S_ = setups(B, p, M)
    O, allow = orders(S_, p)
    costs = dict(SPLIT[M.sym], swap=M.swap if swap is None else swap)
    M1 = dict(ts=M.ts, o=M.o, h=M.h, l=M.l, c=M.G.c)
    rows, amb = FA.run(M1, O, costs, cut=cut if cut else 2 ** 62, delay=delay, gaps=M.gaps, allow=allow.astype(np.int64),
                       trail=p["stop"] == "trail", conf_hi=S_["conf_hi"], conf_lo=S_["conf_lo"])
    return rows


def EXECUTOR(M, B, C, p, cut=2 ** 62, cost_mult=1.0, swap_mult=1.0, delay=0):
    res = detail(M, B, p, cut=cut, delay=delay)[:, :8].copy()
    if cost_mult != 1.0 or swap_mult != 1.0:
        res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
    return res
