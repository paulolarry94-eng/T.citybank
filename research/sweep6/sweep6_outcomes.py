"""Deep M1 study: every setup simulated ALONE, frictionless (no spread, commission, slippage or swaps), all payout
structures in one pass (research/sweep6/PREREGISTRATION.md). The pure-Python twin is `reference()` below (the
specification); research/truth/tests/test_sweep6.py checks they agree.

Pending order: from the first minute after candle 4 closes; skipped if the first minute opens through the level or the
setup is in the weekend window; fills when price trades at the level (buy: low <= level; sell: high >= level), never
20:30-23:00 UTC; cancelled when its life ends, at the Friday 20:30 UTC cutoff, or if price reaches the stop without filling.
Fill price: the level, or the open if the minute opens beyond it (better). The fill minute can only stop out.
Structures (kind, T, be): kind 0 fixed T R; 1 all at TP1; 2 all at TP2; 3 60% at TP1 then the rest at TP2 with the stop at
the entry. be > 0: once price has covered be x the distance from the level to the target, the stop moves to the entry
(from the next minute). Same minute stop and target: stop first, unless optimistic. Friday 20:30 UTC: closed at the last
price. A trade spanning a data hole is dropped. 1R = level to stop.
Also: best excursion before the initial stop, and after the initial stop (up to post_min minutes, not past that week's
Friday cutoff): did price reach TP1 / TP2 / +3R, how far past the stop it went before TP1, and in the first 60 minutes
(furthest past the stop, reached +1R or not).
"""
import os, sys
import numpy as np
from numba import njit

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "body4"))
from body4_fast import _weekend, _fri_cut, BLOCK0, BLOCK1   # noqa: E402

STRUCTS = ([(f"{T}R", 0, float(T), 0.0) for T in range(1, 11)] + [("15R", 0, 15.0, 0.0), ("20R", 0, 20.0, 0.0)]
           + [(f"{T}R-BE75", 0, float(T), 0.75) for T in range(3, 11)]
           + [("TP1", 1, 0.0, 0.0), ("TP2", 2, 0.0, 0.0), ("TP2-BE75", 2, 0.0, 0.75), ("P60", 3, 0.0, 0.0)])
NAMES = [s[0] for s in STRUCTS]
KIND = np.array([s[1] for s in STRUCTS], np.int64)
TT = np.array([s[2] for s in STRUCTS], float)
BE = np.array([s[3] for s in STRUCTS], float)
FRAC1 = 0.6
OUT_KEYS = ("R", "why", "tout", "amb", "status", "tfill", "entry", "tp1R", "tp2R", "mfe", "stop_hit", "p_tp1",
            "p_tp2", "p_3r", "p_past", "p_adv60", "p_fav60")


@njit(cache=True)
def simulate(ts, o, h, l, c, gaps, start, tconf, side, level, stop, texp, bt, LH, LL, kind, T, be, optimistic, post_min):
    N = len(ts); P = len(start); S = len(kind)
    R = np.full((P, S), np.nan, np.float32); why = np.zeros((P, S), np.int8); tout = np.zeros((P, S), np.int64)
    amb = np.zeros((P, S), np.int8)
    status = np.zeros(P, np.int8)            # 0 not placed, 1 expired / cut, 2 cancelled by the stop, 3 filled, 4 filled but dropped
    tfill = np.zeros(P, np.int64); entry = np.full(P, np.nan); tp1R = np.full(P, np.nan); tp2R = np.full(P, np.nan)
    mfe = np.zeros(P, np.float32); stop_hit = np.zeros(P, np.int8)
    p_tp1 = np.zeros(P, np.int8); p_tp2 = np.zeros(P, np.int8); p_3r = np.zeros(P, np.int8)
    p_past = np.full(P, np.nan, np.float32); p_adv60 = np.full(P, np.nan, np.float32); p_fav60 = np.zeros(P, np.int8)
    stp = np.zeros(S); tgt = np.zeros(S); trig = np.zeros(S); op = np.zeros(S, np.bool_); mv = np.zeros(S, np.bool_)
    part = np.zeros(S, np.bool_); px1 = np.zeros(S)
    for p in range(P):
        i = start[p]
        if i >= N:
            continue
        s = side[p]; lvl = level[p]; st = stop[p]; rk = abs(lvl - st)
        if rk <= 0 or _weekend(tconf[p]) or _weekend(ts[i]):
            continue
        if (s > 0 and o[i] <= lvl) or (s < 0 and o[i] >= lvl):
            continue
        status[p] = 1
        cut = _fri_cut(ts[i])
        fi = -1
        while i < N:
            t = ts[i]
            if t >= texp[p] or t >= cut:
                break
            sod = t % 86400
            if not (BLOCK0 <= sod < BLOCK1) and ((s > 0 and l[i] <= lvl) or (s < 0 and h[i] >= lvl)):
                fi = i
                break
            if (s > 0 and l[i] <= st) or (s < 0 and h[i] >= st):
                status[p] = 2
                break
            i += 1
        if fi < 0:
            continue
        status[p] = 3
        t = ts[fi]
        px = min(lvl, o[fi]) if s > 0 else max(lvl, o[fi])
        entry[p] = px; tfill[p] = t
        jb = np.searchsorted(bt, t, side="right") - 2
        a1 = np.nan; a2 = np.nan; nok = 0
        if jb >= 0:
            for m in range(LH.shape[1]):
                x = LH[jb, m] if s > 0 else LL[jb, m]
                if not np.isnan(x) and (x - px) * s > 0:
                    if nok == 0:
                        a1 = x
                    elif nok == 1:
                        a2 = x
                    nok += 1
        if nok >= 1:
            tp1R[p] = (a1 - lvl) * s / rk
        if nok >= 2:
            tp2R[p] = (a2 - lvl) * s / rk
        for q in range(S):
            op[q] = True; mv[q] = False; part[q] = False; px1[q] = 0.0; stp[q] = st
            if kind[q] == 0:
                tgt[q] = lvl + s * T[q] * rk
            elif kind[q] == 1:
                tgt[q] = a1
                if nok < 1:
                    op[q] = False
            elif kind[q] == 2:
                tgt[q] = a2
                if nok < 2:
                    op[q] = False
            else:
                tgt[q] = a1
                if nok < 2:
                    op[q] = False
            trig[q] = lvl + be[q] * (tgt[q] - lvl) if be[q] > 0 else np.nan
        cut = _fri_cut(t)
        si = -1; mf = 0.0; last = fi
        if (s > 0 and l[fi] <= st) or (s < 0 and h[fi] >= st):
            ex = min(st, o[fi]) if s > 0 else max(st, o[fi])
            for q in range(S):
                if op[q]:
                    R[p, q] = (ex - px) / rk * s; why[p, q] = 5; tout[p, q] = t; op[q] = False
            si = fi
        else:
            i = fi + 1
            while i < N:
                t = ts[i]
                if t >= cut:
                    ex = c[i - 1]
                    for q in range(S):
                        if op[q]:
                            r2 = (ex - px) / rk * s
                            R[p, q] = FRAC1 * (px1[q] - px) / rk * s + (1 - FRAC1) * r2 if part[q] else r2
                            why[p, q] = 4; tout[p, q] = cut; op[q] = False
                    break
                if si < 0:
                    if (s > 0 and l[i] <= st) or (s < 0 and h[i] >= st):
                        si = i
                    else:
                        fav = (h[i] - px) / rk if s > 0 else (px - l[i]) / rk
                        if fav > mf:
                            mf = fav
                anyo = False
                for q in range(S):
                    if not op[q]:
                        continue
                    hs = (l[i] <= stp[q]) if s > 0 else (h[i] >= stp[q])
                    ht = (h[i] >= tgt[q]) if s > 0 else (l[i] <= tgt[q])
                    if hs and ht:
                        amb[p, q] = 1
                    if hs and not (ht and optimistic):
                        ex = min(o[i], stp[q]) if s > 0 else max(o[i], stp[q])
                        r2 = (ex - px) / rk * s
                        R[p, q] = FRAC1 * (px1[q] - px) / rk * s + (1 - FRAC1) * r2 if part[q] else r2
                        why[p, q] = 3 if (mv[q] or part[q]) else 1; tout[p, q] = t; op[q] = False
                    elif ht:
                        ex = max(o[i], tgt[q]) if s > 0 else min(o[i], tgt[q])
                        if kind[q] == 3 and not part[q]:
                            part[q] = True; px1[q] = ex; tgt[q] = a2; stp[q] = px
                        else:
                            r2 = (ex - px) / rk * s
                            R[p, q] = FRAC1 * (px1[q] - px) / rk * s + (1 - FRAC1) * r2 if part[q] else r2
                            why[p, q] = 2; tout[p, q] = t; op[q] = False
                    elif be[q] > 0 and not mv[q] and ((s > 0 and h[i] >= trig[q]) or (s < 0 and l[i] <= trig[q])):
                        stp[q] = px; mv[q] = True
                    if op[q]:
                        anyo = True
                last = i
                if not anyo:
                    break
                i += 1
        mfe[p] = mf
        drop = False
        for g in gaps:
            if fi < g <= last:
                drop = True
        if drop:
            status[p] = 4
            for q in range(S):
                R[p, q] = np.nan
            continue
        if si >= 0:
            stop_hit[p] = 1
            cut2 = _fri_cut(ts[si])
            past = 0.0; got1 = False; adv60 = 0.0
            j = si + 1
            while j < N and j <= si + post_min and ts[j] < cut2:
                adv = (st - l[j]) / rk if s > 0 else (h[j] - st) / rk
                if j <= si + 60:
                    if adv > adv60:
                        adv60 = adv
                    if (s > 0 and h[j] >= lvl + rk) or (s < 0 and l[j] <= lvl - rk):
                        p_fav60[p] = 1
                if nok >= 1 and ((s > 0 and h[j] >= a1) or (s < 0 and l[j] <= a1)):
                    if not got1:
                        got1 = True; p_tp1[p] = 1; p_past[p] = past
                if not got1 and adv > past:
                    past = adv
                if nok >= 2 and ((s > 0 and h[j] >= a2) or (s < 0 and l[j] <= a2)):
                    p_tp2[p] = 1
                if (s > 0 and h[j] >= lvl + 3 * rk) or (s < 0 and l[j] <= lvl - 3 * rk):
                    p_3r[p] = 1
                j += 1
            p_adv60[p] = adv60
            if not got1:
                p_past[p] = past
    return (R, why, tout, amb, status, tfill, entry, tp1R, tp2R, mfe, stop_hit, p_tp1, p_tp2, p_3r, p_past, p_adv60, p_fav60)


def run(M1, O, L, optimistic=False, post_min=1440, gaps=None):
    ts = np.asarray(M1["ts"], np.int64)
    start = np.searchsorted(ts, np.asarray(O["t_conf"], np.int64)).astype(np.int64)
    out = simulate(ts, np.asarray(M1["o"], float), np.asarray(M1["h"], float), np.asarray(M1["l"], float),
                   np.asarray(M1["c"], float), np.asarray(gaps if gaps is not None else [], np.int64), start,
                   np.asarray(O["t_conf"], np.int64), np.asarray(O["side"], np.int64), np.asarray(O["level"], float),
                   np.asarray(O["stop"], float), np.asarray(O["t_exp"], np.int64), np.asarray(L["bt"], np.int64), L["LH"], L["LL"],
                   KIND, TT, BE, bool(optimistic), int(post_min))
    return dict(zip(OUT_KEYS, out))


def reference(M1, O, L, idx, q, optimistic=False):
    """Plain-Python specification for ONE setup idx and ONE structure q: returns (status, R, why, tout)."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "body4"))
    from body4_orders import weekend, friday_cut_after, BLOCK
    ts, o, h, l, c = M1["ts"], M1["o"], M1["h"], M1["l"], M1["c"]
    kind, T, be = int(KIND[q]), float(TT[q]), float(BE[q])
    i = int(np.searchsorted(ts, int(O["t_conf"][idx])))
    if i >= len(ts):
        return 0, None, 0, 0
    s, lvl, st = int(O["side"][idx]), float(O["level"][idx]), float(O["stop"][idx]); rk = abs(lvl - st)
    if rk <= 0 or weekend(int(O["t_conf"][idx])) or weekend(int(ts[i])) or (s > 0 and o[i] <= lvl) or (s < 0 and o[i] >= lvl):
        return 0, None, 0, 0
    cut = friday_cut_after(int(ts[i])); fi = None
    while i < len(ts):
        t = int(ts[i])
        if t >= int(O["t_exp"][idx]) or t >= cut:
            return 1, None, 0, 0
        if not (BLOCK[0] <= t % 86400 < BLOCK[1]) and ((s > 0 and l[i] <= lvl) or (s < 0 and h[i] >= lvl)):
            fi = i; break
        if (s > 0 and l[i] <= st) or (s < 0 and h[i] >= st):
            return 2, None, 0, 0
        i += 1
    if fi is None:
        return 1, None, 0, 0
    t = int(ts[fi]); px = min(lvl, o[fi]) if s > 0 else max(lvl, o[fi])
    jb = int(np.searchsorted(L["bt"], t, side="right")) - 2
    lev = [float(x) for x in ((L["LH"][jb] if s > 0 else L["LL"][jb]) if jb >= 0 else []) if not np.isnan(x) and (x - px) * s > 0]
    if kind == 0:
        tgt = lvl + s * T * rk
    elif kind == 1:
        if len(lev) < 1:
            return 3, None, 0, 0
        tgt = lev[0]
    else:
        if len(lev) < 2:
            return 3, None, 0, 0
        tgt = lev[1] if kind == 2 else lev[0]
    trig = lvl + be * (tgt - lvl) if be > 0 else None
    stp, moved, part, p1 = st, False, False, 0.0
    cut = friday_cut_after(t)
    fin = lambda ex: FRAC1 * (p1 - px) / rk * s + (1 - FRAC1) * (ex - px) / rk * s if part else (ex - px) / rk * s
    if (s > 0 and l[fi] <= st) or (s < 0 and h[fi] >= st):
        ex = min(st, o[fi]) if s > 0 else max(st, o[fi])
        return 3, (ex - px) / rk * s, 5, t
    for i in range(fi + 1, len(ts)):
        t = int(ts[i])
        if t >= cut:
            return 3, fin(c[i - 1]), 4, cut
        hs = (l[i] <= stp) if s > 0 else (h[i] >= stp)
        ht = (h[i] >= tgt) if s > 0 else (l[i] <= tgt)
        if hs and not (ht and optimistic):
            ex = min(o[i], stp) if s > 0 else max(o[i], stp)
            return 3, fin(ex), 3 if (moved or part) else 1, t
        if ht:
            ex = max(o[i], tgt) if s > 0 else min(o[i], tgt)
            if kind == 3 and not part:
                part, p1, tgt, stp = True, ex, lev[1], px
                continue
            return 3, fin(ex), 2, t
        if trig is not None and not moved and ((s > 0 and h[i] >= trig) or (s < 0 and l[i] <= trig)):
            stp, moved = px, True
    return 3, None, 0, 0
