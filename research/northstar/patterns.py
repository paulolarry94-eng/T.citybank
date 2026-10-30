"""North Star pattern modules: each turns closed bars into trade candidates (no execution here).

Candidate fields: k0 (entry minute; for market orders the first minute after the decision bar),
side, entry (-1 = market; else limit fill price), stop, jb (bar containing k0), sig (bar the time
stop and ATR refer to), cap (stop cap in ATR), dec_t (time the decision was made).
Every level is computed from bars that had CLOSED at decision time. Definitions: PREREGISTRATION.md §3.
"""
import numpy as np
from numba import njit
from core import limit_scan, BLOCK


def _pack(rows):
    keys = ("k0", "side", "entry", "stop", "jb", "sig", "cap", "dec_t")
    if not rows:
        return {k: np.zeros(0, np.int64 if k in ("k0", "side", "jb", "sig", "dec_t") else np.float64) for k in keys}
    A = list(zip(*rows))
    return {k: np.asarray(A[i], np.int64 if k in ("k0", "side", "jb", "sig", "dec_t") else np.float64) for i, k in enumerate(keys)}


def close_t(B, i):
    return int(B["t"][i] + B["minutes"] * 60)


def _limit(M, B, start, end, side, level, cancel):
    eps = 0.1 * M.cost
    return limit_scan(M.o, M.h, M.l, M.ts, B["first"], B["nxt"], B["c"], start, end, side, level, cancel, M.cost, eps, BLOCK[0], BLOCK[1])


# ----------------------------------------------------------------------------- supply and demand bases
def sd_events(B, nb, k):
    """All base patterns with exactly nb base candles. Returns rows (i_out, kind, base_hi, base_lo) where
    kind is 'RBR', 'DBD', 'DBR' or 'RBD' and i_out is the leg-out bar (decision bar)."""
    o, h, l, c, a = B["o"], B["h"], B["l"], B["c"], B["atr"]
    body, rng = c - o, h - l
    n = len(c); ev = []
    i = np.arange(nb + 1, n)
    A = a[i]
    ok = A > 0
    base_hi = np.max(np.stack([h[i - j] for j in range(1, nb + 1)]), axis=0)
    base_lo = np.min(np.stack([l[i - j] for j in range(1, nb + 1)]), axis=0)
    small = np.all(np.stack([rng[i - j] <= 0.6 * A for j in range(1, nb + 1)]), axis=0)
    lin = body[i - nb - 1]
    in_up, in_dn = lin >= k * A, -lin >= k * A
    out_up = (body[i] >= k * A) & (c[i] > base_hi + 0.1 * A)
    out_dn = (-body[i] >= k * A) & (c[i] < base_lo - 0.1 * A)
    for kind, m in (("RBR", in_up & out_up), ("DBD", in_dn & out_dn), ("DBR", in_dn & out_up), ("RBD", in_up & out_dn)):
        sel = ok & small & m
        for j in np.flatnonzero(sel):
            ev.append((int(i[j]), kind, float(base_hi[j]), float(base_lo[j])))
    ev.sort()
    return ev


def sd_candidates(M, B, nb, k, kinds, entry):
    rows = []; a = B["atr"]; n = len(B["c"])
    for i, kind, bh, bl in sd_events(B, nb, k):
        if kind not in kinds or i + 2 >= n:
            continue
        side = 1 if kind in ("RBR", "DBR") else -1
        A = a[i]
        stop = bl - 0.1 * A if side > 0 else bh + 0.1 * A
        if entry == "break":
            rows.append((B["nxt"][i], side, -1.0, stop, i + 1, i, 4.0, close_t(B, i)))
        else:
            lvl, cancel = (bh, bl) if side > 0 else (bl, bh)
            kf, px, u = _limit(M, B, i + 1, i + 21, side, lvl, cancel)
            if kf >= 0:
                rows.append((kf, side, px, stop, u, u, 4.0, close_t(B, i)))
    return _pack(rows)


# ----------------------------------------------------------------------------- fair value gaps
def fvg_events(B, wmin):
    """Rows (i, side, gap_bot, gap_top, c1_extreme): bullish if low[i] > high[i-2] (gap = [high[i-2], low[i]]),
    bearish if high[i] < low[i-2]; gap height >= wmin x ATR(i). Known when bar i has closed."""
    h, l, a = B["h"], B["l"], B["atr"]
    i = np.arange(2, len(h))
    A = a[i]
    bull = (l[i] > h[i - 2]) & (l[i] - h[i - 2] >= wmin * A) & (A > 0)
    bear = (h[i] < l[i - 2]) & (l[i - 2] - h[i] >= wmin * A) & (A > 0)
    ev = [(int(i[j]), 1, float(h[i[j] - 2]), float(l[i[j]]), float(l[i[j] - 2])) for j in np.flatnonzero(bull)]
    ev += [(int(i[j]), -1, float(h[i[j]]), float(l[i[j] - 2]), float(h[i[j] - 2])) for j in np.flatnonzero(bear)]
    ev.sort()
    return ev


def swing_levels(B, k):
    """For each bar, the most recent CONFIRMED swing high / low (pivot strength k, known k bars later)."""
    h, l = B["h"], B["l"]; n = len(h)
    last_hi = np.full(n, np.nan); last_lo = np.full(n, np.nan)
    cur_hi = cur_lo = np.nan
    for t in range(2 * k, n):
        j = t - k
        if h[j] > h[j - k:j].max() and h[j] > h[j + 1:t + 1].max():
            cur_hi = h[j]
        if l[j] < l[j - k:j].min() and l[j] < l[j + 1:t + 1].min():
            cur_lo = l[j]
        last_hi[t] = cur_hi; last_lo[t] = cur_lo
    return last_hi, last_lo


@njit(cache=True)
def _fvg_b_scan(o, h, l, c, i, side, gb, gt, age):
    """Model B: inside the gap, an opposite-colour candle with its low (long) inside the gap is the
    pullback; a later close beyond the pullback's high triggers. A close beyond the far edge kills it.
    Returns the trigger bar or -1."""
    p = -1
    for u in range(i + 1, min(i + 1 + age, len(c))):
        if side > 0:
            if c[u] < gb:
                return -1
            if p >= 0 and c[u] > h[p]:
                return u
            if c[u] < o[u] and gb <= l[u] <= gt:
                p = u
        else:
            if c[u] > gt:
                return -1
            if p >= 0 and c[u] < l[p]:
                return u
            if c[u] > o[u] and gb <= h[u] <= gt:
                p = u
    return -1


def fvg_candidates(M, B, model, wmin, depth=0.0, buf=0.0, age=30, swings=None):
    rows = []; a = B["atr"]; n = len(B["c"])
    if model == "C" and swings is None:
        swings = swing_levels(B, 3)
    for i, side, gb, gt, c1x in fvg_events(B, wmin):
        if i + 2 >= n:
            continue
        A = a[i]
        stop = c1x - 0.1 * A if side > 0 else c1x + 0.1 * A
        if model == "C":                     # displacement candle (i-1) must close beyond the last confirmed swing
            sh, sl = swings[0][i - 2], swings[1][i - 2]
            ci = B["c"][i - 1]
            if not ((side > 0 and np.isfinite(sh) and ci > sh) or (side < 0 and np.isfinite(sl) and ci < sl)):
                continue
        if model == "B":
            u = _fvg_b_scan(B["o"], B["h"], B["l"], B["c"], i, side, gb, gt, age)
            if u >= 0 and u + 1 < n:
                rows.append((B["nxt"][u], side, -1.0, stop, u + 1, u, 4.0, close_t(B, u)))
            continue
        near = gt if side > 0 else gb
        lvl = near - side * depth * (gt - gb) + side * buf * A
        cancel = gb if side > 0 else gt
        kf, px, u = _limit(M, B, i + 1, i + 1 + age, side, lvl, cancel)
        if kf >= 0:
            rows.append((kf, side, px, stop, u, u, 4.0, close_t(B, i)))
    return _pack(rows)


# ----------------------------------------------------------------------------- Quasimodo
def pivots(B, k):
    """Confirmed alternating pivots as (confirm_bar, bar, type, price); type +1 high, -1 low.
    A pivot at bar j is known at bar j + k. Consecutive same-type pivots keep the more extreme one
    (the replacement is known only when the newer pivot is confirmed)."""
    h, l = B["h"], B["l"]; n = len(h); P = []
    for t in range(2 * k, n):
        j = t - k
        for typ, x, ok in ((1, h[j], h[j] > h[j - k:j].max() and h[j] > h[j + 1:t + 1].max()),
                           (-1, l[j], l[j] < l[j - k:j].min() and l[j] < l[j + 1:t + 1].min())):
            if not ok:
                continue
            if P and P[-1][2] == typ:
                if (typ > 0 and x > P[-1][3]) or (typ < 0 and x < P[-1][3]):
                    P[-1] = (t, j, typ, x)
            else:
                P.append((t, j, typ, x))
    return P


def qm_events(B, k, m):
    """Real-time QM arming. Each time the alternating pivot list changes (a new pivot confirmed, or the
    last pivot replaced by a more extreme one), the last four pivots are checked AT THAT MOMENT.
    Bullish: L1 H1 L2 H2 with L2 < L1 - m ATR, H1 - L2 >= 1 ATR, H2 < H1. Bearish mirror.
    Returns (armed_bar, side, qm_level, head, near_break_level, far_break_level, structure_id)."""
    h, l, a = B["h"], B["l"], B["atr"]; n = len(h); P = []; out = []
    for t in range(2 * k, n):
        j = t - k
        changed = False
        for typ, x, ok in ((1, h[j], h[j] > h[j - k:j].max() and h[j] > h[j + 1:t + 1].max()),
                           (-1, l[j], l[j] < l[j - k:j].min() and l[j] < l[j + 1:t + 1].min())):
            if not ok:
                continue
            if P and P[-1][2] == typ:
                if (typ > 0 and x > P[-1][3]) or (typ < 0 and x < P[-1][3]):
                    P[-1] = (t, j, typ, x); changed = True
            else:
                P.append((t, j, typ, x)); changed = True
        if not changed or len(P) < 4 or a[t] <= 0:
            continue
        p1, p2, p3, p4 = P[-4], P[-3], P[-2], P[-1]; A = a[t]
        sid = (p1[1], p2[1], p3[1])
        if (p1[2], p2[2], p3[2], p4[2]) == (-1, 1, -1, 1):
            L1, H1, L2, H2 = p1[3], p2[3], p3[3], p4[3]
            if L2 < L1 - m * A and H1 - L2 >= A and H2 < H1:
                out.append((t, 1, L1, L2, H2, H1, sid))
        elif (p1[2], p2[2], p3[2], p4[2]) == (1, -1, 1, -1):
            H1, L1, H2, L2 = p1[3], p2[3], p3[3], p4[3]
            if H2 > H1 + m * A and H2 - L1 >= A and L2 > L1:
                out.append((t, -1, H1, H2, L2, L1, sid))
    return out


def qm_triggers(B, k, m, level):
    """(trigger_bar, side, qm_level, head) where trigger = first close beyond the break level within
    30 bars of arming (cancelled by a close beyond the head)."""
    c = B["c"]; n = len(c); out = []; done = set(); busy_until = {}
    for t, side, qml, head, lvl2, lvl1, sid in qm_events(B, k, m):
        if sid in done or t < busy_until.get(sid, -1):
            continue                                     # one trigger per structure; no re-arm while armed
        brk = lvl2 if level == "near" else lvl1
        busy_until[sid] = t + 31
        for u in range(t + 1, min(t + 31, n - 1)):
            if (side > 0 and c[u] < head) or (side < 0 and c[u] > head):
                break
            if (side > 0 and c[u] > brk) or (side < 0 and c[u] < brk):
                out.append((u, side, qml, head)); done.add(sid); break
    out.sort()
    return out


def qm_candidates(M, B, k, m, level, entry, tol=0.0):
    rows = []; a = B["atr"]; n = len(B["c"])
    for u, side, qml, head in qm_triggers(B, k, m, level):
        if u + 2 >= n:
            continue
        A = a[u]
        stop = head - 0.1 * A if side > 0 else head + 0.1 * A
        if entry == "break":
            rows.append((B["nxt"][u], side, -1.0, stop, u + 1, u, 5.0, close_t(B, u)))
        else:
            lvl = qml + side * tol * A
            kf, px, v = _limit(M, B, u + 1, u + 31, side, lvl, head)
            if kf >= 0:
                rows.append((kf, side, px, stop, v, v, 5.0, close_t(B, u)))
    return _pack(rows)


# ----------------------------------------------------------------------------- confluence filters
def recent_flags(B, events, window):
    """events: list of (bar, side). Returns arrays long_ok/short_ok per bar: an event of that side at a bar
    in [D - window, D]."""
    n = len(B["c"]); out = {}
    for s in (1, -1):
        x = np.zeros(n + 1)
        for b, sd in events:
            if sd == s and b < n:
                x[b + 1] += 1
        cs = np.cumsum(x)
        idx = np.arange(n)
        out[s] = (cs[idx + 1] - cs[np.maximum(idx - window, 0)]) > 0
    return out


def filter_keep(cands, B, flags):
    """Keep candidates whose decision bar has a same-side event in the window."""
    if len(cands["k0"]) == 0:
        return np.zeros(0, bool)
    dec_bar = np.searchsorted(B["t"] + B["minutes"] * 60, cands["dec_t"], side="right") - 1
    dec_bar = np.clip(dec_bar, 0, len(B["c"]) - 1)
    return np.where(cands["side"] > 0, flags[1][dec_bar], flags[-1][dec_bar])
