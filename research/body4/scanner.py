"""Owner's body-engulf 4-candle range pattern (2026-11-07, Boom 1000 M5 charts). Detector + trade levels, no backtest.

SELL (BUY is the mirror):
  candle 1 bullish, candle 2 bearish whose BODY engulfs candle 1's body (opens at/above 1's close, closes below 1's open),
  candle 3 bullish, candle 4 bearish whose BODY engulfs candle 3's body. Wicks do not count for the engulfing.
  Range = highest high to lowest low of the four candles (wicks count here). Entry = limit at the range midpoint.
  Stop = the far end of the range (sell: range high; buy: range low). Target = 4R. Breakeven: at +2R the stop moves to entry.
"""
import numpy as np


def body_engulf(o, c, k, side):
    """Candle k's body engulfs candle k-1's body in direction side (-1 bearish k over bullish k-1, +1 the mirror)."""
    if side < 0:
        return c[k - 1] > o[k - 1] and c[k] < o[k] and o[k] >= c[k - 1] and c[k] < o[k - 1]
    return c[k - 1] < o[k - 1] and c[k] > o[k] and o[k] <= c[k - 1] and c[k] > o[k - 1]


def detect(o, h, l, c):
    """Index of the 4th candle, side, range high/low, midpoint (entry), stop, 1R distance."""
    rows = []
    for k in range(3, len(c)):
        for side in (-1, 1):
            if body_engulf(o, c, k - 2, side) and body_engulf(o, c, k, side):
                hi, lo = float(h[k - 3:k + 1].max()), float(l[k - 3:k + 1].min())
                mid = (hi + lo) / 2
                stop = hi if side < 0 else lo
                rows.append((k, side, hi, lo, mid, stop, abs(stop - mid)))
    return rows


def follow(o, h, l, c, k, side, mid, stop, risk, wait=None, target_r=4.0, be_r=2.0, max_bars=600):
    """Bar-by-bar outcome (examples only; the backtest will use M1 / ticks). Same-bar stop and target: stop first."""
    tp = mid - target_r * risk if side < 0 else mid + target_r * risk
    be = mid - be_r * risk if side < 0 else mid + be_r * risk
    j, fill = k + 1, None
    end = len(c) if wait is None else min(len(c), k + 1 + wait)
    while j < end:
        if (side < 0 and h[j] >= mid) or (side > 0 and l[j] <= mid):
            fill = j; break
        if (side < 0 and l[j] <= tp) or (side > 0 and h[j] >= tp):
            return dict(result="target reached before entry: order cancelled", fill=None, exit=j, R=0.0, tp=tp, be=be)
        j += 1
    if fill is None:
        return dict(result="not filled", fill=None, exit=None, R=0.0, tp=tp, be=be)
    sl, moved = stop, False
    for j in range(fill, min(len(c), fill + max_bars)):
        hit_sl = (h[j] >= sl) if side < 0 else (l[j] <= sl)
        if hit_sl and not (j == fill and moved):
            return dict(result="breakeven" if moved else "stop (-1R)", fill=fill, exit=j, R=0.0 if moved else -1.0, tp=tp, be=be)
        if (side < 0 and l[j] <= tp) or (side > 0 and h[j] >= tp):
            return dict(result="target (+4R)", fill=fill, exit=j, R=target_r, tp=tp, be=be)
        if not moved and ((side < 0 and l[j] <= be) or (side > 0 and h[j] >= be)):
            sl, moved = mid, True
    return dict(result="still open", fill=fill, exit=None, R=None, tp=tp, be=be)
