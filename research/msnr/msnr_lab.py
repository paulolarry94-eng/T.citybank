"""Malaysian SnR, engulfing and failed engulfing: a mechanical test.

Levels (body based, from the community definitions):
  A-level (resistance): bar j bullish (c > o), bar j+1 bearish (c < o), and c[j] is the highest close of
          bars j-k..j+k (pivot depth k; k = 1 is the plain candle rule). Level = c[j]. Known when
          bar j+k has closed. Formation wick = highest high of bars j-k..j+k.
  V-level (support): mirror image.
  Fresh until the first bar (after it is known) whose wick reaches it. Only that first touch is traded.
  Levels not touched within 300 bars expire.
Modes
  limit    sell limit at a fresh A-level (buy limit at V), filled minute by minute when price trades
           through it; stop beyond the formation wick + 0.1 ATR (at least 0.25 ATR from the level)
  engulf   after the touch, within 3 bars, a bearish engulfing bar (bullish for V) that closes back
           below the level; enter at the next bar open; stop beyond the highest high since the touch
           + 0.1 ATR. A close beyond the level first cancels it.
  failed   an engulf signal (as above) whose engulfing bar's extreme is closed beyond within 3 bars:
           trade the break at the next open; stop beyond the engulfing bar's other extreme + 0.1 ATR
  rbs      a level closed through by a body flips role (resistance becomes support); buy limit at the
           first retest within 100 bars, stop 0.5 ATR beyond the level
  engulf_any / failed_any: the same candle patterns with no level (baseline)
Every trade: target tgt x risk, time stop 50 bars, one position at a time per variant.
Filters: storyline (trade only with the last closed daily bar's side of its EMA50), entry hours.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "orb"))
import engine as E, gold_lab as GL
from execution import fill_limit, manage

DUMMY = np.zeros(2); DUMMYI = np.array([10 ** 12, 10 ** 12], np.int64)
TIME_STOP = 50


class Lab:
    def __init__(self, sym):
        self.G = GL.Market(sym)
        self.sym, self.cost = sym, self.G.cost
        D = self.G.tf("D1", 0)
        self.Dt, self.Dema = D["t"], E.ema(D["c"], 50)
        self.Dc = D["c"]

    def bars(self, tfn):
        B = self.G.tf(tfn, 120 if tfn in ("H4", "D1") else 0)
        B["first"] = np.r_[0, B["nxt"][:-1]].astype(np.int64)
        B["atr"] = np.nan_to_num(B["atr"], nan=0.0)
        return B

    def story(self, t_close):
        """+1/-1: last closed daily bar above/below its EMA50 at time t_close."""
        k = np.searchsorted(self.Dt + 86400, t_close, side="right") - 1
        k = np.clip(k, 0, len(self.Dt) - 1)
        return np.where(np.isfinite(self.Dema[k]), np.sign(self.Dc[k] - self.Dema[k]), 0)

    # ---------------------------------------------------------------- levels
    def levels(self, B, k):
        o, h, l, c = B["o"], B["h"], B["l"], B["c"]
        n = len(c); out = []
        bull = c > o; bear = c < o
        for j in range(k, n - k - 1):
            win = c[j - k:j + k + 1]
            if bull[j] and bear[j + 1] and c[j] >= win.max() and (win == c[j]).sum() == 1:
                out.append((j, -1, c[j], h[j - k:j + k + 1].max()))
            elif bear[j] and bull[j + 1] and c[j] <= win.min() and (win == c[j]).sum() == 1:
                out.append((j, 1, c[j], l[j - k:j + k + 1].min()))
        return out, k

    # ---------------------------------------------------------------- candidates
    def candidates(self, tfn, k, mode, tgt, htf=None):
        G, B = self.G, self.bars(tfn)
        o, h, l, c, atr = B["o"], B["h"], B["l"], B["c"], B["atr"]
        n = len(c); cost = self.cost; eps = 0.1 * cost
        cands = []        # (fill_minute, side, entry_px or -1 for market, stop, signal_bar, kind)
        if mode in ("engulf_any", "failed_any"):
            for e in range(1, n - 4):
                a = atr[e]
                if a <= 0:
                    continue
                for s in (-1, 1):
                    eng = (c[e] < o[e] and c[e - 1] > o[e - 1] and o[e] >= c[e - 1] and c[e] <= o[e - 1]) if s < 0 else \
                          (c[e] > o[e] and c[e - 1] < o[e - 1] and o[e] <= c[e - 1] and c[e] >= o[e - 1])
                    if not eng:
                        continue
                    if mode == "engulf_any":
                        stop = h[e] + 0.1 * a if s < 0 else l[e] - 0.1 * a
                        cands.append((B["nxt"][e], s, -1.0, stop, e, a))
                    else:
                        for f in range(e + 1, min(e + 4, n - 1)):
                            if (s < 0 and c[f] > h[e]) or (s > 0 and c[f] < l[e]):
                                stop = l[e] - 0.1 * a if s < 0 else h[e] + 0.1 * a
                                cands.append((B["nxt"][f], -s, -1.0, stop, f, a))
                                break
            return cands, B
        if htf is None:
            L, _ = self.levels(B, k)
            Lst = [j + k + 1 for j, _, _, _ in L]
            La = [atr[j + k] for j, _, _, _ in L]
        else:                                     # levels from the higher timeframe, entries on this one
            H = self.bars(htf)
            L, _ = self.levels(H, k)
            known = np.array([H["t"][j + k] + H["minutes"] * 60 for j, _, _, _ in L], np.int64)
            Lst = list(np.searchsorted(B["t"], known))
            La = [H["atr"][j + k] for j, _, _, _ in L]
        for (j, s, lvl, wick), st, a_h in zip(L, Lst, La):
            a = atr[min(st, n - 1)] if htf is not None else a_h
            if htf is not None and mode in ("limit", "rbs"):
                a = a_h
            if a <= 0 or st >= n - 2:
                continue
            if mode == "rbs":
                b = -1
                for u in range(st, min(st + 300, n - 1)):
                    if (s < 0 and c[u] > lvl) or (s > 0 and c[u] < lvl):
                        b = u; break
                if b < 0:
                    continue
                for u in range(b + 1, min(b + 100, n - 1)):
                    if (s < 0 and l[u] <= lvl) or (s > 0 and h[u] >= lvl):
                        side = -s                    # broken resistance -> support: buy
                        kf, px = fill_limit(G.o, G.h, G.l, B["first"][u], B["nxt"][u], side, lvl, cost, eps)
                        if kf >= 0:
                            stop = lvl - 0.5 * a if side > 0 else lvl + 0.5 * a
                            cands.append((kf, side, px, stop, u, a))
                        break
                continue
            u = -1
            for q in range(st, min(st + 300, n - 1)):
                if (s < 0 and h[q] >= lvl) or (s > 0 and l[q] <= lvl):
                    u = q; break
            if u < 0:
                continue
            if mode == "limit":
                kf, px = fill_limit(G.o, G.h, G.l, B["first"][u], B["nxt"][u], s, lvl, cost, eps)
                if kf >= 0:
                    d = max(abs(wick - lvl), 0.25 * a) + 0.1 * a
                    cands.append((kf, s, px, lvl + d if s < 0 else lvl - d, u, a))
                continue
            ext = h[u] if s < 0 else l[u]
            for e in range(u, min(u + 4, n - 4)):
                ext = max(ext, h[e]) if s < 0 else min(ext, l[e])
                eng = (c[e] < o[e] and c[e - 1] > o[e - 1] and o[e] >= c[e - 1] and c[e] <= o[e - 1] and c[e] < lvl) if s < 0 else \
                      (c[e] > o[e] and c[e - 1] < o[e - 1] and o[e] <= c[e - 1] and c[e] >= o[e - 1] and c[e] > lvl)
                if eng:
                    if mode == "engulf":
                        stop = ext + 0.1 * a if s < 0 else ext - 0.1 * a
                        cands.append((B["nxt"][e], s, -1.0, stop, e, a))
                    else:                        # failed engulf
                        for f in range(e + 1, min(e + 4, n - 1)):
                            if (s < 0 and c[f] > h[e]) or (s > 0 and c[f] < l[e]):
                                stop = l[e] - 0.1 * a if s < 0 else h[e] + 0.1 * a
                                cands.append((B["nxt"][f], -s, -1.0, stop, f, a))
                                break
                    break
                if (s < 0 and c[e] > lvl) or (s > 0 and c[e] < lvl):
                    break                        # closed through the level first: no reversal setup
        return cands, B

    # ---------------------------------------------------------------- execution
    def run(self, tfn, k, mode, tgt, story=False, hours=None, htf=None):
        key = (tfn, k, mode, htf)
        if not hasattr(self, "_cache"):
            self._cache = {}
        if key not in self._cache:
            self._cache[key] = self.candidates(tfn, k, mode, tgt, htf)
        cands, B = self._cache[key]
        G = self.G; cost = self.cost
        if not cands:
            return np.zeros(0, dtype=GL.DT)
        cands.sort(key=lambda x: x[0])
        out = []; busy = -1; gi = 0
        sig_t = B["t"] + B["minutes"] * 60
        for kf, side, px, stop, sb, a in cands:
            kf = int(kf)
            if kf <= busy or kf >= len(G.o) - 2:
                continue
            if story and self.story(np.array([sig_t[sb]]))[0] != side:
                continue
            if hours is not None and not (hours[0] <= (G.ts[kf] % 86400) // 3600 < hours[1]):
                continue
            at_open = px < 0
            entry = (G.o[kf] + cost if side > 0 else G.o[kf]) if at_open else px
            dist = (entry - stop) if side > 0 else (stop - entry)
            if dist < 3 * cost or dist <= 0 or (a > 0 and dist > 3 * a):
                continue
            kend = int(B["nxt"][min(sb + TIME_STOP, len(B["nxt"]) - 1)])
            kend = min(kend, len(G.o) - 1)
            gj = np.searchsorted(G.gaps, kf)
            if gj < len(G.gaps) and G.gaps[gj] < kend:
                continue
            kx, r, why, mfe = manage(G.o, G.h, G.l, kf, kend, side, entry, stop, dist, cost, float(tgt), 0.0,
                                     0.0, 1.0, 0.0, 14, DUMMY, DUMMY, DUMMYI, DUMMY, 0, at_open)
            out.append((G.ts[kf], G.ts[kx], side, r, dist, entry))
            busy = kx
        A = np.array(out)
        return GL.pack(A) if len(A) else np.zeros(0, dtype=GL.DT)
