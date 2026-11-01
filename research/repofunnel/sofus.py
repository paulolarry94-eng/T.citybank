"""sofus-nl/swing-trading-strategies @ 1b7cf1c: 18 setups as rules for the d1 engine (PREREG.md section C).

Price-only translation: volume, RS rank, earnings, news, sector baselines, market-regime lines and grades are dropped;
stock percentages become ATR(14) multiples at 2% per ATR. Written once for longs in "view" space; shorts are the
mirror image. Stops: the tighter valid one of those listed. Targets: limit orders. Trailing stops only move up (view).
"""
import os, sys
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d1
from d1 import Rule, prev

NAMES = ["s01_vcp", "s02_cup_handle", "s03_ema_cross", "s04_rsi_pullback", "s07_stage2", "s08_bull_flag",
         "s10_triple_rsi_div", "s11_qullamaggie", "s12_multi_period", "s13_ma_stack", "s14_adx_trend",
         "s16_trend_template", "s18_roc_breakout", "s19_hhv_breakout", "s20_frog_pan", "s21_proximity_pullback",
         "s22_rsi2_reversion", "s23_trend_pullback"]


def rising(x, k=5):
    return x > prev(x, k)


def upper_frac(V):
    rng = V.h - V.l
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(rng > 0, (V.c - V.l) / rng, 0.5)


class Swing(Rule):
    """Common mechanics. Subclasses: sig(V) -> (bool array, dict of per-bar extras or None), plan(V, u, ex) -> dict
    with stops [('atr', k) | ('lvl', x)], tgts [('atr', k, w) | ('lvl', x, w)] (w None = the rest),
    and manage(pos, V, u)."""

    def __init__(self, sym):
        self.sym = sym

    def prepare(self, mk, views):
        Rule.prepare(self, mk, views)
        self.A = views[1].atr(14)
        self.S = {}
        for s in (1, -1):
            V = views[s]
            ok, ex = self.sig(V)
            self.S[s] = (np.nan_to_num(np.asarray(ok, float)) > 0, ex)

    def entry(self, u, s):
        ok, ex = self.S[s]
        if not ok[u] or not np.isfinite(self.A[u]) or self.A[u] <= 0:
            return None
        V = self.V[s]
        pl = self.plan(V, u, ex)
        if pl is None:
            return None
        pl.update(u=u, w=1.0, ref_stop_v=float(V.c[u] - 2 * self.A[u]))
        return pl

    def on_fill(self, mk, pos, u, sig):
        V = self.V[pos.s]; a = self.A[sig["u"]]
        ev = pos.s * pos.units[0][1]
        cands = []
        for st in sig["stops"]:
            x = ev - st[1] * a if st[0] == "atr" else st[1]
            if np.isfinite(x) and x < ev - 1e-12:
                cands.append(x)
        if not cands:
            return False
        stop = max(cands); d = ev - stop
        if d < 3 * mk.cost:
            return False
        lim = []
        for t in sig.get("tgts", []):
            x = ev + t[1] * a if t[0] == "atr" else t[1]
            if np.isfinite(x) and x > ev:
                lim.append((x, t[2]))
        lim.sort(key=lambda z: z[0])
        lim = [(x, 0.5 if w is None else w) for x, w in lim[:-1]] + ([(lim[-1][0], None)] if lim else [])
        # (the farthest target closes whatever is left)
        pos.limits = lim; pos.stop_v = stop
        pos.st.update(d=d, ev=ev, a=a, hi=ev, hc=ev, u0=sig["u"], below=0)
        pos.st.update({k: v for k, v in sig.items() if k not in ("stops", "tgts")})
        return True

    def on_close(self, mk, pos, u):
        V = self.V[pos.s]; st = pos.st
        st["hi"] = max(st["hi"], V.h[u]); st["hc"] = max(st["hc"], V.c[u])
        self.manage(pos, V, u)

    def raise_stop(self, pos, x):
        if x is not None and np.isfinite(x):
            pos.stop_v = max(pos.stop_v, x)

    def t1(self, pos):
        return pos.n_limit_fills >= 1

    def manage(self, pos, V, u):
        pass


# ----------------------------------------------------------------------------- the setups
class VCP(Swing):
    def sig(self, V):
        A = V.atr(14)
        base = (V.c > V.sma(50)) & (V.sma(50) > V.sma(150)) & (V.sma(150) > V.sma(200))
        base &= V.c >= V.hh(252) - 12.5 * A
        base &= (prev(V.c, 65) - prev(V.ll(130), 65)) >= 12.5 * A
        fh = d1.fractal_highs(V.h)
        ok = np.zeros(len(V.c), bool); piv = np.full(len(V.c), np.nan)
        for u in np.flatnonzero(base):
            ks = fh[(fh >= u - 65) & (fh <= u - 2)]
            if len(ks) < 3:
                continue
            dep = []
            for i, k in enumerate(ks):
                e = ks[i + 1] if i + 1 < len(ks) else u
                dep.append(V.h[k] - np.min(V.l[k + 1:e]) if e > k + 1 else 0.0)
            a, b, c = dep[-3:]
            p = V.h[ks[-1]]
            if a > b > c and c <= 0.5 * a and V.c[u] > p >= V.c[u - 1]:
                ok[u] = True; piv[u] = p
        return ok, None

    def plan(self, V, u, ex):
        return dict(stops=[("atr", 1.5)], tgts=[("atr", 2.0, 0.5), ("atr", 4.0, None)])

    def manage(self, pos, V, u):
        if self.t1(pos) and V.c[u] < V.swing_low()[u]:
            pos.exit_all = True


class CupHandle(Swing):
    def sig(self, V):
        A = V.atr(14); n = len(V.c)
        cand = V.sma(50) > V.sma(200)
        ok = np.zeros(n, bool); rl_arr = np.full(n, np.nan)
        for u in np.flatnonzero(cand):
            if u < 230:
                continue
            a = A[u]
            for hl in range(5, 16):
                hs = u - hl
                hh_ = np.max(V.h[hs:u]); hlo = np.min(V.l[hs:u])
                if not V.c[u] > hh_:
                    continue
                RL = np.max(V.h[hs - 5:hs])
                if hh_ > RL:
                    continue
                w0, w1 = hs - 65, hs - 15
                kL = w0 + int(np.argmax(V.h[w0:w1 + 1])); LL = V.h[kL]
                seg = V.l[kL:hs]
                kB = kL + int(np.argmin(seg)); CB = seg.min(); D = LL - CB
                if not (6 * a <= D <= 17.5 * a):
                    continue
                span = hs - 1 - kL
                if span <= 0 or not (0.2 <= (kB - kL) / span <= 0.8):
                    continue
                if RL < LL - 0.1 * D or hlo < CB + 0.5 * D or RL - hlo > 0.12 * D:
                    continue
                if LL - np.min(V.l[max(0, kL - 130):kL]) < 15 * a:
                    continue
                ok[u] = True; rl_arr[u] = RL
                break
        return ok, rl_arr

    def plan(self, V, u, ex):
        return dict(stops=[("atr", 1.5)], tgts=[("atr", 2.5, 0.4), ("atr", 5.0, None)], rl=float(ex[u]))

    def manage(self, pos, V, u):
        if self.t1(pos) and (V.c[u] < V.swing_low()[u] or V.c[u] < pos.st["rl"]):
            pos.exit_all = True


class EMACross(Swing):
    def sig(self, V):
        e9, e21 = V.ema(9), V.ema(21); r = V.rsi(14); adx = V.dmi(14)[2]
        cross = (e9 > e21) & (prev(e9) <= prev(e21))
        return cross & (V.c > V.sma(50)) & (V.sma(50) >= prev(V.sma(50), 5)) & (adx > 20) & (r >= 50) & (r <= 70), None

    def plan(self, V, u, ex):
        return dict(stops=[("atr", 1.5), ("lvl", float(V.ema(21)[u]))], tgts=[("atr", 1.5, 0.5), ("atr", 3.0, None)])

    def manage(self, pos, V, u):
        if V.ema(9)[u] < V.ema(21)[u]:
            pos.exit_all = True; return
        if self.t1(pos):
            self.raise_stop(pos, V.c[u] - 1.5 * self.A[u])


class RSIPullback(Swing):
    def sig(self, V):
        r = V.rsi(14); adx = V.dmi(14)[2]; e21 = V.ema(21)
        was70 = pd.Series(prev(r)).rolling(10, min_periods=10).max().to_numpy() > 70
        return ((V.c > V.sma(200)) & (r >= 40) & (r <= 50) & was70 & (V.c > e21) & rising(e21)
                & (upper_frac(V) >= 0.4) & (adx > 20)), None

    def plan(self, V, u, ex):
        return dict(stops=[("atr", 2.0), ("lvl", float(V.swing_low()[u]))], tgts=[("atr", 1.5, None)])

    def manage(self, pos, V, u):
        r = V.rsi(14)
        if r[u] > 70 >= r[u - 1]:
            pos.exit_all = True; return
        if pos.bars >= 5:
            self.raise_stop(pos, pos.st["hc"] - 2.5 * self.A[u])


class Stage2(Swing):
    def sig(self, V):
        s150 = V.sma(150); A = V.atr(14)
        return (s150 > prev(s150, 20)) & (V.c > prev(V.hh(63))) & (V.c <= s150 + 7.5 * A), None

    def plan(self, V, u, ex):
        return dict(stops=[("lvl", float(V.sma(150)[u])), ("lvl", float(prev(V.ll(63))[u]))], tgts=[("atr", 10.0, 0.5)])

    def on_fill(self, mk, pos, u, sig):
        okk = Swing.on_fill(self, mk, pos, u, sig)
        if okk:
            pos.limits = [(x, 0.5) for x, w in pos.limits]       # partial only: the rest rides the trailing stop
        return okk

    def manage(self, pos, V, u):
        s150 = V.sma(150)
        if s150[u] <= s150[u - 10]:
            pos.exit_all = True; return
        self.raise_stop(pos, s150[u])


class BullFlag(Swing):
    def sig(self, V):
        A = V.atr(14); e21 = V.ema(21); r = V.rsi(14); n = len(V.c)
        cand = (V.c > e21) & (r >= 50) & (r <= 70)
        ok = np.zeros(n, bool); info = np.full((n, 3), np.nan)
        for u in np.flatnonzero(cand):
            if u < 40:
                continue
            for f in range(5, 16):
                fs = u - f
                fh = np.max(V.h[fs:u]); fl = np.min(V.l[fs:u])
                if not V.c[u] > fh or np.any(V.c[fs:u] <= e21[fs:u]):
                    continue
                top = np.max(V.h[fs - 3:fs]); bot = np.min(V.l[fs - 15:fs]); H = top - bot
                if top < fh or H < 5 * A[u] or (top - fl) >= 0.5 * H:
                    continue
                ok[u] = True; info[u] = (fh, fl, H)
                break
        return ok, info

    def plan(self, V, u, ex):
        fh, fl, H = ex[u]
        return dict(stops=[("lvl", float(fl)), ("atr", 1.5)], tgts=[("lvl", float(fh + H), 0.5), ("lvl", float(fh + 1.5 * H), None)])

    def manage(self, pos, V, u):
        if self.t1(pos):
            self.raise_stop(pos, V.swing_low()[u])


class TripleDiv(Swing):
    def sig(self, V):
        r = V.rsi(14); n = len(V.c); fl = d1.fractal_lows(V.l)
        body = np.abs(V.c - V.o); lw = np.minimum(V.o, V.c) - V.l; uw = V.h - np.maximum(V.o, V.c)
        engulf = (V.c > V.o) & (prev(V.o) > prev(V.c)) & (V.c >= prev(V.o)) & (V.o <= prev(V.c))
        hammer = (lw >= 2 * body) & (uw <= body) & (upper_frac(V) >= 2 / 3)
        conf = (engulf | hammer) & (r > 30)
        ok = np.zeros(n, bool); info = np.full((n, 2), np.nan)
        for u in np.flatnonzero(conf):
            ks = fl[(fl >= u - 60) & (fl <= u - 1)]
            if len(ks) < 3:
                continue
            k1, k2, k3 = ks[-3:]
            if u - k3 > 5:
                continue
            if V.l[k1] > V.l[k2] > V.l[k3] and r[k1] < r[k2] < r[k3]:
                ok[u] = True; info[u] = (V.l[k3], np.max(V.h[k1:k3 + 1]))
        return ok, info

    def plan(self, V, u, ex):
        low, res = ex[u]
        return dict(stops=[("lvl", float(low) - 1e-9)], tgts=[("lvl", float(res), 0.5), ("atr", 2.0, None)])

    def manage(self, pos, V, u):
        self.raise_stop(pos, pos.st["hi"] - 2.5 * self.A[u])


class Qull(Swing):
    def sig(self, V):
        A = V.atr(14); e20 = V.ema(20); a5 = V.atr(5); n = len(V.c)
        ok = np.zeros(n, bool); info = np.full(n, np.nan)
        pre = V.c > prev(V.hh(5))
        for u in range(80, n):
            if not pre[u] or not np.isfinite(A[u]):
                continue
            for cl in range(5, 16):
                bs = u - cl
                bh = np.max(V.h[bs:u]); bl = np.min(V.l[bs:u])
                if not V.c[u] > bh:
                    continue
                if np.any(V.c[bs:u] <= e20[bs:u]) or not e20[u - 1] > e20[bs] or not a5[u - 1] < a5[bs]:
                    continue
                w = slice(bs - 63, bs)
                lo_k = int(np.argmin(V.l[w])); hi_k = int(np.argmax(V.h[w]))
                leg = V.h[w][hi_k] - V.l[w][lo_k]
                if lo_k >= hi_k or leg < 15 * A[u] or (bh - bl) >= 0.10 * leg:
                    continue
                ok[u] = True; info[u] = bl
                break
        return ok, info

    def plan(self, V, u, ex):
        return dict(stops=[("lvl", float(ex[u])), ("atr", 1.5)], tgts=[("atr", 2.0, 0.5)])

    def on_fill(self, mk, pos, u, sig):
        okk = Swing.on_fill(self, mk, pos, u, sig)
        if okk:
            pos.limits = [(x, 0.5) for x, w in pos.limits]
        return okk

    def manage(self, pos, V, u):
        if pos.bars >= 25:
            pos.exit_all = True; return
        if self.t1(pos):
            if V.c[u] < V.ema(10)[u]:
                pos.exit_all = True; return
            self.raise_stop(pos, pos.st["hi"] - 1.5 * self.A[u])


def _trigger(V):
    """Pullback to EMA21 (low <= EMA21 < close) or the first new 20-bar closing high after 5 bars without one."""
    e21 = V.ema(21); nh = V.c > prev(V.hh(20))
    recent = pd.Series(prev(nh.astype(float))).rolling(5, min_periods=5).max().to_numpy() > 0
    return ((V.l <= e21) & (e21 < V.c)) | (nh & ~recent)


class MultiPeriod(Swing):
    def sig(self, V):
        c = V.c; s50, s200 = V.sma(50), V.sma(200)
        return ((c > prev(c, 63)) & (c > prev(c, 126)) & (c > prev(c, 252)) & (c > s50) & (c > s200)
                & rising(s50) & rising(s200) & _trigger(V)), None

    def plan(self, V, u, ex):
        return dict(stops=[("atr", 2.0)], tgts=[("atr", 2.5, 0.5)])

    def on_fill(self, mk, pos, u, sig):
        okk = Swing.on_fill(self, mk, pos, u, sig)
        if okk:
            pos.limits = [(x, 0.5) for x, w in pos.limits]
        return okk

    def manage(self, pos, V, u):
        if V.c[u] < V.c[u - 63]:
            pos.exit_all = True; return
        if self.t1(pos):
            self.raise_stop(pos, V.swing_low()[u])


class MAStack(Swing):
    def sig(self, V):
        e10, e21, s50, s200 = V.ema(10), V.ema(21), V.sma(50), V.sma(200)
        A = V.atr(14)
        return ((e10 > e21) & (e21 > s50) & (s50 > s200) & rising(e10) & rising(e21) & rising(s50) & rising(s200)
                & (np.abs(V.c - e10) <= 2.5 * A)), None

    def plan(self, V, u, ex):
        return dict(stops=[("atr", 1.5), ("lvl", float(V.ema(21)[u]))], tgts=[("atr", 2.5, 0.5)])

    def on_fill(self, mk, pos, u, sig):
        okk = Swing.on_fill(self, mk, pos, u, sig)
        if okk:
            pos.limits = [(x, 0.5) for x, w in pos.limits]
        return okk

    def manage(self, pos, V, u):
        if V.ema(10)[u] < V.ema(21)[u] or V.c[u] < V.sma(50)[u]:
            pos.exit_all = True


class ADXTrend(Swing):
    def sig(self, V):
        p, m, adx = V.dmi(14)
        return ((adx > 25) & (adx > prev(adx, 3)) & (p > m) & ((p - m) > prev(p - m)) & (V.c > V.sma(50))
                & (upper_frac(V) >= 0.5)), None

    def plan(self, V, u, ex):
        return dict(stops=[("atr", 1.5), ("lvl", float(V.swing_low()[u]))], tgts=[("atr", 2.0, 0.5)])

    def on_fill(self, mk, pos, u, sig):
        okk = Swing.on_fill(self, mk, pos, u, sig)
        if okk:
            pos.limits = [(x, 0.5) for x, w in pos.limits]
        return okk

    def manage(self, pos, V, u):
        p, m, adx = V.dmi(14)
        if not self.t1(pos):
            if m[u] > p[u] and m[u - 1] <= p[u - 1]:
                pos.exit_all = True
            return
        if adx[u] < 20:
            pos.exit_all = True; return
        self.raise_stop(pos, V.c[u] - 1.5 * self.A[u])


class TrendTemplate(Swing):
    def conds(self, V):
        if not hasattr(V, "_tt"):
            c = V.c; s50, s150, s200 = V.sma(50), V.sma(150), V.sma(200); A = V.atr(14)
            C = np.vstack([(c > s150) & (c > s200), s150 > s200, s200 > prev(s200, 21), (s50 > s150) & (s50 > s200),
                           c > s50, c >= V.ll(252) + 15 * A, c >= V.hh(252) - 12.5 * A])
            V._tt = C
        return V._tt

    def sig(self, V):
        C = self.conds(V)
        allc = C.all(axis=0); fails = (~C).sum(axis=0)
        fresh = pd.Series(prev((fails >= 2).astype(float))).rolling(20, min_periods=20).max().to_numpy() > 0
        ready = np.isfinite(V.hh(252))
        return allc & fresh & ready, None

    def plan(self, V, u, ex):
        return dict(stops=[("atr", 1.5), ("lvl", float(V.sma(50)[u]))], tgts=[("atr", 2.0, 0.33)])

    def on_fill(self, mk, pos, u, sig):
        okk = Swing.on_fill(self, mk, pos, u, sig)
        if okk:
            pos.limits = [(x, 0.33) for x, w in pos.limits]
        return okk

    def manage(self, pos, V, u):
        C = self.conds(V)
        if V.c[u] < V.sma(50)[u] or not C[:, u].all():
            pos.exit_all = True; return
        if self.t1(pos):
            self.raise_stop(pos, max(V.swing_low()[u], V.sma(50)[u]))


class ROCBreakout(Swing):
    def roc(self, V):
        return V.get(("roc21",), lambda: (V.c - prev(V.c, 21)) / np.abs(prev(V.c, 21)))

    def sig(self, V):
        r = self.roc(V)
        return (V.c > prev(V.hh(20))) & (r > 0) & (r > prev(r, 5)) & (V.c > V.sma(50)), None

    def plan(self, V, u, ex):
        return dict(stops=[("lvl", float(prev(V.hh(20))[u])), ("atr", 1.5)], tgts=[("atr", 2.0, 0.5)])

    def on_fill(self, mk, pos, u, sig):
        okk = Swing.on_fill(self, mk, pos, u, sig)
        if okk:
            pos.limits = [(x, 0.5) for x, w in pos.limits]
        return okk

    def manage(self, pos, V, u):
        if self.roc(V)[u] < 0:
            pos.exit_all = True; return
        if self.t1(pos):
            self.raise_stop(pos, V.swing_low()[u])


class HHV(Swing):
    def sig(self, V):
        s50 = V.sma(50)
        return (V.c > prev(V.hh(20))) & (V.c > s50) & rising(s50), None

    def plan(self, V, u, ex):
        return dict(stops=[("lvl", float(V.l[u])), ("atr", 2.0)], tgts=[])

    def manage(self, pos, V, u):
        if V.c[u] < V.get(("pll", 10), lambda: prev(V.ll(10)))[u]:
            pos.exit_all = True


class Frog(Swing):
    def sig(self, V):
        c = V.c; A = V.atr(14); n = len(c)
        dc = np.r_[np.nan, np.diff(c)]
        pos_ = pd.Series((dc > 0).astype(float)).rolling(126, min_periods=126).mean().to_numpy()
        neg_ = pd.Series((dc < 0).astype(float)).rolling(126, min_periods=126).mean().to_numpy()
        pret = c - prev(c, 126)
        ID = np.sign(pret) * (neg_ - pos_)
        q = pd.Series(prev(ID)).rolling(756, min_periods=252).quantile(1 / 3).to_numpy()
        gap = np.abs(V.o - prev(c)) / A
        maxgap = pd.Series(gap).rolling(126, min_periods=126).max().to_numpy()
        return ((pret > 0) & (ID <= q) & (maxgap <= 3) & (c > V.sma(50)) & (c > V.sma(200)) & _trigger(V)), None

    def plan(self, V, u, ex):
        return dict(stops=[("atr", 2.0)], tgts=[("atr", 2.5, 0.5)])

    def on_fill(self, mk, pos, u, sig):
        okk = Swing.on_fill(self, mk, pos, u, sig)
        if okk:
            pos.limits = [(x, 0.5) for x, w in pos.limits]
        return okk

    def manage(self, pos, V, u):
        if abs(V.o[u] - V.c[u - 1]) > 2.5 * self.A[u]:
            pos.exit_all = True; return
        if self.t1(pos):
            self.raise_stop(pos, max(V.swing_low()[u], V.ema(21)[u]))


class Proximity(Swing):
    def sig(self, V):
        A = V.atr(14); e21, s50 = V.ema(21), V.sma(50); hh252 = V.hh(252); n = len(V.c)
        hold = ((V.c > e21) & rising(e21)) | ((V.c > s50) & rising(s50))
        cand = hold & (upper_frac(V) >= 0.5) & np.isfinite(hh252)
        ok = np.zeros(n, bool); info = np.full((n, 3), np.nan)
        for u in np.flatnonzero(cand):
            w = V.h[u - 10:u]
            kRH = u - 10 + int(len(w) - 1 - np.argmax(w[::-1]))     # most recent bar holding the 10-bar high
            RH = V.h[kRH]
            if not (3 <= u - kRH <= 10) or RH < hh252[kRH] - 2.5 * A[u]:
                continue
            PL = np.min(V.l[kRH + 1:u + 1]); dep = RH - PL
            if 1.5 * A[u] <= dep <= 5 * A[u]:
                ok[u] = True; info[u] = (RH, PL, dep)
        return ok, info

    def plan(self, V, u, ex):
        RH, PL, dep = ex[u]
        return dict(stops=[("lvl", float(PL)), ("atr", 1.5)], tgts=[("lvl", float(RH), 0.5)], dep=float(dep))

    def on_fill(self, mk, pos, u, sig):
        okk = Swing.on_fill(self, mk, pos, u, sig)
        if okk:
            T2 = pos.st["ev"] + 2 * pos.st["dep"]
            lim = [(x, 0.5) for x, w in pos.limits if x < T2] + [(T2, None)]
            pos.limits = sorted(lim, key=lambda z: z[0])
        return okk

    def manage(self, pos, V, u):
        if self.t1(pos):
            self.raise_stop(pos, max(V.swing_low()[u], V.c[u] - 1.5 * self.A[u]))


class RSI2(Swing):
    def sig(self, V):
        r2 = V.rsi(2); A = V.atr(14)
        return (V.c > V.sma(200)) & (r2 < 10) & (V.c >= V.ll(252) + 2.5 * A), None

    def plan(self, V, u, ex):
        return dict(stops=[("atr", 2.0)], tgts=[])

    def manage(self, pos, V, u):
        r2 = V.rsi(2)
        if (r2[u] > 70 >= r2[u - 1]) or pos.bars >= 5 or V.c[u] < V.sma(200)[u]:
            pos.exit_all = True


class TrendPullback(Swing):
    def sig(self, V):
        e20, s50 = V.ema(20), V.sma(50); A = V.atr(14)
        near = ((V.l - e20) <= A) | ((V.l - s50) <= A)
        return ((V.c > s50) & (e20 > s50) & rising(e20) & rising(s50) & near & (upper_frac(V) >= 0.5)), None

    def plan(self, V, u, ex):
        return dict(stops=[("atr", 1.5), ("lvl", float(V.ema(20)[u]))], tgts=[("atr", 2.0, 0.5)])

    def on_fill(self, mk, pos, u, sig):
        okk = Swing.on_fill(self, mk, pos, u, sig)
        if okk:
            pos.limits = [(x, 0.5) for x, w in pos.limits]
        return okk

    def manage(self, pos, V, u):
        s50 = V.sma(50)
        if V.c[u] < s50[u] and V.c[u - 1] < s50[u - 1]:
            pos.exit_all = True; return
        if self.t1(pos):
            self.raise_stop(pos, max(V.swing_low()[u], pos.st["hi"] - 1.5 * self.A[u]))


CLASSES = {"s01_vcp": VCP, "s02_cup_handle": CupHandle, "s03_ema_cross": EMACross, "s04_rsi_pullback": RSIPullback,
           "s07_stage2": Stage2, "s08_bull_flag": BullFlag, "s10_triple_rsi_div": TripleDiv, "s11_qullamaggie": Qull,
           "s12_multi_period": MultiPeriod, "s13_ma_stack": MAStack, "s14_adx_trend": ADXTrend,
           "s16_trend_template": TrendTemplate, "s18_roc_breakout": ROCBreakout, "s19_hhv_breakout": HHV,
           "s20_frog_pan": Frog, "s21_proximity_pullback": Proximity, "s22_rsi2_reversion": RSI2,
           "s23_trend_pullback": TrendPullback}
assert list(CLASSES) == NAMES


def make_rule(p, sym):
    return CLASSES[p["rule"]](sym)


def sides_of(p):
    return (1,) if p.get("side", "long") == "long" else (1, -1)
