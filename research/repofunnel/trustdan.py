"""trustdan/trend-following-backtesting-strategies @ a34b7ba: the 48 Pine scripts as rules for the d1 engine.

Translated line by line (PREREG.md section B). Each rule is written once in "view" space (prices x side, highs/lows
swapped), which is exactly Pine's long/short symmetry. Defaults are the source's inputs.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d1
from d1 import Rule, prev

T369 = [3.0, 6.0, 9.0]
BASE = dict(entry=("don", 55), filters=(), stopN=2.0, add=dict(step=0.5, max=4, trig="close", gate=None),
            sizes=None, w0=1.0, init="avg", trail=("don", 10), tighten=None, be=None, targets=None, close_w=1.0,
            time_exit=None, confirm=None)


def R(**kw):
    c = {k: (dict(v) if isinstance(v, dict) else v) for k, v in BASE.items()}
    for k, v in kw.items():
        if k == "add":
            c["add"] = dict(c["add"], **v)
        else:
            c[k] = v
    return c


A10 = dict(add=dict(trig="high"), init="avg", trail=("chand", 22, 3.0), targets=T369)        # alt10 family core
A10E = dict(A10, init="entry")                                                                # ...with entry-price init stop
FRAC = [1.0, 0.75, 0.5, 0.25]
A26 = dict(A10E, sizes=FRAC)
RSI_ADD = dict(trig="high", gate=("rsi", 60))

RULES = {
    "core": R(),
    "alt1": R(entry=("don", 20)),
    "alt2": R(entry=("ema_cross", 50, 200), stopN=2.5, add=dict(trig="high"), trail=("chand", 22, 3.0)),
    "alt3": R(entry=("atr_channel", 100, 2.0), add=dict(trig="high"), trail=("atr_band", 100, 2.0)),
    "alt4": R(entry=("weekly", 26), add=dict(trig="high"), trail=("weekly_lo", 13)),
    "alt5": R(filters=(("tide", 200),)),
    "alt6": R(trail=None),
    "alt7": R(add=dict(trig="high"), trail=("chand", 22, 3.0)),
    "alt8": R(trail=("adaptive", 5, 20, 100, 50)),
    "alt9": R(time_exit=(40, 3)),
    "alt10": R(**A10),
    "alt11": R(sizes=[1.0, 0.75, 0.5, 0.33]),
    "alt12": R(add=dict(step=0.25, max=6, trig="high"), w0=0.75, sizes=[0.75] * 6),
    "alt13": R(add=dict(trig="high", gate=("volgate", 20, 1.0))),
    "alt14": R(add=dict(trig="high", gate=("pullback", 10))),
    "alt15": R(w0=4.0, add=dict(max=1)),
    "alt16": R(filters=(("antichop",),), add=dict(gate=("antichop",))),
    "alt17": R(filters=(("htf", 26),)),
    "alt18": R(sizes="regime"),
    "alt19": R(entry=("intrabar", 55), add=dict(trig="high")),
    "alt20": R(entry=("asym", 55, 35), stopN=(2.0, 2.5), add=dict(step=(0.5, 0.75)), trail=("bug_don", 10)),
    "alt21": R(**dict(A10E, be=("lock", 2.0))),
    "alt22": R(**dict(A10E, trail=("sar", 0.02, 0.02, 0.2))),
    "alt23": R(**dict(A10E, entry=("keltner", 55, 2.5))),
    "alt24": R(**dict(A10E, targets=("volfactor", [2.5, 5.0, 8.0], 100, 0.5))),
    "alt25": R(**dict(A10E, tighten=(30, 1.5))),
    "alt26": R(**A26),
    "alt27": R(**dict(A10E, stopN=1.5, trail=("chand", 22, 2.5), targets=[4.0, 8.0, 12.0])),
    "alt28": R(**dict(A10E, filters=(("adx_ge", 25),))),
    "alt29": R(**dict(A10E, add=dict(trig="high", max=6), w0=0.75, sizes=[0.75] * 6, targets=[1.5, 3.0, 5.0, 7.0, 10.0],
                      close_w=0.75)),
    "alt30": R(**dict(A10E, add=RSI_ADD)),
    "alt31": R(**dict(A26, be=("lock", 2.0))),
    "alt32": R(**dict(A10E, add=RSI_ADD, tighten=(30, 1.5))),
    "alt33": R(**dict(A10E, be=("prog",))),
    "alt34": R(**dict(A26, add=RSI_ADD)),
    "alt35": R(**dict(A26, tighten=(30, 1.5))),
    "alt36": R(**dict(A10E, be=("lock", 2.0), add=RSI_ADD)),
    "alt37": R(**dict(A10E, be=("lock", 2.0), tighten=(30, 1.5))),
    "alt38": R(**dict(A26, be=("lock", 2.0), add=RSI_ADD)),
    "alt39": R(**dict(A10E, targets=("age",))),
    "alt40": R(**dict(A26, be=("lock", 2.0), add=RSI_ADD, tighten=(30, 1.5))),
    "alt41": "special",
    "alt42": "special",
    "alt43": R(**dict(A10E, targets=("vol", 20, 1.15, 0.85))),
    "alt44": R(**dict(A10E, filters=(("adx_gt", 25),), targets=[3.0, 6.0, 9.0, 12.0])),
    "alt45": R(**dict(A10E, filters=(("rsi_gt", 50),), targets=("age",))),
    "alt46": R(**dict(A10E, targets=("asset",))),
    "alt47": R(**dict(A10E, w0=0.5, confirm=(5, 60), targets=[3.0, 6.0, 9.0, 12.0], close_w=0.5)),
}
NAMES = list(RULES)
ASSET = {"EURUSD": [3.0, 6.0, 9.0], "GBPUSD": [3.0, 6.0, 9.0], "USDJPY": [3.0, 6.0, 9.0],
         "US500": [4.0, 7.0, 10.0], "NAS100": [4.0, 7.0, 10.0], "GER40": [4.0, 7.0, 10.0], "UK100": [4.0, 7.0, 10.0],
         "JP225": [4.0, 7.0, 10.0], "XAUUSD": [2.0, 4.0, 6.0], "XAGUSD": [2.0, 4.0, 6.0], "WTI": [2.0, 4.0, 6.0]}

_US500 = {}


def us500_regime_days():
    """(day numbers, risk %) of the US500 SMA50 vs SMA200 regime on merged daily bars (alt18's SPY)."""
    if "r" not in _US500:
        import engine as E
        ts, o, h, l, c = E.load_m1("US500")
        bt, bo, bh, bl, bc, nxt = E.resample(ts, o, h, l, c, 1440, 120)
        B = dict(t=bt.astype(np.int64), o=bo, h=bh, l=bl, c=bc, nxt=nxt.astype(np.int64), first=np.r_[0, nxt[:-1]].astype(np.int64))
        D = d1.merge_daily(B)
        f, s = d1.sma(D["c"], 50), d1.sma(D["c"], 200)
        risk = np.where(f > s, 1.5, np.where(f < s, 0.5, 1.0))
        risk[~(np.isfinite(f) & np.isfinite(s))] = 1.0
        _US500["r"] = (D["day"], risk)
    return _US500["r"]


def weekly(V, D, n_hi, n_lo=None):
    """Pine request.security(weekly) on historical daily bars: the last completed week, switching on Friday's bar.
    Returns per daily bar: weekly close, highest weekly high of the n_hi weeks before, lowest weekly low of the n_lo
    weeks before (view prices)."""
    wk = (D["day"] + 3) // 7
    ids, start = np.unique(wk, return_index=True)
    ends = np.r_[start[1:], len(wk)] - 1
    wh = np.maximum.reduceat(V.h, start); wl = np.minimum.reduceat(V.l, start); wc = V.c[ends]
    hi = prev(d1.highest(wh, n_hi)); lo = prev(d1.lowest(wl, n_lo)) if n_lo else None
    j = np.searchsorted(ids, wk)                           # index of each bar's own week
    use = np.where(D["wd"] == 4, j, j - 1)                 # Friday: this week; otherwise the last completed one
    ok = use >= 0; use = np.clip(use, 0, None)
    f = lambda a: np.where(ok, a[use], np.nan)
    return f(wc), f(hi), (f(lo) if lo is not None else None)


class Turtle(Rule):
    def __init__(self, name, sym):
        self.name = name; self.cfg = RULES[name]; self.sym = sym; self.last_time_exit = -10 ** 9

    def _side(self, x, s):
        return x[0] if s > 0 else x[1]

    def prepare(self, mk, views):
        Rule.prepare(self, mk, views)
        cfg = self.cfg; D = views[1].D
        self.N = views[1].atr(20)
        self.sig = {}; self.arr = {}
        for s in (1, -1):
            V = views[s]; e = cfg["entry"]
            if e[0] == "don":
                sig = V.c > prev(V.hh(e[1]))
            elif e[0] == "asym":
                sig = V.c > prev(V.hh(e[1] if s > 0 else e[2]))
            elif e[0] == "intrabar":
                sig = V.h > prev(V.hh(e[1]))
            elif e[0] == "ema_cross":
                f, sl = V.ema(e[1]), V.ema(e[2])
                sig = (f > sl) & (prev(f) <= prev(sl))
            elif e[0] == "atr_channel":
                sig = V.c > prev(V.sma(e[1]) + e[2] * self.N)
            elif e[0] == "keltner":
                sig = V.c > prev(V.ema(e[1]) + e[2] * V.atr(e[1]))
            elif e[0] == "weekly":
                wc, hi, lo = weekly(V, D, e[1], 13)
                sig = V.c > hi
                self.arr[("wlo", s)] = lo
            for flt in cfg["filters"]:
                sig = sig & self._filter(flt, V, s, D)
            self.sig[s] = np.nan_to_num(sig.astype(float)) > 0
            if cfg["trail"] and cfg["trail"][0] == "weekly_lo" and ("wlo", s) not in self.arr:
                self.arr[("wlo", s)] = weekly(V, D, 26, cfg["trail"][1])[2]
        if cfg["trail"] and cfg["trail"][0] == "sar":
            for s in (1, -1):
                V = views[s]
                self.arr[("sar", s)] = V.get(("sar",) + tuple(cfg["trail"][1:]), lambda: d1.sar(V.h, V.l, V.c, *cfg["trail"][1:]))
        if cfg["sizes"] == "regime":
            self.regime = None
            if mk is not None:
                days, risk = us500_regime_days()
                j = np.searchsorted(days, D["day"], side="right") - 1
                self.regime = np.where(j >= 0, risk[np.clip(j, 0, None)], 1.0)

    def _filter(self, flt, V, s, D):
        k = flt[0]
        if k == "tide":
            return V.c > V.sma(flt[1])
        if k in ("adx_ge", "adx_gt"):
            adx = V.dmi(14)[2]
            return adx >= flt[1] if k == "adx_ge" else adx > flt[1]
        if k == "rsi_gt":
            return V.rsi(14) > flt[1]
        if k == "antichop":
            return self._antichop()
        if k == "htf":
            wc, hi, _ = weekly(V, D, flt[1])
            return wc > hi
        raise ValueError(flt)

    def _antichop(self):
        if not hasattr(self, "_ac"):
            V = self.V[1]; c = V.c
            adx = V.dmi(14)[2]
            ch = np.abs(c - prev(c, 20))
            vol = d1.pd.Series(np.abs(np.diff(c, prepend=np.nan))).rolling(20, min_periods=20).sum().to_numpy()
            er = np.where(vol > 0, ch / vol, 0.0)
            up = (np.diff(c, prepend=np.nan) > 0).astype(float)          # close[i] > close[i+1] for i = 1..20
            ts = d1.pd.Series(prev(up)).rolling(20, min_periods=20).sum().to_numpy() / 20 * 100
            self._ac = (adx > 25) & (er > 0.3) & ((ts > 80) | (ts < 20))
        return self._ac

    def smaN(self, n):
        return self.V[1].get(("smaN", n), lambda: d1.sma(self.N, n))

    def _size(self, unit_no, u):
        cfg = self.cfg
        if cfg["sizes"] == "regime":
            return float(self.regime[u]) if self.regime is not None else 1.0
        if cfg["sizes"]:
            return cfg["sizes"][min(unit_no, len(cfg["sizes"])) - 1]
        return cfg["w0"]

    def entry(self, u, s):
        if not self.sig[s][u] or not np.isfinite(self.N[u]):
            return None
        if self.cfg["time_exit"] and u - self.last_time_exit < self.cfg["time_exit"][1]:
            return None
        V = self.V[s]; stopN = self.cfg["stopN"]; stopN = stopN if np.isscalar(stopN) else self._side(stopN, s)
        vr = None
        if self.cfg["targets"] and self.cfg["targets"][0] == "volfactor":
            vr = float(self.N[u] / self.smaN(self.cfg["targets"][2])[u])
        return dict(w=self._size(1, u), N=float(self.N[u]), ev=float(V.c[u]), stopN=stopN,
                    ref_stop_v=float(V.c[u] - stopN * self.N[u]), vr=vr)

    def on_fill(self, mk, pos, u, sig):
        st = pos.st
        st.update(N=sig["N"], ev=sig["ev"], last=sig["ev"], units=1, hits=0, be=False, bel=0, flag=False, conf=False,
                  stopN=sig["stopN"], vr=sig["vr"])
        st["d"] = sig["stopN"] * sig["N"]
        pos.stop_v = sig["ev"] - sig["stopN"] * sig["N"]       # protective stop from the entry minute (deviation 1)
        return True

    def _targets(self, pos):
        t = self.cfg["targets"]
        if t is None:
            return None
        if isinstance(t, list):
            return t
        if t[0] == "age":
            b = pos.bars
            return [4.0, 7.0, 10.0] if b <= 15 else ([3.0, 6.0, 9.0] if b <= 30 else [2.0, 4.0, 6.0])
        if t[0] == "vol":
            r = self.N[self._u] / self.smaN(t[1])[self._u]
            return [4.0, 7.0, 10.0] if r > t[2] else ([2.0, 4.0, 6.0] if r < t[3] else [3.0, 6.0, 9.0])
        if t[0] == "volfactor":
            vf = 1 + t[3] * (pos.st["vr"] - 1) if pos.st["vr"] is not None and np.isfinite(pos.st["vr"]) else None
            return None if vf is None else [x * vf for x in t[1]]
        if t[0] == "asset":
            return ASSET[self.sym]
        raise ValueError(t)

    def on_close(self, mk, pos, u):
        cfg = self.cfg; st = pos.st; s = pos.s; V = self.V[s]; self._u = u
        N_e = st["N"]; ev = st["ev"]; c = V.c[u]; h = V.h[u]
        add = cfg["add"]; step = add["step"] if np.isscalar(add["step"]) else self._side(add["step"], s)
        # alt47: confirmation add (before the regular adds)
        if cfg["confirm"] and not st["conf"] and 0 < pos.bars <= cfg["confirm"][0] and V.rsi(14)[u] > cfg["confirm"][1]:
            pos.add_w += 1.0 - cfg["w0"]; st["conf"] = True
        # regular adds
        can_add = st["units"] < add["max"] and (not cfg["confirm"] or st["conf"])
        trig = h if add["trig"] == "high" else c
        g = add["gate"]
        if g and g[0] == "pullback":
            if can_add and h >= st["last"] + step * N_e:
                st["flag"] = True
            do_add = st["flag"] and c <= V.ema(g[1])[u]
        else:
            do_add = can_add and trig >= st["last"] + step * N_e
            if do_add and g:
                if g[0] == "rsi":
                    do_add = V.rsi(14)[u] >= g[1]
                elif g[0] == "volgate":
                    do_add = not (self.N[u] > self.smaN(g[1])[u] * g[2])
                elif g[0] == "antichop":
                    do_add = bool(self._antichop()[u])
        if do_add:
            st["units"] += 1
            pos.add_w += self._size(st["units"], u) if not cfg["confirm"] else 1.0
            st["last"] = c; st["flag"] = False
        # targets: touched this bar -> close at the next open (strategy.close)
        tg = self._targets(pos)
        if tg:
            while st["hits"] < len(tg) and h >= ev + tg[st["hits"]] * N_e:
                pos.exit_w += cfg["close_w"]; st["hits"] += 1
        # stop for the next bar
        stopN = st["stopN"]
        init = (pos.avg_v() if cfg["init"] == "avg" else ev) - stopN * N_e
        tr = cfg["trail"]; trail = -np.inf
        if tr:
            k = tr[0]
            if k == "don":
                trail = V.get(("pll", tr[1]), lambda: prev(V.ll(tr[1])))[u]
            elif k == "bug_don":
                trail = V.get(("phh", tr[1]), lambda: prev(V.hh(tr[1])))[u]
            elif k == "chand":
                tn = tr[2]
                if cfg["tighten"] and pos.bars >= cfg["tighten"][0]:
                    tn = cfg["tighten"][1]
                trail = V.hh(tr[1])[u] - tn * N_e
            elif k == "sar":
                trail = self.arr[("sar", s)][u]
            elif k == "adaptive":
                Nh = self.N[max(0, u - tr[3] + 1):u + 1]; Nh = np.sort(Nh[np.isfinite(Nh)])
                thr = Nh[max(0, min(int(round(len(Nh) * tr[4] / 100.0)), len(Nh) - 1))] if len(Nh) else np.inf
                L = tr[2] if self.N[u] > thr else tr[1]
                trail = np.min(V.l[max(0, u - L):u]) if u >= L else np.nan
            elif k == "weekly_lo":
                trail = self.arr[("wlo", s)][u]
            elif k == "atr_band":
                trail = V.get(("band", tr[1], tr[2]), lambda: prev(V.sma(tr[1]) - tr[2] * self.N))[u]
        trail = trail if np.isfinite(trail) else -np.inf
        be = cfg["be"]
        if be and be[0] == "lock":
            if not st["be"] and c - ev >= be[1] * N_e:
                st["be"] = True
            stop = max(ev, trail) if st["be"] else max(init, trail)
        elif be and be[0] == "prog":
            p = c - ev
            st["bel"] = 3 if p >= 3 * N_e else (2 if p >= 2 * N_e else (1 if p >= 1 * N_e else st["bel"]))
            floor = {3: ev + N_e, 2: ev + 0.5 * N_e, 1: ev, 0: init}[st["bel"]]
            stop = max(floor, trail)
        else:
            stop = max(init, trail)
        pos.stop_v = stop
        # time exit (alt9)
        if cfg["time_exit"] and pos.bars >= cfg["time_exit"][0]:
            pos.exit_all = True; self.last_time_exit = u


class Alt41(Rule):
    """Sector-adaptive hybrid: ADX > 25 at entry -> fractional pyramid + chandelier on current N; else 0.5% risk with
    stop entry - 2N and limit targets +2/4/6N (current N), 33% / 50% / rest."""

    def prepare(self, mk, views):
        Rule.prepare(self, mk, views)
        self.N = views[1].atr(20); self.adx = views[1].dmi(14)[2]

    def entry(self, u, s):
        V = self.V[s]
        if not (V.c[u] > V.get(("phh", 55), lambda: prev(V.hh(55)))[u]) or not np.isfinite(self.N[u]):
            return None
        tr = bool(self.adx[u] > 25)
        return dict(w=1.0 if tr else 0.5, tr=tr, N=float(self.N[u]), ev=float(V.c[u]),
                    ref_stop_v=float((V.hh(22)[u] - 3 * self.N[u]) if tr else V.c[u] - 2 * self.N[u]))

    def on_fill(self, mk, pos, u, sig):
        pos.st.update(tr=sig["tr"], N=sig["N"], ev=sig["ev"], n=1, w0=sig["w"], d=2.0 * sig["N"])
        pos.stop_v = sig["ref_stop_v"]
        return True

    def on_close(self, mk, pos, u):
        st = pos.st; V = self.V[pos.s]; N = self.N[u]
        if st["tr"]:
            if st["n"] < 4 and V.c[u] >= st["ev"] + st["n"] * 0.5 * N:
                st["n"] += 1
                pos.add_w += [1.0, 0.75, 0.5, 0.25][st["n"] - 1] * st["N"] / N
            pos.stop_v = V.hh(22)[u] - 3.0 * N
        else:
            pos.stop_v = st["ev"] - 2.0 * N
            tg = [(st["ev"] + 2 * N, 0.33 * st["w0"]), (st["ev"] + 4 * N, 0.5 * st["w0"]), (st["ev"] + 6 * N, None)]
            pos.limits = tg[pos.n_limit_fills:]


class Alt42(Rule):
    """Momentum-gated time exit: adds at entry + k x 0.5N (current N); exit on RSI crossing under 50, at 40 bars unless
    RSI > 65, at 60 bars; stop entry - 2N (current N)."""

    def prepare(self, mk, views):
        Rule.prepare(self, mk, views)
        self.N = views[1].atr(20)

    def entry(self, u, s):
        V = self.V[s]
        if not (V.c[u] > V.get(("phh", 55), lambda: prev(V.hh(55)))[u]) or not np.isfinite(self.N[u]):
            return None
        return dict(w=1.0, N=float(self.N[u]), ev=float(V.c[u]), ref_stop_v=float(V.c[u] - 2 * self.N[u]))

    def on_fill(self, mk, pos, u, sig):
        pos.st.update(N=sig["N"], ev=sig["ev"], n=1, d=2.0 * sig["N"])
        pos.stop_v = sig["ref_stop_v"]
        return True

    def on_close(self, mk, pos, u):
        st = pos.st; V = self.V[pos.s]; N = self.N[u]; r = V.rsi(14)
        out = (r[u] < 50 <= r[u - 1]) or (pos.bars >= 40 and not r[u] > 65) or pos.bars >= 60
        if out:
            pos.exit_all = True
        elif st["n"] < 4 and V.c[u] >= st["ev"] + st["n"] * 0.5 * N:
            st["n"] += 1; pos.add_w += st["N"] / N
        pos.stop_v = st["ev"] - 2.0 * N


def make_rule(p, sym):
    name = p["rule"]
    if name == "alt41":
        return Alt41()
    if name == "alt42":
        return Alt42()
    return Turtle(name, sym)
