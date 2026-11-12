"""Deep M1 study (research/sweep6/PREREGISTRATION.md): the setup detector (v2 reading, superset) and every feature known
when candle 4 closes. Nothing here looks past candle 4.

SELL (BUY is the mirror): candle 1 bullish (doji = bullish), candle 2 bearish closing below candle 1's open, candle 3
bullish, candle 4 bearish closing below candle 3's open; candles 2 and 4 bodies >= body_min (superset 40%). Range = candle 4's
low to the highest high of the four; sell limit at 60% up; stop at the range high.
Sweeps: bar j sweeps a live pivot high when its high trades above it (Pivots HL 10/10, research/sweep4/pivots.py). `swmask`
bit d = bar k-d (d = 0 candle 4, 1 candle 3, 2 candle 2, 3 candle 1, 4 the candle before candle 1, ..., 13 = 10 before
candle 1) swept a pivot on the STOP side (sell: a pivot high); `tgmask` the same for the target side.
"""
import os, sys
import numpy as np
import pandas as pd
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sweep4")); sys.path.insert(0, os.path.join(HERE, "..", "sweep5"))
import pivots as PV                    # noqa: E402
from sweep5_scan import live_levels    # noqa: E402

PIP = {"EURUSD": 1e-4, "GBPUSD": 1e-4, "EURGBP": 1e-4, "USDJPY": 1e-2, "XAUUSD": 0.1, "XAGUSD": 0.01, "WTI": 0.01,
       "US500": 1.0, "NAS100": 1.0, "GER40": 1.0, "UK100": 1.0, "JP225": 1.0}
BACK = 10            # candles before candle 1 searched for a sweep
WIN = BACK + 4       # bars k-13 .. k
ENTRY = 0.6


def detect(o, h, l, c, body_min=0.4):
    n = len(c)
    bull, bear = c >= o, c < o
    hl = h - l
    frac = np.where(hl > 0, np.abs(c - o) / np.where(hl > 0, hl, 1.0), 0.0)
    dn = np.zeros(n, bool); up = np.zeros(n, bool)
    dn[1:] = bull[:-1] & bear[1:] & (c[1:] < o[:-1]) & (frac[1:] >= body_min)
    up[1:] = bear[:-1] & bull[1:] & (c[1:] > o[:-1]) & (frac[1:] >= body_min)
    k = np.arange(3, n)
    sell = dn[k - 2] & dn[k]; buy = up[k - 2] & up[k]
    kk = k[sell | buy]
    side = np.where(buy[sell | buy], 1, -1)
    return kk.astype(np.int64), side.astype(np.int64), frac


@njit(cache=True)
def sweep_bars(h, l, ph, pl, right):
    """Per bar: how many live pivot highs / lows it swept, the most extreme one swept (highest high / lowest low) and
    that pivot's bar index. Same order as pivots.structure: sweeps first, then the pivot confirmed at this bar."""
    n = len(h)
    nH = np.zeros(n, np.int32); topH = np.full(n, np.nan); topHi = np.full(n, -1, np.int64)
    nL = np.zeros(n, np.int32); botL = np.full(n, np.nan); botLi = np.full(n, -1, np.int64)
    sh = np.zeros(n // 2 + 2); shi = np.zeros(n // 2 + 2, np.int64); sl = np.zeros(n // 2 + 2); sli = np.zeros(n // 2 + 2, np.int64)
    nh = 0; nl = 0
    for j in range(n):
        while nh > 0 and h[j] > sh[nh - 1]:
            nH[j] += 1; topH[j] = sh[nh - 1]; topHi[j] = shi[nh - 1]; nh -= 1
        while nl > 0 and l[j] < sl[nl - 1]:
            nL[j] += 1; botL[j] = sl[nl - 1]; botLi[j] = sli[nl - 1]; nl -= 1
        i = j - right
        if i >= 0:
            if ph[i]:
                sh[nh] = h[i]; shi[nh] = i; nh += 1
            if pl[i]:
                sl[nl] = l[i]; sli[nl] = i; nl += 1
    return nH, topH, topHi, nL, botL, botLi


def rolling(x, w, how):
    s = pd.Series(x)
    r = getattr(s.rolling(w, min_periods=1), how)()
    return r.to_numpy()


def setups(B, tf_min, sym, piv=10, body_min=0.4):
    o, h, l, c = (np.asarray(B[x], float) for x in "ohlc")
    t = np.asarray(B["t"], np.int64)
    k, side, frac = detect(o, h, l, c, body_min)
    keep = k >= 1440 + WIN
    k, side = k[keep], side[keep]
    sell = side < 0
    ph, pl = PV.pivots(h, l, piv, piv)
    nH, topH, topHi, nL, botL, botLi = sweep_bars(h, l, ph, pl, piv)
    LH, LL = live_levels(h, l, ph, pl, piv, 3)
    swmask = np.zeros(len(k), np.int64); tgmask = np.zeros(len(k), np.int64); npiv = np.zeros(len(k), np.int64)
    for d in range(WIN):
        j = k - d
        st_side = np.where(sell, nH[j], nL[j]); tg_side = np.where(sell, nL[j], nH[j])
        swmask |= (st_side > 0).astype(np.int64) << d
        tgmask |= (tg_side > 0).astype(np.int64) << d
        npiv += st_side
    has = swmask > 0
    pos = np.full(len(k), -1)
    for d in range(WIN - 1, -1, -1):                       # latest (smallest d) wins
        pos = np.where((swmask >> d) & 1 == 1, d, pos)
    js = np.where(has, k - np.maximum(pos, 0), k)
    lvl_sw = np.where(sell, topH[js], botL[js])
    depth = np.where(has, np.where(sell, h[js] - lvl_sw, lvl_sw - l[js]), np.nan)
    reject = np.where(has, np.where(sell, c[js] < lvl_sw, c[js] > lvl_sw), False)
    age = np.where(has, js - np.where(sell, topHi[js], botLi[js]), -1)
    hi4 = np.max(np.stack([h[k - j] for j in range(4)]), axis=0)
    lo4 = np.min(np.stack([l[k - j] for j in range(4)]), axis=0)
    hi = np.where(sell, hi4, h[k]); lo = np.where(sell, l[k], lo4)
    w = hi - lo
    level = np.where(sell, lo + ENTRY * w, hi - ENTRY * w)
    stop = np.where(sell, hi, lo)
    risk = np.abs(level - stop)
    atr = np.asarray(B["atr"], float)[k]
    atr = np.where(atr > 0, atr, np.nan)
    tr = np.r_[h[0] - l[0], np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1])]
    atr_day = rolling(tr, 1440, "mean")[k]
    dmax = rolling(h, 1440, "max")[k]; dmin = rolling(l, 1440, "min")[k]
    drng = np.where(dmax - dmin > 0, dmax - dmin, np.nan)
    ext = np.where(sell, h[js], l[js])
    room = []
    for m in range(2):
        L = np.where(sell, LL[k, m], LH[k, m])
        room.append(np.where(np.isfinite(L) & ((L - level) * side > 0), (L - level) * side / risk, np.nan))
    tconf = t[k] + tf_min * 60
    pip = PIP[sym]
    S = dict(k=k, side=side, t_conf=tconf, hi=hi, lo=lo, level=level, stop=stop, risk=risk,
             body2=frac[k - 2], body4=frac[k], body_min=np.minimum(frac[k - 2], frac[k]),
             strict2=np.where(sell, o[k - 2] >= c[k - 3], o[k - 2] <= c[k - 3]),
             strict4=np.where(sell, o[k] >= c[k - 1], o[k] <= c[k - 1]),
             swmask=swmask, tgmask=tgmask, sweep_pos=pos, n_sweep_bars=np.array([bin(x).count("1") for x in swmask]),
             pivots_swept=npiv, depth_atr=depth / atr, depth_R=depth / risk, depth_pips=depth / pip, reject=reject,
             pivot_age=age, stop_vs_sweep_R=np.where(has, np.where(sell, hi - ext, ext - lo) / risk, np.nan),
             pullback_atr=np.where(has, np.where(sell, ext - c[k], c[k] - ext) / atr, np.nan),
             range_atr=w / atr, risk_atr=risk / atr, risk_pips=risk / pip,
             ratio4=(h[k] - l[k]) / np.where(h[k - 1] - l[k - 1] > 0, h[k - 1] - l[k - 1], np.nan),
             ratio2=(h[k - 2] - l[k - 2]) / np.where(h[k - 3] - l[k - 3] > 0, h[k - 3] - l[k - 3], np.nan),
             c4pos=np.where(sell, c[k] - lo, hi - c[k]) / np.where(w > 0, w, np.nan),
             hour=((tconf - 1) // 3600) % 24, weekday=((tconf - 1) // 86400 + 3) % 7,
             mom60=(c[k] - c[k - 60]) * side / atr, mom1440=(c[k] - c[k - 1440]) * side / drng,
             vol_regime=atr / atr_day, daypos=np.where(sell, c[k] - dmin, dmax - c[k]) / drng,
             room1=room[0], room2=room[1], two_sided=(tgmask & swmask) >= 0 & (tgmask > 0))
    S["two_sided"] = tgmask > 0
    return S, dict(bt=t, LH=LH, LL=LL, minutes=int(tf_min))


def orders(S, L, life=60):
    return dict(t_conf=S["t_conf"], side=S["side"], level=S["level"], stop=S["stop"],
                t_exp=S["t_conf"] + int(life) * L["minutes"] * 60)
