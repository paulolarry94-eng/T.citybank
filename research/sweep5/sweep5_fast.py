"""Fast (numba) engine for pivot-sweep v2; same rules as the reference sweep5_orders.py (the specification), checked trade
for trade in research/truth/tests/test_sweep5.py.
Rows: 0 t_in, 1 t_out, 2 side, 3 net R, 4 risk, 5 cost R, 6 nights, 7 swap R, 8 setup index, 9 reason (1 stop, 2 target,
3 breakeven stop after TP1, 4 time close, 5 stop in the fill minute, 6 time close after TP1), 10 entry, 11 exit,
12 stop, 13 TP1, 14 TP2, 15 TP1 taken (0/1), 16 best open R before the exit.
exit_mode: 0 partial (60% at TP1, rest to TP2 with the stop at entry +/- (spread + commission)), 1 all at TP1, 2 all at TP2,
3 a fixed target tgt_r R from the level (no pivots needed); be_frac > 0 moves the stop to the entry once price has covered
be_frac of the distance from the level to the final target (from the next minute; 2026-11-12, research/sweep6).
"""
import os, sys
import numpy as np
from numba import njit

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "body4"))
from body4_fast import _weekend, _fri_cut, _nights, BLOCK0, BLOCK1   # noqa: E402

FRAC1 = 0.6
MAXP = 64


@njit(cache=True)
def simulate(ts, o, h, l, c, gaps, start, tconf, side, level, stop, width, texp, allow, bt, LH, LL,
             spread, comm, slip, swap, exit_mode, cut, tgt_r, be_frac):
    N = len(ts); P = len(start)
    out = np.zeros((P + 1, 17)); m = 0
    cost = spread + comm + slip
    pj_ = np.zeros(MAXP, np.int64); ps = np.zeros(MAXP, np.int64); plev = np.zeros(MAXP); pst = np.zeros(MAXP)
    pwid = np.zeros(MAXP); pexp = np.zeros(MAXP, np.int64)
    npend = 0; pcut = 0
    pos = False; xj = 0; xs = 0; xe = 0.0; xst = 0.0; xst0 = 0.0; xr = 0.0; xtp1 = 0.0; xtp2 = 0.0; xtgt = 0.0
    part = False; px1 = 0.0; xi = 0; xt = 0; xcut = 0; xk = 0; xmfe = 0.0; xtrig = 0.0; xbe = False
    pj = 0
    i = start[0] if P > 0 else N
    while i < N:
        t = ts[i]
        why = 0; done = False; cpx = 0.0; ci = 0; ct = 0
        if pos and t >= xcut:
            cpx = c[i - 1] - slip if xs > 0 else c[i - 1] + spread + slip
            why = 6 if part else 4; ci = i - 1; ct = xcut; done = True
        if done:
            ok = True
            for g in gaps:
                if xi < g <= ci:
                    ok = False
            if ok:
                gross = FRAC1 * (px1 - xe) / xr * xs + (1 - FRAC1) * (cpx - xe) / xr * xs if part else (cpx - xe) / xr * xs
                nts = _nights(xt, ct); fin = nts * swap / xr
                out[m, 0] = xt; out[m, 1] = ct; out[m, 2] = xs; out[m, 3] = gross - comm / xr - fin; out[m, 4] = xr
                out[m, 5] = cost / xr; out[m, 6] = nts; out[m, 7] = fin; out[m, 8] = xj; out[m, 9] = why; out[m, 10] = xe
                out[m, 11] = cpx; out[m, 12] = xst0; out[m, 13] = xtp1; out[m, 14] = xtp2; out[m, 15] = 1.0 if part else 0.0
                out[m, 16] = xmfe; m += 1
            pos = False
        if npend > 0:
            k2 = 0
            for q in range(npend):
                if t < pcut and t < pexp[q]:
                    pj_[k2] = pj_[q]; ps[k2] = ps[q]; plev[k2] = plev[q]; pst[k2] = pst[q]; pwid[k2] = pwid[q]; pexp[k2] = pexp[q]
                    k2 += 1
            npend = k2
        if t >= cut:
            npend = 0
            if not pos:
                break
        while pj < P and start[pj] <= i:
            j = pj; pj += 1
            if t >= cut or allow[j] == 0 or _weekend(tconf[j]) or _weekend(t) or pos:
                continue
            s = side[j]; lvl = level[j]; stp = stop[j]; w = width[j]
            if s > 0 and o[i] + spread <= lvl:
                continue
            if s < 0 and o[i] >= lvl:
                continue
            if abs(lvl - stp) <= cost:
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
                pj_[npend] = j; ps[npend] = s; plev[npend] = lvl; pst[npend] = stp; pwid[npend] = w; pexp[npend] = texp[j]
                npend += 1
                pcut = _fri_cut(t)
        if npend > 0 and not pos:
            sod = t % 86400
            blocked = BLOCK0 <= sod < BLOCK1
            best = -1
            for q in range(npend):
                s = ps[q]
                hit = (not blocked) and ((l[i] + spread <= plev[q]) if s > 0 else (h[i] >= plev[q]))
                if hit:
                    if best < 0 or (s > 0 and plev[q] > plev[best]) or (s < 0 and plev[q] < plev[best]):
                        best = q
            if best >= 0:
                s = ps[best]
                px = min(plev[best], o[i] + spread) if s > 0 else max(plev[best], o[i])
                jb = np.searchsorted(bt, t, side="right") - 2
                n_ok = 0; a1 = 0.0; a2 = 0.0
                if jb >= 0:
                    for mm in range(LH.shape[1]):
                        x = LH[jb, mm] if s > 0 else LL[jb, mm]
                        if not np.isnan(x) and (x - px) * s > 0:
                            if n_ok == 0:
                                a1 = x
                            elif n_ok == 1:
                                a2 = x
                            n_ok += 1
                rk = abs(plev[best] - pst[best]); st0 = pst[best]; jj = pj_[best]
                npend = 0
                if n_ok >= 2 or exit_mode == 3:
                    pos = True; xj = jj; xs = s; xe = px; xst = st0; xst0 = st0; xr = rk; xtp1 = a1; xtp2 = a2
                    xtgt = a2 if exit_mode == 2 else a1; part = False; px1 = 0.0; xi = i; xt = t; xcut = _fri_cut(t); xk = i
                    if exit_mode == 3:
                        xtgt = plev[best] + s * tgt_r * rk; xtp1 = xtgt; xtp2 = xtgt
                    xbe = False
                    xtrig = plev[best] + be_frac * (xtgt - plev[best]) if be_frac > 0 else 0.0
                    xmfe = 0.0
                    if (l[i] <= xst) if s > 0 else (h[i] + spread >= xst):
                        cpx = (min(xst, o[i]) - slip) if s > 0 else (max(xst, o[i] + spread) + slip)
                        gross = (cpx - xe) / xr * xs
                        out[m, 0] = xt; out[m, 1] = t; out[m, 2] = xs; out[m, 3] = gross - comm / xr; out[m, 4] = xr
                        out[m, 5] = cost / xr; out[m, 6] = 0; out[m, 7] = 0.0; out[m, 8] = xj; out[m, 9] = 5; out[m, 10] = xe
                        out[m, 11] = cpx; out[m, 12] = xst0; out[m, 13] = xtp1; out[m, 14] = xtp2; out[m, 15] = 0.0; out[m, 16] = 0.0
                        m += 1
                        pos = False
            else:
                k2 = 0
                for q in range(npend):
                    s = ps[q]
                    if not ((l[i] <= pst[q]) if s > 0 else (h[i] + spread >= pst[q])):
                        pj_[k2] = pj_[q]; ps[k2] = ps[q]; plev[k2] = plev[q]; pst[k2] = pst[q]; pwid[k2] = pwid[q]; pexp[k2] = pexp[q]
                        k2 += 1
                npend = k2
        elif pos and i > xk:
            s = xs
            hit_sl = (l[i] <= xst) if s > 0 else (h[i] + spread >= xst)
            hit_tp = (h[i] >= xtgt) if s > 0 else (l[i] + spread <= xtgt)
            fin_now = False
            if hit_sl:
                cpx = (min(o[i], xst) - slip) if s > 0 else (max(o[i] + spread, xst) + slip)
                why = 3 if (part or xbe) else 1; fin_now = True
            elif hit_tp:
                cpx = max(xtgt, o[i]) if s > 0 else min(xtgt, o[i] + spread)
                r_ = (cpx - xe) / xr * s
                if r_ > xmfe:
                    xmfe = r_
                if exit_mode == 0 and not part:
                    part = True; px1 = cpx; xtgt = xtp2; xst = xe + s * (spread + comm); xk = i
                else:
                    why = 2; fin_now = True
            else:
                run_ = (h[i] - xe) / xr if s > 0 else (xe - (l[i] + spread)) / xr
                if run_ > xmfe:
                    xmfe = run_
                if be_frac > 0 and not xbe and not part and ((s > 0 and h[i] >= xtrig) or (s < 0 and l[i] + spread <= xtrig)):
                    xst = xe; xbe = True
            if fin_now:
                ok = True
                for g in gaps:
                    if xi < g <= i:
                        ok = False
                if ok:
                    gross = FRAC1 * (px1 - xe) / xr * xs + (1 - FRAC1) * (cpx - xe) / xr * xs if part else (cpx - xe) / xr * xs
                    nts = _nights(xt, t); fin = nts * swap / xr
                    out[m, 0] = xt; out[m, 1] = t; out[m, 2] = xs; out[m, 3] = gross - comm / xr - fin; out[m, 4] = xr
                    out[m, 5] = cost / xr; out[m, 6] = nts; out[m, 7] = fin; out[m, 8] = xj; out[m, 9] = why; out[m, 10] = xe
                    out[m, 11] = cpx; out[m, 12] = xst0; out[m, 13] = xtp1; out[m, 14] = xtp2; out[m, 15] = 1.0 if part else 0.0
                    out[m, 16] = xmfe; m += 1
                pos = False
        i += 1
        if not pos and npend == 0:
            if pj >= P:
                break
            if start[pj] > i:
                i = start[pj]
    return out[:m]


def run(M1, O, S, costs, exit="partial", allow=None, cut=2 ** 62, gaps=None, tgt_r=0.0, be_frac=0.0):
    ts = np.asarray(M1["ts"], np.int64)
    start = np.searchsorted(ts, np.asarray(O["t_conf"], np.int64)).astype(np.int64)
    P = len(start)
    return simulate(ts, np.asarray(M1["o"], float), np.asarray(M1["h"], float), np.asarray(M1["l"], float),
                    np.asarray(M1["c"], float), np.asarray(gaps if gaps is not None else [], np.int64), start,
                    np.asarray(O["t_conf"], np.int64), np.asarray(O["side"], np.int64), np.asarray(O["level"], float),
                    np.asarray(O["stop"], float), np.asarray(O["width"], float), np.asarray(O["t_exp"], np.int64),
                    np.asarray(allow if allow is not None else np.ones(P), np.int64), np.asarray(S["bt"], np.int64),
                    S["LH"], S["LL"], float(costs["spread"]), float(costs["commission"]), float(costs["slippage"]),
                    float(costs.get("swap", 0.0)), {"partial": 0, "tp1": 1, "tp2": 2, "fixed": 3}[exit], int(cut),
                    float(tgt_r), float(be_frac))
