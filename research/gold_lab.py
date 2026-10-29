"""Gold strategy lab: published / widely used systematic families on every timeframe.

Same fill law as the rest of the research: a signal on a closed bar is entered at the first
minute of the next bar (ask for longs, bid for shorts, $0.45 all-in cost); protective stops
are checked minute by minute and gapped stops fill at the worse open; same-minute
stop+target = loss; stop-order entries (breakouts inside a bar) fill at the level or the
worse open, and a minute that touches both sides is skipped.
"""
import numpy as np
from numba import njit
import engine as E

COST = E.COST["XAUUSD"]
TFS = {"M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
DT = [("t_in", "i8"), ("t_out", "i8"), ("side", "i8"), ("r", "f8"), ("dist", "f8"), ("entry", "f8")]


# ------------------------------------------------------------------ core scanner
@njit(cache=True)
def run_signals(o, h, l, ts, ent_i, side, dist, tgt_r, trail_r, exit_i, cost, gaps):
    """Serial book: signals sorted by entry minute. Each: stop = dist, optional target
    (tgt_r * dist), optional chandelier trail (trail_r), forced exit at minute exit_i."""
    n = len(ent_i); out = np.zeros((n, 6)); k = 0; busy = -1
    g = 0
    for s in range(n):
        i0 = ent_i[s]; i1 = exit_i[s]
        if i0 <= busy or i0 >= len(o) - 1 or i1 <= i0:
            continue
        if i1 >= len(o): i1 = len(o) - 1
        # skip trades that would span a data hole
        while g < len(gaps) and gaps[g] < i0: g += 1
        if g < len(gaps) and gaps[g] < i1:
            busy = i1; continue
        sd = side[s]; d = dist[s]
        entry = o[i0] + cost if sd > 0 else o[i0]
        sl = entry - d if sd > 0 else entry + d
        tp = (entry + tgt_r[s] * d if sd > 0 else entry - tgt_r[s] * d) if tgt_r[s] > 0 else 0.0
        peak = 0.0; px = 0.0; xi = i1
        done = False
        for i in range(i0, i1):
            if sd > 0:
                if l[i] <= sl:
                    px = sl if (o[i] > sl or i == i0) else o[i]; px = min(px, sl); xi = i; done = True; break
                if tp > 0 and h[i] >= tp:
                    px = tp; xi = i; done = True; break
                fav = (h[i] - entry) / d
            else:
                if h[i] + cost >= sl:
                    ao = o[i] + cost
                    px = sl if (ao < sl or i == i0) else ao; px = max(px, sl); xi = i; done = True; break
                if tp > 0 and l[i] + cost <= tp:
                    px = tp; xi = i; done = True; break
                fav = (entry - (l[i] + cost)) / d
            if trail_r[s] > 0 and fav > peak:
                peak = fav
                if peak >= trail_r[s]:
                    tr = peak - trail_r[s]
                    new = entry + tr * d if sd > 0 else entry - tr * d
                    if (sd > 0 and new > sl) or (sd < 0 and new < sl):
                        sl = new
        if not done:
            px = o[i1] if sd > 0 else o[i1] + cost
        r = (px - entry) / d if sd > 0 else (entry - px) / d
        out[k, 0] = ts[i0]; out[k, 1] = ts[xi]; out[k, 2] = sd; out[k, 3] = r
        out[k, 4] = d; out[k, 5] = entry; k += 1
        busy = xi
    return out[:k]


def pack(arr):
    t = np.zeros(len(arr), dtype=DT)
    for j, name in enumerate(["t_in", "t_out", "side", "r", "dist", "entry"]):
        t[name] = arr[:, j]
    return t


class Market:
    def __init__(self, sym="XAUUSD"):
        self.sym = sym
        self.cost = E.COST[sym]
        self.m1 = E.load_m1(sym)
        self.ts, self.o, self.h, self.l, self.c = self.m1
        self.gaps = E.data_gaps(self.ts)
        self.bars = {}

    def tf(self, name, offset=120):
        key = (name, offset)
        if key not in self.bars:
            m = TFS[name]
            off = offset if m >= 240 else 0
            bt, bo, bh, bl, bc, nxt = E.resample(*self.m1, m, off)
            self.bars[key] = dict(t=bt, o=bo, h=bh, l=bl, c=bc, nxt=nxt,
                                  atr=E.atr_sma(bh, bl, bc, 14), minutes=m)
        return self.bars[key]

    def run(self, ent_bar, side, dist, B, tgt_r=0.0, trail_r=0.0, exit_bar=None, hold=None):
        """ent_bar: signal bar indices (entry at next bar's first minute)."""
        ent_bar = np.asarray(ent_bar, np.int64)
        ok = ent_bar < len(B["t"]) - 2
        ent_bar, side, dist = ent_bar[ok], np.asarray(side)[ok], np.asarray(dist)[ok]
        if exit_bar is None:
            exit_bar = np.minimum(ent_bar + (hold if hold else 10 ** 6), len(B["t"]) - 2)
        else:
            exit_bar = np.asarray(exit_bar, np.int64)[ok]
        ent_i = B["nxt"][ent_bar].astype(np.int64)
        exit_i = B["nxt"][np.minimum(exit_bar, len(B["t"]) - 1)].astype(np.int64)
        n = len(ent_i)
        tg = np.full(n, float(tgt_r)); trl = np.full(n, float(trail_r))
        o = np.argsort(ent_i, kind="stable")
        res = run_signals(self.o, self.h, self.l, self.ts, ent_i[o], np.asarray(side, np.int64)[o],
                          np.asarray(dist, np.float64)[o], tg, trl, exit_i[o], self.cost, self.gaps)
        return pack(res)


# ------------------------------------------------------------------ indicators
def sma(x, n):
    cs = np.cumsum(np.r_[0.0, x]); out = np.full(len(x), np.nan)
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def rolling_max(x, n):
    out = np.full(len(x), np.nan)
    from numpy.lib.stride_tricks import sliding_window_view as sw
    out[n:] = sw(x, n).max(axis=1)[:-1]          # highest of the PREVIOUS n bars
    return out


def rolling_min(x, n):
    out = np.full(len(x), np.nan)
    from numpy.lib.stride_tricks import sliding_window_view as sw
    out[n:] = sw(x, n).min(axis=1)[:-1]
    return out


def rsi(c, n):
    d = np.diff(c, prepend=c[0]); up = np.where(d > 0, d, 0.0); dn = np.where(d < 0, -d, 0.0)
    a = 1.0 / n; ru = np.zeros_like(c); rd = np.zeros_like(c)
    for i in range(1, len(c)):
        ru[i] = ru[i - 1] + a * (up[i] - ru[i - 1]); rd[i] = rd[i - 1] + a * (dn[i] - rd[i - 1])
    return 100 - 100 / (1 + ru / np.maximum(rd, 1e-12))


def first_true_after(cond, starts, cap):
    """For each start bar s, the first bar u > s where cond[u] is True (or s + cap)."""
    idx = np.flatnonzero(cond)
    out = np.empty(len(starts), np.int64)
    for j, s in enumerate(starts):
        k = np.searchsorted(idx, s + 1)
        u = idx[k] if k < len(idx) else s + cap
        out[j] = min(u, s + cap)
    return out


# ------------------------------------------------------------------ families
def donchian(G, tfn, n=20, mult=2.0, trail=1.5, sides=(1, -1), turtle_exit=False):
    B = G.tf(tfn); hh, ll = rolling_max(B["h"], n), rolling_min(B["l"], n)
    up = B["c"] > hh; dn = B["c"] < ll
    t = np.flatnonzero((up & (1 in sides)) | (dn & (-1 in sides)))
    sd = np.where(up[t], 1, -1); dist = mult * B["atr"][t]
    ok = np.isfinite(dist) & (dist > 1.5 * G.cost); t, sd, dist = t[ok], sd[ok], dist[ok]
    if not turtle_exit:
        return G.run(t, sd, dist, B, trail_r=trail)
    m = max(2, n // 2); xl, xh = rolling_min(B["l"], m), rolling_max(B["h"], m)
    ex = np.empty(len(t), np.int64)
    exl = first_true_after(B["c"] < xl, t, 10 ** 6); exs = first_true_after(B["c"] > xh, t, 10 ** 6)
    ex = np.where(sd > 0, exl, exs)
    return G.run(t, sd, dist, B, exit_bar=ex)


def ma_cross(G, tfn, fast=20, slow=50, mult=3.0, sides=(1, -1)):
    B = G.tf(tfn); f, s = E.ema(B["c"], fast), E.ema(B["c"], slow)
    pos = np.where(f > s, 1, -1); pos[~(np.isfinite(f) & np.isfinite(s))] = 0
    flip = np.flatnonzero((pos[1:] != pos[:-1]) & (pos[1:] != 0)) + 1
    sd = pos[flip]; keep = np.isin(sd, sides); flip, sd = flip[keep], sd[keep]
    nxt_flip = np.r_[flip[1:], len(B["t"]) - 2] if len(flip) else flip
    # exit at the next flip of the full series (opposite cross), not just the next kept one
    allflip = np.flatnonzero((pos[1:] != pos[:-1])) + 1
    ex = np.array([allflip[np.searchsorted(allflip, x + 1)] if np.searchsorted(allflip, x + 1) < len(allflip)
                   else len(B["t"]) - 2 for x in flip], np.int64)
    dist = mult * B["atr"][flip]; ok = np.isfinite(dist) & (dist > 1.5 * G.cost)
    return G.run(flip[ok], sd[ok], dist[ok], B, exit_bar=ex[ok])


def rsi2(G, tfn, lo=10, hi=90, mult=2.0, sides=(1, -1), cap=10):
    B = G.tf(tfn); c = B["c"]; r = rsi(c, 2); m200 = sma(c, 200); m5 = sma(c, 5)
    L = (r < lo) & (c > m200); S = (r > hi) & (c < m200)
    t = np.flatnonzero((L & (1 in sides)) | (S & (-1 in sides)))
    sd = np.where(L[t], 1, -1)
    exl = first_true_after(c > m5, t, cap); exs = first_true_after(c < m5, t, cap)
    ex = np.where(sd > 0, exl, exs); dist = mult * B["atr"][t]
    ok = np.isfinite(dist) & (dist > 1.5 * G.cost)
    return G.run(t[ok], sd[ok], dist[ok], B, exit_bar=ex[ok])


def bollinger(G, tfn, n=20, k=2.0, mult=2.0, sides=(1, -1), cap=20):
    B = G.tf(tfn); c = B["c"]; m = sma(c, n)
    sd_ = np.full(len(c), np.nan)
    from numpy.lib.stride_tricks import sliding_window_view as sw
    sd_[n - 1:] = sw(c, n).std(axis=1)
    L = c < m - k * sd_; S = c > m + k * sd_
    t = np.flatnonzero((L & (1 in sides)) | (S & (-1 in sides)))
    side = np.where(L[t], 1, -1)
    exl = first_true_after(c >= m, t, cap); exs = first_true_after(c <= m, t, cap)
    ex = np.where(side > 0, exl, exs); dist = mult * B["atr"][t]
    ok = np.isfinite(dist) & (dist > 1.5 * G.cost)
    return G.run(t[ok], side[ok], dist[ok], B, exit_bar=ex[ok])


def ibs(G, tfn, lo=0.2, hi=0.8, mult=2.0, sides=(1, -1)):
    B = G.tf(tfn); rng = B["h"] - B["l"]; v = (B["c"] - B["l"]) / np.where(rng > 0, rng, np.nan)
    L = v < lo; S = v > hi
    t = np.flatnonzero((L & (1 in sides)) | (S & (-1 in sides)))
    side = np.where(L[t], 1, -1); dist = mult * B["atr"][t]
    ok = np.isfinite(dist) & (dist > 1.5 * G.cost)
    return G.run(t[ok], side[ok], dist[ok], B, hold=1)


def mtf_trend(G, tfn, n=20, mult=2.0, trail=1.5, slow=50):
    """Donchian on tfn, only in the direction of the D1 EMA(slow) slope (awesome repo:
    multi-timeframe trend)."""
    B = G.tf(tfn); D = G.tf("D1"); de = E.ema(D["c"], slow)
    slope = np.sign(de - np.r_[np.nan, de[:-1]])
    # map each tfn bar to the last COMPLETED daily bar before it
    di = np.searchsorted(D["t"] + 86400, B["t"] + B["minutes"] * 60, side="right") - 1
    trend = np.where(di >= 0, slope[np.clip(di, 0, len(slope) - 1)], 0)
    hh, ll = rolling_max(B["h"], n), rolling_min(B["l"], n)
    up = (B["c"] > hh) & (trend > 0); dn = (B["c"] < ll) & (trend < 0)
    t = np.flatnonzero(up | dn); sd = np.where(up[t], 1, -1); dist = mult * B["atr"][t]
    ok = np.isfinite(dist) & (dist > 1.5 * G.cost)
    return G.run(t[ok], sd[ok], dist[ok], B, trail_r=trail)


@njit(cache=True)
def _stop_entries(o, h, l, ts, starts, ends, up_lvl, dn_lvl, stop_d, tgt_r, exit_at, cost, gaps):
    """Inside-bar stop-order entries (volatility breakout / opening range): first touch of
    up_lvl or dn_lvl in [start, end); a minute touching both is skipped. Then manage
    stop/target until exit_at (minute index)."""
    n = len(starts); out = np.zeros((n, 6)); k = 0; busy = -1; g = 0
    for s in range(n):
        a, b = starts[s], ends[s]
        if a <= busy or b <= a or b >= len(o):
            continue
        side = 0; i0 = -1; entry = 0.0
        for i in range(a, b):
            hu = h[i] + cost >= up_lvl[s]; hd = l[i] <= dn_lvl[s]
            if hu and hd:
                break
            if hu:
                side = 1; i0 = i; entry = max(up_lvl[s], o[i] + cost); break
            if hd:
                side = -1; i0 = i; entry = min(dn_lvl[s], o[i]); break
        if side == 0:
            continue
        x1 = exit_at[s]
        while g < len(gaps) and gaps[g] < i0: g += 1
        if g < len(gaps) and gaps[g] < x1:
            continue
        d = stop_d[s]
        sl = entry - d if side > 0 else entry + d
        tp = (entry + tgt_r * d if side > 0 else entry - tgt_r * d) if tgt_r > 0 else 0.0
        px = 0.0; xi = x1; done = False
        for i in range(i0, x1):
            if side > 0:
                if l[i] <= sl:
                    px = min(sl if (o[i] > sl or i == i0) else o[i], sl); xi = i; done = True; break
                if tp > 0 and h[i] >= tp and i > i0:
                    px = tp; xi = i; done = True; break
            else:
                if h[i] + cost >= sl:
                    ao = o[i] + cost
                    px = max(sl if (ao < sl or i == i0) else ao, sl); xi = i; done = True; break
                if tp > 0 and l[i] + cost <= tp and i > i0:
                    px = tp; xi = i; done = True; break
        if not done:
            px = o[x1] if side > 0 else o[x1] + cost
        r = (px - entry) / d if side > 0 else (entry - px) / d
        out[k, 0] = ts[i0]; out[k, 1] = ts[xi]; out[k, 2] = side; out[k, 3] = r
        out[k, 4] = d; out[k, 5] = entry; k += 1; busy = xi
    return out[:k]


def vol_breakout(G, tfn, k=0.5):
    """Larry Williams: buy stop at open + k * previous range, sell stop at open - k * range,
    stop back at the open, exit at the bar's close."""
    B = G.tf(tfn); rng = np.r_[np.nan, (B["h"] - B["l"])[:-1]]
    starts = np.r_[0, B["nxt"][:-1]].astype(np.int64); ends = B["nxt"].astype(np.int64)
    up = B["o"] + k * rng; dn = B["o"] - k * rng; d = k * rng
    ok = np.isfinite(d) & (d > 1.5 * G.cost)
    ends_c = np.minimum(ends, len(G.o) - 1)
    res = _stop_entries(G.o, G.h, G.l, G.ts, starts[ok], ends_c[ok], up[ok], dn[ok], d[ok], 0.0,
                        ends_c[ok], G.cost, G.gaps)
    return pack(res)


def opening_range(G, start_h=7, minutes=60, exit_h=20, tgt_r=1.0):
    """Opening-range breakout: range of the first `minutes` after start_h (UTC), trade the
    first break of it until exit_h, stop at the other side, target tgt_r x range."""
    ts = G.ts; days = np.unique(ts // 86400)
    st, en, up, dn, d, ex = [], [], [], [], [], []
    for dd in days:
        t0 = dd * 86400 + start_h * 3600
        a = np.searchsorted(ts, t0); b = np.searchsorted(ts, t0 + minutes * 60)
        z = np.searchsorted(ts, dd * 86400 + exit_h * 3600)
        if b - a < minutes * 0.6 or z <= b or z >= len(ts):
            continue
        hi, lo = G.h[a:b].max(), G.l[a:b].min()
        if hi - lo <= 2 * G.cost:
            continue
        st.append(b); en.append(z); up.append(hi); dn.append(lo); d.append(hi - lo); ex.append(z)
    A = lambda x, t=np.float64: np.array(x, t)
    res = _stop_entries(G.o, G.h, G.l, ts, A(st, np.int64), A(en, np.int64), A(up), A(dn), A(d),
                        float(tgt_r), A(ex, np.int64), G.cost, G.gaps)
    return pack(res)


Gold = Market   # backwards-compatible name
