"""Daily liquidity mechanics: Asian range, previous day high/low, previous week high/low.

Sweep & reclaim : price trades beyond a level, then a bar CLOSES back inside within K bars
                  -> trade back into the range; stop beyond the sweep extreme.
Failed sweep    : after a reclaim, a bar closes beyond the sweep extreme -> trade the break.
Follow-through  : after a reclaim, price reaches the opposite level and a bar closes beyond it
                  -> trade the continuation.
Combinations    : 'stack' = the sweep also took the previous day's level; 'bias' = sell only
                  above last week's midpoint, buy only below it.

Fill law as everywhere: signal on a closed bar, entry at the next minute's open (+cost for
longs), minute-by-minute stops (gaps fill at the worse open), same-minute stop+target = loss.
Minimum stop = 0.15 x previous-day ATR and >= 3 x cost, so no micro-stop is scored on
one-minute data that cannot resolve it.
"""
import numpy as np
from numba import njit
import engine as E

DAY = 86400
DT = [("t_in", "i8"), ("t_out", "i8"), ("side", "i8"), ("r", "f8"), ("dist", "f8"), ("entry", "f8")]


@njit(cache=True)
def sweep_events(bh, bl, bc, w0, w1, H, L, K):
    """Per period p (bars w0[p]..w1[p]-1): first sweep of H (short side) and of L (long side).
    Returns per period: reclaim bar, sweep extreme, failed-sweep bar, follow-through bar for
    each side (-1 = none)."""
    P = len(w0)
    out = -np.ones((P, 8), np.int64)
    ext = np.zeros((P, 2))
    for p in range(P):
        for side in (0, 1):                     # 0 = sweep of H (short), 1 = sweep of L (long)
            js = -1; jr = -1; sx = 0.0
            for j in range(w0[p], w1[p]):
                if js < 0:
                    if (side == 0 and bh[j] > H[p]) or (side == 1 and bl[j] < L[p]):
                        js = j; sx = bh[j] if side == 0 else bl[j]
                    else:
                        continue
                sx = max(sx, bh[j]) if side == 0 else min(sx, bl[j])
                if (side == 0 and bc[j] < H[p]) or (side == 1 and bc[j] > L[p]):
                    jr = j; break
                if j - js >= K:
                    break
            if jr < 0:
                continue
            out[p, side * 4 + 0] = jr; ext[p, side] = sx
            reached = False
            for j in range(jr + 1, w1[p]):
                if out[p, side * 4 + 1] < 0 and ((side == 0 and bc[j] > sx) or (side == 1 and bc[j] < sx)):
                    out[p, side * 4 + 1] = j
                if not reached and ((side == 0 and bl[j] <= L[p]) or (side == 1 and bh[j] >= H[p])):
                    reached = True
                if reached and out[p, side * 4 + 2] < 0 and ((side == 0 and bc[j] < L[p]) or (side == 1 and bc[j] > H[p])):
                    out[p, side * 4 + 2] = j
    return out, ext


@njit(cache=True)
def run_abs(o, h, l, ts, ent_i, side, sl, tp_abs, tp_r, exit_i, cost, min_d, gaps):
    """Serial book with absolute stops; target either absolute (tp_abs) or R-multiple (tp_r)."""
    n = len(ent_i); out = np.zeros((n, 6)); k = 0; busy = -1; g = 0
    for s in range(n):
        i0 = ent_i[s]; i1 = exit_i[s]
        if i0 <= busy or i0 >= len(o) - 1 or i1 <= i0 or i1 >= len(o):
            continue
        while g < len(gaps) and gaps[g] < i0: g += 1
        if g < len(gaps) and gaps[g] < i1:
            continue
        sd = side[s]
        entry = o[i0] + cost if sd > 0 else o[i0]
        d = entry - sl[s] if sd > 0 else sl[s] - entry
        if d < min_d[s] or d <= 0:
            continue
        if tp_r[s] > 0:
            tp = entry + tp_r[s] * d if sd > 0 else entry - tp_r[s] * d
        else:
            tp = tp_abs[s]
            if tp > 0 and ((sd > 0 and tp <= entry) or (sd < 0 and tp >= entry)):
                continue                     # already at/through the target: nothing to trade
        px = 0.0; xi = i1; done = False
        for i in range(i0, i1):
            if sd > 0:
                if l[i] <= sl[s]:
                    px = min(sl[s] if (o[i] > sl[s] or i == i0) else o[i], sl[s]); xi = i; done = True; break
                if tp > 0 and h[i] >= tp:
                    px = tp; xi = i; done = True; break
            else:
                if h[i] + cost >= sl[s]:
                    ao = o[i] + cost
                    px = max(sl[s] if (ao < sl[s] or i == i0) else ao, sl[s]); xi = i; done = True; break
                if tp > 0 and l[i] + cost <= tp:
                    px = tp; xi = i; done = True; break
        if not done:
            px = o[i1] if sd > 0 else o[i1] + cost
        r = (px - entry) / d if sd > 0 else (entry - px) / d
        out[k, 0] = ts[i0]; out[k, 1] = ts[xi]; out[k, 2] = sd; out[k, 3] = r
        out[k, 4] = d; out[k, 5] = entry; k += 1; busy = xi
    return out[:k]


def pack(a):
    t = np.zeros(len(a), dtype=DT)
    for j, nm in enumerate(["t_in", "t_out", "side", "r", "dist", "entry"]):
        t[nm] = a[:, j]
    return t


class Lab:
    def __init__(self, sym):
        self.sym = sym; self.cost = E.COST[sym]
        self.m1 = E.load_m1(sym); self.ts, self.o, self.h, self.l, self.c = self.m1
        self.gaps = E.data_gaps(self.ts)
        bt, bo, bh, bl, bc, _ = E.resample(*self.m1, 1440, 0)
        self.D = dict(t=bt, h=bh, l=bl, c=bc, atr=E.atr_sma(bh, bl, bc, 14))
        self.bars = {}

    def tf(self, m):
        if m not in self.bars:
            bt, bo, bh, bl, bc, nxt = E.resample(*self.m1, m, 0)
            self.bars[m] = dict(t=bt, h=bh, l=bl, c=bc, nxt=nxt, m=m)
        return self.bars[m]

    # ---- period definitions -------------------------------------------------
    def days(self, sweep_from=7, sweep_to=16, exit_h=20):
        """Per weekday: Asian range (00-07 UTC), previous-day H/L and ATR, previous-week H/L,
        sweep window and exit minute."""
        D = self.D; ts = self.ts
        dkey = D["t"] // DAY
        wkey = (dkey + 3) // 7                              # ISO-week (Monday start)
        wk_h, wk_l = {}, {}
        for i, w in enumerate(wkey):
            wk_h[w] = max(wk_h.get(w, -np.inf), D["h"][i]); wk_l[w] = min(wk_l.get(w, np.inf), D["l"][i])
        rows = []
        for i in range(15, len(dkey)):
            day0 = dkey[i] * DAY
            if ((dkey[i] + 3) % 7) > 4:
                continue
            a = np.searchsorted(ts, day0); b = np.searchsorted(ts, day0 + 7 * 3600)
            if b - a < 120:
                continue
            ah, al = self.h[a:b].max(), self.l[a:b].min()
            pw = wkey[i] - 1
            if pw not in wk_h:
                continue
            rows.append((day0, ah, al, D["h"][i - 1], D["l"][i - 1], D["atr"][i - 1], wk_h[pw], wk_l[pw],
                         day0 + sweep_from * 3600, day0 + sweep_to * 3600, day0 + exit_h * 3600))
        return np.array(rows)

    def weeks(self):
        """Per week: previous-week H/L, window Mon 00:00 - Fri 16:00, exit Fri 20:00."""
        D = self.D; dkey = D["t"] // DAY; wkey = (dkey + 3) // 7
        rows = []
        uw = np.unique(wkey)
        for w in uw[1:]:
            prev = wkey == w - 1; cur = np.flatnonzero(wkey == w)
            if not prev.any() or len(cur) == 0:
                continue
            mon = (w * 7 - 3) * DAY
            atr = D["atr"][cur[0] - 1] if cur[0] > 0 else np.nan
            rows.append((mon, D["h"][prev].max(), D["l"][prev].min(), atr, mon, mon + 4 * DAY + 16 * 3600,
                         mon + 4 * DAY + 20 * 3600))
        return np.array(rows)

    # ---- strategy builder ---------------------------------------------------
    def build(self, level="asian", tfm=15, K=8, kind="reclaim", target="opposite", combo=None,
              buf_atr=0.05, min_stop_atr=0.15):
        B = self.tf(tfm)
        if level == "weekly":
            P = self.weeks()
            H, L, atr = P[:, 1], P[:, 2], P[:, 3]
            t_from, t_to, t_exit = P[:, 4], P[:, 5], P[:, 6]
            pdh = pdl = pwm = None
        else:
            P = self.days()
            if level == "asian":
                H, L = P[:, 1], P[:, 2]
            else:                                            # previous day
                H, L = P[:, 3], P[:, 4]
            atr = P[:, 5]; t_from, t_to, t_exit = P[:, 8], P[:, 9], P[:, 10]
            pdh, pdl, pwm = P[:, 3], P[:, 4], (P[:, 6] + P[:, 7]) / 2
        ok = np.isfinite(atr) & (H > L)
        H, L, atr, t_from, t_to, t_exit = H[ok], L[ok], atr[ok], t_from[ok], t_to[ok], t_exit[ok]
        if pdh is not None:
            pdh, pdl, pwm = pdh[ok], pdl[ok], pwm[ok]
        w0 = np.searchsorted(B["t"], t_from).astype(np.int64)
        w1 = np.searchsorted(B["t"] + B["m"] * 60, t_to, side="right").astype(np.int64)
        ev, ext = sweep_events(B["h"], B["l"], B["c"], w0, w1, H.astype(np.float64), L.astype(np.float64), K)
        exit_i = np.searchsorted(self.ts, t_exit).astype(np.int64)
        rows = []   # (entry_minute, side, sl, tp_abs, tp_r, exit_minute, min_d)
        for p in range(len(H)):
            buf = buf_atr * atr[p]; md = max(min_stop_atr * atr[p], 3 * self.cost)
            mid = (H[p] + L[p]) / 2
            for sideix, (jr, jf, jc) in enumerate(((ev[p, 0], ev[p, 1], ev[p, 2]), (ev[p, 4], ev[p, 5], ev[p, 6]))):
                sx = ext[p, sideix]
                rev_side = -1 if sideix == 0 else 1          # sweep of H -> short
                if kind == "reclaim" and jr >= 0:
                    if combo in ("stack", "stack+bias") and pdh is not None:
                        if (rev_side < 0 and not sx > pdh[p]) or (rev_side > 0 and not sx < pdl[p]):
                            continue
                    if combo in ("bias", "stack+bias") and pwm is not None:
                        px = B["c"][jr]
                        if (rev_side < 0 and px < pwm[p]) or (rev_side > 0 and px > pwm[p]):
                            continue
                    sl = sx + buf if rev_side < 0 else sx - buf
                    if target == "opposite":
                        tpa, tpr = (L[p] if rev_side < 0 else H[p]), 0.0
                    elif target == "mid":
                        tpa, tpr = mid, 0.0
                    else:
                        tpa, tpr = 0.0, float(target)
                    rows.append((B["nxt"][jr], rev_side, sl, tpa, tpr, exit_i[p], md))
                elif kind == "failed" and jf >= 0:
                    s = -rev_side                            # break in the sweep direction
                    lvl = H[p] if s > 0 else L[p]
                    sl = lvl - buf if s > 0 else lvl + buf
                    rows.append((B["nxt"][jf], s, sl, 0.0, float(target), exit_i[p], md))
                elif kind == "follow" and jc >= 0:
                    s = rev_side
                    sl = mid
                    rows.append((B["nxt"][jc], s, sl, 0.0, float(target), exit_i[p], md))
        if not rows:
            return np.zeros(0, dtype=DT)
        R = np.array(rows); o = np.argsort(R[:, 0], kind="stable")
        R = R[o]
        res = run_abs(self.o, self.h, self.l, self.ts, R[:, 0].astype(np.int64), R[:, 1].astype(np.int64),
                      R[:, 2].copy(), R[:, 3].copy(), R[:, 4].copy(), R[:, 5].astype(np.int64), self.cost,
                      R[:, 6].copy(), self.gaps)
        return pack(res)


def variants():
    for tfm in (5, 15):
        for lvl in ("asian", "prevday"):
            for tg in ("opposite", "mid", "1", "2"):
                yield f"SWEEP_{lvl}_M{tfm}_tp{tg}", dict(level=lvl, tfm=tfm, kind="reclaim", target=tg)
            for tg in ("1", "2"):
                yield f"FAILED_{lvl}_M{tfm}_tp{tg}", dict(level=lvl, tfm=tfm, kind="failed", target=tg)
                yield f"FOLLOW_{lvl}_M{tfm}_tp{tg}", dict(level=lvl, tfm=tfm, kind="follow", target=tg)
        for combo in ("stack", "bias", "stack+bias"):
            for tg in ("opposite", "2"):
                yield f"SWEEP_asian_{combo}_M{tfm}_tp{tg}", dict(level="asian", tfm=tfm, kind="reclaim", target=tg, combo=combo)
        for tg in ("opposite", "2"):
            yield f"SWEEP_prevday_bias_M{tfm}_tp{tg}", dict(level="prevday", tfm=tfm, kind="reclaim", target=tg, combo="bias")
    for tg in ("opposite", "mid", "2"):
        yield f"SWEEP_weekly_H1_tp{tg}", dict(level="weekly", tfm=60, K=6, kind="reclaim", target=tg)
    for tg in ("1", "2"):
        yield f"FAILED_weekly_H1_tp{tg}", dict(level="weekly", tfm=60, K=6, kind="failed", target=tg)
        yield f"FOLLOW_weekly_H1_tp{tg}", dict(level="weekly", tfm=60, K=6, kind="follow", target=tg)
