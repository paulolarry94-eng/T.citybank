"""Daily structure, round two.

1 Trend-aligned intraday sweeps  (Asian / previous-day level swept and reclaimed only in the
  direction of the daily trend; hold to next day 20:00; target the opposite daily pool)
2 Daily-candle sweeps            (D1 bar trades through PDH/PDL and closes back inside ->
  trade from next day open, stop beyond the sweep bar, multi-day hold); weekly equivalent
3 Turtle Soup Plus One (Raschke) (close beyond the prior 20-day extreme set >= 3 days earlier;
  next day a stop order back through that extreme fades it)
4 NR4 / NR7 breakout (Crabel)    (narrowest range of 4/7 days -> next day stop orders at the
  range extremes, stop at the other side, exit at day end)
5 Failed daily sweep -> continuation (the day after a daily sweep closes beyond its extreme)
Same fill law and costs as everything else.
"""
import numpy as np
import engine as E, gold_lab as GL, liquidity as LQ

DAY = 86400


def daily(G):
    D = G.tf("D1", offset=0)                      # UTC days
    return D


def d1_trend(D, fast=20, slow=50):
    f, s = E.ema(D["c"], fast), E.ema(D["c"], slow)
    return np.where(f > s, 1, np.where(f < s, -1, 0))


def _run_abs(G, ent_i, side, sl, tp_abs, tp_r, exit_i, min_d):
    if len(ent_i) == 0:
        return np.zeros(0, dtype=GL.DT)
    o = np.argsort(ent_i, kind="stable")
    A = lambda x, t=np.float64: np.asarray(x, t)[o]
    res = LQ.run_abs(G.o, G.h, G.l, G.ts, A(ent_i, np.int64), A(side, np.int64), A(sl), A(tp_abs), A(tp_r),
                     A(exit_i, np.int64), G.cost, A(min_d), G.gaps)
    return LQ.pack(res)


def daily_sweep(G, level="day", target="2", hold=3, trend=None, failed=False, buf=0.05):
    """Daily (or weekly) candle sweep & close back inside -> next bar open. failed=True:
    the following bar closes beyond the sweep extreme -> continuation instead."""
    if level == "day":
        B = daily(G)
    else:
        B = G.tf("D1", offset=0)
        # build weekly bars from daily
        dk = B["t"] // DAY; wk = (dk + 3) // 7
        starts = np.flatnonzero(np.r_[True, wk[1:] != wk[:-1]]); ends = np.r_[starts[1:], len(wk)]
        B = dict(t=B["t"][starts], o=B["o"][starts], h=np.maximum.reduceat(B["h"], starts),
                 l=np.minimum.reduceat(B["l"], starts), c=B["c"][ends - 1], nxt=B["nxt"][ends - 1])
        B["atr"] = E.atr_sma(B["h"], B["l"], B["c"], 14)
    h, l, c, atr, nxt = B["h"], B["l"], B["c"], B["atr"], B["nxt"]
    tr = d1_trend(daily(G)) if trend else None
    ent, side, sl, tpa, tpr, ex, md = [], [], [], [], [], [], []
    n = len(c)
    for t in range(15, n - hold - 2):
        if not np.isfinite(atr[t]):
            continue
        for s, swept in ((-1, h[t] > h[t - 1] and c[t] < h[t - 1]), (1, l[t] < l[t - 1] and c[t] > l[t - 1])):
            if not swept:
                continue
            ext = h[t] if s < 0 else l[t]
            if failed:
                u = t + 1
                if not ((s < 0 and c[u] > ext) or (s > 0 and c[u] < ext)):
                    continue
                s2 = -s; stop = (h[t - 1] if s2 > 0 else l[t - 1])        # back inside = wrong
                stop = stop - buf * atr[t] if s2 > 0 else stop + buf * atr[t]
                e_bar, s_use = u, s2
            else:
                stop = ext + buf * atr[t] if s < 0 else ext - buf * atr[t]
                e_bar, s_use = t, s
            if trend and tr is not None and level == "day":
                if tr[e_bar] != s_use:
                    continue
            ent.append(nxt[e_bar]); side.append(s_use); sl.append(stop)
            if target == "pool":
                tpa.append(l[t - 1] if s_use < 0 else h[t - 1]); tpr.append(0.0)
            else:
                tpa.append(0.0); tpr.append(float(target))
            ex.append(nxt[min(e_bar + hold, n - 1)]); md.append(max(0.15 * atr[t], 3 * G.cost))
    return _run_abs(G, ent, side, sl, tpa, tpr, ex, md)


def turtle_soup_plus_one(G, n=20, gap=3, target="2", hold=3, buf=0.05, tfn="D1"):
    B = G.tf(tfn, offset=0); h, l, c, atr, nxt = B["h"], B["l"], B["c"], B["atr"], B["nxt"]
    starts = np.r_[0, nxt[:-1]].astype(np.int64)
    st, en, up, dn, d, ex = [], [], [], [], [], []
    N = len(c)
    for t in range(n + 2, N - hold - 2):
        if not np.isfinite(atr[t]):
            continue
        win_l = l[t - n:t]; win_h = h[t - n:t]
        lo, hi = win_l.min(), win_h.max()
        lo_age = n - 1 - int(np.argmin(win_l)); hi_age = n - 1 - int(np.argmax(win_h))
        u = t + 1
        if c[t] < lo and lo_age >= gap:        # long setup: buy stop back at the old low
            st.append(starts[u]); en.append(nxt[u]); up.append(lo); dn.append(-1e18)
            d.append(max(lo - (l[t] - buf * atr[t]), 3 * G.cost)); ex.append(nxt[min(u + hold, N - 1)])  # stop: signal day's low, known in advance
        elif c[t] > hi and hi_age >= gap:      # short setup: sell stop back at the old high
            st.append(starts[u]); en.append(nxt[u]); up.append(1e18); dn.append(hi)
            d.append(max((h[t] + buf * atr[t]) - hi, 3 * G.cost)); ex.append(nxt[min(u + hold, N - 1)])
    if not st:
        return np.zeros(0, dtype=GL.DT)
    A = lambda x, t=np.float64: np.array(x, t)
    tg = 0.0 if target == "none" else float(target)
    res = GL._stop_entries(G.o, G.h, G.l, G.ts, A(st, np.int64), np.minimum(A(en, np.int64), len(G.o) - 1),
                           A(up), A(dn), A(d), tg, np.minimum(A(ex, np.int64), len(G.o) - 1), G.cost, G.gaps)
    return GL.pack(res)


def nr_breakout(G, k=7, hold_days=1, tgt="0", tfn="D1"):
    B = G.tf(tfn, offset=0); h, l, nxt = B["h"], B["l"], B["nxt"]
    rng = h - l; starts = np.r_[0, nxt[:-1]].astype(np.int64)
    st, en, up, dn, d, ex = [], [], [], [], [], []
    N = len(h)
    for t in range(k, N - hold_days - 2):
        if rng[t] <= 0 or rng[t] > rng[t - k + 1:t + 1].min() + 1e-12:
            continue
        u = t + 1
        st.append(starts[u]); en.append(nxt[u]); up.append(h[t]); dn.append(l[t]); d.append(rng[t])
        ex.append(nxt[min(u + hold_days - 1, N - 1)])
    A = lambda x, t=np.float64: np.array(x, t)
    res = GL._stop_entries(G.o, G.h, G.l, G.ts, A(st, np.int64), np.minimum(A(en, np.int64), len(G.o) - 1),
                           A(up), A(dn), A(d), float(tgt), np.minimum(A(ex, np.int64), len(G.o) - 1), G.cost, G.gaps)
    return GL.pack(res)


def trend_sweep(L, G, level="asian", target="pool", tfm=15, nextday=True):
    """Intraday sweep & reclaim, only in the direction of the daily EMA20/50 trend; exit next
    day 20:00 UTC; target the opposite daily pool (PDH for longs / PDL for shorts) or R."""
    D = daily(G); tr = d1_trend(D); dkey = D["t"] // DAY
    trend_of_day = dict(zip(dkey, np.r_[0, tr[:-1]]))          # trend known at the day's open
    P = L.days(7, 16, 44 if nextday else 20)                    # exit hour 44 = next day 20:00
    B = L.tf(tfm)
    H, Lo = (P[:, 1], P[:, 2]) if level == "asian" else (P[:, 3], P[:, 4])
    w0 = np.searchsorted(B["t"], P[:, 8]).astype(np.int64)
    w1 = np.searchsorted(B["t"] + B["m"] * 60, P[:, 9], side="right").astype(np.int64)
    ev, ext = LQ.sweep_events(B["h"], B["l"], B["c"], w0, w1, H.astype(np.float64), Lo.astype(np.float64), 8)
    exit_i = np.searchsorted(G.ts, P[:, 10]).astype(np.int64)
    ent, side, sl, tpa, tpr, ex, md = [], [], [], [], [], [], []
    for p in range(len(P)):
        trd = trend_of_day.get(int(P[p, 0] // DAY), 0)
        atr = P[p, 5]
        if not np.isfinite(atr) or trd == 0:
            continue
        for sideix, s in ((0, -1), (1, 1)):
            jr = ev[p, sideix * 4]
            if jr < 0 or s != trd:
                continue
            sx = ext[p, sideix]
            ent.append(B["nxt"][jr]); side.append(s)
            sl.append(sx - 0.05 * atr if s > 0 else sx + 0.05 * atr)
            if target == "pool":
                tpa.append(P[p, 3] if s > 0 else P[p, 4]); tpr.append(0.0)
            else:
                tpa.append(0.0); tpr.append(float(target))
            ex.append(exit_i[p]); md.append(max(0.15 * atr, 3 * G.cost))
    return _run_abs(G, ent, side, sl, tpa, tpr, ex, md)


def variants():
    for tg in ("pool", "2", "3"):
        for lvl in ("asian", "prevday"):
            for nd in (True, False):
                yield f"TRSWEEP_{lvl}_tp{tg}_{'2day' if nd else '1day'}", ("trend_sweep", dict(level=lvl, target=tg, nextday=nd))
    for lvl in ("day", "week"):
        for tg in ("pool", "2"):
            for hold in (2, 5):
                yield f"DSWEEP_{lvl}_tp{tg}_h{hold}", ("daily_sweep", dict(level=lvl, target=tg, hold=hold))
                yield f"DSWEEP_{lvl}_FAILED_tp{tg}_h{hold}", ("daily_sweep", dict(level=lvl, target="2" if tg == "pool" else tg, hold=hold, failed=True))
        if lvl == "day":
            for tg in ("pool", "2"):
                yield f"DSWEEP_day_trend_tp{tg}_h5", ("daily_sweep", dict(level="day", target=tg, hold=5, trend=True))
    for tfn in ("D1", "H4"):
        for tg in ("1", "2", "none"):
            yield f"TSOUP1_{tfn}_tp{tg}", ("turtle_soup_plus_one", dict(target=tg, tfn=tfn))
    for k in (4, 7):
        for tg in ("0", "1"):
            yield f"NR{k}_D1_tp{tg}", ("nr_breakout", dict(k=k, tgt=tg))
