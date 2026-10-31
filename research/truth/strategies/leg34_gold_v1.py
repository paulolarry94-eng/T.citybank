"""Owner's "Leg 34" setup on gold, 5-minute chart (owner's screenshots of 29-30 Oct 2026 and answers, 2026-10-31).
Rules fixed here BEFORE any result was seen; every open choice is listed under ASSUMPTIONS.

SELL (BUY is the mirror). Same structure detector as sop_4leg_v1 (calibrated on the owner's 12 case studies):
  Legs counted back from the newest swing: Leg 4 = swing high -> Leg 3 = swing low -> Leg 2 = LOWER swing high ->
  Leg 1 = LOWER swing low; Leg 4 to Leg 1 within 30 candles.
  A high counts as a leg only if it breaks above the 10 EMA with an engulfing there (owner: "the heads that don't break
  above the 10 EMA and form a leg formation, an engulfing above the 10 EMA, don't count"): bearish candle(s) closing
  below the WHOLE bullish candle they eat, the first one opening above the EMA.
  EMA(10) slope read like a line chart: after Leg 2 the EMA makes a lower low than at Leg 3 and stays below its Leg 4
  peak (owner: "the blue line ... sloping down and you see a sell setup").
  Entry: sell limit inside the WHOLE eaten Leg 4 candle (body and wick): its low + 30% of its range. (The EUR documents'
  70% rule is NOT used: on the owner's dated gold trades of 30 Oct 2026 both checkable entries sit at 30% of the eaten
  candle, 4011.95 vs 4011.74 and 4007.97 vs 4008.0, and the 70% rule misses both fills. Structure-only calibration,
  research/sop/leg34_parity.py, done before any result.)
  Stop: Leg 4 high + buffer. Order life: 8 hours = 96 five-minute candles (owner: "a limit is fine but expires after
  8 hrs"); the lab also cancels it when a candle closes beyond the stop.
  Exits compared (owner: "try both and compare, and explore if trailing increases alpha"), executors.managed:
    t3 / t4      fixed target 3R / 4R, no breakeven
    t3be / t4be  the same with the stop moved to entry at +1R (owner's earlier "breakeven at 1:1")
    ladder       breakeven at +1R, then each completed R locks the previous one (+2R -> stop +1R, ...), no target
    ema          breakeven at +1R, then exit after the first 5-min candle that closes beyond the 10 EMA, no target
  Time stop 288 candles (24 hours) for every exit.
OWNER'S ANSWERS (2026-10-31): the name is "Leg 34"; the zone is the whole eaten candle; small heads inside the move do
  not count; limit valid 8 hours; compare 3R and 4R and test trailing; EMA slope as above. Not answered (defaults here):
ASSUMPTIONS: stop buffer on gold, two readings tested: "fixed" = $0.35 (3.5 pips at gold's $0.10 pip) and "scaled" =
  0.032% of price (3.5 EUR pips at 1.10, the same relative size as on the owner's EUR cases); trading hours: "all" and
  the owner's earlier window 06:00-17:00 UTC ("owner"; note the dated screenshots trade 21:30-05:00 UTC); whole-candle
  tolerance 0.0027% of price (the 0.3-pip EUR feed tolerance, scaled); swing size k = 3, 4, 5 candles.
DATA DISCIPLINE: the owner's screenshots are from late October 2026 (found by price: 30 Oct 2026 01:20 UTC candle), so
  the final untouched check is January-September 2026; October 2026 is reported separately (research/sop/leg34_2026.py).
SEARCH WARNING: 3 swing sizes x 2 engulfing types x 2 windows x 2 buffers x 6 exits = 144 configurations; the deflated
  Sharpe charges for all of them.
Costs: Exness Zero realistic for XAUUSD ($0.16 round trip incl. commission and slippage); limit fills at the worst
  measured monthly Zero spread.
Priors (memory, 2026-10-31): sop_4leg_v1 (EUR/GBP M5-M30, 2R) and sop_4leg_gold_v1 (gold H4/D1, 2R) rejected; ~1,400
  liquidity-sweep variants rejected (P7); limit retests suffer adverse selection (P2). What differs: gold on M5 (never
  tested), 3R/4R targets and trailing exits (never tested), 8-hour order life, and gold's cost is small relative to the stop.
"""
import os, json, sys
import numpy as np

NAME = "leg34_gold_v1"
HYPOTHESIS = ("On gold's 5-minute chart, after a 4-3-2-1 trend structure with engulfing legs above (below) the 10 EMA and a "
              "falling (rising) EMA, price returns to the eaten Leg 4 candle within 8 hours and continues the trend far "
              "enough for 3-4R targets or a trailing exit to pay after costs.")
RULES = __doc__
FAMILY = ["engulfing", "structure", "retest", "limit-entry", "intraday", "ema", "owner-idea", "gold", "trailing"]
MARKETS = ["XAUUSD"]
TIMEFRAMES = ["M5"]
GRID = {"k": [3, 4, 5], "engulf": ["perfect", "any"], "window": ["all", "owner"], "buffer": ["fixed", "scaled"],
        "exit": ["t3", "t4", "t3be", "t4be", "ladder", "ema"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}          # exits live in the executor (grid key "exit")
TIME_STOP = 288
STOP_CAP_ATR = 1e9
VALID = 96                                                       # 8 hours of 5-minute candles
_here = os.path.dirname(os.path.abspath(__file__))
_cz = json.load(open(os.path.join(_here, "..", "costs_exness_zero.json")))["realistic"]
COSTS = {s: _cz[s] for s in MARKETS}
_sp = json.load(open(os.path.join(_here, "..", "..", "results", "exness", "zero_spreads.json")))
FILL_SPREAD = {s: max(v["mean"] for k, v in _sp.items() if k.split()[0] == s) for s in MARKETS}
TOL_REL = 2.7e-5                                                 # whole-candle tolerance, share of price
BUF_FIXED = 0.35; BUF_REL = 3.2e-4                               # stop buffer beyond the Leg 4 extreme
MAXD = 30                                                        # Leg 4 to Leg 1, candles
ENTRY_PCT = 0.3                                                  # 30% into the eaten candle (calibrated, see RULES)
WINDOWS = {"owner": (6, 17), "all": (0, 24)}                     # UTC hours [start, end)
sys.path.insert(0, os.path.join(_here, ".."))
import executors
_CACHE = {}


def ema(c, n=10):
    a = 2.0 / (n + 1); e = np.empty(len(c)); e[0] = c[0]
    for i in range(1, len(c)):
        e[i] = a * c[i] + (1 - a) * e[i - 1]
    return e


EXECUTOR = executors.managed(exit_key="exit", time_stop_bars=TIME_STOP, ema_fn=ema)


def _in_window(hour, w):
    a, b = WINDOWS[w]
    return (a <= hour < b) if a < b else (hour >= a or hour < b)


def engulfings(o, h, l, c, e, side, kinds):
    """(done_bar, eaten_bar, kind) sorted by done_bar. Sell: bearish candle(s) closing below the WHOLE bullish candle
    they eat (its low, within the tolerance); perfect = one candle, slow = 2-3 consecutive candles; the first engulfing
    candle opens above the 10 EMA and the eaten candle's high is above it. Buy: mirror."""
    o, h, l, c, e = (np.asarray(x, float) for x in (o, h, l, c, e)); n = len(c)
    if side < 0:
        eat = c > o; run = c < o
        beyond = lambda i, j: c[i] <= l[j] * (1 + TOL_REL)
        ema_ok = lambda j: (o[j + 1] > e[j + 1]) & (h[j] > e[j])
    else:
        eat = c < o; run = c > o
        beyond = lambda i, j: c[i] >= h[j] * (1 - TOL_REL)
        ema_ok = lambda j: (o[j + 1] < e[j + 1]) & (l[j] < e[j])
    out = {}
    for m in ((1,) if kinds == "perfect" else (1, 2, 3)):
        if n <= m:
            continue
        i = np.arange(m, n); j = i - m
        ok = eat[j] & beyond(i, j) & ema_ok(j)
        for x in range(1, m + 1):
            ok &= run[j + x]
        for x in range(1, m):
            ok &= ~beyond(j + x, j)
        for ii in i[ok]:
            if ii not in out:
                out[int(ii)] = (int(ii), int(ii - m), "perfect" if m == 1 else "slow")
    return [out[k] for k in sorted(out)]


def _qualify(EGd, s, s_next):
    return [x for jj in range(s - 2, s_next) for x in EGd.get(jj, ()) if x[0] <= s_next]


def setups(B, p, M=None):
    key = (getattr(M, "sym", None), B["minutes"], len(B["c"]), int(B["t"][-1]), p["k"], p["engulf"])
    if key not in _CACHE:
        _CACHE[key] = _setups(B, p)
    return _CACHE[key]


def _setups(B, p):
    from numpy.lib.stride_tricks import sliding_window_view as sw
    o, h, l, c = (np.asarray(B[x], float) for x in ("o", "h", "l", "c")); n = len(c)
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
    pts = []; used = set(); res = []
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
            side = -1 if ty == -1 else 1
            r = _try(pts, side, EGs[side], h, l, c, e, d)
            if r and (r["legs"][0], side) not in used:
                used.add((r["legs"][0], side)); res.append(r)
    return res


def _try(pts, side, EGd, h, l, c, e, d):
    """Sell: newest point = Leg 1 (a low); Leg 2 = newest QUALIFIED high before it; Leg 4 = the qualified high before
    that, higher than Leg 2; Leg 3 = lowest low between; Leg 1 below Leg 3; unqualified highs may not break the
    structure. Buy: mirror. Returns the entry inside the eaten Leg 4 candle and the Leg 4 extreme (stop = it + buffer)."""
    X = 1 if side < 0 else -1
    if pts[-1][1] != -X:
        return None
    s1, p1 = pts[-1][0], pts[-1][2]
    ext = (lambda a, b: a > b) if X == 1 else (lambda a, b: a < b)
    legs_q = []
    for q in range(len(pts) - 2, -1, -1):
        if pts[q][0] < s1 - MAXD - 2:
            break
        if pts[q][1] != X:
            continue
        nxt = pts[q + 1][0] if q + 1 < len(pts) else s1
        eg = _qualify(EGd, pts[q][0], nxt)
        legs_q.append((q, eg))
        if len([x for x in legs_q if x[1]]) >= 2:
            break
    qual = [(q, eg) for q, eg in legs_q if eg]
    if len(qual) < 2:
        return None
    (q2, eg2), (q4, eg4) = qual[0], qual[1]
    s2, p2 = pts[q2][0], pts[q2][2]; s4, p4 = pts[q4][0], pts[q4][2]
    if not ext(p4, p2):
        return None
    for q, _ in legs_q:
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
        return None
    if s1 - s4 > MAXD:
        return None
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
    pct = ENTRY_PCT
    if side < 0:
        entry = l[jx] + pct * rng
        if not (c[d] < entry <= p4):
            return None
    else:
        entry = h[jx] - pct * rng
        if not (p4 <= entry < c[d]):
            return None
    return dict(d=d, side=side, legs=(s4, s3, s2, s1), entry=entry, p4=p4, pct=pct,
                eg4=[x[2] for x in eg4], eg2=[x[2] for x in eg2])


def stop_of(s, buffer):
    b = BUF_FIXED if buffer == "fixed" else BUF_REL * s["p4"]
    return s["p4"] + b if s["side"] < 0 else s["p4"] - b


def signals(B, p, M):
    t = np.asarray(B["t"]); mins = B["minutes"]; w = p["window"]
    rows = []
    for s in setups(B, p, M):
        dec_t = int(t[s["d"]] + mins * 60)
        hour = (dec_t % 86400) // 3600
        if not _in_window(hour, w):
            continue
        valid = VALID
        a, b = WINDOWS[w]
        if w != "all":                                           # cancel at the window's end, if sooner
            day0 = (dec_t // 86400) * 86400
            end_t = day0 + b * 3600 if (a < b or hour < b) else day0 + 86400 + b * 3600
            valid = min(valid, int((end_t - dec_t) // (mins * 60)))
        if valid <= 0:
            continue
        rows.append((s["d"], s["side"], stop_of(s, p["buffer"]), s["entry"], valid))
    return rows
