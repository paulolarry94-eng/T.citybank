"""Owner's 3:30 EMA retest edge (owner's charts and answers, 2026-11-02). Rules fixed BEFORE any backtest result.
Full pre-registration and the owner's words: research/owner330/PREREGISTRATION.md.

Every market, every New York business day:
 1 ANCHOR (M30). The 30-minute candle that opens at the anchor time must cross the 10 EMA with its body: SELL day if it
   opens above and closes below, BUY day if it opens below and closes above. The EMA is the 10-period EMA of M30 closes as it
   stood when the candle opened (the value of the previous candle; comparing the close with it is the same as comparing it
   with the line drawn on the candle). No cross = no trade. The candle's full high-low (wick to wick) is THE RANGE.
   anchor = wat1530: 15:30 Nigerian time (14:30 UTC) every day (the owner's October charts);
            ny0930:  09:30 New York, moving with US daylight saving (the owner's "always 9:30 New York").
 2 WATCH (M5). From the first M5 candle after the anchor closes. Cancel the day if an M5 candle CLOSES beyond the
   opposite end of the range (above it on a sell day); a wick through it does not cancel.
 3 REFERENCE (M5). The first M5 candle that crosses the M5 10 EMA in the bias direction (previous close on the other side,
   this close on the bias side) and trades inside the range (its high-low touches the range; the owner's gold 29 Oct
   reference closed below the range but its high reached into it). One reference per day.
 4 ENTRY (sell; buy is the mirror). Stop at the reference high.
   displaced reference (range >= 1.5 x the average range of the 10 M5 candles before it): sell limit at its 50% level;
   otherwise entry = A:  sell stop at the reference low (fills when price trades through it);
                    B<n>: price first trades below the reference low, then a sell limit at the low catches the pullback
                          within n M5 candles (15 / 30 / 60 minutes); no pullback, no trade.
   Pending orders die at a cancel close (step 2) or at the time exit. No fills 20:30-23:00 UTC (the lab's rollover block).
   Trades whose stop is closer than 3 x the round-trip cost are skipped (the lab's standard rule).
 5 EXIT. Target = 2R / 3R / 4R. Breakeven on: the stop moves to the entry once price has gone +1R. Time exit 16:00 New
   York (US cash close, "end of the New York session"); no trade is held to the next day. Same minute: stop first; the
   target and the breakeven move are not checked on the fill minute (conservative).
 6 NEWS. Skip US NFP, CPI and FOMC decision days (research/truth/calendars/us_news_days.json, official dates).
Grid: anchor [wat1530, ny0930] x entry [A, B3, B6, B12] x target [2, 3, 4] x breakeven [0, 1] = 48 configurations.
Markets (all with data): XAUUSD XAGUSD EURUSD GBPUSD USDJPY EURGBP WTI US500 NAS100 GER40 UK100 JP225.
Costs: RoboForex Prime published (research/truth/costs_roboforex_prime.json) where available; XAGUSD and UK100 use the lab
  standard. No overnight holds, so no swaps.
Selection (owner: cycle-centric): gate-passing configurations are ranked by 2011-19 edge quality s = mean R / spread of R,
  which sets the return per 10-trade cycle inside a drawdown cap (P28), instead of the lab's default t.
Control (research/truth/controls.py, never selected): the same rules with the anchor 2 hours later (16:30 UTC / 11:30 New York).
Priors (told to the owner): intraday session patterns were rejected after costs on these markets (ORB at the New York
  open, the London best-setup scanner, the Leg 34 pocket scan over 11 markets x sessions; P1, P14, P21).
"""
import os, sys, json, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from numba import njit

NAME = "owner330_ema_retest_v1"
HYPOTHESIS = ("When the 30-minute candle at the New York open crosses its 10 EMA, the first M5 EMA cross back inside that "
              "candle's range, traded on the break of the M5 candle with a fixed R target, pays more than costs.")
RULES = __doc__
FAMILY = ["session", "ema", "retest", "intraday", "ny-open", "breakout", "multi-market", "owner-idea"]
MARKETS = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
TIMEFRAMES = ["M5"]
GRID = {"anchor": ["wat1530", "ny0930"], "entry": ["A", "B3", "B6", "B12"], "target": [2, 3, 4], "be": [0, 1]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 10 ** 6
STOP_CAP_ATR = 1e9
SELECT_BY = "s"
EMA_N, DISP_N, DISP_X, MIN_R_COST, CONTROL_SHIFT_H = 10, 10, 1.5, 3.0, 2
_here = os.path.dirname(os.path.abspath(__file__))
_rf = json.load(open(os.path.join(_here, "..", "costs_roboforex_prime.json")))["realistic"]
COSTS = {m: _rf[m] for m in MARKETS if m in _rf}
_cal = json.load(open(os.path.join(_here, "..", "calendars", "us_news_days.json")))
NEWS = {dt.date.fromisoformat(d) for k in ("nfp", "cpi", "fomc") for d in _cal[k]}
NY, WAT = ZoneInfo("America/New_York"), ZoneInfo("Africa/Lagos")
BLOCK = (20 * 3600 + 1800, 23 * 3600)
ENTRY_WIN = {"A": 0, "B3": 15, "B6": 30, "B12": 60}               # minutes the pullback may take after the break
REASON = {1: "stop", 2: "target", 3: "time", 4: "breakeven"}


def ema(x, n=EMA_N):
    return pd.Series(np.asarray(x, float)).ewm(span=n, adjust=False).mean().to_numpy()


def anchor_times(D, anchor, sample="flow"):
    """(anchor open, time exit) in UTC seconds for New York date D."""
    if anchor == "wat1530":
        a = dt.datetime(D.year, D.month, D.day, 15, 30, tzinfo=WAT)
    else:
        a = dt.datetime(D.year, D.month, D.day, 9, 30, tzinfo=NY)
    if sample == "control":
        a = a + dt.timedelta(hours=CONTROL_SHIFT_H)
    x = dt.datetime(D.year, D.month, D.day, 16, 0, tzinfo=NY)
    return int(a.timestamp()), int(x.timestamp())


_CACHE = {}


def setups(B, p, M):
    """All reference setups (one per day at most) as a dict of arrays; cached per market, anchor and history length."""
    sample = p.get("sample", "flow")
    t5 = np.asarray(B["t"], np.int64)
    key = (M.sym, p["anchor"], sample, len(t5), int(t5[-1]) if len(t5) else 0)
    if key in _CACHE:
        return _CACHE[key]
    o5, h5, l5, c5 = (np.asarray(B[k], float) for k in ("o", "h", "l", "c"))
    nxt = np.asarray(B["nxt"], np.int64)
    rows = dict(j=[], side=[], rhi=[], rlo=[], disp=[], kdec=[], kcancel=[], ktime=[], H=[], L=[], ta=[], date=[])
    out = None
    if len(t5) > 100:
        g = t5 // 1800                                                  # M30 candles from M5 candles
        st = np.flatnonzero(np.r_[True, g[1:] != g[:-1]]); en = np.r_[st[1:], len(t5)]
        m30_t = g[st] * 1800
        m30_o, m30_c = o5[st], c5[en - 1]
        m30_h, m30_l = np.maximum.reduceat(h5, st), np.minimum.reduceat(l5, st)
        e30 = ema(m30_c)
        e5 = ema(c5)
        rng = h5 - l5
        avg_prev = pd.Series(rng).rolling(DISP_N).mean().shift(1).to_numpy()
        pos30 = {int(t): i for i, t in enumerate(m30_t)}
        mts = np.asarray(M.ts, np.int64)
        d0 = dt.datetime.utcfromtimestamp(int(t5[0])).date(); d1 = dt.datetime.utcfromtimestamp(int(t5[-1])).date()
        D = d0
        while D <= d1:
            if D.weekday() < 5 and D not in NEWS:
                ta, tx = anchor_times(D, p["anchor"], sample)
                ia = pos30.get(ta)
                if ia is not None and ia >= EMA_N:
                    sa, ea = st[ia], en[ia] - 1                         # first and last M5 candle of the anchor
                    if t5[sa] == ta and t5[ea] == ta + 1500:
                        Ep, op_, cl_ = e30[ia - 1], m30_o[ia], m30_c[ia]
                        side = -1 if (op_ > Ep and cl_ < Ep) else (1 if (op_ < Ep and cl_ > Ep) else 0)
                        if side != 0:
                            H, L = m30_h[ia], m30_l[ia]
                            j = ea + 1
                            ref = -1
                            while j < len(t5) and t5[j] + 300 <= tx:
                                if (side < 0 and c5[j] > H) or (side > 0 and c5[j] < L):
                                    break                               # closed beyond the opposite end: cancel
                                cross = (side < 0 and c5[j - 1] > e5[j - 1] and c5[j] < e5[j]) or \
                                        (side > 0 and c5[j - 1] < e5[j - 1] and c5[j] > e5[j])
                                if cross and l5[j] <= H and h5[j] >= L:       # the candle touches the range
                                    ref = j; break
                                j += 1
                            if ref >= 0:
                                jc = ref + 1; kc = -1
                                while jc < len(t5) and t5[jc] + 300 <= tx:
                                    if (side < 0 and c5[jc] > H) or (side > 0 and c5[jc] < L):
                                        kc = int(nxt[jc]); break
                                    jc += 1
                                kt = int(np.searchsorted(mts, tx))
                                disp = bool(np.isfinite(avg_prev[ref]) and rng[ref] >= DISP_X * avg_prev[ref])
                                for k_, v_ in (("j", ref), ("side", side), ("rhi", h5[ref]), ("rlo", l5[ref]), ("disp", disp),
                                               ("kdec", int(nxt[ref])), ("kcancel", kc if kc >= 0 else kt), ("ktime", kt),
                                               ("H", H), ("L", L), ("ta", ta), ("date", D.toordinal())):
                                    rows[k_].append(v_)
            D += dt.timedelta(days=1)
    out = {k: np.asarray(v, np.float64 if k in ("rhi", "rlo", "H", "L") else (np.bool_ if k == "disp" else np.int64))
           for k, v in rows.items()}
    _CACHE[key] = out
    return out


def signals(B, p, M):
    S_ = setups(B, p, M)
    return [(int(j), int(s), float(hi if s < 0 else lo)) for j, s, hi, lo in zip(S_["j"], S_["side"], S_["rhi"], S_["rlo"])]


@njit(cache=False)
def _blocked(t, blo, bhi):
    s = t % 86400
    return blo <= s < bhi


@njit(cache=False)
def simulate(o, h, l, ts, gaps, kdec, side, rhi, rlo, disp, kcancel, ktime, win, tgt, be, cost, cut, delay, blo, bhi, min_r):
    """Orders and exits minute by minute. Returns rows: t_in, t_out, side, net R, stop distance, cost R, nights, financing R,
    entry, stop, target, exit price, exit reason (1 stop, 2 target, 3 time, 4 breakeven), displaced, setup index."""
    n = len(kdec); out = np.zeros((n, 15)); m = 0; N = len(o); eps = 0.1 * cost
    for j in range(n):
        sd = side[j]; k0 = kdec[j] + delay; kend = min(kcancel[j], ktime[j])
        if k0 >= N - 2:
            continue
        if ts[k0] >= cut:
            break
        stop = rhi[j] if sd < 0 else rlo[j]
        kin = -1; entry = 0.0
        if disp[j] or win == 0:
            if disp[j]:                                                 # limit at the 50% level
                lev = 0.5 * (rhi[j] + rlo[j])
            else:                                                       # stop order at the far end (A)
                lev = rlo[j] if sd < 0 else rhi[j]
            for i in range(k0, kend):
                if _blocked(ts[i], blo, bhi):
                    continue
                if disp[j]:
                    if sd < 0 and h[i] >= lev + eps:
                        kin = i; entry = max(lev, o[i]); break
                    if sd > 0 and l[i] + cost <= lev - eps:
                        kin = i; entry = min(lev, o[i] + cost); break
                else:
                    if sd < 0 and l[i] <= lev:
                        kin = i; entry = min(lev, o[i]); break
                    if sd > 0 and h[i] + cost >= lev:
                        kin = i; entry = max(lev, o[i] + cost); break
            if kin >= 0 and delay > 0 and not disp[j] and kin + delay < N:   # latency: stop orders fill a minute late
                kin = kin + delay
                entry = min(entry, o[kin]) if sd < 0 else max(entry, o[kin] + cost)
        else:                                                           # B: break first, then the pullback to the level
            lev = rlo[j] if sd < 0 else rhi[j]
            kb = -1
            for i in range(k0, kend):
                if (sd < 0 and l[i] < lev) or (sd > 0 and h[i] > lev):
                    kb = i; break
            if kb >= 0:
                for i in range(kb + 1, kend):
                    if ts[i] > ts[kb] + win * 60:
                        break
                    if _blocked(ts[i], blo, bhi):
                        continue
                    if sd < 0 and h[i] >= lev + eps:
                        kin = i; entry = max(lev, o[i]); break
                    if sd > 0 and l[i] + cost <= lev - eps:
                        kin = i; entry = min(lev, o[i] + cost); break
        if kin < 0 or kin >= ktime[j]:
            continue
        d = entry - stop if sd > 0 else stop - entry
        if d <= 0 or d < min_r * cost:
            continue
        tp = entry + tgt * d if sd > 0 else entry - tgt * d
        trig = entry + d if sd > 0 else entry - d
        cur = stop; armed = False; kx = -1; px = 0.0; why = 0
        for i in range(kin, N):
            if i >= ktime[j]:
                kx = i; px = o[i] if sd > 0 else o[i] + cost; why = 3; break
            if sd > 0:
                if l[i] <= cur:
                    px = o[i] if (i > kin and o[i] < cur) else cur; kx = i; why = 4 if armed else 1; break
                if i > kin and h[i] >= tp:
                    px = tp; kx = i; why = 2; break
                if be == 1 and not armed and i > kin and h[i] >= trig:
                    armed = True; cur = entry
            else:
                if h[i] + cost >= cur:
                    px = o[i] + cost if (i > kin and o[i] + cost > cur) else cur; kx = i; why = 4 if armed else 1; break
                if i > kin and l[i] + cost <= tp:
                    px = tp; kx = i; why = 2; break
                if be == 1 and not armed and i > kin and l[i] + cost <= trig:
                    armed = True; cur = entry
        if kx < 0:
            continue
        skip = False
        for g in gaps:
            if kin <= g < kx:
                skip = True; break
        if skip:
            continue
        r = (px - entry) / d if sd > 0 else (entry - px) / d
        out[m, 0] = ts[kin]; out[m, 1] = ts[kx]; out[m, 2] = sd; out[m, 3] = r; out[m, 4] = d; out[m, 5] = cost / d
        out[m, 8] = entry; out[m, 9] = stop; out[m, 10] = tp; out[m, 11] = px; out[m, 12] = why
        out[m, 13] = 1.0 if disp[j] else 0.0; out[m, 14] = j; m += 1
    return out[:m]


def detail(M, B, p, cut=2 ** 62, delay=0):
    """Full trade records (15 columns, see simulate) for one market and configuration."""
    S_ = setups(B, p, M)
    if len(S_["j"]) == 0:
        return np.zeros((0, 15))
    return simulate(np.asarray(M.o, float), np.asarray(M.h, float), np.asarray(M.l, float), np.asarray(M.ts, np.int64),
                    np.asarray(M.gaps, np.int64), S_["kdec"], S_["side"], S_["rhi"], S_["rlo"], S_["disp"], S_["kcancel"],
                    S_["ktime"], int(ENTRY_WIN[p["entry"]]), float(p["target"]), int(p["be"]), float(M.cost),
                    int(cut if cut else 2 ** 62), int(delay), BLOCK[0], BLOCK[1], MIN_R_COST)


def EXECUTOR(M, B, C, p, cut=2 ** 62, cost_mult=1.0, swap_mult=1.0, delay=0):
    res = detail(M, B, p, cut=cut, delay=delay)[:, :8].copy()
    if cost_mult != 1.0:
        res[:, 3] -= (cost_mult - 1.0) * res[:, 5]
    return res
