"""Owner's pivot-sweep body-engulf range (2026-11-12). Detector and trade levels; orders run in sweep4_orders / sweep4_fast.

SELL (BUY is the mirror), on closed candles of one timeframe:
  1. the four candles: candle 1 bullish, candle 2 bearish and its BODY engulfs candle 1's body (opens at/above 1's close,
     closes below 1's open), candle 3 bullish, candle 4 bearish and its body engulfs candle 3's body (as before).
  2. candles 2 and 4 each have a body of at least 60% of their own high-low. No lookback rule.
  3. the sweep: the four candles come right after a live pivot HIGH is swept (pivots.py: TradingView Pivot Points High
     Low). sweep "c12": candle 1 or candle 2 is the first bar to trade above that pivot high. sweep "near" (the wider
     reading): the candle before candle 1, or any of the four.
  4. the range: from candle 4's LOW up to the HIGHEST HIGH of the four candles.
  5. entry: a sell limit 60% of the way up the range (lo + 0.6 x range). Stop: the highest high + buffer x range.
     1R = entry to stop. Targets: sweep4 strategy file.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "body4"))
import body4_scan as SC   # noqa: E402
import pivots as PV       # noqa: E402

BODY_MIN, ENTRY, K = 0.6, 0.6, 12


def setups(B, tf_min, piv=10, body_min=BODY_MIN):
    """Every four-candle pattern with the 60% bodies, with its range, sweep flags and the live pivots on its target side.
    Uses at candle 4 only bars up to candle 4."""
    o, h, l, c = (np.asarray(B[x], float) for x in "ohlc")
    D = SC.detect_arrays(o, h, l, c, engulf="body")
    keep = (D["body2"] >= body_min) & (D["body4"] >= body_min)
    k = D["k"][keep]; side = D["side"][keep]
    hi4 = np.max(np.stack([h[k - j] for j in range(4)]), axis=0) if len(k) else np.zeros(0)
    lo4 = np.min(np.stack([l[k - j] for j in range(4)]), axis=0) if len(k) else np.zeros(0)
    hi = np.where(side > 0, h[k], hi4)            # buy: candle 4's high down to the lowest low of the four
    lo = np.where(side > 0, lo4, l[k])            # sell: candle 4's low up to the highest high of the four
    ph, pl, sw_hi, sw_lo, sw_hi_i, sw_lo_i, lev = PV.structure(h, l, piv, piv, k.astype(np.int64), side.astype(np.int64), K)
    sw = np.where(side[:, None] > 0, np.stack([sw_lo[np.maximum(k - j, 0)] for j in (4, 3, 2, 1, 0)], axis=1),
                  np.stack([sw_hi[np.maximum(k - j, 0)] for j in (4, 3, 2, 1, 0)], axis=1)) if len(k) else np.zeros((0, 5))
    has = ~np.isnan(sw)                           # columns: candle before candle 1, candles 1, 2, 3, 4
    c12 = has[:, 1] | has[:, 2]
    near = has.any(axis=1)
    # the swept level nearest to the trade (sell: the highest swept pivot high; buy: the lowest swept pivot low)
    with np.errstate(all="ignore"):
        lvl = np.where(side > 0, np.nanmin(np.where(has, sw, np.inf), axis=1), np.nanmax(np.where(has, sw, -np.inf), axis=1))
    lvl = np.where(near, lvl, np.nan)
    t = np.asarray(B["t"], np.int64)
    return dict(k=k.astype(np.int64), side=side.astype(np.int64), hi=hi, lo=lo, c4=c[k], t_conf=t[k] + tf_min * 60,
                c12=c12, near=near, swept=lvl, lev=lev, ph=ph, pl=pl, body2=D["body2"][keep], body4=D["body4"][keep])


def levels(S, buffer=0.0, entry=ENTRY):
    """Entry, stop and 1R for every setup."""
    w = S["hi"] - S["lo"]
    lvl = np.where(S["side"] > 0, S["hi"] - entry * w, S["lo"] + entry * w)
    stp = np.where(S["side"] > 0, S["lo"] - buffer * w, S["hi"] + buffer * w)
    return lvl, stp, np.abs(lvl - stp), w


def structural_r(S, lvl, risk, which=1, rmin=3.0, rmax=15.0):
    """Target in R at a live pivot on the target side: which=1 the nearest pivot at least rmin R away, which=2 the next
    pivot beyond that one. nan when there is none within rmax R (then the structural rule has no trade)."""
    r = (S["lev"] - lvl[:, None]) * S["side"][:, None] / risk[:, None]
    ok = (r >= rmin) & (r <= rmax)
    out = np.full(len(lvl), np.nan)
    for q in range(len(lvl)):
        j = np.flatnonzero(ok[q])
        if len(j) >= which:
            out[q] = r[q, j[which - 1]]
    return out


def pivot_r(S, lvl, risk, n=2):
    """Owner 2026-11-12: "you pass the first pivot, then the next pivot is the TP": target in R at the n-th live pivot on
    the target side beyond the entry (known when candle 4 closes), with no minimum or maximum R. nan if there is none."""
    r = (S["lev"][:, n - 1] - lvl) * S["side"] / risk
    return np.where(r > 0, r, np.nan)
