"""ORB 50 — execution simulation (order fills and position management), on 1-minute bid bars.

Price conventions (MT5): charts and data are BID. A long buys at ASK = bid + cost and sells at
bid; a short sells at bid and buys back at ask. `cost` is the all-in round-trip cost (spread +
commission + slippage), so every trade pays it exactly once.

Conservative rules where one minute's path is unknown:
* a stop and a target (or partial) touched in the same minute -> the stop is taken;
* a stop jumped by a gap fills at the worse opening price, never at the stop;
* the minute in which a pending order fills is checked against the stop as well;
* break-even and trailing changes computed from a minute apply from the next minute;
* limit orders need price to trade THROUGH the level by `eps`, a touch is not a fill.
"""
import numpy as np
from numba import njit

STOP, TARGET, SESSION_END = 1, 2, 3


@njit(cache=True)
def fill_stop(o, h, l, k0, k1, side, level, cost):
    """Buy stop fills when ask >= level, sell stop when bid <= level; fill at the level or the
    worse open. Returns (minute, price) or (-1, 0)."""
    for k in range(k0, k1):
        if side > 0:
            if h[k] + cost >= level:
                return k, max(level, o[k] + cost)
        else:
            if l[k] <= level:
                return k, min(level, o[k])
    return -1, 0.0


@njit(cache=True)
def fill_limit(o, h, l, k0, k1, side, level, cost, eps):
    """Buy limit fills when ask trades below level - eps; sell limit when bid trades above
    level + eps. Fill at the level or the better open."""
    for k in range(k0, k1):
        if side > 0:
            if l[k] + cost <= level - eps:
                return k, min(level, o[k] + cost)
        else:
            if h[k] >= level + eps:
                return k, max(level, o[k])
    return -1, 0.0


@njit(cache=True)
def manage(o, h, l, k0, kend, side, entry, stop, dist, cost, tgt_r, be_r, part_f, part_r,
           trail_m, trail_n, bh, bl, bnxt, atr, jb, at_open):
    """Hold a position from minute k0 to the session close (exit at the open of minute kend).
    jb = execution bar containing k0. at_open = entry was at the open of k0 (market order).
    Partial: part_f of the position closes at +part_r; if trail_m > 0 the remainder trails a
    chandelier stop (highest high of the last trail_n bars - trail_m * ATR), which only starts
    after the partial when a partial is used. Returns (exit_minute, R, reason, MFE_R)."""
    rem = 1.0
    real = 0.0
    part_done = part_f <= 0.0
    be_done = be_r <= 0.0
    tgt = entry + side * tgt_r * dist
    pl = entry + side * part_r * dist
    mfe = 0.0
    for k in range(k0, kend):
        exact = (k == k0) and not at_open      # pending-order fill minute: no gap logic
        if side > 0:
            if l[k] <= stop:
                px = stop if (exact or o[k] > stop) else o[k]
                return k, real + rem * (px - entry) / dist, STOP, mfe
            if not part_done and h[k] >= pl:
                px = pl if (exact or o[k] < pl) else o[k]
                real += part_f * (px - entry) / dist
                rem -= part_f
                part_done = True
            if tgt_r > 0 and h[k] >= tgt:
                px = tgt if (exact or o[k] < tgt) else o[k]
                return k, real + rem * (px - entry) / dist, TARGET, max(mfe, (h[k] - entry) / dist)
            fav = (h[k] - entry) / dist
        else:
            ah = h[k] + cost
            al = l[k] + cost
            ao = o[k] + cost
            if ah >= stop:
                px = stop if (exact or ao < stop) else ao
                return k, real + rem * (entry - px) / dist, STOP, mfe
            if not part_done and al <= pl:
                px = pl if (exact or ao > pl) else ao
                real += part_f * (entry - px) / dist
                rem -= part_f
                part_done = True
            if tgt_r > 0 and al <= tgt:
                px = tgt if (exact or ao > tgt) else ao
                return k, real + rem * (entry - px) / dist, TARGET, max(mfe, (entry - al) / dist)
            fav = (entry - al) / dist
        if fav > mfe:
            mfe = fav
        if not be_done and fav >= be_r:
            be_done = True
            if side > 0:
                stop = max(stop, entry)
            else:
                stop = min(stop, entry)
        if k + 1 >= bnxt[jb]:                  # execution bar jb has just closed
            if trail_m > 0 and part_done and atr[jb] > 0:
                j0 = max(jb - trail_n + 1, 0)
                if side > 0:
                    hh = bh[j0]
                    for q in range(j0 + 1, jb + 1):
                        if bh[q] > hh:
                            hh = bh[q]
                    new = hh - trail_m * atr[jb]
                    if new > stop:
                        stop = new
                else:
                    ll = bl[j0]
                    for q in range(j0 + 1, jb + 1):
                        if bl[q] < ll:
                            ll = bl[q]
                    new = ll + trail_m * atr[jb]
                    if new < stop:
                        stop = new
            jb += 1
    px = o[kend] if side > 0 else o[kend] + cost
    r = (px - entry) / dist if side > 0 else (entry - px) / dist
    return kend, real + rem * r, SESSION_END, mfe
