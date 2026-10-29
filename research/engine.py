"""TimelessCity research engine — a faithful Python copy of the v2.42 EA rules.

Every rule here is read from mt5/TimelessCity.mq5. Where the EA depends on something
a price file cannot show (the live news calendar), that is stated, not invented.

THE FILL LAW (hard wall 4): a trade exists only from the first one-minute bar that
opens AFTER the signal bar has closed. It is filled at that bar's open plus the all-in
cost. If one minute could have touched both the stop and the target, it is scored a
LOSS. Stops that are jumped over fill at the worse bar open, never at the stop price.
"""
import glob, os
import numpy as np
from numba import njit

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

# All-in cost per trade side used for entry (spread + slippage), in price units.
# Gold/EUR/JPY are the dossier's own broker tiers; measured tick spreads are compared
# against these in the report rather than silently swapped in.
COST = {"XAUUSD": 0.45, "EURUSD": 0.00015, "GBPUSD": 0.00018, "USDJPY": 0.012}
PIP = {"XAUUSD": 0.1, "EURUSD": 0.0001, "GBPUSD": 0.0001, "USDJPY": 0.01}


# ----------------------------------------------------------------------------- data
def load_m1(sym, y0=2011, y1=2025):
    parts = []
    for y in range(y0, y1 + 1):
        f = os.path.join(DATA, f"{sym}_M1_bid_{y}.npz")
        if not os.path.exists(f):
            raise FileNotFoundError(f"missing {sym} {y}")
        d = np.load(f)
        parts.append((d["ts"] // 1000, d["o"], d["h"], d["l"], d["c"]))
    ts = np.concatenate([p[0] for p in parts]).astype(np.int64)
    o, h, l, c = (np.concatenate([p[i] for p in parts]).astype(np.float64) for i in (1, 2, 3, 4))
    order = np.argsort(ts, kind="stable")
    ts, o, h, l, c = ts[order], o[order], h[order], l[order], c[order]
    keep = np.ones(len(ts), bool)
    keep[1:] = ts[1:] != ts[:-1]                      # drop duplicate minutes
    # drop no-tick filler minutes (flat bar at the previous close): some exports fill
    # weekends/holidays with them; MT5 has no bar for a minute without ticks.
    flat = (o == h) & (h == l) & (l == c)
    flat[1:] &= o[1:] == c[:-1]
    flat[0] = False
    keep &= ~flat
    return ts[keep], o[keep], h[keep], l[keep], c[keep]


def resample(ts, o, h, l, c, minutes, offset_min=0):
    """Bars aligned to UTC multiples of `minutes` (+offset). Returns bar open time,
    OHLC, and the index of the first M1 bar of the NEXT bar (= first tradeable minute
    after this bar closes)."""
    sec = minutes * 60
    key = (ts - offset_min * 60) // sec
    starts = np.flatnonzero(np.r_[True, key[1:] != key[:-1]])
    ends = np.r_[starts[1:], len(ts)]
    bo = o[starts]
    bh = np.maximum.reduceat(h, starts)
    bl = np.minimum.reduceat(l, starts)
    bc = c[ends - 1]
    bt = key[starts] * sec + offset_min * 60
    return bt, bo, bh, bl, bc, ends          # ends[i] = first M1 index after bar i


def ema(x, n):
    a = 2.0 / (n + 1)
    out = np.empty_like(x)
    out[:n] = np.nan
    out[n - 1] = x[:n].mean()
    for i in range(n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def atr_sma(h, l, c, n=14):
    """MT5 iATR = simple moving average of true range."""
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    cs = np.cumsum(np.r_[0.0, tr])
    out = np.full(len(tr), np.nan)
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


# ------------------------------------------------------------- S1: Impulse4 patterns
def s1_patterns(bo, bh, bl, bc, em, up=True, min_engulf=2, max_engulf=6, max_base=30,
                min_kids=1):
    """All Impulse4 (strict 4-candle, no counter) setups exactly as DetectAndArm builds
    them. Returns arrays: a, brk, sl, entry_lvl, risk0, gap. The detection-time checks
    (ATR bands, recency, window) are applied later at each candidate bar close."""
    n = len(bo)
    bull = bc > bo
    bear = bc < bo
    same = bull if up else bear
    out = []
    for a in range(1, n - 5):
        if not (same[a] and same[a + 1] and same[a + 2] and same[a + 3]):
            continue
        if same[a - 1] or same[a + 4]:
            continue
        d = a + 3
        sl = bl[a] if up else bh[a]
        ent = bc[d]
        last_ext = bl[d] if up else bh[d]
        risk0 = abs(ent - sl)
        if risk0 <= 0:
            continue
        if not np.isfinite(em[a]):
            continue
        if up and not (bo[a] < em[a]):
            continue
        if (not up) and not (bo[a] > em[a]):
            continue
        eng = -1
        for j in range(d + 1, min(d + max_engulf, n - 1) + 1):
            if up and (bl[j] < sl or bc[j] > ent):
                break
            if (not up) and (bh[j] > sl or bc[j] < ent):
                break
            if (up and bc[j] < last_ext) or ((not up) and bc[j] > last_ext):
                eng = j
                break
        if eng < 0 or eng - d < min_engulf:
            continue
        brk = -1
        for j in range(eng + 1, min(eng + 1 + max_base, n - 1) + 1):
            if up and bl[j] < sl:
                break
            if (not up) and bh[j] > sl:
                break
            if (up and bc[j] > ent) or ((not up) and bc[j] < ent):
                brk = j
                break
        if brk < 0 or brk - eng - 1 < min_kids:
            continue
        base = bl[eng:brk].min() if up else bh[eng:brk].max()
        if up and base <= sl:
            continue
        if (not up) and base >= sl:
            continue
        out.append((a, brk, sl, ent, risk0, abs(base - sl)))
    if not out:
        return {k: np.array([]) for k in ("a", "brk", "sl", "ent", "risk0", "gap")}
    arr = np.array(out)
    return {"a": arr[:, 0].astype(np.int64), "brk": arr[:, 1].astype(np.int64),
            "sl": arr[:, 2], "ent": arr[:, 3], "risk0": arr[:, 4], "gap": arr[:, 5]}


# ------------------------------------------------------------------ path scanners
@njit(cache=True)
def scan_fixed(o, h, l, i0, side, entry, sl, tp, cost):
    """Flat stop/target from M1 index i0 (entry at o[i0]). Long exits on bid; short
    exits on ask = bid + cost. Same-minute stop+target = loss. Returns (exit_idx, px)."""
    n = len(o)
    for i in range(i0, n):
        if side > 0:
            hit_sl = l[i] <= sl
            hit_tp = h[i] >= tp
            if hit_sl:
                px = sl if o[i] > sl or i == i0 else o[i]
                return i, min(px, sl)
            if hit_tp:
                return i, tp
        else:
            ah = h[i] + cost
            al = l[i] + cost
            hit_sl = ah >= sl
            hit_tp = al <= tp
            if hit_sl:
                ao = o[i] + cost
                px = sl if ao < sl or i == i0 else ao
                return i, max(px, sl)
            if hit_tp:
                return i, tp
    return n - 1, o[n - 1] if side > 0 else o[n - 1] + cost


@njit(cache=True)
def scan_trail(o, h, l, i0, side, entry, dist, trail_r, cost):
    """Chandelier trail in R (ManageTrendTrail): initial stop -1R; once the best
    excursion reaches +trail_r, stop = peak - trail_r (never loosens). Conservative
    minute order: the OLD stop is checked before the minute's new high raises it."""
    n = len(o)
    sl = entry - dist if side > 0 else entry + dist
    peak = 0.0
    for i in range(i0, n):
        if side > 0:
            if l[i] <= sl:
                px = sl if (o[i] > sl or i == i0) else o[i]
                return i, min(px, sl)
            fav = (h[i] - entry) / dist
        else:
            if h[i] + cost >= sl:
                ao = o[i] + cost
                px = sl if (ao < sl or i == i0) else ao
                return i, max(px, sl)
            fav = (entry - (l[i] + cost)) / dist
        if fav > peak:
            peak = fav
            if peak >= trail_r:
                tr = peak - trail_r
                new = entry + tr * dist if side > 0 else entry - tr * dist
                if (side > 0 and new > sl) or (side < 0 and new < sl):
                    sl = new
    return n - 1, o[n - 1] if side > 0 else o[n - 1] + cost


# ----------------------------------------------------------------- instance replay
class Pause:
    """Restraint engine: InpMaxLossDays consecutive losing days -> InpPauseDays pause."""
    def __init__(self, max_days=3, pause_days=7, on=True):
        self.on, self.max_days, self.pause_days = on, max_days, pause_days
        self.until = 0
        self.streak = 0
        self.day = None
        self.net = 0.0

    def blocked(self, t):
        if not self.on:
            return False
        self._roll(t)
        if self.until and t < self.until:
            return True
        if self.until and t >= self.until:
            self.until = 0
            self.streak = 0
        return False

    def _roll(self, t):
        d = t // 86400
        if self.day is not None and d != self.day:
            if self.net < 0:
                self.streak += 1
                if self.streak >= self.max_days and not self.until:
                    self.until = t + self.pause_days * 86400
            elif self.net > 0:
                self.streak = 0
            self.net = 0.0
            self.day = None

    def record(self, t, r):
        if not self.on:
            return
        self._roll(t)
        d = t // 86400
        if self.day is None:
            self.day = d
        self.net += r


def run_s1(sym, m1, tfs=(30, 20), gap_band=(1.0, 2.0), max_stop_atr=3.0, rr=1.0,
           sides=(1,), deadzone=(16, 20), pause=True, offset_min=0, min_spread_x=1.5,
           cost=None):
    """Replay one S1 reversion instance (one position at a time) over the M1 record."""
    ts, o, h, l, c = m1
    cost = COST[sym] if cost is None else cost
    events = []      # (time_bar_close, tf_priority, entry_m1_index, side, sl, sigkey)
    for pri, tf in enumerate(sorted(tfs, reverse=True)):     # EA order: larger TF first
        bt, bo, bh, bl, bc, nxt = resample(ts, o, h, l, c, tf, offset_min)
        em = ema(bc, 10)
        at = atr_sma(bh, bl, bc, 14)
        for side in sides:
            P = s1_patterns(bo, bh, bl, bc, em, up=side > 0)
            for k in range(len(P["a"])):
                a, brk = P["a"][k], P["brk"][k]
                for t in (brk, brk + 1, brk + 2):      # breakout within last 3 closed bars
                    if t >= len(bt) - 1 or a < t - 78:  # 80-bar detection window
                        continue
                    A = at[t]
                    if not np.isfinite(A) or A <= 0:
                        continue
                    if P["risk0"][k] > max_stop_atr * A:
                        continue
                    g = P["gap"][k]
                    if gap_band[1] > 0 and g > gap_band[1] * A:
                        continue
                    if gap_band[0] > 0 and g < gap_band[0] * A:
                        continue
                    close_time = bt[t] + tf * 60
                    events.append((close_time, pri, int(nxt[t]), side, P["sl"][k],
                                   (tf, int(t)), int(a)))
    events.sort(key=lambda e: (e[0], e[1], -e[3], e[6]))
    trades, busy_until, used = [], -1, set()
    pz = Pause(on=pause)
    i = 0
    while i < len(events):
        tc, pri, j0, side, sl, key, a = events[i]
        i += 1
        if j0 >= len(ts) or j0 <= busy_until or key in used:
            continue
        tnow = int(ts[j0])
        if deadzone:
            hr = (tnow // 3600) % 24
            if deadzone[0] <= hr < deadzone[1]:
                continue
        if pz.blocked(tnow):
            continue
        entry = o[j0] + cost if side > 0 else o[j0]
        if (side > 0 and entry <= sl) or (side < 0 and entry >= sl):
            continue
        dist = abs(entry - sl)
        if dist < min_spread_x * cost:
            continue
        tp = entry + rr * dist if side > 0 else entry - rr * dist
        xi, px = scan_fixed(o, h, l, j0, side, entry, sl, tp, cost)
        r = (px - entry) / dist if side > 0 else (entry - px) / dist
        used.add(key)            # g_lastSig: never re-arm on the same signal bar
        trades.append((tnow, int(ts[xi]), side, r, dist, entry))
        pz.record(int(ts[xi]), r)
        busy_until = xi
    return np.array(trades, dtype=[("t_in", "i8"), ("t_out", "i8"), ("side", "i8"),
                                   ("r", "f8"), ("dist", "f8"), ("entry", "f8")])


def run_trend(sym, m1, tf=240, n_don=20, atr_mult=2.0, trail_r=1.5, sides=(1,),
              pause=True, offset_min=0, cost=None, min_spread_x=1.5):
    """Replay one Donchian trend instance (DetectDonchian + ManageTrendTrail)."""
    ts, o, h, l, c = m1
    cost = COST[sym] if cost is None else cost
    bt, bo, bh, bl, bc, nxt = resample(ts, o, h, l, c, tf, offset_min)
    at = atr_sma(bh, bl, bc, 14)
    hh = np.full(len(bc), np.nan)
    ll = np.full(len(bc), np.nan)
    for t in range(n_don, len(bc)):
        hh[t] = bh[t - n_don:t].max()
        ll[t] = bl[t - n_don:t].min()
    trades, busy_until = [], -1
    pz = Pause(on=pause)
    for t in range(n_don, len(bc) - 1):
        side = 1 if bc[t] > hh[t] else (-1 if bc[t] < ll[t] else 0)
        if side == 0 or side not in sides:
            continue
        j0 = int(nxt[t])
        if j0 >= len(ts) or j0 <= busy_until:
            continue
        tnow = int(ts[j0])
        if pz.blocked(tnow):
            continue
        A = at[t]
        if not np.isfinite(A) or A <= 0:
            continue
        entry = o[j0] + cost if side > 0 else o[j0]
        dist = atr_mult * A
        if dist < min_spread_x * cost:
            continue
        xi, px = scan_trail(o, h, l, j0, side, entry, dist, trail_r, cost)
        r = (px - entry) / dist if side > 0 else (entry - px) / dist
        trades.append((tnow, int(ts[xi]), side, r, dist, entry))
        pz.record(int(ts[xi]), r)
        busy_until = xi
    return np.array(trades, dtype=[("t_in", "i8"), ("t_out", "i8"), ("side", "i8"),
                                   ("r", "f8"), ("dist", "f8"), ("entry", "f8")])


# ---------------------------------------------------------------------- statistics
def stats(tr, split_year=2019):
    if len(tr) == 0:
        return {"n": 0}
    r = tr["r"]
    yrs = (tr["t_in"].max() - tr["t_in"].min()) / (365.25 * 86400)
    y = 1970 + tr["t_in"] // int(365.2425 * 86400)
    import datetime as dt
    year = np.array([dt.datetime.utcfromtimestamp(t).year for t in tr["t_in"]])
    w, ls = r[r > 0], r[r <= 0]
    streak = best = 0
    for x in r:
        streak = streak + 1 if x <= 0 else 0
        best = max(best, streak)
    per_year = {int(Y): float(r[year == Y].sum()) for Y in np.unique(year)}
    ins, oos = r[year < split_year], r[year >= split_year]
    return {"n": len(r), "per_yr": len(r) / max(yrs, 1e-9), "win": float((r > 0).mean()),
            "avg_w": float(w.mean()) if len(w) else 0.0,
            "avg_l": float(ls.mean()) if len(ls) else 0.0,
            "E": float(r.mean()), "pf": float(w.sum() / -ls.sum()) if ls.sum() < 0 else np.inf,
            "E_is": float(ins.mean()) if len(ins) else np.nan,
            "E_oos": float(oos.mean()) if len(oos) else np.nan,
            "n_is": len(ins), "n_oos": len(oos),
            "pos_years": sum(v > 0 for v in per_year.values()), "years": len(per_year),
            "max_consec_loss": best, "best": float(r.max()), "per_year": per_year}
