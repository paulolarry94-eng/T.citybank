"""Higher-frequency strategy families (from the awesome-systematic-trading families that our
data can test: momentum & reversal, seasonality, time-series momentum).

All trades: entry at the first minute at/after the entry time, at ask for longs / bid for
shorts (cost added), protective stop = k x daily ATR (checked minute by minute, gapped
stops fill at the worse open), otherwise exit at the first minute at/after the exit time
(long exits on bid, short exits on ask). R = P&L / stop distance.
"""
import numpy as np
from numba import njit
import engine as E

DAY = 86400


@njit(cache=True)
def scan_window(o, h, l, i0, i1, side, entry, sl, cost):
    """Stop-protected hold from minute i0 to the open of minute i1."""
    for i in range(i0, i1):
        if side > 0:
            if l[i] <= sl:
                px = sl if (o[i] > sl or i == i0) else o[i]
                return i, min(px, sl)
        else:
            if h[i] + cost >= sl:
                ao = o[i] + cost
                px = sl if (ao < sl or i == i0) else ao
                return i, max(px, sl)
    if side > 0:
        return i1, o[i1]
    return i1, o[i1] + cost


def daily_bars(ts, o, h, l, c):
    bt, bo, bh, bl, bc, nxt = E.resample(ts, o, h, l, c, 1440, 0)
    atr = E.atr_sma(bh, bl, bc, 14)
    return bt, bo, bh, bl, bc, atr


def _trade(m1, gaps, t_entry, t_exit, side, dist, cost):
    ts, o, h, l, c = m1
    i0 = np.searchsorted(ts, t_entry)
    i1 = np.searchsorted(ts, t_exit)
    if i0 >= len(ts) - 1 or i1 >= len(ts) or i1 <= i0:
        return None
    if ts[i0] - t_entry > 6 * 3600:          # market closed at entry time (holiday)
        return None
    if E.crosses_gap(gaps, i0, i1):
        return None
    entry = o[i0] + cost if side > 0 else o[i0]
    sl = entry - dist if side > 0 else entry + dist
    xi, px = scan_window(o, h, l, i0, i1, side, entry, sl, cost)
    r = (px - entry) / dist if side > 0 else (entry - px) / dist
    return (int(ts[i0]), int(ts[xi]), side, r, dist, entry)


def _pack(rows):
    return np.array(rows, dtype=[("t_in", "i8"), ("t_out", "i8"), ("side", "i8"),
                                 ("r", "f8"), ("dist", "f8"), ("entry", "f8")])


def weekday(t):
    return int((t // DAY + 3) % 7)    # 0 = Monday


def run_session(sym, m1, h_in, h_out, side, k_stop=1.0, cost=None):
    """Seasonality: every weekday, fixed direction from h_in to h_out (UTC hours)."""
    ts = m1[0]; cost = E.COST[sym] if cost is None else cost
    bt, bo, bh, bl, bc, atr = daily_bars(*m1)
    gaps = E.data_gaps(ts)
    rows = []
    for d in range(15, len(bt)):
        day0 = (bt[d] // DAY) * DAY
        if weekday(day0) > 4:
            continue
        A = atr[d - 1]
        if not np.isfinite(A):
            continue
        t0 = day0 + h_in * 3600
        t1 = day0 + h_out * 3600 if h_out > h_in else day0 + DAY + h_out * 3600
        tr = _trade(m1, gaps, t0, t1, side, k_stop * A, cost)
        if tr: rows.append(tr)
    return _pack(rows)


def run_intraday_momentum(sym, m1, h_sig, h_out=20, follow=True, k_stop=1.0, cost=None):
    """Intraday momentum: sign of the move from 00:00 UTC to h_sig sets the trade
    direction (follow) or its opposite (fade), held from h_sig to h_out."""
    ts, o, h, l, c = m1; cost = E.COST[sym] if cost is None else cost
    bt, bo, bh, bl, bc, atr = daily_bars(*m1)
    gaps = E.data_gaps(ts)
    rows = []
    for d in range(15, len(bt)):
        day0 = (bt[d] // DAY) * DAY
        if weekday(day0) > 4:
            continue
        A = atr[d - 1]
        if not np.isfinite(A):
            continue
        i_a = np.searchsorted(ts, day0); i_b = np.searchsorted(ts, day0 + h_sig * 3600) - 1
        if i_b <= i_a or i_b >= len(ts):
            continue
        move = c[i_b] - o[i_a]
        if abs(move) < 0.25 * A:           # no clear morning direction
            continue
        side = (1 if move > 0 else -1) * (1 if follow else -1)
        tr = _trade(m1, gaps, day0 + h_sig * 3600, day0 + h_out * 3600, side, k_stop * A, cost)
        if tr: rows.append(tr)
    return _pack(rows)


def run_reversal(sym, m1, k_move=1.0, k_stop=1.0, cost=None):
    """Short-term reversal: after a day whose range-adjusted move exceeds k_move x ATR,
    trade against it for the next day (00:00 -> 20:00 UTC)."""
    ts = m1[0]; cost = E.COST[sym] if cost is None else cost
    bt, bo, bh, bl, bc, atr = daily_bars(*m1)
    gaps = E.data_gaps(ts)
    rows = []
    for d in range(16, len(bt)):
        A = atr[d - 1]
        if not np.isfinite(A):
            continue
        move = bc[d - 1] - bo[d - 1]
        if abs(move) < k_move * A:
            continue
        day0 = (bt[d] // DAY) * DAY
        if weekday(day0) > 4:
            continue
        side = -1 if move > 0 else 1
        tr = _trade(m1, gaps, day0, day0 + 20 * 3600, side, k_stop * A, cost)
        if tr: rows.append(tr)
    return _pack(rows)


def run_tsmom_weekly(sym, m1, lookback=20, k_stop=2.0, sides=(1, -1), cost=None):
    """Time-series momentum: each Monday 00:00 UTC, trade the sign of the last `lookback`
    daily closes; exit Friday 20:00 UTC or at the 2xATR stop."""
    ts = m1[0]; cost = E.COST[sym] if cost is None else cost
    bt, bo, bh, bl, bc, atr = daily_bars(*m1)
    gaps = E.data_gaps(ts)
    rows = []
    for d in range(lookback + 15, len(bt)):
        day0 = (bt[d] // DAY) * DAY
        if weekday(day0) != 0:
            continue
        A = atr[d - 1]
        if not np.isfinite(A):
            continue
        side = 1 if bc[d - 1] > bc[d - 1 - lookback] else -1
        if side not in sides:
            continue
        tr = _trade(m1, gaps, day0, day0 + 4 * DAY + 20 * 3600, side, k_stop * A, cost)
        if tr: rows.append(tr)
    return _pack(rows)
