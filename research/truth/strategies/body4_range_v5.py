"""Owner's body-engulf 4-candle range, version 5 (owner, 2026-11-08, after the XAGUSD M5 chart: "test both engulf, loosen
ones, then test the data in 2023-2025, then try layering timeframes: one big with small, both align, then entry in small").
Fixed BEFORE any v5 result. Pre-registration: research/body4/PREREGISTRATION_V5.md.

Changes from v4:
  engulf  "body": candles 2 and 4 fully cover the previous body (v1-v4); "loose": they only close beyond the previous
          candle's open (a gap at the open is allowed, as in the owner's silver chart).
  layer   "none", or "on": a small-timeframe setup trades only if the bigger timeframe had a setup in the SAME direction
          whose candle 4 closed at most 2 big candles earlier (big: M1->M15, M5->H1, M15->H4, M30->H4, H1->H4, H4->D1 with
          the day starting 22:00 UTC). The big setup must pass the same intent and lookback rules. Entry, stop and target
          come from the small setup.
  window  "safe" only (owner: "trade only on safe windows"): candle 4 closes 07:00-19:00 UTC, no US news days (NFP, CPI,
          FOMC), everything flat at 20:30 UTC.
  narrowed from the v1-v4 development results (2011-22 only; stated as such): entry 50% only (70% lost more in 70-84% of
  pairs), stop buffer 0% (owner's rule) or 20% (the least bad), targets 2R, 3R, 5R, 10R.
Unchanged: lookback >= 3 of 5 (dojis bullish; on/off), skip when candle 4 closes beyond the midpoint, breakeven at 75% of
the way (on/off), waiting orders (first fill removes the others), wider opposite range wins, cancel when the target is
reached before the fill, RoboForex Prime costs (spread decides fills), the lab's swaps.
SEARCH 6 timeframes x engulf 2 x layer 2 x target 4 x breakeven 2 x buffer 2 x lookback 2 = 768 configurations.
Priors (told to the owner): v1-v4 rejected (4,416 settings, about 0 before costs); multi-timeframe four-candle scans and
the loose "closes beyond the open" engulf with an EMA were rejected (ema4 family); layering is new.
"""
import os, sys, json
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "body4"))
import body4_scan as SC    # noqa: E402
import body4_fast as FA    # noqa: E402

NAME = "body4_range_v5"
HYPOTHESIS = ("A small-timeframe body-engulf range that agrees with the same setup on a bigger timeframe (strict or loose "
              "engulfing), traded in safe hours, reaches 2R-10R often enough to pay its costs.")
RULES = __doc__
FAMILY = ["engulfing", "owner-idea", "limit-entry", "breakeven", "intraday", "multi-market", "multi-timeframe", "range", "large-target", "session", "news-filter", "layering"]
MARKETS = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4"]
GRID = {"engulf": ["body", "loose"], "layer": ["none", "on"], "target": [2, 3, 5, 10], "be": [1, 0], "buffer": [0.0, 0.2], "lookback": [1, 0]}
ENTRY = 0.5
HTF = {"M1": "M15", "M5": "H1", "M15": "H4", "M30": "H4", "H1": "H4", "H4": "D1"}
HTF_MIN = {"M15": 15, "H1": 60, "H4": 240, "D1": 1440}
LAYER_BARS = 2
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
    key = (M.sym, int(B["minutes"]), sample, len(t), int(t[-1]) if len(t) else 0, DOJI_BULLISH, p["engulf"])
    if key not in _CACHE:
        _CACHE[key] = SC.setups(B, int(B["minutes"]), sample=sample, doji_bullish=DOJI_BULLISH, engulf=p["engulf"])
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
_HTFB = {}


def _htf_bars(M, htf):
    if htf != "D1":
        return M.bars(htf)
    if (M.sym, "D1") not in _HTFB:
        import importlib.util
        spec = importlib.util.spec_from_file_location("lab_engine", os.path.join(_here, "..", "..", "engine.py"))
        EN = importlib.util.module_from_spec(spec); spec.loader.exec_module(EN)
        bt, bo, bh, bl, bc, _ = EN.resample(M.ts, M.o, M.h, M.l, M.G.c, 1440, 22 * 60)    # trading day from 22:00 UTC
        _HTFB[(M.sym, "D1")] = dict(t=np.asarray(bt, np.int64), o=bo, h=bh, l=bl, c=bc, minutes=1440)
    return _HTFB[(M.sym, "D1")]


def _big_setups(M, B, p):
    """The bigger timeframe's setups that pass the intent and (if on) lookback rules, same engulf type."""
    htf = HTF[{1: "M1", 5: "M5", 15: "M15", 30: "M30", 60: "H1", 240: "H4"}[int(B["minutes"])]]
    H = _htf_bars(M, htf)
    SH = SC.setups(H, HTF_MIN[htf], sample=p.get("sample", "flow"), doji_bullish=DOJI_BULLISH, engulf=p["engulf"])
    mid = (SH["hi"] + SH["lo"]) / 2
    ok = np.where(SH["side"] > 0, SH["c4"] > mid, SH["c4"] < mid)
    if p["lookback"]:
        ok &= SH["lookback"] >= 3
    return SH["t_conf"][ok], SH["side"][ok], HTF_MIN[htf] * 60


def _allow(M, B, p, S_):
    key = (M.sym, int(B["minutes"]), p.get("sample", "flow"), p["engulf"], p["layer"], p["lookback"], len(S_["k"]))
    if key not in _ALLOW:
        a = allow_mask(S_, "safe")
        if p["layer"] == "on":
            tb, sb, sec = _big_setups(M, B, p)
            a = a * SC.layer_mask(S_["t_conf"], S_["side"], tb, sb, LAYER_BARS * sec)
        _ALLOW[key] = a
    return _ALLOW[key]


def detail(M, B, p, cut=2 ** 62, delay=0, swap=None):
    """All 16 columns of body4_fast.simulate for one market and configuration (see that file)."""
    S_ = setups(B, p, M)
    costs = dict(SPLIT[M.sym], swap=M.swap if swap is None else swap)
    M1 = dict(ts=M.ts, o=M.o, h=M.h, l=M.l, c=M.G.c)
    rows, amb = FA.run(M1, S_, costs, dict(entry=ENTRY, buffer=p["buffer"], be=p["be"], lookback=p["lookback"],
                                           target=p["target"], be_frac=BE_FRAC),
                       cut=cut if cut else 2 ** 62, delay=delay, gaps=M.gaps, allow=_allow(M, B, p, S_), day_close=True)
    return rows


def EXECUTOR(M, B, C, p, cut=2 ** 62, cost_mult=1.0, swap_mult=1.0, delay=0):
    res = detail(M, B, p, cut=cut, delay=delay)[:, :8].copy()
    if cost_mult != 1.0 or swap_mult != 1.0:
        res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
    return res
