"""Daily-bar position engine for the repo funnel (research/repofunnel/PREREG.md, sections A-D).

Bars: the lab's D1 bars with the Sunday-evening stub merged into Monday ("merged bars").
Indicators: Pine-equivalent (Wilder RMA for ATR/RSI/DMI, Pine EMA seeded with the first value, Pine SAR).
Fills (minute resolution, the lab's fill law): decisions at a merged bar's close; market orders fill at the open of the
first minute after it, deferred out of the 20:30-23:00 UTC rollover block; stop and limit orders are checked minute by
minute; a stop and a limit in the same minute -> the stop; a gap fills at the worse open (stops) or the better open
(limits). Longs pay the ask (bid + all-in cost) on entry, shorts pay it on exit.

One position per market. Pyramid units and partial exits belong to the position, and each position is ONE trade row in
the lab's format [t_in, t_out, side, net R, R unit (price), cost R, nights, financing R]. A rule works in "view" space:
prices multiplied by the side (+1 long, -1 short) with highs and lows swapped, so every rule is written once, for longs.
"""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
for _p in (ROOT, os.path.join(ROOT, "northstar")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import core

WARMUP = 260                      # merged bars without entries (indicator warm-up)
BLO, BHI = core.BLOCK             # rollover block, seconds of the UTC day


# ----------------------------------------------------------------------------- merged daily bars
def merge_daily(B):
    """Fold weekend stub bars (bar start on Saturday or Sunday, UTC) into the next bar.
    Returns dict: t, o, h, l, c (merged OHLC), first, nxt (minute range), last_b (lab bar index that ends the merged
    bar: signals refer to it), day (UTC day number of that lab bar), wd (its weekday, Monday = 0)."""
    t = np.asarray(B["t"], np.int64)
    n = len(t)
    wd = ((t // 86400) + 3) % 7
    first = np.asarray(B["first"], np.int64); nxt = np.asarray(B["nxt"], np.int64)
    grp = np.zeros(n, np.int64); g = 0
    for i in range(n):
        grp[i] = g
        if not (wd[i] >= 5 and i + 1 < n and t[i + 1] - t[i] <= 3 * 86400):
            g += 1
    starts = np.r_[0, np.flatnonzero(np.diff(grp)) + 1]
    ends = np.r_[starts[1:], n] - 1
    o = np.asarray(B["o"], float); h = np.asarray(B["h"], float); l = np.asarray(B["l"], float); c = np.asarray(B["c"], float)
    D = dict(t=t[starts], o=o[starts], h=np.maximum.reduceat(h, starts), l=np.minimum.reduceat(l, starts), c=c[ends],
             first=first[starts], nxt=nxt[ends], last_b=ends.astype(np.int64))
    D["day"] = t[ends] // 86400
    D["wd"] = ((D["day"] + 3) % 7).astype(np.int64)
    D["n"] = len(starts)
    return D


# ----------------------------------------------------------------------------- Pine-equivalent indicators
def sma(x, n):
    return pd.Series(x).rolling(n, min_periods=n).mean().to_numpy()


def ema(x, n):
    """Pine ta.ema: seeded with the first value."""
    x = np.asarray(x, float); out = np.empty_like(x); a = 2.0 / (n + 1)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def rma(x, n):
    """Pine ta.rma: SMA of the first n values, then Wilder smoothing (NaN-aware start)."""
    x = np.asarray(x, float); out = np.full_like(x, np.nan)
    ok = np.flatnonzero(np.isfinite(x))
    if len(ok) < n:
        return out
    s = ok[0]
    if s + n > len(x):
        return out
    out[s + n - 1] = np.mean(x[s:s + n])
    a = 1.0 / n
    for i in range(s + n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def true_range(h, l, c):
    pc = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    tr[0] = h[0] - l[0]
    return tr


def atr(h, l, c, n):
    return rma(true_range(h, l, c), n)


def rsi(c, n):
    ch = np.r_[np.nan, np.diff(c)]
    up = rma(np.maximum(ch, 0.0), n); dn = rma(np.maximum(-ch, 0.0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100 - 100 / (1 + up / dn)
    r = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, r))
    r[~(np.isfinite(up) & np.isfinite(dn))] = np.nan
    return r


def dmi(h, l, c, n, adx_n=None):
    """Pine ta.dmi(n, adx_n) -> (+DI, -DI, ADX)."""
    adx_n = adx_n or n
    up = np.r_[np.nan, np.diff(h)]; down = -np.r_[np.nan, np.diff(l)]
    pdm = np.where((up > down) & (up > 0), up, 0.0); mdm = np.where((down > up) & (down > 0), down, 0.0)
    pdm[0] = np.nan; mdm[0] = np.nan
    tr = rma(true_range(h, l, c), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        plus = 100 * rma(pdm, n) / tr; minus = 100 * rma(mdm, n) / tr
        s = plus + minus
        adx = 100 * rma(np.abs(plus - minus) / np.where(s == 0, 1, s), adx_n)
    return plus, minus, adx


def highest(x, n):
    return pd.Series(x).rolling(n, min_periods=n).max().to_numpy()


def lowest(x, n):
    return pd.Series(x).rolling(n, min_periods=n).min().to_numpy()


def prev(x, k=1):
    x = np.asarray(x, float)
    return np.r_[np.full(k, np.nan), x[:-k]] if k > 0 else x


def sar(h, l, c, start, inc, mx):
    """Pine ta.sar (reference implementation)."""
    n = len(c); out = np.full(n, np.nan)
    result = maxmin = acc = np.nan; below = None
    for i in range(1, n):
        first_trend = False
        if i == 1:
            if c[1] > c[0]:
                below = True; maxmin = h[1]; result = l[0]
            else:
                below = False; maxmin = l[1]; result = h[0]
            first_trend = True; acc = start
        result = result + acc * (maxmin - result)
        if below:
            if result > l[i]:
                first_trend = True; below = False; result = max(h[i], maxmin); maxmin = l[i]; acc = start
        else:
            if result < h[i]:
                first_trend = True; below = True; result = min(l[i], maxmin); maxmin = h[i]; acc = start
        if not first_trend:
            if below:
                if h[i] > maxmin:
                    maxmin = h[i]; acc = min(acc + inc, mx)
            else:
                if l[i] < maxmin:
                    maxmin = l[i]; acc = min(acc + inc, mx)
        if below:
            result = min(result, l[i - 1])
            if i > 1:
                result = min(result, l[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return out


def fractal_low_last(l):
    """Value of the most recent confirmed 3-bar fractal low as known at each bar's close (the fractal at k is
    confirmed when bar k+1 closes)."""
    l = np.asarray(l, float); n = len(l); out = np.full(n, np.nan); last = np.nan
    for u in range(2, n):
        k = u - 1
        if l[k] < l[k - 1] and l[k] < l[u]:
            last = l[k]
        out[u] = last
    return out


def fractal_lows(l):
    """Indices k of confirmed 3-bar fractal lows (confirmed at k+1)."""
    l = np.asarray(l, float)
    k = np.arange(1, len(l) - 1)
    return k[(l[k] < l[k - 1]) & (l[k] < l[k + 1])]


def fractal_highs(h):
    h = np.asarray(h, float)
    k = np.arange(1, len(h) - 1)
    return k[(h[k] > h[k - 1]) & (h[k] > h[k + 1])]


class View:
    """Prices seen from one side: s = +1 as is; s = -1 negated with highs and lows swapped. Indicator cache."""

    def __init__(self, D, s):
        self.s = s; self.D = D
        if s > 0:
            self.o, self.h, self.l, self.c = D["o"], D["h"], D["l"], D["c"]
        else:
            self.o, self.h, self.l, self.c = -D["o"], -D["l"], -D["h"], -D["c"]
        self._c = {}

    def get(self, key, fn):
        if key not in self._c:
            self._c[key] = fn()
        return self._c[key]

    def atr(self, n):
        return self.get(("atr", n), lambda: atr(self.h, self.l, self.c, n))

    def sma(self, n):
        return self.get(("sma", n), lambda: sma(self.c, n))

    def ema(self, n):
        return self.get(("ema", n), lambda: ema(self.c, n))

    def rsi(self, n):
        return self.get(("rsi", n), lambda: rsi(self.c, n))

    def dmi(self, n):
        return self.get(("dmi", n), lambda: dmi(self.h, self.l, self.c, n))

    def hh(self, n):
        return self.get(("hh", n), lambda: highest(self.h, n))

    def ll(self, n):
        return self.get(("ll", n), lambda: lowest(self.l, n))

    def hc(self, n):
        return self.get(("hc", n), lambda: highest(self.c, n))

    def swing_low(self):
        return self.get(("swl",), lambda: fractal_low_last(self.l))


# ----------------------------------------------------------------------------- the position
class Position:
    def __init__(self, s, u0):
        self.s = s; self.u0 = u0
        self.units = []                # [weight remaining, real fill price, fill minute]
        self.bars = 0                  # Pine barsInPos (incremented at each close while open)
        self.stop_v = None             # active stop level (view) for the next bar
        self.limits = []               # active limit orders: [view level, weight or None (= all)]
        self.exit_all = False; self.exit_w = 0.0; self.add_w = 0.0; self.add_meta = None
        self.realized = 0.0; self.nights_w = 0.0; self.cost_w = 0.0
        self.k_first = None; self.k_last = None
        self.n_limit_fills = 0
        self.st = {}                   # rule state

    def weight(self):
        return sum(x[0] for x in self.units)

    def avg_v(self):
        w = self.weight()
        return self.s * sum(x[0] * x[1] for x in self.units) / w if w > 0 else np.nan


class Market:
    """Minute data and costs of one lab market (core.Mkt) plus its merged daily bars."""

    def __init__(self, M, B):
        self.M = M; self.sym = M.sym
        self.o = np.asarray(M.o, float); self.h = np.asarray(M.h, float); self.l = np.asarray(M.l, float)
        self.c = np.asarray(M.G.c, float); self.ts = np.asarray(M.ts, np.int64)
        self.gaps = np.asarray(M.gaps, np.int64); self.cost = float(M.cost); self.swap = float(M.swap)
        self.D = merge_daily(B)
        self.views = {s: View(self.D, s) for s in (1, -1)}


def _fill_minute(mk, k, k_end):
    """First minute >= k (and < k_end) outside the rollover block, or -1."""
    ts = mk.ts
    while k < k_end:
        tod = ts[k] % 86400
        if not (BLO <= tod < BHI):
            return k
        k += 1
    return -1


def _mkt_price(mk, k, side, opening):
    """Market fill at minute k's open: buying pays the ask (bid + cost)."""
    buy = (side > 0) == opening
    return mk.o[k] + mk.cost if buy else mk.o[k]


def _close_w(mk, pos, w, px, k):
    """Close weight w (first in, first out) at real price px in minute k. Returns weight closed."""
    left = w; done = 0.0
    while left > 1e-12 and pos.units:
        u = pos.units[0]
        q = min(u[0], left)
        pos.realized += pos.s * (px - u[1]) * q
        pos.nights_w += q * core.nights_held(int(mk.ts[u[2]]), int(mk.ts[k]))
        u[0] -= q; left -= q; done += q
        if u[0] <= 1e-12:
            pos.units.pop(0)
    pos.k_last = k
    return done


def _open_unit(mk, pos, w, k):
    px = _mkt_price(mk, k, pos.s, True)
    pos.units.append([w, px, k]); pos.cost_w += w
    if pos.k_first is None:
        pos.k_first = k
    return px


def _scan(mk, pos, k0, k1):
    """Intrabar: stop and limit orders from minute k0 to k1 (exclusive). Mutates pos; returns True if flat."""
    if k0 >= k1 or not pos.units:
        return not pos.units
    s = pos.s; cost = mk.cost
    ks = k1
    if pos.stop_v is not None and np.isfinite(pos.stop_v):
        S = s * pos.stop_v
        hit = (mk.l[k0:k1] <= S) if s > 0 else (mk.h[k0:k1] + cost >= S)
        j = int(np.argmax(hit)) if hit.any() else -1
        if j >= 0:
            ks = k0 + j
    ev = []
    for i, (lv, w) in enumerate(pos.limits):
        T = s * lv
        hit = (mk.h[k0:ks] >= T) if s > 0 else (mk.l[k0:ks] + cost <= T)
        if hit.any():
            ev.append((k0 + int(np.argmax(hit)), lv, i, lv, w))
    ev.sort(key=lambda e: (e[0], e[1]))
    filled = set()
    for k, _, i, lv, w in ev:
        if not pos.units:
            break
        T = s * lv
        px = max(T, mk.o[k]) if s > 0 else min(T, mk.o[k] + cost)
        _close_w(mk, pos, pos.weight() if w is None else w, px, k)
        pos.n_limit_fills += 1; filled.add(i)
    if filled:
        pos.limits = [x for i, x in enumerate(pos.limits) if i not in filled]
    if pos.units and ks < k1:
        S = s * pos.stop_v
        px = min(S, mk.o[ks]) if s > 0 else max(S, mk.o[ks] + cost)
        _close_w(mk, pos, pos.weight(), px, ks)
    return not pos.units


def _row(mk, pos):
    d = pos.st["d"]
    if pos.k_first is None or d <= 0:
        return None
    g = mk.gaps
    j = np.searchsorted(g, pos.k_first)
    if j < len(g) and g[j] < pos.k_last:
        return None                                    # spans a hole in the data: discarded, never scored
    fin = pos.nights_w * mk.swap / d
    nights = pos.nights_w / max(pos.cost_w, 1e-12)
    return [mk.ts[pos.k_first], mk.ts[pos.k_last], pos.s, pos.realized / d - fin, d, pos.cost_w * mk.cost / d, nights, fin]


def simulate(mk, rule, sides=(1, -1), cut=core.CUT, delay=0, warmup=WARMUP):
    """Run one rule on one market. rule (see Rule): prepare(mk, views), entry(u, s) -> dict|None,
    on_fill(mk, pos, u, sig) -> bool (False cancels the entry), on_add(mk, pos, u), on_close(mk, pos, u).
    Returns trade rows (lab format)."""
    D = mk.D; n = D["n"]
    views = mk.views
    rule.prepare(mk, views)
    rows = []; pos = None; pend = None; entries_on = True
    cut = cut if cut else 2 ** 62

    def finish(p):
        r = _row(mk, p)
        if r is not None:
            rows.append(r)

    for u in range(n):
        k_first, k_end = int(D["first"][u]), int(D["nxt"][u])
        k_scan = k_first
        # 1. market orders at the open of bar u (deferred out of the rollover block; stops stay live meanwhile)
        mo_pos = pos is not None and (pos.exit_all or pos.exit_w > 0 or pos.add_w > 0)
        if pend is not None or mo_pos:
            k = _fill_minute(mk, k_first + delay, k_end)
            if k >= 0:
                if pos is not None and k > k_first and _scan(mk, pos, k_first, k):
                    finish(pos); pos = None
                k_scan = k
                if pos is not None and (pos.exit_all or pos.exit_w > 0):
                    w = pos.weight() if pos.exit_all else min(pos.exit_w, pos.weight())
                    _close_w(mk, pos, w, _mkt_price(mk, k, pos.s, False), k)
                    pos.exit_all = False; pos.exit_w = 0.0
                    if not pos.units:
                        finish(pos); pos = None
                if pos is not None and pos.add_w > 0:
                    _open_unit(mk, pos, pos.add_w, k)
                    pos.add_w = 0.0
                    rule.on_add(mk, pos, u)
                if pos is None and pend is not None:
                    s, sig = pend
                    if mk.ts[k] >= cut:
                        entries_on = False
                    else:
                        p = Position(s, u)
                        _open_unit(mk, p, sig.get("w", 1.0), k)
                        if rule.on_fill(mk, p, u, sig):
                            pos = p
                    pend = None
        # 2. stops and limits during bar u
        if pos is not None and _scan(mk, pos, k_scan, k_end):
            finish(pos); pos = None
        # 3. the close of bar u
        if pos is not None:
            pos.bars += 1
            rule.on_close(mk, pos, u)
        elif pend is None:
            if not entries_on:
                break
            if u >= warmup:
                for s in sides:
                    sig = rule.entry(u, s)
                    if sig:
                        pend = (s, sig)
                        break
    if pos is not None and pos.units:                    # still open at the end of the data: close at the last price
        k = len(mk.ts) - 1
        px = mk.c[k] if pos.s > 0 else mk.c[k] + mk.cost
        _close_w(mk, pos, pos.weight(), px, k)
        finish(pos)
    return np.asarray(rows, float).reshape(-1, 8)


class Rule:
    """Base rule: override what you need."""

    def prepare(self, mk, views):
        self.V = views; self.mk = mk

    def entry(self, u, s):
        return None

    def on_fill(self, mk, pos, u, sig):
        return True

    def on_add(self, mk, pos, u):
        pass

    def on_close(self, mk, pos, u):
        pass


# ----------------------------------------------------------------------------- lab glue
_MK = {}


def market_for(M, B):
    key = (M.sym, len(B["t"]), int(B["t"][-1]))
    if key not in _MK:
        _MK.clear(); _MK[key] = Market(M, B)
    return _MK[key]


def executor(make_rule, sides_of):
    """Lab EXECUTOR: make_rule(p, sym) -> rule; sides_of(p) -> tuple of sides."""
    def run(M, B, C, p, cut=core.CUT, cost_mult=1.0, swap_mult=1.0, delay=0):
        mk = market_for(M, B)
        res = simulate(mk, make_rule(p, M.sym), sides_of(p), cut=cut, delay=int(delay))
        if len(res) and (cost_mult != 1.0 or swap_mult != 1.0):
            res = res.copy(); res[:, 3] -= (cost_mult - 1.0) * res[:, 5] + (swap_mult - 1.0) * res[:, 7]
        return res
    return run


def signal_rows(B, make_rule, p, sym, sides):
    """Raw entry signals for the lab's look-ahead check and candidate list: (lab bar, side, indicative stop)."""
    D = merge_daily(B)
    views = {s: View(D, s) for s in (1, -1)}
    rule = make_rule(p, sym)
    rule.prepare(None, views)
    rows = []
    for u in range(WARMUP, D["n"]):
        for s in sides:
            sig = rule.entry(u, s)
            if sig:
                rows.append((int(D["last_b"][u]), int(s), float(s * sig.get("ref_stop_v", np.nan))))
                break
    return rows
