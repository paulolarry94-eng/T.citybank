"""Custom exit engines for strategies whose exits are not target / trail / time stop.

A strategy file opts in with   EXECUTOR = executors.bailout(...)
The lab then calls EXECUTOR(M, B, C, p, cut, cost_mult, swap_mult, delay) instead of the North Star core; it must
return the core's trade rows [t_in, t_out, side, net R, stop distance, cost R, nights, financing R].
Fill law as everywhere: longs pay the ask (bid + cost), exits at the bid; shorts the reverse; gapped stops fill at
the worse open; trades spanning a data hole are discarded; one position at a time.
"""
import datetime as dt
from zoneinfo import ZoneInfo
import numpy as np
from numba import njit
import core

NY = ZoneInfo("America/New_York")


def ny_window(ts, lo_min, hi_min):
    """Boolean per minute: New York local time within [lo_min, hi_min] minutes after midnight (DST-aware)."""
    days = ts // 86400
    ud, inv = np.unique(days, return_inverse=True)
    off = np.array([int(dt.datetime.fromtimestamp(int(d) * 86400 + 43200, tz=NY).utcoffset().total_seconds()) for d in ud])[inv]
    m = ((ts + off) % 86400) // 60
    return (m >= lo_min) & (m <= hi_min)


@njit(cache=True)
def _bailout(o, h, l, c, ts, gaps, bail, k0s, sides, entries, dists, cost, swap, cut, delay):
    n = len(k0s); out = np.zeros((n, 8)); m = 0; busy = -1; N = len(o)
    for j in range(n):
        k0 = k0s[j] + delay
        if k0 <= busy or k0 >= N - 2:
            continue
        if ts[k0] >= cut:
            break
        sd = sides[j]; d = dists[j]
        entry = entries[j]
        if delay > 0:                                          # latency: fill at the later minute's open, if worse
            entry = max(entry, o[k0] + cost) if sd > 0 else min(entry, o[k0])
        stop = entry - d if sd > 0 else entry + d
        kx = N - 1; px = c[N - 1] if sd > 0 else c[N - 1] + cost
        for i in range(k0, N):
            if sd > 0:
                if l[i] <= stop:
                    px = stop if (o[i] > stop or i == k0) else o[i]; px = min(px, stop); kx = i; break
                if bail[i] and i > k0 and c[i] > entry:
                    px = c[i]; kx = i; break
            else:
                if h[i] + cost >= stop:
                    ao = o[i] + cost
                    px = stop if (ao < stop or i == k0) else ao; px = max(px, stop); kx = i; break
                if bail[i] and i > k0 and c[i] + cost < entry:
                    px = c[i] + cost; kx = i; break
        busy = kx
        skip = False
        for g in gaps:
            if k0 <= g < kx:
                skip = True; break
        if skip:
            continue
        r = (px - entry) / d if sd > 0 else (entry - px) / d
        nts = core.nights_held(ts[k0], ts[kx])
        fin = nts * swap / d
        out[m, 0] = ts[k0]; out[m, 1] = ts[kx]; out[m, 2] = sd; out[m, 3] = r - fin; out[m, 4] = d
        out[m, 5] = cost / d; out[m, 6] = nts; out[m, 7] = fin; m += 1
    return out[:m]


def bailout(stop_key, unit, ny_from="16:45", ny_to="16:55"):
    """Exit at the first minute inside the New York window when the trade is in profit; otherwise only the fixed
    stop. stop_key: the parameter holding the stop size; unit: 'pips' (x 0.0001, x 0.01 for JPY) or 'pct' (of entry)."""
    lo = int(ny_from[:2]) * 60 + int(ny_from[3:]); hi = int(ny_to[:2]) * 60 + int(ny_to[3:])
    cache = {}

    def run(M, B, C, p, cut=core.CUT, cost_mult=1.0, swap_mult=1.0, delay=0):
        if len(C["k0"]) == 0:
            return np.zeros((0, 8))
        if M.sym not in cache:
            cache[M.sym] = ny_window(M.ts.astype(np.int64), lo, hi)
        o = np.argsort(C["k0"], kind="stable")
        ent = C["entry"][o]
        if unit == "pips":
            pip = 0.01 if M.sym.endswith("JPY") else 0.0001
            d = np.full(len(o), float(p[stop_key]) * pip)
        else:
            d = ent * float(p[stop_key]) / 100.0
        res = _bailout(M.o, M.h, M.l, M.G.c, M.ts.astype(np.int64), M.gaps.astype(np.int64), cache[M.sym],
                       C["k0"][o].astype(np.int64), C["side"][o].astype(np.int64), ent.astype(np.float64), d.astype(np.float64),
                       M.cost, M.swap, cut if cut else 2 ** 62, int(delay))
        if cost_mult != 1.0 or swap_mult != 1.0:
            res = res.copy(); res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
        return res
    return run


def _next_arrow(o, h, l, c, ts, gaps, k0s, sides, stops, exk, cost, swap, cut, delay, blo, bhi):
    """Exit at the open of the minute after the next arrow (exk, sorted M1 indices), or at the protective stop."""
    return _exit_on(o, h, l, c, ts, gaps, k0s, sides, stops, exk, exk, cost, swap, cut, delay, blo, bhi)


@njit(cache=True)
def _exit_on(o, h, l, c, ts, gaps, k0s, sides, stops, exl, exs, cost, swap, cut, delay, blo, bhi):
    """Exit longs at the first index in exl after entry (shorts: exs), at that minute's open; or at the stop."""
    n = len(k0s); out = np.zeros((n, 8)); m = 0; busy = -1; busy_open = False; N = len(o)
    for j in range(n):
        k0 = k0s[j] + delay
        if k0 < busy or (k0 == busy and not busy_open) or k0 >= N - 2:
            continue
        if ts[k0] >= cut:
            break
        tod = ts[k0] % 86400
        if blo <= tod < bhi:
            continue
        sd = sides[j]; stop = stops[j]
        exk = exl if sd > 0 else exs
        ne = len(exk)
        entry = o[k0] + cost if sd > 0 else o[k0]
        d = entry - stop if sd > 0 else stop - entry
        if d <= 0:
            continue
        lo, hi = 0, ne                                           # first exit arrow strictly after the signal's entry
        while lo < hi:
            mid = (lo + hi) // 2
            if exk[mid] <= k0s[j]:
                lo = mid + 1
            else:
                hi = mid
        ke = exk[lo] if lo < ne else N - 1
        kx = ke; at_open = True
        px = o[ke] if sd > 0 else o[ke] + cost
        for i in range(k0, ke):
            if sd > 0:
                if l[i] <= stop:
                    px = o[i] if (i > k0 and o[i] < stop) else stop; kx = i; at_open = False; break
            else:
                if h[i] + cost >= stop:
                    px = o[i] + cost if (i > k0 and o[i] + cost > stop) else stop; kx = i; at_open = False; break
        busy = kx; busy_open = at_open
        skip = False
        for g in gaps:
            if k0 <= g < kx:
                skip = True; break
        if skip:
            continue
        r = (px - entry) / d if sd > 0 else (entry - px) / d
        nts = core.nights_held(ts[k0], ts[kx])
        fin = nts * swap / d
        out[m, 0] = ts[k0]; out[m, 1] = ts[kx]; out[m, 2] = sd; out[m, 3] = r - fin; out[m, 4] = d
        out[m, 5] = cost / d; out[m, 6] = nts; out[m, 7] = fin; m += 1
    return out[:m]


def next_arrow(arrow_bars):
    """Executor: hold until the next arrow (any colour change), exit at the next bar's open, or at the stop.
    arrow_bars(B, p) -> sorted bar indices of every arrow (all of them, not only the ones that were traded)."""
    def run(M, B, C, p, cut=core.CUT, cost_mult=1.0, swap_mult=1.0, delay=0):
        if len(C["k0"]) == 0:
            return np.zeros((0, 8))
        ab = np.asarray(arrow_bars(B, p), np.int64)
        ab = ab[ab < len(B["nxt"])]
        exk = np.sort(np.asarray(B["nxt"], np.int64)[ab])
        o = np.argsort(C["k0"], kind="stable")
        res = _exit_on(M.o, M.h, M.l, M.G.c, M.ts.astype(np.int64), M.gaps.astype(np.int64),
                       C["k0"][o].astype(np.int64), C["side"][o].astype(np.int64), C["stop"][o].astype(np.float64), exk, exk,
                       M.cost, M.swap, cut if cut else 2 ** 62, int(delay), core.BLOCK[0], core.BLOCK[1])
        if cost_mult != 1.0 or swap_mult != 1.0:
            res = res.copy(); res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
        return res
    return run


def exit_when(exit_bars):
    """Executor: exit at the next bar's open after the first closed bar where the exit condition holds (for longs and
    shorts separately), or at the stop. exit_bars(B, p) -> (bar indices where longs exit, bar indices where shorts exit)."""
    def run(M, B, C, p, cut=core.CUT, cost_mult=1.0, swap_mult=1.0, delay=0):
        if len(C["k0"]) == 0:
            return np.zeros((0, 8))
        nxt = np.asarray(B["nxt"], np.int64)
        xl, xs = exit_bars(B, p)
        xl = np.sort(nxt[np.asarray(xl, np.int64)]); xs = np.sort(nxt[np.asarray(xs, np.int64)])
        o = np.argsort(C["k0"], kind="stable")
        res = _exit_on(M.o, M.h, M.l, M.G.c, M.ts.astype(np.int64), M.gaps.astype(np.int64),
                       C["k0"][o].astype(np.int64), C["side"][o].astype(np.int64), C["stop"][o].astype(np.float64), xl, xs,
                       M.cost, M.swap, cut if cut else 2 ** 62, int(delay), core.BLOCK[0], core.BLOCK[1])
        if cost_mult != 1.0 or swap_mult != 1.0:
            res = res.copy(); res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
        return res
    return run
