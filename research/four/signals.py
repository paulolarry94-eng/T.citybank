"""Four strategy families: entry signals only (management is applied separately).

Every signal is decided on a CLOSED bar i and entered at the next bar's first minute. Each signal
carries a side and a structural stop price (used only when the 'struct' stop is chosen).
Trend filter (where used): EMA50 > EMA200 and close > EMA200 = up (mirror = down).

TC  trend continuation
    ema20 / ema50  in an up trend, a bar of the last 5 dipped to the EMA (low <= EMA), and bar i
                   closes above the previous bar's high and above the EMA -> buy (mirror for sells).
                   Structural stop: lowest low of the last 5 bars - 0.2 ATR.
    don20 / don55  in an up trend, close above the highest high of the previous N bars -> buy.
                   Structural stop: lowest low of the last 10 bars - 0.2 ATR.
FB  failed breakout reversal (N = 20 / 55)
    wick   bar i trades above the previous-N-bar high but closes back below it -> sell.
           Structural stop: bar i high + 0.2 ATR.
    close  a bar of the last 3 closed above its previous-N-bar high, bar i closes back below that
           level -> sell. Structural stop: highest high since the breakout + 0.2 ATR.
    filter none, or 'trend': only the trades that go WITH the trend (a failed breakdown in an up
           trend -> buy; a failed breakout in an up trend is skipped).
VC  volatility contraction -> expansion
    bbw10 / bbw20  Bollinger(20, 2) width in the lowest 10% / 20% of the last 120 bars; box = the
                   last 10 bars' high/low. nr7: the narrowest range of 7 bars; box = that bar.
                   Within the next 5 bars, the first close outside the box -> trade that way.
                   Structural stop: the other side of the box - 0.2 ATR.
    filter none / trend (breakouts only in the trend direction)
VE  volatility expansion follow-through
    a bar with range >= X x ATR(14) of the previous bar (X = 1.5 / 2.0 / 2.5) closing in the top
    25% of its range -> buy next open (bottom 25% -> sell). Structural stop: the bar's low - 0.2 ATR.
    filter none / trend
"""
import numpy as np
import engine as E, gold_lab as GL


def trend(B):
    c = B["c"]; e50, e200 = E.ema(c, 50), E.ema(c, 200)
    up = (e50 > e200) & (c > e200); dn = (e50 < e200) & (c < e200)
    return np.where(up, 1, np.where(dn, -1, 0))


def _pack(idx, side, stop):
    return np.asarray(idx, np.int64), np.asarray(side, np.int64), np.asarray(stop, np.float64)


def tc(B, kind):
    o, h, l, c, a = B["o"], B["h"], B["l"], B["c"], B["atr"]
    T = trend(B); n = len(c); I, S, P = [], [], []
    if kind.startswith("ema"):
        p = int(kind[3:]); em = E.ema(c, p)
        for i in range(205, n - 1):
            if T[i] == 1 and (l[i - 5:i] <= em[i - 5:i]).any() and c[i] > h[i - 1] and c[i] > em[i]:
                I.append(i); S.append(1); P.append(l[i - 5:i + 1].min() - 0.2 * a[i])
            elif T[i] == -1 and (h[i - 5:i] >= em[i - 5:i]).any() and c[i] < l[i - 1] and c[i] < em[i]:
                I.append(i); S.append(-1); P.append(h[i - 5:i + 1].max() + 0.2 * a[i])
    else:
        N = int(kind[3:]); hh, ll = GL.rolling_max(h, N), GL.rolling_min(l, N)
        for i in range(205, n - 1):
            if T[i] == 1 and c[i] > hh[i]:
                I.append(i); S.append(1); P.append(l[i - 9:i + 1].min() - 0.2 * a[i])
            elif T[i] == -1 and c[i] < ll[i]:
                I.append(i); S.append(-1); P.append(h[i - 9:i + 1].max() + 0.2 * a[i])
    return _pack(I, S, P)


def fb(B, N, mode, filt):
    o, h, l, c, a = B["o"], B["h"], B["l"], B["c"], B["atr"]
    T = trend(B); n = len(c); hh, ll = GL.rolling_max(h, N), GL.rolling_min(l, N)
    I, S, P = [], [], []
    last_up = last_dn = -10
    for i in range(205, n - 1):
        cand = []
        if mode == "wick":
            if h[i] > hh[i] and c[i] < hh[i]:
                cand.append((-1, h[i] + 0.2 * a[i]))
            if l[i] < ll[i] and c[i] > ll[i]:
                cand.append((1, l[i] - 0.2 * a[i]))
        else:
            if c[i - 1] > hh[i - 1] or c[i - 2] > hh[i - 2] or c[i - 3] > hh[i - 3]:
                for b in (i - 1, i - 2, i - 3):
                    if c[b] > hh[b]:
                        if c[i] < hh[b] and b > last_up:
                            cand.append((-1, h[b:i + 1].max() + 0.2 * a[i])); last_up = i
                        break
            if c[i - 1] < ll[i - 1] or c[i - 2] < ll[i - 2] or c[i - 3] < ll[i - 3]:
                for b in (i - 1, i - 2, i - 3):
                    if c[b] < ll[b]:
                        if c[i] > ll[b] and b > last_dn:
                            cand.append((1, l[b:i + 1].min() - 0.2 * a[i])); last_dn = i
                        break
        for s, p in cand:
            if filt == "trend" and T[i] != s:
                continue
            I.append(i); S.append(s); P.append(p)
    return _pack(I, S, P)


def vc(B, kind, filt):
    o, h, l, c, a = B["o"], B["h"], B["l"], B["c"], B["atr"]
    T = trend(B); n = len(c)
    from numpy.lib.stride_tricks import sliding_window_view as sw
    sd = np.full(n, np.nan); sd[19:] = sw(c, 20).std(axis=1)
    m = GL.sma(c, 20); bbw = 4 * sd / m
    rng = h - l
    I, S, P = [], [], []
    box_hi = box_lo = np.nan; expiry = -1
    for i in range(205, n - 1):
        if i <= expiry and np.isfinite(box_hi):
            s = 1 if c[i] > box_hi else (-1 if c[i] < box_lo else 0)
            if s != 0:
                if not (filt == "trend" and T[i] != s):
                    I.append(i); S.append(s); P.append(box_lo - 0.2 * a[i] if s > 0 else box_hi + 0.2 * a[i])
                expiry = -1; box_hi = np.nan
                continue
        if kind == "nr7":
            hit = rng[i] <= rng[i - 6:i + 1].min()
            if hit:
                box_hi, box_lo, expiry = h[i], l[i], i + 5
        else:
            q = 10 if kind == "bbw10" else 20
            w = bbw[i - 120:i]
            if np.isfinite(bbw[i]) and np.isfinite(w).all() and (w < bbw[i]).mean() * 100 <= q:
                box_hi, box_lo, expiry = h[i - 9:i + 1].max(), l[i - 9:i + 1].min(), i + 5
    return _pack(I, S, P)


def ve(B, X, filt):
    o, h, l, c, a = B["o"], B["h"], B["l"], B["c"], B["atr"]
    T = trend(B); n = len(c); I, S, P = [], [], []
    for i in range(205, n - 1):
        r = h[i] - l[i]
        if not (a[i - 1] > 0 and r >= X * a[i - 1]):
            continue
        pos = (c[i] - l[i]) / r
        s = 1 if pos >= 0.75 else (-1 if pos <= 0.25 else 0)
        if s == 0 or (filt == "trend" and T[i] != s):
            continue
        I.append(i); S.append(s); P.append(l[i] - 0.2 * a[i] if s > 0 else h[i] + 0.2 * a[i])
    return _pack(I, S, P)


def entry_sets():
    """(family, variant name, function(B))."""
    out = []
    for k in ("ema20", "ema50", "don20", "don55"):
        out.append(("TC", k, lambda B, k=k: tc(B, k)))
    for N in (20, 55):
        for mode in ("wick", "close"):
            for f in ("none", "trend"):
                out.append(("FB", f"n{N}_{mode}_{f}", lambda B, N=N, mode=mode, f=f: fb(B, N, mode, f)))
    for k in ("bbw10", "bbw20", "nr7"):
        for f in ("none", "trend"):
            out.append(("VC", f"{k}_{f}", lambda B, k=k, f=f: vc(B, k, f)))
    for X in (1.5, 2.0, 2.5):
        for f in ("none", "trend"):
            out.append(("VE", f"x{X:g}_{f}", lambda B, X=X, f=f: ve(B, X, f)))
    return out
