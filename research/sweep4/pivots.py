"""Pivot Points High Low, as the TradingView indicator of that name (owner's chart: "Pivots HL 10 10 10 10").

A pivot HIGH at bar i (left L, right R): high[i] is higher than the highs of the R bars after it, and not lower than the
highs of the L bars before it (ties: the later of two equal highs is the pivot, the usual reading of ta.pivothigh; the
indicator's source cannot be fetched here, so the tie rule is our reading). A pivot LOW is the mirror.
A pivot is only KNOWN when bar i+R has closed: TradingView draws its label back at bar i, which is why pivots seem to
"appear randomly" on a live chart. Nothing here uses a pivot before bar i+R closes.

A pivot level is LIVE from its confirmation until the first later bar that trades through it (high > a pivot high, low <
a pivot low). That first bar is the SWEEP of the pivot. Live pivot highs are always ordered: the newest is the lowest.
"""
import numpy as np
from numba import njit


@njit(cache=True)
def pivots(h, l, left, right):
    n = len(h)
    ph = np.zeros(n, np.bool_); pl = np.zeros(n, np.bool_)
    for i in range(left, n - right):
        ok = True
        for j in range(i + 1, i + right + 1):
            if h[j] >= h[i]:
                ok = False; break
        if ok:
            for j in range(i - left, i):
                if h[j] > h[i]:
                    ok = False; break
        ph[i] = ok
        ok = True
        for j in range(i + 1, i + right + 1):
            if l[j] <= l[i]:
                ok = False; break
        if ok:
            for j in range(i - left, i):
                if l[j] < l[i]:
                    ok = False; break
        pl[i] = ok
    return ph, pl


@njit(cache=True)
def structure(h, l, left, right, ks, sides, K):
    """One pass over the bars, using at bar j only bars 0..j.
    Returns
      ph, pl          pivot flags at the pivot bar (known right bars later)
      sw_hi, sw_lo    for each bar: the highest live pivot HIGH it swept (nan if none) / the lowest live pivot LOW
      sw_hi_i, sw_lo_i  the bar index of that swept pivot (-1 if none)
      lev             for each setup (candle 4 at bar ks[q], side sides[q]): the K nearest live pivots on the TARGET side
                      as known when candle 4 closes (buy: pivot highs, nearest = lowest first; sell: pivot lows), nan-padded
    """
    n = len(h)
    ph, pl = pivots(h, l, left, right)
    sw_hi = np.full(n, np.nan); sw_lo = np.full(n, np.nan)
    sw_hi_i = np.full(n, -1, np.int64); sw_lo_i = np.full(n, -1, np.int64)
    sh = np.zeros(n // 2 + 2); sl = np.zeros(n // 2 + 2)
    shi = np.zeros(n // 2 + 2, np.int64); sli = np.zeros(n // 2 + 2, np.int64)
    nh = 0; nl = 0
    lev = np.full((len(ks), K), np.nan)
    q = 0
    for j in range(n):
        while nh > 0 and h[j] > sh[nh - 1]:
            sw_hi[j] = sh[nh - 1]; sw_hi_i[j] = shi[nh - 1]; nh -= 1
        while nl > 0 and l[j] < sl[nl - 1]:
            sw_lo[j] = sl[nl - 1]; sw_lo_i[j] = sli[nl - 1]; nl -= 1
        i = j - right
        if i >= left:
            if ph[i]:
                sh[nh] = h[i]; shi[nh] = i; nh += 1
            if pl[i]:
                sl[nl] = l[i]; sli[nl] = i; nl += 1
        while q < len(ks) and ks[q] == j:
            if sides[q] > 0:
                for m in range(min(K, nh)):
                    lev[q, m] = sh[nh - 1 - m]
            else:
                for m in range(min(K, nl)):
                    lev[q, m] = sl[nl - 1 - m]
            q += 1
    return ph, pl, sw_hi, sw_lo, sw_hi_i, sw_lo_i, lev


def confirmations(t, h, l, ph, pl, right, tf_min):
    """Pivot confirmations as an event list for the trailing stop: (time known = close of bar i+right, price)."""
    t = np.asarray(t, np.int64); n = len(t)
    ih = np.flatnonzero(ph); il = np.flatnonzero(pl)
    ih = ih[ih + right < n]; il = il[il + right < n]
    return (t[ih + right] + tf_min * 60, np.asarray(h, float)[ih]), (t[il + right] + tf_min * 60, np.asarray(l, float)[il])
