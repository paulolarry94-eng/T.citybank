"""North Star execution core: bars, bias, pending limit orders, the serial trade book with financing
and the rollover session block. Pattern modules (patterns.py) only produce candidates.

All rules are those of PREREGISTRATION.md section 1.
"""
import os, sys
import numpy as np
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "orb"))
import engine as E, gold_lab as GL
from execution import manage

MINUTES = {"M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
SWAP = {"XAUUSD": 0.20, "EURUSD": 0.00006, "GBPUSD": 0.00006, "USDJPY": 0.008}     # per night held, price units
BLOCK = (20 * 3600 + 1800, 23 * 3600)        # 20:30-23:00 UTC: no entries, no pending fills
TIME_STOP = 50
CUT = 1672531200                             # 2023-01-01: grids never see fills from here on


class Mkt:
    def __init__(self, sym):
        self.G = GL.Market(sym)
        self.sym, self.cost, self.swap = sym, self.G.cost, SWAP[sym]
        self.o, self.h, self.l, self.ts, self.gaps = self.G.o, self.G.h, self.G.l, self.G.ts, self.G.gaps
        self._b = {}
        H4 = self.bars("H4")
        self._h4_close_t = H4["t"] + 240 * 60
        self._h4_bias = np.sign(H4["c"] - E.ema(H4["c"], 50))
        self._h4_bias[~np.isfinite(self._h4_bias)] = 0

    def bars(self, tf):
        if tf in self._b:
            return self._b[tf]
        m = MINUTES[tf]
        bt, bo, bh, bl, bc, nxt = E.resample(self.G.ts, self.G.o, self.G.h, self.G.l, self.G.c, m, 120 if m >= 240 else 0)
        nxt = nxt.astype(np.int64)
        B = dict(t=bt.astype(np.int64), o=bo, h=bh, l=bl, c=bc, nxt=nxt, first=np.r_[0, nxt[:-1]].astype(np.int64), minutes=m)
        B["atr"] = np.nan_to_num(E.atr_sma(bh, bl, bc, 14), nan=0.0)
        self._b[tf] = B
        return B

    def bias_at(self, t):
        """H4 EMA50 bias from the last H4 bar CLOSED at or before time(s) t."""
        k = np.searchsorted(self._h4_close_t, t, side="right") - 1
        return np.where(k >= 0, self._h4_bias[np.clip(k, 0, None)], 0).astype(np.int64)


@njit(cache=True)
def in_block(t, lo, hi):
    s = t % 86400
    return lo <= s < hi


@njit(cache=True)
def limit_scan(o, h, l, ts, bfirst, bnxt, bc, start, end, side, level, cancel, cost, eps, blo, bhi):
    """Pending limit order from bar `start` to bar `end` (exclusive). Fills minute by minute when price
    trades through `level` by eps (never in the rollover block); after each unfilled bar, a close beyond
    `cancel` kills it. Returns (fill minute, fill price, fill bar) or (-1, 0, -1)."""
    for u in range(start, min(end, len(bfirst))):
        for k in range(bfirst[u], bnxt[u]):
            if in_block(ts[k], blo, bhi):
                continue
            if side > 0:
                if l[k] + cost <= level - eps:
                    return k, min(level, o[k] + cost), u
            else:
                if h[k] >= level + eps:
                    return k, max(level, o[k]), u
        if (side > 0 and bc[u] < cancel) or (side < 0 and bc[u] > cancel):
            return -1, 0.0, -1
    return -1, 0.0, -1


@njit(cache=True)
def nights_held(t_in, t_out):
    """22:00 UTC rollovers between entry and exit on weekdays; Wednesday counts three times."""
    n = 0
    d0 = t_in // 86400
    d1 = t_out // 86400
    for d in range(d0, d1 + 1):
        rt = d * 86400 + 79200
        if t_in < rt <= t_out:
            wd = (d + 3) % 7
            if wd < 5:
                n += 3 if wd == 2 else 1
    return n


@njit(cache=True)
def run_book(o, h, l, ts, bnxt, bh, bl, batr, k0s, sides, entries, stops, jbs, sigs, caps, cost, tgt, trail,
             tstop, gaps, swap, cut, blo, bhi, delay):
    """Serial book over candidates sorted by k0. entries[i] < 0 = market order at the open of minute
    k0 (+delay); otherwise a limit fill at that price in minute k0. Returns rows: t_in, t_out, side,
    net R (costs + financing), stop distance, cost in R, nights, financing in R."""
    n = len(k0s); out = np.zeros((n, 8)); m = 0; busy = -1; g = 0; nb = len(bnxt)
    for c in range(n):
        k0 = k0s[c]
        mkt = entries[c] < 0
        if mkt:
            k0 = k0 + delay
        if k0 <= busy or k0 >= len(o) - 2:
            continue
        if ts[k0] >= cut:
            break
        if mkt and in_block(ts[k0], blo, bhi):
            continue
        sd = sides[c]
        entry = (o[k0] + cost if sd > 0 else o[k0]) if mkt else entries[c]
        stop = stops[c]
        dist = (entry - stop) if sd > 0 else (stop - entry)
        a = batr[sigs[c]]
        if dist < 3 * cost or dist <= 0 or (a > 0 and dist > caps[c] * a):
            continue
        kend = bnxt[min(sigs[c] + tstop, nb - 1)]
        if kend >= len(o):
            kend = len(o) - 1
        if kend <= k0:
            continue
        while g < len(gaps) and gaps[g] < k0:
            g += 1
        if g < len(gaps) and gaps[g] < kend:
            continue
        kx, r, why, mfe = manage(o, h, l, k0, kend, sd, entry, stop, dist, cost, tgt, 0.0, 0.0, 1.0,
                                 trail, 22, bh, bl, bnxt, batr, jbs[c], mkt)
        nts = nights_held(ts[k0], ts[kx])
        fin = nts * swap / dist
        out[m, 0] = ts[k0]; out[m, 1] = ts[kx]; out[m, 2] = sd; out[m, 3] = r - fin; out[m, 4] = dist
        out[m, 5] = cost / dist; out[m, 6] = nts; out[m, 7] = fin
        m += 1; busy = kx
    return out[:m]


def execute(M, B, cands, tgt, trail, cut=CUT, cost_mult=1.0, swap_mult=1.0, delay=0, bias=False, keep=None):
    """cands: dict of arrays k0, side, entry, stop, jb, sig, cap, dec_t (decision time, for the bias)."""
    if len(cands["k0"]) == 0:
        return np.zeros((0, 8))
    sel = np.ones(len(cands["k0"]), bool)
    if bias:
        sel &= M.bias_at(cands["dec_t"]) == cands["side"]
    if keep is not None:
        sel &= keep
    o = np.argsort(cands["k0"][sel], kind="stable")
    f = lambda k, t=np.float64: np.ascontiguousarray(cands[k][sel][o], dtype=t)
    res = run_book(M.o, M.h, M.l, M.ts, B["nxt"], B["h"], B["l"], B["atr"], f("k0", np.int64), f("side", np.int64),
                   f("entry"), f("stop"), f("jb", np.int64), f("sig", np.int64), f("cap"), M.cost, float(tgt), float(trail),
                   TIME_STOP, M.gaps, M.swap, cut if cut else 2 ** 62, BLOCK[0], BLOCK[1], int(delay))
    if cost_mult != 1.0 or swap_mult != 1.0:          # stress: exact extra cost and financing per trade, in R
        res = res.copy()
        res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
    return res
