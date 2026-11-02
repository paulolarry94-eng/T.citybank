"""Sweep-and-Shift Reversal (SSR), owner's spec 2026-11-02, XAUUSD and EURUSD. Rules fixed BEFORE any result.

Owner's spec, coded literally where it is exact; the choices needed to make it exact are marked (choice).
Bars: the lab feeds M15 bars; H1 bars are built from them. An hour counts only when its 45-minute M15 bar exists
(so a finished hour is known in real time); its OHLC are the M15 bars of that hour. ATR(14) = mean true range of the
previous 14 finished H1 bars (choice: ATR known before the sweep bar).
Bearish setup (mirror for bullish, choice: the spec describes the short side; the mirror is traded too):
  sweep      H1 bar k with high >= HH20 + 0.5 x ATR, HH20 = highest high of the 20 H1 bars before k;
  reclaim    an H1 close below HH20 on bar k, k+1 or k+2 ("within 3 bars"); the first such bar is m;
  shift      after bar m closes, an M15 bar closes below the lowest low of the 20 M15 bars before it, within the next
             5 M15 bars or the next 5 H1 bars (= 20 M15 bars) (choice: "within the next 5 bars" is ambiguous, both
             are in the grid); the first such M15 bar is the confirmation bar;
  entry      confirm: short at the confirmation bar's close (market order at the next M15 open);
             first:   "or at the 50% retracement of the sweep candle, whichever comes first": a sell limit at the
                      midpoint of bar k, placed when bar m closes if price is below it, valid through the shift window;
                      if it fills first that is the trade (even if no shift follows, as written); otherwise short at the
                      confirmation close;
  stop       0.25 x ATR above the highest high of bars k..m (the sweep high);
  target     the lowest low of the 20 H1 bars before k (the prior swing low, sell-side liquidity), moved out to 2R
             from the fill if it is closer ("minimum 2R");
  time stop  48 hours (choice: the spec has none). One position per market at a time. Swaps as the lab.
Control (owner: "same setup on non-sweep days"; never selected; research/truth/controls.py): bar k comes within 0.5 x
  ATR of HH20 without exceeding it (choice: a near miss, so control setups are comparable in place and number); then the
  same reclaim (bar k itself), shift, entry, stop and target rules.
Grid: shift window [5 x M15, 5 x H1] x entry [confirm, first] = 4 configurations; XAUUSD and EURUSD (the owner's choice).
Costs: RoboForex Prime published (XAUUSD 0.16, EURUSD 0.000055 round trip; research/truth/costs_roboforex_prime.json).
  Prime's published gold swaps are side-specific (long -0.60, short +0.19 per oz per night); the lab charges its
  symmetric estimate (0.20); research/truth/controls.py reports the trades at Prime's published swaps too.
Trade counts (mechanics check before any result): 2011-19 rows XAUUSD / EURUSD: 5xM15 confirm 234 / 341, 5xM15 first
  1,915 / 2,576, 5xH1 confirm 803 / 1,142, 5xH1 first 2,218 / 3,006 ("first" fills its retracement limit on setups that
  never shift, as written, so it trades far more); control near misses are 4-5 times as common as sweeps.
Priors (told to the owner): about 1,400 liquidity-grab variants rejected (P7: continuation beats reversal); the closest,
  LG3 sweep + market-structure shift on H1 (4 markets, 192 settings), was +0.126R in 2011-19, -0.06R in 2020-22 and
  -0.185R in 2023-25 (gold -0.16R, EURUSD +0.01R). 2023-25 for this family has therefore been seen: this run's final
  look is not a clean holdout. Resting retracement entries suffer adverse selection (P2).
"""
import os, sys, json
import numpy as np
import pandas as pd

NAME = "ssr_sweep_shift_v1"
HYPOTHESIS = ("A sweep beyond the 20-bar extreme that is reclaimed and followed by a lower-timeframe structure break traps "
              "breakout traders; fading it to the opposite liquidity pool earns more than costs, and more than a near miss.")
RULES = __doc__
FAMILY = ["liquidity", "sweep", "mss", "smc", "ict", "reversal", "intraday", "xauusd", "eurusd", "owner-idea"]
MARKETS = ["XAUUSD", "EURUSD"]
TIMEFRAMES = ["M15"]
GRID = {"window": ["5xM15", "5xH1"], "entry": ["confirm", "first"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 192
STOP_CAP_ATR = 1e9
LOOK, ATR_N, SWEEP_ATR, STOP_ATR, MSS_N, MIN_R = 20, 14, 0.5, 0.25, 20, 2.0
WIN = {"5xM15": 5, "5xH1": 20}
_here = os.path.dirname(os.path.abspath(__file__))
_rf = json.load(open(os.path.join(_here, "..", "costs_roboforex_prime.json")))["realistic"]
COSTS = {m: _rf[m] for m in MARKETS}
sys.path.insert(0, os.path.join(_here, ".."))
import executors


def hourly(B):
    """Finished H1 bars from M15 bars: (close index in M15, open, high, low, close) for hours whose :45 bar exists."""
    t = np.asarray(B["t"], np.int64)
    hr = t // 3600
    df = pd.DataFrame(dict(hr=hr, o=B["o"], h=B["h"], l=B["l"], c=B["c"], i=np.arange(len(t)), last=(t % 3600) == 2700))
    g = df.groupby("hr", sort=True)
    H = pd.DataFrame(dict(o=g.o.first(), h=g.h.max(), l=g.l.min(), c=g.c.last(), i=g.i.last(), done=g["last"].any()))
    H = H[H.done]
    return H.i.to_numpy(np.int64), H.o.to_numpy(float), H.h.to_numpy(float), H.l.to_numpy(float), H.c.to_numpy(float)


def _setups(B, p, cost):
    """All setups as rows for the lab plus {(side, stop): target price}."""
    hi_idx, Ho, Hh, Hl, Hc = hourly(B)
    n = len(Hh)
    if n < LOOK + ATR_N + 2:
        return [], {}
    c = np.asarray(B["c"], float); h = np.asarray(B["h"], float); l = np.asarray(B["l"], float)
    N = len(c)
    pc = np.r_[np.nan, Hc[:-1]]
    tr = np.maximum(Hh - Hl, np.maximum(np.abs(Hh - pc), np.abs(Hl - pc)))
    atr = pd.Series(tr).rolling(ATR_N).mean().shift(1).to_numpy()
    hh = pd.Series(Hh).rolling(LOOK).max().shift(1).to_numpy()
    ll = pd.Series(Hl).rolling(LOOK).min().shift(1).to_numpy()
    lo20 = pd.Series(l).rolling(MSS_N).min().shift(1).to_numpy()        # M15: lowest low of the 20 bars before
    hi20 = pd.Series(h).rolling(MSS_N).max().shift(1).to_numpy()
    sample = p.get("sample", "flow")
    W = WIN[p["window"]]
    rows, tgt = [], {}
    for k in range(LOOK + 1, n):
        A = atr[k]
        if not np.isfinite(A) or A <= 0 or not np.isfinite(hh[k]):
            continue
        for side in (-1, 1):                                          # -1: sweep of highs -> short; +1: sweep of lows -> long
            if side < 0:
                lvl = hh[k]
                hit = Hh[k] >= lvl + SWEEP_ATR * A if sample == "flow" else (lvl - SWEEP_ATR * A <= Hh[k] < lvl)
            else:
                lvl = ll[k]
                hit = Hl[k] <= lvl - SWEEP_ATR * A if sample == "flow" else (lvl < Hl[k] <= lvl + SWEEP_ATR * A)
            if not hit:
                continue
            m = None
            for mm in range(k, min(k + 3, n)):
                if (side < 0 and Hc[mm] < lvl) or (side > 0 and Hc[mm] > lvl):
                    m = mm; break
            if m is None:
                continue
            ext = Hh[k:m + 1].max() if side < 0 else Hl[k:m + 1].min()
            stop = ext + STOP_ATR * A if side < 0 else ext - STOP_ATR * A
            target = ll[k] if side < 0 else hh[k]
            mid = 0.5 * (Hh[k] + Hl[k])
            cb = int(hi_idx[m])                                       # M15 bar that closes the reclaim hour
            end = min(cb + W, N - 1)
            conf = None
            for j in range(cb + 1, end + 1):
                if (side < 0 and np.isfinite(lo20[j]) and c[j] < lo20[j]) or (side > 0 and np.isfinite(hi20[j]) and c[j] > hi20[j]):
                    conf = j; break
            key = (side, round(float(stop), 8))
            use_limit = p["entry"] == "first" and ((side < 0 and c[cb] < mid) or (side > 0 and c[cb] > mid))
            if use_limit:
                rows.append((cb, side, float(stop), float(mid), W))
                tgt[key] = float(target)
                touched = conf is not None and (
                    (side < 0 and (h[cb + 1:conf + 1] >= mid + 0.1 * cost).any()) or
                    (side > 0 and (l[cb + 1:conf + 1] + cost <= mid - 0.1 * cost).any()))
                if conf is not None and not touched:
                    rows.append((conf, side, float(stop))); tgt[key] = float(target)
            elif conf is not None:
                rows.append((conf, side, float(stop))); tgt[key] = float(target)
    return rows, tgt


def signals(B, p, M):
    return _setups(B, p, M.cost)[0]


def _targets(B, p, C):
    """Target price per candidate, looked up by (side, stop); the stop identifies the setup."""
    tmap = _setups(B, p, 0.0)[1]                                      # targets do not depend on cost
    return np.array([tmap.get((int(sd), round(float(st), 8)), np.nan) for sd, st in zip(C["side"], C["stop"])], np.float64)


EXECUTOR = executors.bracket_prices(_targets, min_r=MIN_R, time_stop_bars=TIME_STOP)
