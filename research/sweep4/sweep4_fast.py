"""Fast (numba) engine for the owner's pivot-sweep body-engulf range. Same rules as the reference sweep4_orders.py, which
is the specification; research/truth/tests/test_sweep4.py checks that the two agree trade for trade.

It is the body-engulf engine (research/body4/body4_fast.py) with these changes: every setup arrives with its own entry
level, stop and target (in R); no lookback, midpoint or breakeven rules; optional pivot trailing stop.

simulate(...) returns (rows, ambiguous minutes); one row per trade:
  0 t_in, 1 t_out, 2 side, 3 net R (after spread, commission, slippage and swaps), 4 risk (1R in price),
  5 cost R (round-trip cost / risk, for the lab's cost stress), 6 nights, 7 swap R, 8 setup index, 9 reason
  (1 stop, 2 target, 3 trailed stop, 4 time close, 5 stop in the fill minute), 10 entry, 11 exit, 12 first stop,
  13 target, 14 stop trailed (0/1), 15 ambiguous minute in the trade (0/1), 16 best open profit in R before the exit
Pivot trailing stop (trail): after the fill, each time a new pivot on the stop side is CONFIRMED (buy: a pivot low; sell: a
pivot high), and it lies between the current stop and the price, the stop moves to it from that minute.
"""

import numpy as np
from numba import njit

WEEK = 7 * 86400
FRI_CUT = 4 * 86400 + 20 * 3600 + 1800
SUN_OPEN = 6 * 86400 + 23 * 3600
BLOCK0, BLOCK1 = 20 * 3600 + 1800, 23 * 3600
MAXP = 64
REASON = {1: "stop", 2: "target", 3: "trailed stop", 4: "time close", 5: "stop in the fill minute"}


@njit(cache=True)
def _wsec(t):
    return (t - 345600) % WEEK


@njit(cache=True)
def _weekend(t):
    s = _wsec(t)
    return FRI_CUT <= s < SUN_OPEN


@njit(cache=True)
def _fri_cut(t):
    s = _wsec(t)
    base = t - s
    return base + FRI_CUT if s < FRI_CUT else base + WEEK + FRI_CUT


@njit(cache=True)
def _day_cut(t):
    """The next 20:30 UTC at or after t (the daily close before the rollover; used by the safe-window mode)."""
    s = t % 86400
    return t - s + 73800 if s < 73800 else t - s + 86400 + 73800


@njit(cache=True)
def _cut(t, day_close):
    return _day_cut(t) if day_close else _fri_cut(t)


@njit(cache=True)
def _nights(t_in, t_out):
    n = 0
    for d in range(t_in // 86400, t_out // 86400 + 1):
        rt = d * 86400 + 79200
        if t_in < rt <= t_out:
            wd = (d + 3) % 7
            if wd < 5:
                n += 3 if wd == 2 else 1
    return n


@njit(cache=True)
def _record(out, m, gaps, xj, xs, xe, xst0, xr, xtp, xmv, xi, xt, ci, ct, px, why, comm, swap, cost, xamb, xmfe):
    for g in gaps:
        if xi < g <= ci:
            return m                                   # the trade spans a hole in the data: dropped
    gross = (px - xe) / xr * xs
    nts = _nights(xt, ct)
    fin = nts * swap / xr
    out[m, 0] = xt; out[m, 1] = ct; out[m, 2] = xs; out[m, 3] = gross - comm / xr - fin; out[m, 4] = xr
    out[m, 5] = cost / xr; out[m, 6] = nts; out[m, 7] = fin; out[m, 8] = xj; out[m, 9] = why; out[m, 10] = xe
    out[m, 11] = px; out[m, 12] = xst0; out[m, 13] = xtp; out[m, 14] = 1.0 if xmv else 0.0; out[m, 15] = xamb
    out[m, 16] = xmfe
    return m + 1


@njit(cache=True)
def simulate(ts, o, h, l, c, gaps, start, tconf, side, lev, stop, tgt, wid, spread, comm, slip, swap, cut, allow, day_close,
             trail, eh_t, eh_p, el_t, el_p):
    N = len(ts); P = len(start)
    out = np.zeros((P + 1, 17)); m = 0
    cost = spread + comm + slip
    pp = np.zeros(MAXP, np.int64); ps = np.zeros(MAXP, np.int64)
    plev = np.zeros(MAXP); pstop = np.zeros(MAXP); ptp = np.zeros(MAXP); pwid = np.zeros(MAXP)
    npend = 0; pcut = 0
    pos = False; xj = 0; xs = 0; xe = 0.0; xst = 0.0; xst0 = 0.0; xr = 0.0; xtp = 0.0; xbe = 0.0
    xmv = False; xi = 0; xt = 0; xcut = 0; xamb = 0; xmfe = 0.0; xq = 0
    amb = 0
    pj = 0
    i = start[0] if P > 0 else N
    while i < N:
        t = ts[i]
        # 1. Friday cutoff (the data usually jumps from Friday evening to Sunday night)
        if pos and t >= xcut:
            cpx = c[i - 1] - slip if xs > 0 else c[i - 1] + spread + slip
            m = _record(out, m, gaps, xj, xs, xe, xst0, xr, xtp, xmv, xi, xt, i - 1, xcut, cpx, 4, comm, swap, cost, xamb, xmfe)
            pos = False
        if npend > 0 and t >= pcut:
            npend = 0
        if t >= cut:
            npend = 0
            if not pos:
                break
        # 2. new setups that became tradeable
        while pj < P and start[pj] <= i:
            j = pj; pj += 1
            if t >= cut:
                continue
            s = side[j]
            if allow[j] == 0:
                continue
            if _weekend(tconf[j]) or _weekend(t):
                continue
            if pos:
                continue
            w = wid[j]
            lvl = lev[j]
            if s > 0 and o[i] + spread <= lvl:
                continue
            if s < 0 and o[i] >= lvl:
                continue
            stp = stop[j]
            rk = abs(lvl - stp)
            if rk <= cost:
                continue
            if npend > 0 and ps[0] != s:
                mx = pwid[0]
                for q in range(1, npend):
                    if pwid[q] > mx:
                        mx = pwid[q]
                if w > mx:
                    npend = 0
                else:
                    continue
            if npend < MAXP:
                pp[npend] = j; ps[npend] = s; plev[npend] = lvl; pstop[npend] = stp
                ptp[npend] = lvl + s * tgt[j] * rk; pwid[npend] = w
                npend += 1
                pcut = _cut(t, day_close)
        # 3. pending orders
        if npend > 0 and not pos:
            sod = t % 86400
            blocked = BLOCK0 <= sod < BLOCK1
            best = -1
            for q in range(npend):                     # first pass: which order fills (no data is moved yet)
                s = ps[q]
                hit_tp = (h[i] >= ptp[q]) if s > 0 else (l[i] + spread <= ptp[q])
                hit = (not blocked) and ((l[i] + spread <= plev[q]) if s > 0 else (h[i] >= plev[q]))
                if hit_tp:
                    if hit:
                        amb += 1
                elif hit:
                    if best < 0 or (s > 0 and plev[q] > plev[best]) or (s < 0 and plev[q] < plev[best]):
                        best = q
            if best >= 0:
                s = ps[best]
                px = min(plev[best], o[i] + spread) if s > 0 else max(plev[best], o[i])     # a gap fills at the open
                # stop, target and breakeven level are fixed prices set with the order; 1R = planned entry to stop
                pos = True; xj = pp[best]; xs = s; xe = px; xst = pstop[best]; xst0 = xst; xr = abs(plev[best] - xst)
                xtp = ptp[best]; xmv = False; xi = i; xt = t; xcut = _cut(t, day_close)
                xamb = 0; xmfe = 0.0
                xq = np.searchsorted(el_t if s > 0 else eh_t, t, side="right") if trail else 0
                npend = 0                              # every other pending order is removed
                if (l[i] <= xst) if s > 0 else (h[i] + spread >= xst):
                    amb += 1; xamb = 1
                    cpx = (min(xst, o[i]) - slip) if s > 0 else (max(xst, o[i] + spread) + slip)
                    m = _record(out, m, gaps, xj, xs, xe, xst0, xr, xtp, xmv, xi, xt, i, t, cpx, 5, comm, swap, cost, xamb, xmfe)
                    pos = False
            else:
                k2 = 0                                 # second pass: drop the orders whose target came first
                for q in range(npend):
                    s = ps[q]
                    hit_tp = (h[i] >= ptp[q]) if s > 0 else (l[i] + spread <= ptp[q])
                    if hit_tp:
                        continue
                    pp[k2] = pp[q]; ps[k2] = ps[q]; plev[k2] = plev[q]; pstop[k2] = pstop[q]; ptp[k2] = ptp[q]
                    pwid[k2] = pwid[q]; k2 += 1
                npend = k2
        # 4. open trade, from the minute after the fill
        elif pos and i > xi:
            s = xs
            if trail:                                  # pivots confirmed since the last minute: the stop follows them
                if s > 0:
                    while xq < len(el_t) and el_t[xq] <= t:
                        if xst < el_p[xq] < o[i]:
                            xst = el_p[xq]; xmv = True
                        xq += 1
                else:
                    while xq < len(eh_t) and eh_t[xq] <= t:
                        if o[i] + spread < eh_p[xq] < xst:
                            xst = eh_p[xq]; xmv = True
                        xq += 1
            hit_sl = (l[i] <= xst) if s > 0 else (h[i] + spread >= xst)
            hit_tp = (h[i] >= xtp) if s > 0 else (l[i] + spread <= xtp)
            if hit_sl:
                if hit_tp:
                    amb += 1; xamb = 1
                if s > 0:
                    cpx = (o[i] if o[i] < xst else xst) - slip
                else:
                    cpx = (o[i] + spread if o[i] + spread > xst else xst) + slip
                m = _record(out, m, gaps, xj, xs, xe, xst0, xr, xtp, xmv, xi, xt, i, t, cpx, 3 if xmv else 1, comm, swap, cost, xamb, xmfe)
                pos = False
            elif hit_tp:
                cpx = (o[i] if o[i] > xtp else xtp) if s > 0 else (o[i] + spread if o[i] + spread < xtp else xtp)
                xmfe = max(xmfe, (cpx - xe) / xr * s)
                m = _record(out, m, gaps, xj, xs, xe, xst0, xr, xtp, xmv, xi, xt, i, t, cpx, 2, comm, swap, cost, xamb, xmfe)
                pos = False
            else:
                run_ = (h[i] - xe) / xr if s > 0 else (xe - (l[i] + spread)) / xr
                if run_ > xmfe:
                    xmfe = run_
        # 5. next minute (jump ahead when nothing is open or pending)
        i += 1
        if not pos and npend == 0:
            if pj >= P:
                break
            if start[pj] > i:
                i = start[pj]
    return out[:m], amb


def run(M1, S, costs, cut=2 ** 62, delay=0, gaps=None, allow=None, day_close=False, trail=False, conf_hi=None, conf_lo=None):
    """M1 = dict(ts, o, h, l, c); S = dict of per-setup arrays: t_conf, side, level, stop, tgt (R), width;
    costs = dict(spread, commission, slippage, swap); conf_hi / conf_lo = (times, prices) of pivot confirmations (trail)."""
    ts = np.asarray(M1["ts"], np.int64)
    start = np.searchsorted(ts, np.asarray(S["t_conf"], np.int64) + 60 * int(delay)).astype(np.int64)
    e = (np.zeros(0, np.int64), np.zeros(0))
    eh, el = (conf_hi or e), (conf_lo or e)
    return simulate(ts, np.asarray(M1["o"], float), np.asarray(M1["h"], float), np.asarray(M1["l"], float),
                    np.asarray(M1["c"], float), np.asarray(gaps if gaps is not None else [], np.int64), start,
                    np.asarray(S["t_conf"], np.int64), np.asarray(S["side"], np.int64), np.asarray(S["level"], float),
                    np.asarray(S["stop"], float), np.asarray(S["tgt"], float), np.asarray(S["width"], float),
                    float(costs["spread"]), float(costs["commission"]), float(costs["slippage"]), float(costs.get("swap", 0.0)),
                    int(cut), np.asarray(allow if allow is not None else np.ones(len(start)), np.int64), bool(day_close),
                    bool(trail), np.asarray(eh[0], np.int64), np.asarray(eh[1], float), np.asarray(el[0], np.int64),
                    np.asarray(el[1], float))
