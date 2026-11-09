"""Owner's body-engulf 4-candle range, version 6 (owner, 2026-11-09): "the second and last candle must be 60% body and
above, no tiny body; the lookback updated to just 2 candles (a sell needs two bearish candles before the setup); test if
60% body is better than just two bearish candles; hammer down everywhere on all markets; minimum 1:4, test 5R and 6R".
Fixed BEFORE any v6 result. Pre-registration: research/body4/PREREGISTRATION_V6.md.

Pattern: candles 1-4 alternate; candles 2 and 4 body-engulf candles 1 and 3 (strict, the owner's original rule); range =
high-low of the four; skip when candle 4 closes beyond the midpoint.
  body60  1: candles 2 and 4 each have a body >= 60% of their own high-low; 0: no body rule.
  lb2     1: the 2 candles right before candle 1 both go the trade's way (dojis bullish); 0: no lookback.
Orders: limit at 50% of the range, stop at the range end, target 4R / 5R / 6R, no breakeven; waiting orders (first fill
removes the others), a wider opposite range replaces them, cancel if the target is reached before the fill.
Safe window: candle 4 closes 07:00-19:00 UTC, no US news days, everything flat at 20:30 UTC. RoboForex Prime costs.
SEARCH 6 timeframes x body60 2 x lb2 2 x target 3 = 72 configurations.
Priors (told to the owner): v1-v5 and the gold study rejected; body share and lookback made no difference on gold; 4R-6R
hit rates at chance in v4.
"""
import os, sys, json
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "body4"))
import body4_scan as SC    # noqa: E402
import body4_fast as FA    # noqa: E402

NAME = "body4_range_v6"
HYPOTHESIS = ("A body-engulf range whose engulfing candles are at least 60% body, after two candles in the trade's "
              "direction, traded in safe hours, reaches 4R-6R often enough to pay its costs.")
RULES = __doc__
FAMILY = ["engulfing", "owner-idea", "limit-entry", "intraday", "multi-market", "multi-timeframe", "range", "large-target",
          "session", "news-filter", "candle-body", "lookback"]
MARKETS = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4"]
GRID = {"body60": [1, 0], "lb2": [1, 0], "target": [4, 5, 6]}
ENTRY, BUFFER, BODY_MIN = 0.5, 0.0, 0.6
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
DOJI_BULLISH = True
SAFE_FROM, SAFE_TO = 7 * 3600, 19 * 3600
_cal = json.load(open(os.path.join(_here, "..", "calendars", "us_news_days.json")))
import datetime as _dt                        # noqa: E402
from zoneinfo import ZoneInfo as _Z           # noqa: E402
NEWS = {_dt.date.fromisoformat(d) for k in ("nfp", "cpi", "fomc") for d in _cal[k]}
_NY = _Z("America/New_York")
_CACHE, _ALLOW = {}, {}


def safe_mask(S_):
    """1 = candle 4 closes 07:00-19:00 UTC and not on a US news day."""
    tc = np.asarray(S_["t_conf"], np.int64)
    sod = tc % 86400
    news = np.array([_dt.datetime.fromtimestamp(int(x) - 1, _NY).date() in NEWS for x in tc], bool)
    return ((sod >= SAFE_FROM) & (sod < SAFE_TO) & ~news).astype(np.int64)


def setups(B, p, M):
    sample = p.get("sample", "flow")
    t = np.asarray(B["t"], np.int64)
    key = (M.sym, int(B["minutes"]), sample, len(t), int(t[-1]) if len(t) else 0)
    if key not in _CACHE:
        _CACHE[key] = SC.setups(B, int(B["minutes"]), sample=sample, doji_bullish=DOJI_BULLISH, engulf="body")
    return _CACHE[key]


def _allow(M, B, p, S_):
    key = (M.sym, int(B["minutes"]), p.get("sample", "flow"), int(p["body60"]), int(p["lb2"]), len(S_["k"]))
    if key not in _ALLOW:
        a = safe_mask(S_).astype(bool)
        if p["body60"]:
            a &= (S_["body2"] >= BODY_MIN) & (S_["body4"] >= BODY_MIN)
        if p["lb2"]:
            a &= S_["lookback2"] >= 2
        _ALLOW[key] = a.astype(np.int64)
    return _ALLOW[key]


def signals(B, p, M):
    """What the lab's look-ahead check sees: every setup that passes the pattern, intent and v6 rules at candle 4, with its
    stop. The orders themselves are run by EXECUTOR on M1 data."""
    S_ = setups(B, p, M)
    mid = (S_["hi"] + S_["lo"]) / 2
    ok = np.where(S_["side"] > 0, S_["c4"] > mid, S_["c4"] < mid) & (_allow(M, B, p, S_) == 1)
    stop = np.where(S_["side"] > 0, S_["lo"], S_["hi"])
    return [(int(k), int(s), float(x)) for k, s, x in zip(S_["k"][ok], S_["side"][ok], stop[ok])]


def detail(M, B, p, cut=2 ** 62, delay=0, swap=None):
    """All 16 columns of body4_fast.simulate for one market and configuration (see that file)."""
    S_ = setups(B, p, M)
    costs = dict(SPLIT[M.sym], swap=M.swap if swap is None else swap)
    M1 = dict(ts=M.ts, o=M.o, h=M.h, l=M.l, c=M.G.c)
    rows, amb = FA.run(M1, S_, costs, dict(entry=ENTRY, buffer=BUFFER, be=0, lookback=0, target=p["target"], be_frac=0.75),
                       cut=cut if cut else 2 ** 62, delay=delay, gaps=M.gaps, allow=_allow(M, B, p, S_), day_close=True)
    return rows


def EXECUTOR(M, B, C, p, cut=2 ** 62, cost_mult=1.0, swap_mult=1.0, delay=0):
    res = detail(M, B, p, cut=cut, delay=delay)[:, :8].copy()
    if cost_mult != 1.0 or swap_mult != 1.0:
        res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
    return res
