"""Pivot-sweep range v2 (owner's chart reading, 2026-11-12; research/sweep5/PREREGISTRATION.md). Detector + live pivot levels.

SELL (BUY is the mirror): candle 1 bullish (doji = bullish), candle 2 bearish closing below candle 1's open (loose engulf),
candle 3 bullish (doji = bullish), candle 4 bearish closing below candle 3's open; candles 2 and 4 bodies >= 50%.
Sweep of a live pivot high: `now` by the candle before candle 1, candle 1 or 2; `recent` by any candle from 6 before
candle 1 through candle 2. Range = candle 4's low to the highest high of the four; entry 60% up from candle 4's low.
"""
import os, sys
import numpy as np
from numba import njit

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sweep4"))
import pivots as PV   # noqa: E402

BODY_MIN, ENTRY, K = 0.5, 0.6, 3


def detect(o, h, l, c, body_min=BODY_MIN):
    o, h, l, c = (np.asarray(x, float) for x in (o, h, l, c))
    n = len(c)
    bull, bear = c >= o, c < o
    hl = h - l
    frac = np.where(hl > 0, np.abs(c - o) / np.where(hl > 0, hl, 1.0), 0.0)
    dn = np.zeros(n, bool); up = np.zeros(n, bool)
    dn[1:] = bull[:-1] & bear[1:] & (c[1:] < o[:-1]) & (frac[1:] >= body_min)     # bearish candle engulfing (loose) a bullish one
    up[1:] = bear[:-1] & bull[1:] & (c[1:] > o[:-1]) & (frac[1:] >= body_min)
    k = np.arange(3, n)
    sell = dn[k - 2] & dn[k]
    buy = up[k - 2] & up[k]
    kk = k[sell | buy]
    side = np.where(buy[sell | buy], 1, -1)
    return kk.astype(np.int64), side.astype(np.int64)


@njit(cache=True)
def live_levels(h, l, ph, pl, right, K):
    """After each bar closes: the K nearest live pivot highs (ascending) and lows (descending), nan-padded. A pivot at bar
    i enters when bar i+right closes; a level leaves when a bar trades through it."""
    n = len(h)
    LH = np.full((n, K), np.nan); LL = np.full((n, K), np.nan)
    sh = np.zeros(n // 2 + 2); sl = np.zeros(n // 2 + 2); nh = 0; nl = 0
    for j in range(n):
        while nh > 0 and h[j] > sh[nh - 1]:
            nh -= 1
        while nl > 0 and l[j] < sl[nl - 1]:
            nl -= 1
        i = j - right
        if i >= 0:
            if ph[i]:
                sh[nh] = h[i]; nh += 1
            if pl[i]:
                sl[nl] = l[i]; nl += 1
        for m in range(min(K, nh)):
            LH[j, m] = sh[nh - 1 - m]
        for m in range(min(K, nl)):
            LL[j, m] = sl[nl - 1 - m]
    return LH, LL


def setups(B, tf_min, piv=10, body_min=BODY_MIN):
    o, h, l, c = (np.asarray(B[x], float) for x in "ohlc")
    k, side = detect(o, h, l, c, body_min)
    ph, pl, sw_hi, sw_lo, _, _, _ = PV.structure(h, l, piv, piv, np.zeros(0, np.int64), np.zeros(0, np.int64), 1)
    swept_hi, swept_lo = ~np.isnan(sw_hi), ~np.isnan(sw_lo)
    sw = np.where(side > 0, 0, 0).astype(bool)
    def window(a, b):
        out = np.zeros(len(k), bool)
        for d in range(a, b + 1):                               # bars k-d
            idx = np.maximum(k - d, 0)
            out |= np.where(side > 0, swept_lo[idx], swept_hi[idx]) & (k - d >= 0)
        return out
    now = window(2, 4)                                          # candle 2, candle 1, the candle before candle 1
    recent = window(2, 9)                                       # ... back to 6 candles before candle 1
    hi4 = np.max(np.stack([h[k - j] for j in range(4)]), axis=0) if len(k) else np.zeros(0)
    lo4 = np.min(np.stack([l[k - j] for j in range(4)]), axis=0) if len(k) else np.zeros(0)
    hi = np.where(side > 0, h[k], hi4); lo = np.where(side > 0, lo4, l[k])
    LH, LL = live_levels(h, l, ph, pl, piv, K)
    t = np.asarray(B["t"], np.int64)
    return dict(k=k, side=side, hi=hi, lo=lo, t_conf=t[k] + tf_min * 60, now=now, recent=recent, ph=ph, pl=pl,
                bt=t, LH=LH, LL=LL, minutes=int(tf_min))


def orders(S, stop="range", life=24, entry=ENTRY):
    w = S["hi"] - S["lo"]
    lvl = np.where(S["side"] > 0, S["hi"] - entry * w, S["lo"] + entry * w)
    buf = 0.5 if stop == "wide" else 0.0
    stp = np.where(S["side"] > 0, S["lo"] - buf * w, S["hi"] + buf * w)
    return dict(t_conf=S["t_conf"], side=S["side"], level=lvl, stop=stp, width=w,
                t_exp=S["t_conf"] + int(life) * S["minutes"] * 60)
