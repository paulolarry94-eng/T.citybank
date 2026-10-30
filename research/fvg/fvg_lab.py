"""Fair Value Gaps (ICT): a mechanical test.

Bullish FVG at bar i (candle 3): low[i] > high[i-2]; gap = (high[i-2], low[i]); displacement candle
i-1 bullish with body >= disp x ATR; gap height >= gmin x ATR. Known when bar i has closed.
Bearish FVG: mirror (high[i] < low[i-2]).

Modes
  edge   buy limit at the gap's upper edge (low[i]) on the first retrace, within 20 bars; cancelled
         if a bar closes below the gap before the fill
  ce     same with the limit at the gap midpoint ("consequent encroachment")
  ifvg   inversion: a bar closes below the gap (within 50 bars) -> the gap becomes resistance; sell
         limit at the gap's lower edge on the retest within 20 bars; stop above the gap top + 0.25 ATR;
         cancelled by a close above the gap
  fade   gap-fill hypothesis: sell at the next open after a bullish FVG forms, target the gap's upper
         edge, stop above candle 3's high + 0.25 ATR (mirror for bearish)
Stops for edge/ce: 'origin' = beyond candle 1's far extreme - 0.1 ATR (the classic ICT stop);
'gap' = beyond the gap's far edge - 0.25 ATR.
Filters at entry: daily bias (last closed D1 bar vs its EMA50, trade only with it); killzones
(entries 07-10 or 12-15 UTC; M15 only).
Management: target {1.5, 2, 3 R, none}, chandelier trail {none, 3 ATR}, time stop 50 bars,
one position at a time. Same 1-minute fill law and all-in costs as every other study.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "orb"))
import engine as E, gold_lab as GL
from execution import fill_limit, manage

TIME_STOP = 50


class Lab:
    def __init__(self, sym):
        self.G = GL.Market(sym); self.sym = sym; self.cost = self.G.cost
        D = self.G.tf("D1", 0)
        self.Dt, self.Dema, self.Dc = D["t"], E.ema(D["c"], 50), D["c"]
        self._c = {}

    def bars(self, tfn):
        B = self.G.tf(tfn, 120 if tfn in ("H4", "D1") else 0)
        B["first"] = np.r_[0, B["nxt"][:-1]].astype(np.int64)
        B["atr"] = np.nan_to_num(B["atr"], nan=0.0)
        return B

    def bias(self, t_close):
        k = np.searchsorted(self.Dt + 86400, t_close, side="right") - 1
        k = min(max(k, 0), len(self.Dt) - 1)
        return 0 if not np.isfinite(self.Dema[k]) else int(np.sign(self.Dc[k] - self.Dema[k]))

    def candidates(self, tfn, mode, disp, gmin, stop):
        key = (tfn, mode, disp, gmin, stop)
        if key in self._c:
            return self._c[key]
        G, B = self.G, self.bars(tfn)
        o, h, l, c, a = B["o"], B["h"], B["l"], B["c"], B["atr"]
        n = len(c); cost = self.cost; eps = 0.1 * cost
        out = []          # (fill_minute, side, entry(-1 = market), stop, tgt_abs or nan, signal_bar, atr)
        for i in range(2, n - 2):
            at = a[i - 2] if a[i - 2] > 0 else a[i]
            if at <= 0:
                continue
            for s in (1, -1):
                if s > 0:
                    if not (l[i] > h[i - 2]):
                        continue
                    gb, gt = h[i - 2], l[i]
                    body = c[i - 1] - o[i - 1]
                else:
                    if not (h[i] < l[i - 2]):
                        continue
                    gb, gt = h[i], l[i - 2]
                    body = o[i - 1] - c[i - 1]
                if body < disp * at or (gt - gb) < gmin * at:
                    continue
                if mode == "market":                       # follow the displacement at once, ICT stop
                    stp = (l[i - 2] - 0.1 * at) if s > 0 else (h[i - 2] + 0.1 * at)
                    out.append((int(B["nxt"][i]), s, -1.0, stp, np.nan, i, at))
                    continue
                if mode == "fade":
                    ext = h[i] if s > 0 else l[i]
                    stp = ext + 0.25 * at if s > 0 else ext - 0.25 * at
                    tgt = gt if s > 0 else gb
                    out.append((int(B["nxt"][i]), -s, -1.0, stp, tgt, i, at))
                    continue
                if mode in ("edge", "ce"):
                    lvl = (gt if s > 0 else gb) if mode == "edge" else 0.5 * (gt + gb)
                    if stop == "origin":
                        stp = (l[i - 2] - 0.1 * at) if s > 0 else (h[i - 2] + 0.1 * at)
                    else:
                        stp = (gb - 0.25 * at) if s > 0 else (gt + 0.25 * at)
                    for u in range(i + 1, min(i + 21, n - 1)):
                        kf, px = fill_limit(G.o, G.h, G.l, B["first"][u], B["nxt"][u], s, lvl, cost, eps)
                        if kf >= 0:
                            out.append((int(kf), s, px, stp, np.nan, u, at))
                            break
                        if (s > 0 and c[u] < gb) or (s < 0 and c[u] > gt):
                            break
                    continue
                # ifvg: the gap is closed through, then retested from the other side
                inv = -1
                for u in range(i + 1, min(i + 51, n - 1)):
                    if (s > 0 and c[u] < gb) or (s < 0 and c[u] > gt):
                        inv = u; break
                if inv < 0:
                    continue
                side = -s
                lvl = gb if s > 0 else gt
                stp = (gt + 0.25 * at) if s > 0 else (gb - 0.25 * at)
                for u in range(inv + 1, min(inv + 21, n - 1)):
                    kf, px = fill_limit(G.o, G.h, G.l, B["first"][u], B["nxt"][u], side, lvl, cost, eps)
                    if kf >= 0:
                        out.append((int(kf), side, px, stp, np.nan, u, at))
                        break
                    if (side < 0 and c[u] > gt) or (side > 0 and c[u] < gb):
                        break
        out.sort(key=lambda x: x[0])
        self._c[key] = (out, B)
        return out, B

    def run(self, tfn, mode, disp, gmin, stop, tgt, trail, bias=False, kill=False, cut=None):
        cands, B = self.candidates(tfn, mode, disp, gmin, stop)
        G = self.G; cost = self.cost
        res = []; busy = -1
        sig_t = B["t"] + B["minutes"] * 60
        for kf, side, px, stp, tabs, sb, at in cands:
            if kf <= busy or kf >= len(G.o) - 2:
                continue
            if cut is not None and G.ts[kf] >= cut:
                break
            if bias and self.bias(G.ts[kf]) != side:          # only daily bars closed before the fill
                continue
            if kill:
                hr = (G.ts[kf] % 86400) // 3600
                if not (7 <= hr < 10 or 12 <= hr < 15):
                    continue
            at_open = px < 0
            entry = (G.o[kf] + cost if side > 0 else G.o[kf]) if at_open else px
            dist = (entry - stp) if side > 0 else (stp - entry)
            if dist < 3 * cost or dist <= 0 or dist > 4 * at:
                continue
            if np.isfinite(tabs):
                tr = (tabs - entry) / dist if side > 0 else (entry - tabs) / dist
                if tr <= 0.2:
                    continue
                tg = tr
            else:
                tg = tgt
            kend = int(B["nxt"][min(sb + TIME_STOP, len(B["nxt"]) - 1)])
            kend = min(kend, len(G.o) - 1)
            gj = np.searchsorted(G.gaps, kf)
            if gj < len(G.gaps) and G.gaps[gj] < kend:
                continue
            kx, r, why, mfe = manage(G.o, G.h, G.l, kf, kend, side, entry, stp, dist, cost, float(tg), 0.0, 0.0, 1.0,
                                     float(trail), 22, B["h"], B["l"], B["nxt"].astype(np.int64), B["atr"],
                                     int(np.searchsorted(B["first"], kf, side="right") - 1), at_open)
            res.append((G.ts[kf], G.ts[kx], side, r, dist, cost / dist))
            busy = kx
        return np.array(res) if res else np.zeros((0, 6))
