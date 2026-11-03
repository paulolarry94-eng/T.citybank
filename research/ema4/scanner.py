"""The owner's 4-flip EMA pattern (2026-11-02): one timeframe, one pattern.

    import scanner; P = scanner.detect(o, h, l, c)       # every pattern in a bar series

SELL pattern (BUY is the mirror), four CONSECUTIVE candles, each crossing the 10 EMA with its body:
  1 breaks OUT above (opens at/below the EMA, closes at/above it)      "buy"
  2 breaks back IN below (opens at/above, closes at/below)             "sell"
  3 breaks out above again                                             "buy"
  4 breaks back in below                                               "sell"
Grade (engulf="open", v1): B+ = the 4th candle CLOSES below the 3rd candle's OPEN; A+ = also the 2nd below the 1st's OPEN.
Grade (engulf="extreme", owner 2026-11-03, full engulfing): B+ = the 4th CLOSES below the 3rd candle's LOW (above its HIGH
       for buys); A+ = also the 2nd closed below the 1st candle's LOW (above its HIGH).
       Only the 2nd engulfing, or none = rejected (owner's charts of 22 and 26 Oct 2026).
The EMA is the line drawn on each candle: 10-period EMA of closes including that candle (TradingView ema(close, 10)).
A candle within `tol` x ATR(14) of the line counts as touching it; a candle needs a body larger than `min_body` x ATR(14)
(a doji is not a breakout: owner's 22 Oct 07:55 candle).
fresh=True (owner 2026-11-03, v3): each break must come from the other side - the previous candle CLOSED on the other side of
the EMA (GBPUSD 10 Sep 2012 06:00: the candle before had closed 0.31 pip below, so 06:00 was no break). A previous close
within fresh_tol x ATR (0.02, about 0.06 pip on EURUSD M5) of the line counts as either side (owner's EURUSD 20 Aug 2014
07:15 candle closed exactly ON the line, and the owner takes 07:20 as the 1st candle).
clear (owner 2026-11-03, v4: "the breakouts too should be obvious"): each candle's open AND close must be at least
clear x ATR(14) from the EMA on their sides. The owner's approved charts: faintest 0.08 ATR (20 Oct, 0.25 pip), 0.16 ATR
(EURUSD 20 Aug 2014); the 27 Oct chart's 3rd candle sits on the line (about 0.01 ATR). Feeds differ by tenths of a pip, so near-dojis on the line flip
between brokers (owner's 27 Oct 16:50 candle: a small bullish body on TradingView, a doji in our feed). Overlapping windows are all patterns (owner's 20 Oct chart:
a sell on candles 12:35-12:50 and a buy on 12:40-12:55).
margin: how far beyond the open the engulfing close must be, in ATR(14) (0 = any amount; feeds differ by tenths of a pip).
Trade (owner): entry at 50% of the 4th candle (wick to wick), stop beyond the 4th candle's extreme; targets 1-4R.
"""
import numpy as np
import pandas as pd

EMA_N = 10


def ema(c, n=EMA_N):
    return pd.Series(np.asarray(c, float)).ewm(span=n, adjust=False).mean().to_numpy()


def atr(h, l, c, n=14):
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h, pc) - np.minimum(l, pc)
    return pd.Series(tr).rolling(n, min_periods=1).mean().to_numpy()


def flips(o, c, e, tol=0.0, body=0.0, fresh=False, ftol=0.0, clear=0.0):
    """up[j]: candle j's body crosses the EMA upward; dn[j]: downward (within tol of the line counts as touching).
    body: minimum body (|close - open|) in price units; a doji is not a breakout (owner's 22 Oct 07:55 candle)."""
    up = (o <= e + tol - clear) & (c >= e - tol + clear) & (c - o > body)    # clear > 0: an OBVIOUS break - the
    dn = (o >= e - tol + clear) & (c <= e + tol - clear) & (o - c > body)    # body starts and ends clear of the line
    if fresh:                                   # a real break: the previous candle closed on the other side of the EMA
        pc, pe = np.r_[np.nan, c[:-1]], np.r_[np.nan, e[:-1]]   # (within ftol of the line counts as either side)
        up &= pc <= pe + ftol
        dn &= pc >= pe - ftol
    return up, dn


def detect(o, h, l, c, e=None, margin=0.0, tol=0.0, min_body=0.0, engulf="open", fresh=False, fresh_tol=0.02, clear=0.0):
    """Every pattern. Returns a dict of arrays: i4 (index of the 4th candle), side (-1 sell, +1 buy), grade (2 A+, 1 B+,
    0 rejected: four flips without the 4th engulfing, kept for audits), entry50, hi4, lo4, hi_all, lo_all (the 4 candles)."""
    o, h, l, c = (np.asarray(x, float) for x in (o, h, l, c))
    e = ema(c) if e is None else np.asarray(e, float)
    a = atr(h, l, c)
    up, dn = flips(o, c, e, tol * a, min_body * a, fresh, fresh_tol * np.r_[a[0], a[:-1]], clear * a)
    n = len(c); i = np.arange(3, n)
    sell = up[i - 3] & dn[i - 2] & up[i - 1] & dn[i]
    buy = dn[i - 3] & up[i - 2] & dn[i - 1] & up[i]
    out = {k: [] for k in ("i4", "side", "grade", "entry50", "hi4", "lo4", "hi3", "lo3", "hi_all", "lo_all", "atr")}
    for side, m in ((-1, sell), (1, buy)):
        for k in i[m]:
            mg = margin * a[k]
            if engulf == "open":                     # v1: close beyond the previous candle's OPEN
                ref3, ref1 = o[k - 1], o[k - 3]
            else:                                    # owner 2026-11-03: close beyond its full range (low for sells)
                ref3, ref1 = (l[k - 1], l[k - 3]) if side < 0 else (h[k - 1], h[k - 3])
            if side < 0:
                e4 = c[k] < ref3 - mg; e2 = c[k - 2] < ref1 - mg
            else:
                e4 = c[k] > ref3 + mg; e2 = c[k - 2] > ref1 + mg
            grade = 2 if (e4 and e2) else (1 if e4 else 0)
            for kk, v in (("i4", k), ("side", side), ("grade", grade), ("entry50", 0.5 * (h[k] + l[k])), ("hi4", h[k]),
                          ("lo4", l[k]), ("hi3", h[k - 1]), ("lo3", l[k - 1]), ("hi_all", h[k - 3:k + 1].max()), ("lo_all", l[k - 3:k + 1].min()), ("atr", a[k])):
                out[kk].append(v)
    srt = np.argsort(np.asarray(out["i4"]), kind="stable")
    return {k: np.asarray(v)[srt] for k, v in out.items()}


GRADE = {2: "A+", 1: "B+", 0: "rejected"}


def detect_pa(o, h, l, c):
    """Owner 2026-11-03: the same four candles WITHOUT the EMA, A+ only (pure price action).
    SELL: 1 bullish; 2 bearish closing below candle 1's LOW; 3 bullish; 4 bearish closing below candle 3's LOW.
    BUY (mirror): 1 bearish; 2 bullish closing above candle 1's HIGH; 3 bearish; 4 bullish closing above candle 3's HIGH.
    grade 2 = that pattern; grade 0 = four alternating-colour candles WITHOUT both closes beyond (the control).
    Same output fields as detect()."""
    o, h, l, c = (np.asarray(x, float) for x in (o, h, l, c))
    a = atr(h, l, c)
    bull, bear = c > o, c < o
    n = len(c); i = np.arange(3, n)
    sell_alt = bull[i - 3] & bear[i - 2] & bull[i - 1] & bear[i]
    buy_alt = bear[i - 3] & bull[i - 2] & bear[i - 1] & bull[i]
    out = {k: [] for k in ("i4", "side", "grade", "entry50", "hi4", "lo4", "hi3", "lo3", "hi_all", "lo_all", "atr")}
    for side, m in ((-1, sell_alt), (1, buy_alt)):
        for k in i[m]:
            if side < 0:
                ok = c[k - 2] < l[k - 3] and c[k] < l[k - 1]
            else:
                ok = c[k - 2] > h[k - 3] and c[k] > h[k - 1]
            for kk, v in (("i4", k), ("side", side), ("grade", 2 if ok else 0), ("entry50", 0.5 * (h[k] + l[k])), ("hi4", h[k]),
                          ("lo4", l[k]), ("hi3", h[k - 1]), ("lo3", l[k - 1]), ("hi_all", h[k - 3:k + 1].max()),
                          ("lo_all", l[k - 3:k + 1].min()), ("atr", a[k])):
                out[kk].append(v)
    srt = np.argsort(np.asarray(out["i4"]), kind="stable")
    return {k: np.asarray(v)[srt] for k, v in out.items()}
