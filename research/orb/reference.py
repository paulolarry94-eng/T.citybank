"""Slow, literal re-implementation of the main ORB rules, used only to cross-check the fast
kernel trade by trade. Builds its own 5-minute bars from the raw minutes of each day and
walks every minute in plain Python. Covers entry modes 0-3, stops 0-3, fixed targets,
break-even and the close-back-inside invalidation."""
import numpy as np


def day_bars(M, t_from, t_to):
    i0 = np.searchsorted(M.ts, t_from); i1 = np.searchsorted(M.ts, t_to)
    bars = []
    cur = None
    for i in range(i0, i1):
        key = M.ts[i] // 300
        if cur is None or key != cur["key"]:
            if cur is not None:
                bars.append(cur)
            cur = dict(key=key, t=key * 300, o=M.o[i], h=M.h[i], l=M.l[i], c=M.c[i], first=i, last=i)
        else:
            cur["h"] = max(cur["h"], M.h[i]); cur["l"] = min(cur["l"], M.l[i]); cur["c"] = M.c[i]; cur["last"] = i
    if cur is not None:
        bars.append(cur)
    return bars


def hold(M, k0, kend, side, entry, stop, dist, tgt_r, be_r, at_open):
    c = M.cost
    tgt = entry + side * tgt_r * dist
    be_on = False
    for k in range(k0, kend):
        o, h, l = M.o[k], M.h[k], M.l[k]
        exact = (k == k0) and not at_open
        if side > 0:
            if l <= stop:
                px = stop if (exact or o > stop) else o
                return k, (px - entry) / dist
            if tgt_r > 0 and h >= tgt:
                px = tgt if (exact or o < tgt) else o
                return k, (px - entry) / dist
            fav = (h - entry) / dist
        else:
            if h + c >= stop:
                px = stop if (exact or o + c < stop) else o + c
                return k, (entry - px) / dist
            if tgt_r > 0 and l + c <= tgt:
                px = tgt if (exact or o + c > tgt) else o + c
                return k, (entry - px) / dist
            fav = (entry - (l + c)) / dist
        if be_r > 0 and not be_on and fav >= be_r:
            be_on = True
            stop = max(stop, entry) if side > 0 else min(stop, entry)
    px = M.o[kend] if side > 0 else M.o[kend] + c
    return kend, ((px - entry) if side > 0 else (entry - px)) / dist


def run_day(M, D, d, p, atr_by_t, orb):
    c = M.cost
    ORH, ORL = D["orh"][d], D["orl"][d]; MID = (ORH + ORL) / 2
    t_or = D["t_open"][d] + orb * 60
    t_cut = D["t_open"][d] + 3 * 3600
    kend = D["iend"][d]
    bars = day_bars(M, t_or, t_cut)
    armed = {1: True, -1: True}
    pend = None          # dict(side, kind, level, stop)
    pb = None
    for b in bars:
        a = atr_by_t.get(b["t"], 0.0)
        # fills inside this bar
        if pend is not None and pend.get("level") is not None:
            s = pend["side"]
            for k in range(b["first"], min(b["last"] + 1, kend)):
                o, h, l = M.o[k], M.h[k], M.l[k]
                fill = None
                if pend["kind"] == "limit":
                    if s > 0 and l + c <= pend["level"] - 0.1 * c:
                        fill = min(pend["level"], o + c)
                    if s < 0 and h >= pend["level"] + 0.1 * c:
                        fill = max(pend["level"], o)
                else:
                    if s > 0 and h + c >= pend["level"]:
                        fill = max(pend["level"], o + c)
                    if s < 0 and l <= pend["level"]:
                        fill = min(pend["level"], o)
                if fill is not None:
                    stop = pend["stop"]
                    dist = (fill - stop) * s
                    if dist >= p["min_risk"] * c and dist > 0:
                        kx, r = hold(M, k, kend, s, fill, stop, dist, p["tgt"], p["be"], False)
                        return (M.ts[k], M.ts[kx], s, r)
                    pend = None; pb = None
                    break
        if a <= 0:
            continue
        cl, hi, lo, op = b["c"], b["h"], b["l"], b["o"]
        if cl <= ORH:
            armed[1] = True
        if cl >= ORL:
            armed[-1] = True
        if pend is not None:
            s = pend["side"]
            if (s > 0 and cl < ORH) or (s < 0 and cl > ORL):
                pend = None; pb = None
                if not ((s > 0 and armed[-1] and cl < ORL - p["buf"] * a) or (s < 0 and armed[1] and cl > ORH + p["buf"] * a)):
                    continue
            else:
                if p["entry"] == 3:
                    if not pb["disp"]:
                        pb["hh"] = max(pb["hh"], hi if s > 0 else -lo)
                        pb["disp"] = pb["hh"] - (ORH if s > 0 else -ORL) >= p["disp"] * a
                    else:
                        bear = (cl < op) if s > 0 else (cl > op)
                        if bear:
                            pb["n"] += 1
                            ph = hi if s > 0 else lo
                            pl = lo if s > 0 else hi
                            pb["lo"] = pl if pb["n"] == 1 else (min(pb["lo"], pl) if s > 0 else max(pb["lo"], pl))
                            if pb["n"] >= p["pb_k"]:
                                pend["level"] = ph + s * p["ebuf"] * a
                                pend["stop"] = stop_of(p, s, ORH, ORL, MID, a, pend["level"], pb["lo"])
                        elif pend["level"] is None:
                            pb["n"] = 0
                            pb["hh"] = max(pb["hh"], hi if s > 0 else -lo)
                continue
        s = 0
        if armed[1] and cl > ORH + p["buf"] * a and p["side"] >= 0:
            s = 1; armed[1] = False
        elif armed[-1] and cl < ORL - p["buf"] * a and p["side"] <= 0:
            s = -1; armed[-1] = False
        if s == 0:
            continue
        swing = lo if s > 0 else hi
        if p["entry"] == 0:
            k = b["last"] + 1
            if k >= kend:
                continue
            fill = M.o[k] + c if s > 0 else M.o[k]
            stop = stop_of(p, s, ORH, ORL, MID, a, fill, swing)
            dist = (fill - stop) * s
            if dist >= p["min_risk"] * c and dist > 0:
                kx, r = hold(M, k, kend, s, fill, stop, dist, p["tgt"], p["be"], True)
                return (M.ts[k], M.ts[kx], s, r)
        elif p["entry"] == 1:
            lvl = (hi if s > 0 else lo) + s * p["ebuf"] * a
            pend = dict(side=s, kind="stop", level=lvl, stop=stop_of(p, s, ORH, ORL, MID, a, lvl, swing))
        elif p["entry"] == 2:
            lvl = (ORH if s > 0 else ORL) + s * p["tol"] * a
            pend = dict(side=s, kind="limit", level=lvl, stop=stop_of(p, s, ORH, ORL, MID, a, lvl, swing))
        elif p["entry"] == 3:
            hh = hi if s > 0 else -lo
            pend = dict(side=s, kind="stop", level=None, stop=None)
            pb = dict(hh=hh, disp=hh - (ORH if s > 0 else -ORL) >= p["disp"] * a, n=0, lo=None)
    return None


def stop_of(p, s, ORH, ORL, MID, a, ref, swing):
    sb = p["sbuf"] * a
    if p["stop"] == 0:
        return ORL - sb if s > 0 else ORH + sb
    if p["stop"] == 1:
        return swing - sb if s > 0 else swing + sb
    if p["stop"] == 2:
        return ref - p["stop_k"] * a if s > 0 else ref + p["stop_k"] * a
    return MID - sb if s > 0 else MID + sb
