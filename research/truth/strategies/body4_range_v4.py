"""Owner's body-engulf 4-candle range, version 4 (owner, 2026-11-08: "what made the biggest loser ... avoid them all ...
test 2RR all the way to 10RR ... trade only on safe windows ... find the RR that hits 50% of the time and the config that
makes that possible"). Fixed BEFORE any v4 result. Pre-registration: research/body4/PREREGISTRATION_V4.md.

Changes from v3: (1) targets 2R, 3R, 4R, 5R, 6R, 7R, 8R, 9R and 10R; (2) window "all" (v3 rules) or "safe":
  - setups only when candle 4 closes between 07:00 and 19:00 UTC (London and New York hours; no Asian session),
  - no setups on US high-impact news days (NFP, CPI, FOMC statement; New York date of candle 4),
  - every order cancelled and every trade closed at 20:30 UTC each day (before the rollover: no overnight holds, no
    swaps, no overnight gaps, no Asian session).
Unchanged from v3: pattern, lookback (>= 3 of 5, dojis bullish; on/off), skip when candle 4 closes beyond the midpoint,
entry 50% / 70%, stop at the range end + buffer 0/5/10/20%, breakeven at 75% of the way to the target (on/off), waiting
orders (first fill removes the others), wider opposite range wins, cancel when price reaches the target before the fill,
Friday close, RoboForex Prime costs (spread decides fills, commission per trade, slippage on stops), the lab's swaps.
SEARCH 6 timeframes x target 9 x window 2 x entry 2 x breakeven 2 x buffer 4 x lookback 2 = 3,456 configurations.
Priors (told to the owner): v1-v3 rejected (960 settings, about 0 before costs); session windows chosen in advance gave no
edge before (P17, osc_turn_sessions_v1, Leg 34 pocket scan). This window is chosen to cut costs and gap risk, not edge.
"""
import os, sys, json
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "body4"))
import body4_scan as SC    # noqa: E402
import body4_fast as FA    # noqa: E402

NAME = "body4_range_v4"
HYPOTHESIS = ("Traded only in liquid London/New York hours, away from US news days and flat before the rollover, the "
              "body-engulf range reaches some target between 2R and 10R often enough to pay its costs.")
RULES = __doc__
FAMILY = ["engulfing", "owner-idea", "limit-entry", "breakeven", "intraday", "multi-market", "multi-timeframe", "range", "large-target", "session", "news-filter"]
MARKETS = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4"]
GRID = {"target": [2, 3, 4, 5, 6, 7, 8, 9, 10], "window": ["safe", "all"], "entry": [0.5, 0.7], "be": [1, 0], "buffer": [0.0, 0.05, 0.1, 0.2], "lookback": [1, 0]}
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
SAFE_FROM, SAFE_TO = 7 * 3600, 19 * 3600     # candle 4 must close in [07:00, 19:00) UTC in the safe window
_cal = json.load(open(os.path.join(_here, "..", "calendars", "us_news_days.json")))
import datetime as _dt                        # noqa: E402
from zoneinfo import ZoneInfo as _Z           # noqa: E402
NEWS = {_dt.date.fromisoformat(d) for k in ("nfp", "cpi", "fomc") for d in _cal[k]}
_NY = _Z("America/New_York")


def allow_mask(S_, window):
    """1 = the setup may trade in this window (safe: London/New York hours and not a US news day)."""
    if window != "safe":
        return np.ones(len(S_["k"]), np.int64)
    tc = np.asarray(S_["t_conf"], np.int64)
    sod = tc % 86400
    inwin = (sod >= SAFE_FROM) & (sod < SAFE_TO)
    news = np.array([_dt.datetime.fromtimestamp(int(x) - 1, _NY).date() in NEWS for x in tc], bool)
    return (inwin & ~news).astype(np.int64)
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
    ok &= _allow(M, B, p, S_) == 1
    w = S_["hi"] - S_["lo"]
    stop = np.where(S_["side"] > 0, S_["lo"] - p["buffer"] * w, S_["hi"] + p["buffer"] * w)
    return [(int(k), int(s), float(x)) for k, s, x in zip(S_["k"][ok], S_["side"][ok], stop[ok])]


_ALLOW = {}


def _allow(M, B, p, S_):
    key = (M.sym, int(B["minutes"]), p.get("sample", "flow"), p["window"], len(S_["k"]))
    if key not in _ALLOW:
        _ALLOW[key] = allow_mask(S_, p["window"])
    return _ALLOW[key]


def detail(M, B, p, cut=2 ** 62, delay=0, swap=None):
    """All 16 columns of body4_fast.simulate for one market and configuration (see that file)."""
    S_ = setups(B, p, M)
    costs = dict(SPLIT[M.sym], swap=M.swap if swap is None else swap)
    M1 = dict(ts=M.ts, o=M.o, h=M.h, l=M.l, c=M.G.c)
    rows, amb = FA.run(M1, S_, costs, dict(entry=p["entry"], buffer=p["buffer"], be=p["be"], lookback=p["lookback"],
                                           target=p["target"], be_frac=BE_FRAC),
                       cut=cut if cut else 2 ** 62, delay=delay, gaps=M.gaps, allow=_allow(M, B, p, S_),
                       day_close=p["window"] == "safe")
    return rows


def EXECUTOR(M, B, C, p, cut=2 ** 62, cost_mult=1.0, swap_mult=1.0, delay=0):
    res = detail(M, B, p, cut=cut, delay=delay)[:, :8].copy()
    if cost_mult != 1.0 or swap_mult != 1.0:
        res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
    return res
