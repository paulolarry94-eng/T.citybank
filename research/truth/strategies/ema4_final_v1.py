"""FINAL TASK (owner 2026-11-03): "out of all the positive variants, use the best and add another indicator that'll go very
well with it to have an additional confluence". Fixed BEFORE the final test: research/final/PREREGISTRATION.md.
BEST VARIANT (chosen AFTER seeing 2011-22 results, ranked over ~6,200 settings by t over 2011-22; HINDSIGHT, said plainly):
ema4_flip_v1 at H4, entry at the 4th candle's close, stop 4th candle + 0.25 ATR, 2R target, A+ and B+.
CONFLUENCE (trend=1): trade only with the H4 50-EMA trend - sell only if the 4th candle closes below the 50 EMA, buy only if
above (the 10-EMA fight resolving with the bigger trend; P6/P7). trend=0 is the variant without it, for comparison.
Because the variant was picked on 2011-22, the clean test is the 2023-25 holdout (one logged look) and Jan-Oct 2026.
---- v1 rules (unchanged) ----
Owner's 4-flip EMA pattern (owner's charts and answers, 2026-11-02).
Pre-registration: research/ema4/PREREGISTRATION.md; detector: research/ema4/scanner.py (replay of the owner's six charts:
research/results/ema4/).

PATTERN (SELL; BUY is the mirror), four consecutive candles of one timeframe, each crossing the 10 EMA with its body:
  1 out above (bullish: opens at/below the line, closes at/above it), 2 back in below (bearish), 3 out above, 4 back in below.
  A doji (no body) is not a breakout (owner: "no"). EMA = 10-period EMA of closes, the line drawn on each candle.
  B+ = the 4th closes below the 3rd candle's open; A+ = also the 2nd closed below the 1st candle's open; otherwise rejected.
TRADE
  entry  mid50: limit at 50% of the 4th candle (wick to wick), live for 3 candles of the pattern timeframe;
         close: market at the 4th candle's close (the next minute's open).            (owner: "test both")
  stop   c4: beyond the 4th candle's extreme; all4: beyond the extreme of all four candles; + buffer 0 / 0.1 / 0.25 / 0.5
         x ATR(14) of the pattern timeframe.                                           (owner: "test it out")
  target 1R / 2R / 3R / 4R.                                                            (owner: "targets test 1-4R")
  exit   at the target, the stop, or the daily close (20:30 UTC, before the rollover; owner: "close daily").
  grade  A: A+ only; AB: A+ and B+.                                                    (owner: "test both")
  orders A new pattern deletes the pending order (owner: an opposite-direction pattern deletes the previous one; a newer
         same-direction pattern replaces it too). One position per market; patterns while a position is open are skipped.
  skip   US NFP, CPI and FOMC days (New York date of the 4th candle's close); stops closer than 3 x the round-trip cost.
         No fills 20:30-23:00 UTC (the lab's rollover block). No overnight holds, so no swaps.
SEARCH (owner: "all hours, all timeframes, all markets ... find where, how and what time it works most")
  timeframes M5 M15 M30 H1 H4 x entry 2 x stop 2 x buffer 4 x target 4 x grade 2 = 640 configurations, 12 markets, all hours.
  "Where and when" (market x timeframe x session cells) is a separate, pre-registered learn-then-check study:
  research/ema4/where_when.py.
CONTROL (controls.py): the same trade on REJECTED four-flip patterns (the 4th did not engulf the 3rd open).
Costs: RoboForex Prime published (research/truth/costs_roboforex_prime.json); XAGUSD and UK100 use the lab standard.
Selection: cycle-centric (edge quality s), as for the owner's earlier ideas.
Priors (told to the owner): every earlier idea of this family (4-leg engulfing SOP, Leg 34, the 3:30 retest; M5 EMA and
engulfing patterns with limit entries) was rejected: about zero before costs, and costs took 0.1-0.2R (P1, P2, P14).
"""
import os, sys, json, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np
from numba import njit

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "ema4"))
import scanner as SC   # noqa: E402

NAME = "ema4_final_v1"
HYPOTHESIS = ("Four consecutive candles crossing the 10 EMA in turn, with the 4th closing beyond the 3rd candle's open (B+), "
              "or also the 2nd beyond the 1st (A+), predict a move in the 4th candle's direction larger than costs.")
RULES = __doc__
FAMILY = ["ema", "engulfing", "intraday", "multi-market", "multi-timeframe", "owner-idea", "limit-entry", "chop"]
MARKETS = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["H4"]
GRID = {"entry": ["close"], "stop": ["c4"], "buffer": [0.25], "target": [2], "grade": ["AB"], "trend": [0, 1]}
TREND_N = 50
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 10 ** 6
STOP_CAP_ATR = 1e9
SELECT_BY = "s"
WAIT_BARS, MIN_R_COST, DAY_CLOSE = 3, 3.0, 20 * 3600 + 1800
_rf = json.load(open(os.path.join(_here, "..", "costs_roboforex_prime.json")))["realistic"]
COSTS = {m: _rf[m] for m in MARKETS if m in _rf}
_cal = json.load(open(os.path.join(_here, "..", "calendars", "us_news_days.json")))
NEWS = {dt.date.fromisoformat(d) for k in ("nfp", "cpi", "fomc") for d in _cal[k]}
NY = ZoneInfo("America/New_York")
BLOCK = (20 * 3600 + 1800, 23 * 3600)
REASON = {1: "stop", 2: "target", 3: "daily close"}
_CACHE = {}


def next_close(t):
    """The first daily close (20:30 UTC) strictly after t, skipping Saturday/Sunday closes."""
    d = (t // 86400) * 86400 + DAY_CLOSE
    d = np.where(d <= t, d + 86400, d)
    wd = ((d // 86400) + 3) % 7                     # 0 = Monday
    d = np.where(wd == 5, d + 2 * 86400, np.where(wd == 6, d + 86400, d))
    return d


def setups(B, p, M):
    """All patterns of the bar series (cached per market, timeframe, sample and history length)."""
    sample = p.get("sample", "flow")
    t = np.asarray(B["t"], np.int64)
    key = (M.sym, int(B["minutes"]), sample, len(t), int(t[-1]) if len(t) else 0)
    if key in _CACHE:
        return _CACHE[key]
    P = SC.detect(B["o"], B["h"], B["l"], B["c"])
    keep = (P["grade"] == 0) if sample == "control" else (P["grade"] > 0)
    t4 = t[P["i4"]] + int(B["minutes"]) * 60                       # the 4th candle's close
    nyd = [dt.datetime.fromtimestamp(int(x) - 1, NY).date() for x in t4]
    keep &= np.array([d not in NEWS for d in nyd], bool)
    S_ = {k: v[keep] for k, v in P.items()}
    S_["t4"] = t4[keep]
    S_["grade_ab"] = S_["grade"] if sample != "control" else np.ones(int(keep.sum()), np.int64) * 2
    S_["atrb"] = np.asarray(B["atr"], float)[S_["i4"]]
    e50 = SC.ema(B["c"], TREND_N)
    S_["trend_ok"] = np.where(S_["side"] < 0, np.asarray(B["c"], float)[S_["i4"]] < e50[S_["i4"]],
                              np.asarray(B["c"], float)[S_["i4"]] > e50[S_["i4"]])
    S_["kdec"] = np.asarray(B["nxt"], np.int64)[S_["i4"]]
    _CACHE[key] = S_
    return S_


def select(S_, p):
    m = np.ones(len(S_["i4"]), bool) if p["grade"] == "AB" else (S_["grade_ab"] == 2)
    if int(p.get("trend", 0)) == 1:
        m &= S_["trend_ok"]
    return {k: v[m] for k, v in S_.items()}


def stops(S_, p):
    hi, lo = (S_["hi4"], S_["lo4"]) if p["stop"] == "c4" else (S_["hi_all"], S_["lo_all"])
    b = float(p["buffer"]) * S_["atrb"]
    return np.where(S_["side"] < 0, hi + b, lo - b).astype(np.float64)


def signals(B, p, M):
    S_ = select(setups(B, p, M), p)
    return [(int(j), int(s), float(x)) for j, s, x in zip(S_["i4"], S_["side"], stops(S_, p))]


@njit(cache=False)
def simulate(o, h, l, ts, gaps, kdec, kwin, kday, side, lev, stp, mode, tgt, cost, cut, delay, blo, bhi, min_r):
    """Sequential orders for one market: rows t_in, t_out, side, net R, stop distance, cost R, 0, 0, entry, stop, target,
    exit price, reason (1 stop, 2 target, 3 daily close), setup index."""
    n = len(kdec); out = np.zeros((n, 14)); m = 0; N = len(o); eps = 0.1 * cost; busy = -1
    for j in range(n):
        k0 = kdec[j] + delay
        if k0 >= N - 2 or k0 <= busy:
            continue
        if ts[k0] >= cut:
            break
        kend = min(kwin[j], kday[j])
        if j + 1 < n and kdec[j + 1] > kdec[j]:
            kend = min(kend, kdec[j + 1])                   # a newer pattern deletes this pending order
        sd = side[j]; stop = stp[j]; kin = -1; entry = 0.0
        for i in range(k0, min(kend, N)):
            s = ts[i] % 86400
            if mode == 1:                                   # market at the 4th candle's close (not in the rollover block)
                if not (blo <= s < bhi):
                    kin = i; entry = o[i] if sd < 0 else o[i] + cost
                break
            if blo <= s < bhi:
                continue
            if sd < 0 and h[i] >= lev[j] + eps:
                kin = i; entry = max(lev[j], o[i]); break
            if sd > 0 and l[i] + cost <= lev[j] - eps:
                kin = i; entry = min(lev[j], o[i] + cost); break
        if kin < 0:
            continue
        d = stop - entry if sd < 0 else entry - stop
        if d <= 0 or d < min_r * cost:
            continue
        tp = entry + tgt * d if sd > 0 else entry - tgt * d
        kx = -1; px = 0.0; why = 0
        for i in range(kin, N):
            if i >= kday[j]:
                kx = i; px = o[i] if sd > 0 else o[i] + cost; why = 3; break
            if sd > 0:
                if l[i] <= stop:
                    px = o[i] if (i > kin and o[i] < stop) else stop; kx = i; why = 1; break
                if i > kin and h[i] >= tp:
                    px = tp; kx = i; why = 2; break
            else:
                if h[i] + cost >= stop:
                    px = o[i] + cost if (i > kin and o[i] + cost > stop) else stop; kx = i; why = 1; break
                if i > kin and l[i] + cost <= tp:
                    px = tp; kx = i; why = 2; break
        if kx < 0:
            continue
        busy = kx
        skip = False
        for g in gaps:
            if kin <= g < kx:
                skip = True; break
        if skip:
            continue
        r = (px - entry) / d if sd > 0 else (entry - px) / d
        out[m, 0] = ts[kin]; out[m, 1] = ts[kx]; out[m, 2] = sd; out[m, 3] = r; out[m, 4] = d; out[m, 5] = cost / d
        out[m, 8] = entry; out[m, 9] = stop; out[m, 10] = tp; out[m, 11] = px; out[m, 12] = why; out[m, 13] = j; m += 1
    return out[:m]


def detail(M, B, p, cut=2 ** 62, delay=0):
    """Full trade records (14 columns, see simulate) for one market and configuration."""
    S_ = select(setups(B, p, M), p)
    if len(S_["i4"]) == 0:
        return np.zeros((0, 14))
    ts = np.asarray(M.ts, np.int64)
    win_t = S_["t4"] + WAIT_BARS * int(B["minutes"]) * 60
    kwin = np.searchsorted(ts, win_t) if p["entry"] == "mid50" else S_["kdec"] + 10 ** 6
    kday = np.searchsorted(ts, next_close(S_["t4"]))
    return simulate(np.asarray(M.o, float), np.asarray(M.h, float), np.asarray(M.l, float), ts, np.asarray(M.gaps, np.int64),
                    S_["kdec"].astype(np.int64), np.asarray(kwin, np.int64), np.asarray(kday, np.int64), S_["side"].astype(np.int64),
                    S_["entry50"].astype(np.float64), stops(S_, p), 0 if p["entry"] == "mid50" else 1, float(p["target"]),
                    float(M.cost), int(cut if cut else 2 ** 62), int(delay), BLOCK[0], BLOCK[1], MIN_R_COST)


def EXECUTOR(M, B, C, p, cut=2 ** 62, cost_mult=1.0, swap_mult=1.0, delay=0):
    res = detail(M, B, p, cut=cut, delay=delay)[:, :8].copy()
    if cost_mult != 1.0:
        res[:, 3] -= (cost_mult - 1.0) * res[:, 5]
    return res
