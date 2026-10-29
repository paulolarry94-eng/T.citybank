"""ORB 50 — strategy logic: one state machine per session-day for Models A, B and C and for the
separate failed-breakout reversal hypothesis. Orders it emits are filled and managed by
execution.py. Every decision uses only completed execution bars (default M5) and completed H4
bars; pending orders are re-evaluated bar by bar and filled minute by minute.

The state machine is written for a long setup in DIRECTION-NORMALISED prices (x_s = s * x, so
a short's lows become highs); levels are mapped back to real prices before they reach the
execution layer. This keeps long and short logic literally identical.

Entry modes
  0  market: next minute open after the breakout bar closes beyond ORH + buf*ATR
  1  stop:   buy stop ebuf*ATR above the breakout bar's high (valid until invalidated / cutoff)
  2  retest: buy limit at ORH + tol*ATR after the breakout close (valid until invalidated / cutoff)
  3  pullback by candle count: after the breakout close and a displacement of disp*ATR beyond
     the OR, pb_k consecutive bearish bars; buy stop ebuf*ATR above the last (pb_hi=0) or the
     highest (pb_hi=1) pullback bar; follows further pullback bars down; dies on invalidation
  4  pullback by ATR retracement: as 3 but the pullback is a retracement of pb_atr*ATR from the
     post-breakout high; buy stop above the latest bar high (follows lower highs down)
  5  failed-breakout REVERSAL (separate hypothesis): a bar that trades beyond ORH + buf*ATR but
     closes back inside the OR (the min_fails-th such bar) -> sell at the next minute open
Stops   0 far side of the OR | 1 swing (breakout bar extreme; pullback extreme for modes 3/4;
        session extreme for mode 5) | 2 stop_k*ATR from entry | 3 OR midpoint |
        4 chandelier: highest high of the last atr_p bars - stop_k*ATR
"""
import numpy as np
from numba import njit
from execution import fill_stop, fill_limit, manage

PARAMS = dict(
    side=0, buf=0.0, entry=0, tol=0.25, pb_k=2, pb_atr=0.5, disp=0.0, ebuf=0.0,
    stop=0, stop_k=2.0, sbuf=0.0, tgt=0.0, trail=0.0, part_f=0.0, part_r=1.0, be=0.0,
    imp=0.0, max_fails=-1, vol=0.0, bias=0, inval=0, min_risk=3.0, delay=0, pb_hi=0,
    max_tr=1, atr_p=14, min_fails=1,
)
KEYS = list(PARAMS)
KI = {k: i for i, k in enumerate(KEYS)}
TR_DT = np.dtype([("d", "i8"), ("t_in", "i8"), ("t_out", "i8"), ("side", "i8"), ("r", "f8"),
                  ("dist", "f8"), ("entry", "f8"), ("reason", "i8"), ("mfe", "f8"), ("j", "i8")])


@njit(cache=True)
def _bar_of(bfirst, k):
    return np.searchsorted(bfirst, k, side="right") - 1


@njit(cache=True)
def _stop(smode, s, ORLs, MIDs, a, sbuf, stop_k, entry_s, swing_s, chand_s):
    """Stop in normalised prices (below a normalised long)."""
    if smode == 0:
        return ORLs - sbuf * a
    if smode == 1:
        return swing_s - sbuf * a
    if smode == 2:
        return entry_s - stop_k * a
    if smode == 3:
        return MIDs - sbuf * a
    return chand_s - stop_k * a


@njit(cache=True)
def run_kernel(o, h, l, ts, bo, bh, bl, bc, bfirst, bnxt, atr, bias, rvol,
               orh_a, orl_a, b0_a, bcut_a, iend_a, allow, P, cost):
    side_mode = int(P[0]); buf = P[1]; emode = int(P[2]); tol = P[3]; pbk = int(P[4])
    pba = P[5]; disp = P[6]; ebuf = P[7]; smode = int(P[8]); stop_k = P[9]; sbuf = P[10]
    tgt_r = P[11]; trail_m = P[12]; part_f = P[13]; part_r = P[14]; be_r = P[15]
    imp = P[16]; max_fails = int(P[17]); vol_k = P[18]; use_bias = P[19] > 0
    inval = int(P[20]); min_d = P[21] * cost; delay = int(P[22]); pbmode = int(P[23])
    max_tr = int(P[24]); atr_p = int(P[25]); min_fails = int(P[26])
    eps = 0.1 * cost
    nd = len(orh_a)
    out = np.zeros((nd * max_tr, 10))
    m = 0
    for d in range(nd):
        if not allow[d]:
            continue
        ORH = orh_a[d]; ORL = orl_a[d]; MID = 0.5 * (ORH + ORL)
        kend = iend_a[d]; jcut = bcut_a[d]
        taken = 0
        state = 0                 # 0 idle, 1 pending stop, 2 pending limit, 3 pullback hunt
        s = 0
        lvl = 0.0                 # pending level (normalised); 0 = none placed
        pstop = 0.0               # stop attached to the pending order (normalised)
        arm_up = True; arm_dn = True
        fails_up = 0; fails_dn = 0
        hh = 0.0; lo_since = 0.0; displaced = False
        pb_cnt = 0; pb_hi = 0.0; pb_lo = 0.0
        sess_hi = ORH; sess_lo = ORL
        sig_j = -1
        j = b0_a[d]
        while j < jcut and taken < max_tr:
            # ------------------------------------------------ 1. pending order during bar j
            if state == 1 or state == 2 or (state == 3 and lvl != 0.0):
                k1 = min(bnxt[j], kend)
                real_lvl = s * lvl
                if state == 2:
                    kf, px = fill_limit(o, h, l, bfirst[j], k1, s, real_lvl, cost, eps)
                else:
                    kf, px = fill_stop(o, h, l, bfirst[j], k1, s, real_lvl, cost)
                if kf >= 0:
                    stp = s * pstop
                    dist = (px - stp) if s > 0 else (stp - px)
                    if dist >= min_d and dist > 0:
                        kx, r, why, mfe = manage(o, h, l, kf, kend, s, px, stp, dist, cost, tgt_r, be_r,
                                                 part_f, part_r, trail_m, atr_p, bh, bl, bnxt, atr, j, False)
                        out[m, 0] = d; out[m, 1] = ts[kf]; out[m, 2] = ts[kx]; out[m, 3] = s
                        out[m, 4] = r; out[m, 5] = dist; out[m, 6] = px; out[m, 7] = why
                        out[m, 8] = mfe; out[m, 9] = sig_j
                        m += 1; taken += 1
                        if taken >= max_tr:
                            break
                        state = 0; lvl = 0.0
                        j = _bar_of(bfirst, kx) + 1
                        continue
                    state = 0; lvl = 0.0                   # stop too tight: setup consumed
            # ------------------------------------------------ 2. bar j has closed
            a = atr[j]
            cl = bc[j]; hi = bh[j]; lo = bl[j]; op = bo[j]
            if hi > sess_hi:
                sess_hi = hi
            if lo < sess_lo:
                sess_lo = lo
            if a <= 0.0:
                j += 1
                continue
            if cl <= ORH:
                arm_up = True
            if cl >= ORL:
                arm_dn = True
            if state == 0:
                f_up = hi > ORH + buf * a and cl < ORH
                f_dn = lo < ORL - buf * a and cl > ORL
                if f_up:
                    fails_up += 1
                if f_dn:
                    fails_dn += 1
                if emode == 5:                              # ---- reversal hypothesis
                    rs = 0
                    if f_up and fails_up >= min_fails and side_mode <= 0:
                        rs = -1
                    elif f_dn and fails_dn >= min_fails and side_mode >= 0:
                        rs = 1
                    if rs != 0 and use_bias and bias[j] != rs:
                        rs = 0
                    if rs != 0:
                        kf = bnxt[j] + delay
                        if kf < kend:
                            px = o[kf] + cost if rs > 0 else o[kf]
                            ext_s = sess_lo if rs > 0 else -sess_hi     # the failed extreme, normalised
                            if smode == 2:
                                stp_s = rs * px - stop_k * a
                            elif smode == 4:
                                j0 = max(j - atr_p + 1, 0)
                                ch = bh[j0] if rs > 0 else -bl[j0]
                                for q in range(j0, j + 1):
                                    v = bh[q] if rs > 0 else -bl[q]
                                    if v > ch:
                                        ch = v
                                stp_s = ch - stop_k * a
                            else:                                       # beyond the failed extreme
                                stp_s = ext_s - sbuf * a
                            stp = rs * stp_s
                            dist = (px - stp) if rs > 0 else (stp - px)
                            if dist >= min_d and dist > 0:
                                kx, r, why, mfe = manage(o, h, l, kf, kend, rs, px, stp, dist, cost, tgt_r, be_r,
                                                         part_f, part_r, trail_m, atr_p, bh, bl, bnxt, atr,
                                                         _bar_of(bfirst, kf), True)
                                out[m, 0] = d; out[m, 1] = ts[kf]; out[m, 2] = ts[kx]; out[m, 3] = rs
                                out[m, 4] = r; out[m, 5] = dist; out[m, 6] = px; out[m, 7] = why
                                out[m, 8] = mfe; out[m, 9] = j
                                m += 1; taken += 1
                                if taken >= max_tr:
                                    break
                                j = _bar_of(bfirst, kx) + 1
                                continue
                    j += 1
                    continue
                up = arm_up and cl > ORH + buf * a
                dn = arm_dn and cl < ORL - buf * a
                s = 0
                if up and side_mode >= 0:
                    s = 1; arm_up = False
                elif dn and side_mode <= 0:
                    s = -1; arm_dn = False
                if s != 0:
                    ok = True
                    if use_bias and bias[j] != s:
                        ok = False
                    if imp > 0 and (hi - lo) > imp * a:
                        ok = False
                    if max_fails >= 0 and (fails_up if s > 0 else fails_dn) > max_fails:
                        ok = False
                    if vol_k > 0 and rvol[j] < vol_k:
                        ok = False
                    if ok:
                        sig_j = j
                        his = hi if s > 0 else -lo        # normalised extremes of the breakout bar
                        los = lo if s > 0 else -hi
                        ORHs = ORH if s > 0 else -ORL
                        ORLs = ORL if s > 0 else -ORH
                        MIDs = s * MID
                        j0 = max(j - atr_p + 1, 0)
                        ch = bh[j0] if s > 0 else -bl[j0]
                        for q in range(j0, j + 1):
                            v = bh[q] if s > 0 else -bl[q]
                            if v > ch:
                                ch = v
                        if emode == 0:
                            kf = bnxt[j] + delay
                            if kf < kend:
                                px = o[kf] + cost if s > 0 else o[kf]
                                stp = s * _stop(smode, s, ORLs, MIDs, a, sbuf, stop_k, s * px, los, ch)
                                dist = (px - stp) if s > 0 else (stp - px)
                                if dist >= min_d and dist > 0:
                                    kx, r, why, mfe = manage(o, h, l, kf, kend, s, px, stp, dist, cost, tgt_r,
                                                             be_r, part_f, part_r, trail_m, atr_p, bh, bl, bnxt,
                                                             atr, _bar_of(bfirst, kf), True)
                                    out[m, 0] = d; out[m, 1] = ts[kf]; out[m, 2] = ts[kx]; out[m, 3] = s
                                    out[m, 4] = r; out[m, 5] = dist; out[m, 6] = px; out[m, 7] = why
                                    out[m, 8] = mfe; out[m, 9] = j
                                    m += 1; taken += 1
                                    if taken >= max_tr:
                                        break
                                    j = _bar_of(bfirst, kx) + 1
                                    continue
                        elif emode == 1:
                            state = 1
                            lvl = his + ebuf * a
                            pstop = _stop(smode, s, ORLs, MIDs, a, sbuf, stop_k, lvl, los, ch)
                        elif emode == 2:
                            state = 2
                            lvl = ORHs + tol * a
                            pstop = _stop(smode, s, ORLs, MIDs, a, sbuf, stop_k, lvl, los, ch)
                        else:
                            state = 3; lvl = 0.0
                            hh = his; lo_since = 1e300
                            displaced = (hh - ORHs) >= disp * a
                            pb_cnt = 0
                j += 1
                continue
            # ---------------------------------------------- states 1-3: normalised bar
            his = hi if s > 0 else -lo
            los = lo if s > 0 else -hi
            cls = s * cl; ops = s * op
            ORHs = ORH if s > 0 else -ORL
            ORLs = ORL if s > 0 else -ORH
            MIDs = s * MID
            if inval == 0:
                dead = cls < ORHs
            elif inval == 1:
                dead = cls < MIDs
            else:
                dead = cls < ORLs
            if dead:
                state = 0; lvl = 0.0
                # the same close may be an opposite breakout: let the idle branch see this bar
                if (s > 0 and arm_dn and cl < ORL - buf * a) or (s < 0 and arm_up and cl > ORH + buf * a):
                    continue
                j += 1
                continue
            if state == 3:
                j0 = max(j - atr_p + 1, 0)
                ch = bh[j0] if s > 0 else -bl[j0]
                for q in range(j0, j + 1):
                    v = bh[q] if s > 0 else -bl[q]
                    if v > ch:
                        ch = v
                if not displaced:
                    if his > hh:
                        hh = his
                    displaced = (hh - ORHs) >= disp * a
                elif emode == 3:
                    if cls < ops:                          # a pullback bar
                        pb_cnt += 1
                        if pb_cnt == 1:
                            pb_hi = his; pb_lo = los
                        else:
                            pb_hi = his if pbmode == 0 else max(pb_hi, his)
                            pb_lo = min(pb_lo, los)
                        if pb_cnt >= pbk:
                            lvl = pb_hi + ebuf * a
                            pstop = _stop(smode, s, ORLs, MIDs, a, sbuf, stop_k, lvl, pb_lo, ch)
                    elif lvl == 0.0:                       # pullback interrupted before it qualified
                        pb_cnt = 0
                        if his > hh:
                            hh = his
                else:                                      # emode 4: ATR retracement
                    if lvl == 0.0:
                        if his >= hh:
                            hh = his; lo_since = 1e300
                        else:
                            if los < lo_since:
                                lo_since = los
                            if hh - lo_since >= pba * a:
                                pb_lo = lo_since
                                lvl = his + ebuf * a
                                pstop = _stop(smode, s, ORLs, MIDs, a, sbuf, stop_k, lvl, pb_lo, ch)
                    else:
                        if los < pb_lo:
                            pb_lo = los
                        if his + ebuf * a < lvl:
                            lvl = his + ebuf * a
                        pstop = _stop(smode, s, ORLs, MIDs, a, sbuf, stop_k, lvl, pb_lo, ch)
            j += 1
    return out[:m]


def to_trades(a):
    t = np.zeros(len(a), dtype=TR_DT)
    for i, nm in enumerate(TR_DT.names):
        t[nm] = a[:, i]
    return t


def params(**kw):
    p = dict(PARAMS)
    for k, v in kw.items():
        if k not in p:
            raise KeyError(k)
        p[k] = v
    return p


def run(M, session, orb, allow=None, bias_cfg=None, cost=None, **kw):
    """Run one configuration on one market/session/ORB length. Returns trades (TR_DT) with
    r = net R after costs. bias_cfg: dict for Market.bias (Model B) when bias=1."""
    p = params(**kw)
    D = M.days(session, orb)
    B = M.B
    atr = M.atr[int(p["atr_p"])]
    bias = M.bias(**(bias_cfg or {})) if p["bias"] else np.zeros(len(B["t"]), np.int64)
    rvol = M.rvol() if p["vol"] > 0 else np.zeros(len(B["t"]))
    if allow is None:
        allow = np.ones(len(D["orh"]), np.bool_)
    P = np.array([float(p[k]) for k in KEYS])
    res = run_kernel(M.o, M.h, M.l, M.ts, B["o"], B["h"], B["l"], B["c"], B["first"], B["nxt"], atr, bias,
                     rvol, D["orh"], D["orl"], D["b0"], D["bcut"], D["iend"], allow, P,
                     M.cost if cost is None else cost)
    return to_trades(res)
