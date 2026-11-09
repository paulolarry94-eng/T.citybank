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


def detect_arrays(o, h, l, c, sample="flow", doji_bullish=False, engulf="body"):
    """Vectorised detector (same rule as detect()). sample="control": the same alternating four candles where NEITHER
    the 2nd nor the 4th candle body-engulfs the candle before it (the shape without the engulfing).
    Returns arrays k (index of candle 4), side, hi, lo, lookback (candles going the trade's way among the 5 before
    candle 1; dojis count for neither side)."""
    o, h, l, c = (np.asarray(x, float) for x in (o, h, l, c))
    n = len(c)
    bull, bear = c > o, c < o
    eng_dn, eng_up, alt_dn, alt_up = (np.zeros(n, bool) for _ in range(4))
    alt_dn[1:] = bull[:-1] & bear[1:]
    alt_up[1:] = bear[:-1] & bull[1:]
    if engulf == "loose":       # owner 2026-11-08: only "closes beyond the previous candle's open" (a gap at the open is allowed)
        eng_dn[1:] = alt_dn[1:] & (c[1:] < o[:-1])
        eng_up[1:] = alt_up[1:] & (c[1:] > o[:-1])
    else:                       # "body": the body fully covers the previous body (opens at/beyond its close)
        eng_dn[1:] = alt_dn[1:] & (o[1:] >= c[:-1]) & (c[1:] < o[:-1])
        eng_up[1:] = alt_up[1:] & (o[1:] <= c[:-1]) & (c[1:] > o[:-1])
    k = np.arange(3, n)
    if sample == "control":
        sell = alt_dn[k - 2] & alt_dn[k] & ~eng_dn[k - 2] & ~eng_dn[k]
        buy = alt_up[k - 2] & alt_up[k] & ~eng_up[k - 2] & ~eng_up[k]
    else:
        sell = eng_dn[k - 2] & eng_dn[k]
        buy = eng_up[k - 2] & eng_up[k]
    kk = k[sell | buy]
    side = np.where(buy[sell | buy], 1, -1)
    hi = np.max(np.stack([h[kk - j] for j in range(4)]), axis=0) if len(kk) else np.zeros(0)
    lo = np.min(np.stack([l[kk - j] for j in range(4)]), axis=0) if len(kk) else np.zeros(0)
    # lookback colours: a doji (open = close) counts for neither side, or as BULLISH when doji_bullish (owner, 2026-11-08:
    # "a doji counts ... that doji was bullish", i.e. close >= open is bullish, as charts colour it)
    lb_bull = (c >= o) if doji_bullish else bull
    cb, cs = np.r_[0, np.cumsum(lb_bull)], np.r_[0, np.cumsum(bear)]   # cb[i] = bullish candles among 0..i-1
    a, b = np.maximum(kk - 8, 0), np.maximum(kk - 3, 0)                 # candles k-8 .. k-4
    lb = np.where(side > 0, cb[b] - cb[a], cs[b] - cs[a])
    # v6 (owner, 2026-11-09): body share of candles 2 and 4 (body / own high-low), and the 2-candle lookback (the two
    # candles right before candle 1, k-5 and k-4, going the trade's way; same doji rule as the 5-candle lookback)
    hl = h - l
    frac = np.where(hl > 0, np.abs(c - o) / np.where(hl > 0, hl, 1.0), 0.0)
    a2 = np.maximum(kk - 5, 0)                                          # candles k-5 .. k-4
    lb2 = np.where(side > 0, cb[b] - cb[a2], cs[b] - cs[a2])
    return dict(k=kk.astype(np.int64), side=side.astype(np.int64), hi=hi, lo=lo, lookback=lb.astype(np.int64),
                body2=frac[kk - 2] if len(kk) else np.zeros(0), body4=frac[kk] if len(kk) else np.zeros(0),
                lookback2=lb2.astype(np.int64))


def setups(B, tf_min, sample="flow", doji_bullish=False, engulf="body"):
    """detect_arrays plus what the order engines need: t_conf (time candle 4 closes) and c4 (its close)."""
    P = detect_arrays(B["o"], B["h"], B["l"], B["c"], sample=sample, doji_bullish=doji_bullish, engulf=engulf)
    P["t_conf"] = (np.asarray(B["t"], np.int64)[P["k"]] + tf_min * 60).astype(np.int64)
    P["c4"] = np.asarray(B["c"], float)[P["k"]]
    return P


def layer_mask(t_small, side_small, t_big, side_big, window_sec):
    """1 where a small-timeframe setup has a big-timeframe setup in the SAME direction whose candle 4 closed at or before
    it, at most window_sec earlier (owner 2026-11-08: "one big with small, both align, then entry in small")."""
    t_small = np.asarray(t_small, np.int64); side_small = np.asarray(side_small)
    out = np.zeros(len(t_small), np.int64)
    for sd in (1, -1):
        tb = np.sort(np.asarray(t_big, np.int64)[np.asarray(side_big) == sd])
        m = side_small == sd
        if not len(tb) or not m.any():
            continue
        i = np.searchsorted(tb, t_small[m], side="right") - 1
        ok = i >= 0
        last = np.where(ok, tb[np.maximum(i, 0)], 0)
        out[np.flatnonzero(m)] = (ok & (t_small[m] - last < window_sec)).astype(np.int64)
    return out
