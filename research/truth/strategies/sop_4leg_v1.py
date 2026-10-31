"""Owner's 4-leg engulfing "SOP" (12 case-study documents, 2026-10-31). Rules as read from the documents; every
choice the documents leave open is listed under ASSUMPTIONS and fixed here BEFORE any result was seen.

SELL (BUY is the mirror):
  Structure, legs counted back from the newest swing: Leg 4 = swing high -> Leg 3 = swing low -> Leg 2 = LOWER swing
  high -> Leg 1 = LOWER swing low. Leg 4 to Leg 1 within 30 candles (case #8 rejected at 40).
  Engulfing at Leg 4 and at Leg 2: a bearish candle (perfect) or 2-3 consecutive bearish candles (slow) closing below
  the open of the bullish candle they "eat"; the engulfing candle(s) open and low ABOVE the 10 EMA. Highs that form
  below the EMA do not count as legs.
  EMA(10) aligned: after Leg 2 the EMA line breaks its own Leg-3 swing in the trade's direction (a lower low for sells)
  and is still below its Leg-4 peak (no break of structure against the trade; case EU#4 was rejected for one).
  Entry: sell limit inside the bullish candle eaten at Leg 4: its low + 30% of its range; 70% when Leg 4 has more than
  one engulfing or the eaten candle is not the Leg 4 high ("not at the highest point").
  Stop: Leg 4 high + 3.5 pips (the case-study boxes: e.g. #6 low 1.15929 -> stop 1.15896). Target: 2R.
  Time window (setup found inside it; the order is cancelled at the window's end): tested over all windows (owner).
  Retest: the limit order lives `valid` candles (owner: "better with less than 10 candles, also test for optimal").
  Breakeven: stop to entry at +1R, tested with and without (owner). The lab also cancels an order when a bar closes
  beyond the stop, and fills it only when the price trades through it.
OWNER'S ANSWERS (2026-10-31, given before any result): check all trading windows; swings of 3-4 candles and higher;
  engulfing = the WHOLE candle (close beyond the eaten candle's wick); stop 3.5 pips beyond the Leg 4 high; retest within
  10 candles and test the optimum; breakeven at 1:1, compare with and without.
ASSUMPTIONS (still open after the answers; one reading each): swing = a bar whose high (low) is the extreme of k bars
  on each side, known k bars later (k = the owner's "3-4 candles and higher"); engulfing "at" a leg = the eaten candle is
  the swing bar or one of the two before it and the engulfing completes within 3 bars; the owner's own window is read as
  06:00-17:00 UTC (07:30 entry taken, 19:50 rejected, UTC+1 charts).
CALIBRATION (structure only, never on results; research/sop/parity_cases.py, output research/results/sop/):
  the detector was adjusted until it found the owner's own case-study setups: EMA test on the engulfing candle's open
  (document 1), 0.3-pip feed tolerance (document 2), EMA alignment = break of the EMA's Leg-3 swing in the trade's
  direction (case #6), legs = only swings with a qualifying engulfing (EU#3). Result: same legs, entry and stop as the
  owner on EU#3, GU#1, documents 1-2, #6, #10 (owner's chart dates corrected by price: #10 = 23 Jan 2026, EU#1 = 7 Jan,
  #7 = 5 Jan, #8 = 31 Dec); owner-rejected EU#4 and #8 not flagged; EU#1 and #7 same legs but another entry; EU#2, #9
  missed. The cases lie in Oct 2025-Jan 2026: the lab's 2023-25 look and the 2026 check therefore start Feb 2026 as the
  only fully untouched period (research/sop/holdout_2026.py).
SEARCH WARNING: 7 windows x 3 swing sizes x 2 engulfing types x 3 retest limits x 2 breakeven x 3 timeframes = 756
  configurations per market; the deflated Sharpe charges for all of them (P10, P17).
Markets EURUSD, GBPUSD (the owner's pairs); timeframes M5, M15, M30 (all appear in the cases).
Costs: Exness Zero realistic (measured spreads + high-end commission + slippage), research/truth/costs_exness_zero.json.
Priors: 8 related ideas (Quasimodo, liquidity grabs, engulfing, supply/demand, FVG; ~17,800 configurations) all
rejected; limit retest entries tested worse than market entries (P2). What differs: the specific stack of filters.
"""
import os, json
import numpy as np

NAME = "sop_4leg_v1"
HYPOTHESIS = ("After a clean two-swing trend structure with engulfing rejections at both swing extremes and an aligned "
              "EMA, price returns to the origin engulfing zone (Leg 4) and continues the trend from there.")
RULES = __doc__
FAMILY = ["engulfing", "structure", "retest", "limit-entry", "intraday", "ema", "owner-idea"]
MARKETS = ["EURUSD", "GBPUSD"]
TIMEFRAMES = ["M5", "M15", "M30"]
GRID = {"k": [3, 4, 5], "engulf": ["perfect", "any"],
        "window": ["owner", "asia", "london", "overlap", "ny", "london_ny", "all"],
        "valid": [5, 10, 20], "be": [0, 1]}
MANAGEMENT = {"tgt": [2.0], "trail": [0.0], "bias": [0]}          # the target and breakeven live in the executor
TIME_STOP = 200
STOP_CAP_ATR = 1e9
_cz = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "costs_exness_zero.json")))["realistic"]
COSTS = {s: _cz[s] for s in MARKETS}
# Limit fills use the measured Exness Zero spread (worst monthly mean, conservative); commission + slippage are still paid
_sp = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "results", "exness", "zero_spreads.json")))
FILL_SPREAD = {s: max(v["mean"] for k, v in _sp.items() if k.split()[0] == s) for s in MARKETS}
PIP = 0.0001; TOL = 0.3 * 0.0001; BUF = 3.5; MAXD = 30                         # Leg 4 to Leg 1, candles
WINDOWS = {"owner": (6, 17), "asia": (23, 7), "london": (7, 12), "overlap": (12, 16), "ny": (16, 20),
           "london_ny": (7, 16), "all": (0, 24)}                 # UTC hours [start, end); asia wraps midnight
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import executors
EXECUTOR = executors.bracket(tgt=2.0, be_key="be", time_stop_bars=TIME_STOP)
_CACHE = {}


def _in_window(hour, w):
    a, b = WINDOWS[w]
    return (a <= hour < b) if a < b else (hour >= a or hour < b)


def ema(c, n=10):
    a = 2.0 / (n + 1); e = np.empty(len(c)); e[0] = c[0]
    for i in range(1, len(c)):
        e[i] = a * c[i] + (1 - a) * e[i - 1]
    return e


def engulfings(o, h, l, c, e, side, kinds):
    """List of (done_bar, eaten_bar, kind), sorted by done_bar. side -1: bearish candle(s) closing below the WHOLE bullish
    candle they eat (its low, within TOL); +1 the mirror. Perfect = one candle, slow = 2-3 consecutive candles (the first
    one that qualifies for a given done_bar). The first engulfing candle must OPEN on the far side of the 10 EMA (above it
    for sells, below for buys): the owner's "open ... above/below EMA" (calibrated on document 1, where the eaten candle
    opens 1.5 pips under the EMA and the engulfing candles above it). Whole-candle tolerance TOL = 0.3 pip for feed
    differences (document 2: the owner's 3-candle engulfing closes 0.1 pip short of the eaten low on Exness prices)."""
    o, h, l, c, e = (np.asarray(x, float) for x in (o, h, l, c, e)); n = len(c)
    if side < 0:
        eat = c[:, None] > o[:, None]; run = c < o
        beyond = lambda i, j: c[i] <= l[j] + TOL
        ema_ok = lambda j: (o[j + 1] > e[j + 1]) & (h[j] > e[j])
    else:
        eat = c[:, None] < o[:, None]; run = c > o
        beyond = lambda i, j: c[i] >= h[j] - TOL
        ema_ok = lambda j: (o[j + 1] < e[j + 1]) & (l[j] < e[j])
    eat = eat[:, 0]
    out = {}
    for m in ((1,) if kinds == "perfect" else (1, 2, 3)):
        if n <= m:
            continue
        i = np.arange(m, n); j = i - m
        ok = eat[j] & beyond(i, j) & ema_ok(j)
        for x in range(1, m + 1):
            ok &= run[j + x]
        for x in range(1, m):                                 # not engulfed earlier in the run
            ok &= ~beyond(j + x, j)
        for ii in i[ok]:
            if ii not in out:
                out[int(ii)] = (int(ii), int(ii - m), "perfect" if m == 1 else "slow")
    return [out[k] for k in sorted(out)]


def _qualify(EGd, s, s_next, side, h, l):
    """Engulfings that make swing s (high for sells, low for buys) a leg: the eaten candle lies between two candles before
    the swing and the next opposite swing, and the engulfing completes by then. EGd: {eaten bar: [engulfings]}."""
    return [x for jj in range(s - 2, s_next) for x in EGd.get(jj, ()) if x[0] <= s_next]


def setups(B, p, M=None):
    """All setups (any hour): dicts with decision bar, side, legs, entry, stop, entry pct, engulfing kinds. Cached per
    market, timeframe, swing size and engulfing type (the window, retest limit and breakeven do not change them)."""
    key = (getattr(M, "sym", None), B["minutes"], len(B["c"]), int(B["t"][-1]), p["k"], p["engulf"])
    if key in _CACHE:
        return _CACHE[key]
    res = _setups(B, p)
    _CACHE[key] = res
    return res


def _setups(B, p):
    from numpy.lib.stride_tricks import sliding_window_view as sw
    o, h, l, c, t = (np.asarray(B[x], float) for x in ("o", "h", "l", "c", "t")); n = len(c)
    k = int(p["k"]); e = ema(c)
    EGs = {}
    for sd in (-1, 1):
        d_ = {}
        for x in engulfings(o, h, l, c, e, sd, p["engulf"]):
            d_.setdefault(x[1], []).append(x)
        EGs[sd] = d_
    isH = np.zeros(n, bool); isL = np.zeros(n, bool)
    if n > 2 * k + 1:
        Wh = sw(h, k).max(axis=1); Wl = sw(l, k).min(axis=1)
        mid = slice(k, n - k)
        isH[mid] = (h[mid] >= Wh[0:n - 2 * k]) & (h[mid] > Wh[k + 1:n - k + 1])
        isL[mid] = (l[mid] <= Wl[0:n - 2 * k]) & (l[mid] < Wl[k + 1:n - k + 1])
    pts = []                                                  # compressed alternating swings [idx, type(+1 high/-1 low), price]
    used = set(); res = []
    for j in np.flatnonzero(isH | isL):
        d = int(j) + k
        newpt = []
        if isH[j]:
            newpt.append((int(j), 1, h[j]))
        if isL[j]:
            newpt.append((int(j), -1, l[j]))
        for (jj, ty, px) in newpt:
            if pts and pts[-1][1] == ty:
                if (ty == 1 and px > pts[-1][2]) or (ty == -1 and px < pts[-1][2]):
                    pts[-1] = [jj, ty, px]
                else:
                    continue
            else:
                pts.append([jj, ty, px])
            side = -1 if ty == -1 else 1                      # a new low may complete a sell setup; a new high a buy setup
            r = _try(pts, side, EGs[side], o, h, l, c, e, d)
            if r and (r["legs"][0], side) not in used:
                used.add((r["legs"][0], side)); res.append(r)
    return res


def _try(pts, side, EGd, o, h, l, c, e, d):
    """Sell: newest point = Leg 1 (a low). Leg 2 = the newest QUALIFIED high before it (highs without an engulfing are not
    legs, but none may exceed Leg 2); Leg 4 = the newest qualified high before Leg 2, higher than Leg 2 (and not exceeded
    in between); Leg 3 = the lowest low between Leg 4 and Leg 2; Leg 1 below Leg 3. Buy: mirror."""
    X = 1 if side < 0 else -1                                 # type of the legs that need an engulfing (+1 highs for sells)
    if pts[-1][1] != -X:
        return None
    s1, p1 = pts[-1][0], pts[-1][2]
    ext = (lambda a, b: a > b) if X == 1 else (lambda a, b: a < b)          # "beyond" for the leg extremes
    legs_q = []                                               # qualified X-type points before Leg 1, newest first
    for q in range(len(pts) - 2, -1, -1):
        if pts[q][0] < s1 - MAXD - 2:
            break                                             # Leg 4 must be within MAXD candles of Leg 1
        if pts[q][1] != X:
            continue
        nxt = pts[q + 1][0] if q + 1 < len(pts) else s1
        eg = _qualify(EGd, pts[q][0], nxt, side, h, l)
        legs_q.append((q, eg))
        if len([x for x in legs_q if x[1]]) >= 2:
            break
    qual = [(q, eg) for q, eg in legs_q if eg]
    if len(qual) < 2:
        return None
    (q2, eg2), (q4, eg4) = qual[0], qual[1]
    s2, p2 = pts[q2][0], pts[q2][2]; s4, p4 = pts[q4][0], pts[q4][2]
    if not ext(p4, p2):
        return None                                           # Leg 2 must be a lower high (sells)
    for q, _ in legs_q:                                       # unqualified X points may not break the structure
        if q > q2 and ext(pts[q][2], p2):
            return None
        if q4 < q < q2 and ext(pts[q][2], p4):
            return None
    mids = [pts[q][2] for q in range(q4 + 1, q2) if pts[q][1] == -X]
    if not mids:
        return None
    p3 = min(mids) if X == 1 else max(mids)
    s3 = [pts[q][0] for q in range(q4 + 1, q2) if pts[q][2] == p3][0]
    if not ext(p3, p1):
        return None                                           # Leg 1 must be a lower low (sells)
    if s1 - s4 > MAXD:
        return None
    # EMA aligned (calibrated on cases #6, EU#3, EU#4, documents 1-2): after Leg 2 the EMA breaks its Leg-3 swing in the
    # trade's direction (a lower low for sells, a higher high for buys), and it has not broken back past its Leg-4 extreme
    if X == 1:
        ok = e[s2:d + 1].min() < e[s3:s2 + 1].min() and e[d] < e[s4:s3 + 1].max()
    else:
        ok = e[s2:d + 1].max() > e[s3:s2 + 1].max() and e[d] > e[s4:s3 + 1].min()
    if not ok:
        return None
    jx = (max if X == 1 else min)(eg4, key=lambda x: h[x[1]] if X == 1 else l[x[1]])[1]
    rng = h[jx] - l[jx]
    if rng <= 0:
        return None
    at_extreme = (h[jx] >= p4) if X == 1 else (l[jx] <= p4)
    pct = 0.7 if (len(eg4) > 1 or not at_extreme) else 0.3
    if side < 0:
        entry = l[jx] + pct * rng; stop = p4 + BUF * PIP
        if not (c[d] < entry < stop):
            return None
    else:
        entry = h[jx] - pct * rng; stop = p4 - BUF * PIP
        if not (stop < entry < c[d]):
            return None
    return dict(d=d, side=side, legs=(s4, s3, s2, s1), entry=entry, stop=stop, pct=pct,
                eg4=[x[2] for x in eg4], eg2=[x[2] for x in eg2])


def signals(B, p, M):
    t = np.asarray(B["t"]); mins = B["minutes"]; w = p["window"]
    rows = []
    for s in setups(B, p, M):
        dec_t = int(t[s["d"]] + mins * 60)
        hour = (dec_t % 86400) // 3600
        if not _in_window(hour, w):
            continue
        valid = int(p["valid"])
        a, b = WINDOWS[w]
        if w != "all":                                        # cancel at the window's end
            day0 = (dec_t // 86400) * 86400
            end_t = day0 + b * 3600 if (a < b or hour < b) else day0 + 86400 + b * 3600
            valid = min(valid, int((end_t - dec_t) // (mins * 60)))
        if valid <= 0:
            continue
        rows.append((s["d"], s["side"], s["stop"], s["entry"], valid))
    return rows
