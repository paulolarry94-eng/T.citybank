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
