"""Replay of the owner's Dark Mimas settings (Marco Solito, free EA on MQL5) on EURUSD and GBPUSD M1 2011-2025.

The EA and its Dark Oscillator are compiled and closed; the oscillator's formula is not published. So this tests the
FAMILY the settings describe, with three reconstructions of a smooth oscillator that turns green when rising and red
when falling (manual p.5-6: "Buy Green Arrow, Sell Red Arrow"). Everything below was fixed before any run (2026-10-31).

Settings read from the owner's .set files (both MT4 and MT5 copies agree):
  Classic Mode No Grid : strategy 1 (buy at green arrow, sell at red arrow), close on the opposite signal, no stop
                         (StopTargetMode=0), take target 5000 points (500 pips), fixed 0.01 lot, one trade per bar,
                         buy and sell not at the same time -> an always-in-the-market stop-and-reverse system.
  "Not Open Orders" set : same first-order signal, closing on the indicator OFF, grid ON with fixed 0.01 lots, a new
                         grid order at a new bar's open when price is >= 50 points (5 pips) against the last order,
                         up to 50 orders per side, buy and sell baskets at the same time, basket take profit 50 points
                         (5 pips) from the weighted average, basket stop 500 points (50 pips) from the weighted average
                         (StopTargetMode=2, CloseMode=1), MaxSpread 2000 (no spread filter).
Oscillator reconstructions on the chart timeframe, median price (H+L)/2, period 15, LWMA (method 3):
  R1 slope of LWMA(median, 15)
  R2 LWMA(CCI-like(median, 15), 15)            (CCI-like = (p - SMA15) / (0.015 x mean abs deviation))
  R3 TSI-like: 100 x LWMA(LWMA(dp,15),15) / LWMA(LWMA(|dp|,15),15)
  green = the line rose on the last closed bar; an arrow = a colour change; action at the next bar's open.
Markets EURUSD, GBPUSD (the vendor's recommended pairs that we have data for); timeframes M5, M15, H1 (vendor's list).
Cost profiles (round trip per 0.01-lot order, in price units; swaps per night at 22:00 UTC, x3 Wednesday):
  research      : 1.5 / 1.8 pips, swap 0.6 pip/night            (the lab standard)
  exness_zero   : measured Zero spread (~0.1 pip) + $7/lot commission (0.7 pip) + 0.2 pip slippage = 1.0 pip, swaps
  exness_zero_sf: the same without swaps (if the account is swap-free on these pairs)
  no_costs_diagnostic: no costs and no swaps (shows whether any edge exists before costs; not a tradable profile)
Equity is marked at the worse of each minute's high/low; same-minute target and stop = stop.

    python3 research/gridbot/dark_mimas_sim.py -> research/results/gridbot/dark_mimas.json
"""
import os, sys, json
import numpy as np
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import engine as E

OUT = os.path.join(HERE, "..", "results", "gridbot")
PIP = 0.0001
PROFILES = {"research": {"EURUSD": (1.5, 0.6), "GBPUSD": (1.8, 0.6)},
            "exness_zero": {"EURUSD": (1.0, 0.6), "GBPUSD": (1.0, 0.6)},
            "exness_zero_sf": {"EURUSD": (1.0, 0.0), "GBPUSD": (1.0, 0.0)},
            "no_costs_diagnostic": {"EURUSD": (0.0, 0.0), "GBPUSD": (0.0, 0.0)}}   # is there any edge before costs?


def lwma(x, n):
    """Linear-weighted moving average: weight n on the newest value, 1 on the oldest. x must be NaN-free."""
    w = np.arange(1, n + 1, dtype=float)
    out = np.full(len(x), np.nan)
    out[n - 1:] = np.convolve(x, w[::-1], mode="valid") / w.sum()
    return out


def sma(x, n):
    c = np.cumsum(np.r_[0.0, x]); out = np.full(len(x), np.nan); out[n - 1:] = (c[n:] - c[:-n]) / n; return out


def oscillator(kind, bh, bl, n=15):
    p = (bh + bl) / 2
    if kind == "R1":
        return lwma(p, n)
    if kind == "R2":
        m = sma(p, n); md = np.full(len(p), np.nan)
        win = np.lib.stride_tricks.sliding_window_view(p, n)
        md[n - 1:] = np.mean(np.abs(win - m[n - 1:, None]), axis=1)
        cci = (p - m) / (0.015 * np.where(md > 0, md, np.nan))
        cci = np.nan_to_num(cci)
        return lwma(cci, n)
    dp = np.r_[0.0, np.diff(p)]
    num = lwma(np.nan_to_num(lwma(dp, n)), n); den = lwma(np.nan_to_num(lwma(np.abs(dp), n)), n)
    return 100 * num / np.where(den > 0, den, np.nan)


def arrows(line):
    """+1 where the line turns up (green arrow), -1 where it turns down, on the closed bar. Flat steps (|change|
    below 1e-9 of the line's scale) keep the previous colour."""
    dl = np.diff(np.nan_to_num(line), prepend=0.0)
    tol = 1e-9 * np.nanmax(np.abs(line))
    d = np.where(np.abs(dl) > tol, np.sign(dl), 0.0)
    d[~np.isfinite(line)] = 0.0
    nz = np.flatnonzero(d)                                   # forward-fill flat steps with the last colour
    fill = np.zeros(len(d), np.int64) - 1
    fill[nz] = nz
    fill = np.maximum.accumulate(fill)
    col = np.where(fill >= 0, d[np.maximum(fill, 0)], 0.0)
    prev = np.r_[0.0, col[:-1]]
    a = np.zeros(len(d), np.int64)
    a[(col > 0) & (prev < 0)] = 1; a[(col < 0) & (prev > 0)] = -1
    return a


@njit(cache=True)
def _night(t, last_day):
    d = t // 86400
    if (t % 86400) >= 79200 and d != last_day:
        wd = (d + 3) % 7
        if wd < 5:
            return d, (3.0 if wd == 2 else 1.0)
        return d, 0.0
    return last_day, 0.0


@njit(cache=True)
def classic(ts, o, h, l, c, act, side, tp, cost, swap):
    """Stop-and-reverse at each arrow; take profit at +tp; no stop. Returns trades and the equity drawdown."""
    n = len(ts); m = len(act)
    tr = np.zeros((m + 2, 5)); k = 0          # t_in, t_out, side, net, gross
    pos = 0; ent = 0.0; tin = 0; fin = 0.0
    realized = 0.0; peak = 0.0; maxdd = 0.0; last_day = -1; j = 0
    for i in range(n):
        while j < m and act[j] < i:
            j += 1
        if j < m and act[j] == i:
            s = side[j]
            if pos != 0 and pos != s:
                g = (o[i] - ent) * pos
                tr[k, 0] = tin; tr[k, 1] = ts[i]; tr[k, 2] = pos; tr[k, 3] = g - cost - fin; tr[k, 4] = g; k += 1
                realized += g - cost - fin; pos = 0
            if pos == 0:
                pos = s; ent = o[i]; tin = ts[i]; fin = 0.0
        last_day, mult = _night(ts[i], last_day)
        if pos != 0 and mult > 0:
            fin += swap * mult
        if pos == 1 and h[i] >= ent + tp:
            g = tp; tr[k, 0] = tin; tr[k, 1] = ts[i]; tr[k, 2] = 1; tr[k, 3] = g - cost - fin; tr[k, 4] = g; k += 1
            realized += g - cost - fin; pos = 0
        elif pos == -1 and l[i] <= ent - tp:
            g = tp; tr[k, 0] = tin; tr[k, 1] = ts[i]; tr[k, 2] = -1; tr[k, 3] = g - cost - fin; tr[k, 4] = g; k += 1
            realized += g - cost - fin; pos = 0
        eq = realized
        if pos == 1:
            eq += (l[i] - ent) - cost - fin
        elif pos == -1:
            eq += (ent - h[i]) - cost - fin
        if realized > peak:
            peak = realized
        if peak - eq > maxdd:
            maxdd = peak - eq
    return tr[:k], maxdd


@njit(cache=True)
def grid(ts, o, h, l, c, bar_open_idx, act, side, step, tp, sl, max_orders, cost, swap):
    """Independent buy and sell baskets. First order at an arrow (if that side is flat and no basket of that side
    closed during the current chart bar); a grid order at a chart-bar open when price is >= step against the last
    order; basket closes at weighted average +/- tp (profit) or -/+ sl (loss). Equal lots (fixed 0.01)."""
    n = len(ts); nb_open = len(bar_open_idx); m = len(act)
    be = np.zeros(max_orders); nb = 0; se = np.zeros(max_orders); ns = 0
    bfin = 0.0; sfin = 0.0
    realized = 0.0; peak = 0.0; maxdd = 0.0; min_eq = 0.0; last_day = -1
    baskets = np.zeros((4 * m + 10, 5)); kb = 0        # t_close, side, orders, net, 1=target/0=stop
    yr = np.zeros(20)
    bo_j = 0; a_j = 0; bclosed_bar = -1; sclosed_bar = -1; cur_bar = -1; max_n = 0
    for i in range(n):
        y = int(ts[i] // 31556952) + 1970 - 2011
        if y < 0: y = 0
        if y > 19: y = 19
        new_bar = False
        while bo_j < nb_open and bar_open_idx[bo_j] < i:
            bo_j += 1
        if bo_j < nb_open and bar_open_idx[bo_j] == i:
            new_bar = True; cur_bar = bo_j
        while a_j < m and act[a_j] < i:
            a_j += 1
        if a_j < m and act[a_j] == i:
            s = side[a_j]
            if s == 1 and nb == 0 and bclosed_bar != cur_bar:
                be[0] = o[i]; nb = 1; bfin = 0.0; realized -= cost; yr[y] -= cost
            if s == -1 and ns == 0 and sclosed_bar != cur_bar:
                se[0] = o[i]; ns = 1; sfin = 0.0; realized -= cost; yr[y] -= cost
        if new_bar:
            if 0 < nb < max_orders and o[i] <= be[nb - 1] - step:
                be[nb] = o[i]; nb += 1; realized -= cost; yr[y] -= cost
            if 0 < ns < max_orders and o[i] >= se[ns - 1] + step:
                se[ns] = o[i]; ns += 1; realized -= cost; yr[y] -= cost
            if nb > max_n: max_n = nb
            if ns > max_n: max_n = ns
        last_day, mult = _night(ts[i], last_day)
        if mult > 0:
            realized -= swap * mult * (nb + ns); yr[y] -= swap * mult * (nb + ns)
        if nb > 0:
            avg = 0.0
            for q in range(nb): avg += be[q]
            avg /= nb
            px = -1.0; hit = -1
            if l[i] <= avg - sl:
                px = avg - sl; hit = 0
            elif h[i] >= avg + tp:
                px = avg + tp; hit = 1
            if hit >= 0:
                g = 0.0
                for q in range(nb): g += px - be[q]
                realized += g; yr[y] += g
                baskets[kb, 0] = ts[i]; baskets[kb, 1] = 1; baskets[kb, 2] = nb; baskets[kb, 3] = g; baskets[kb, 4] = hit; kb += 1
                nb = 0; bclosed_bar = cur_bar
        if ns > 0:
            avg = 0.0
            for q in range(ns): avg += se[q]
            avg /= ns
            px = -1.0; hit = -1
            if h[i] >= avg + sl:
                px = avg + sl; hit = 0
            elif l[i] <= avg - tp:
                px = avg - tp; hit = 1
            if hit >= 0:
                g = 0.0
                for q in range(ns): g += se[q] - px
                realized += g; yr[y] += g
                baskets[kb, 0] = ts[i]; baskets[kb, 1] = -1; baskets[kb, 2] = ns; baskets[kb, 3] = g; baskets[kb, 4] = hit; kb += 1
                ns = 0; sclosed_bar = cur_bar
        fl = 0.0
        for q in range(nb): fl += l[i] - be[q]
        for q in range(ns): fl += se[q] - h[i]
        eq = realized + fl
        if realized > peak: peak = realized
        if peak - eq > maxdd: maxdd = peak - eq
        if eq < min_eq: min_eq = eq
    fl = 0.0
    for q in range(nb): fl += c[n - 1] - be[q]
    for q in range(ns): fl += se[q] - c[n - 1]
    return baskets[:kb], realized, fl, maxdd, min_eq, max_n, yr


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for sym in ("EURUSD", "GBPUSD"):
        ts, o, h, l, c = E.load_m1(sym)
        years = (ts[-1] - ts[0]) / (365.25 * 86400)
        for tf in (5, 15, 60):
            bt, bo, bh, bl, bc, ends = E.resample(ts, o, h, l, c, tf)
            for kind in ("R1", "R2", "R3"):
                a = arrows(oscillator(kind, bh, bl))
                idx = np.flatnonzero(a != 0); idx = idx[ends[idx] < len(ts)]
                act = ends[idx].astype(np.int64); side = a[idx].astype(np.int64)
                for prof, P in PROFILES.items():
                    cost, swap = P[sym][0] * PIP, P[sym][1] * PIP
                    tr, dd = classic(ts, o, h, l, c, act, side, 500 * PIP, cost, swap)
                    net = tr[:, 3] / PIP; gross = tr[:, 4] / PIP
                    yrs = np.array([np.datetime64(int(t), "s").astype("datetime64[Y]").astype(int) + 1970 for t in tr[:, 1]])
                    by_year = {int(y): round(float(net[yrs == y].sum()), 1) for y in np.unique(yrs)}
                    pf = net[net > 0].sum() / max(1e-9, -net[net < 0].sum())
                    rows.append(dict(set="classic no grid", sym=sym, tf=tf, osc=kind, profile=prof, trades=int(len(net)),
                                     trades_per_year=round(len(net) / years), win_rate=round(float((net > 0).mean()), 3),
                                     gross_pips_per_trade=round(float(gross.mean()), 2), net_pips_per_trade=round(float(net.mean()), 2),
                                     net_pips_total=round(float(net.sum())), usd_per_001lot_total=round(float(net.sum()) * 0.1),
                                     profit_factor=round(float(pf), 3), max_dd_pips=round(dd / PIP),
                                     negative_years=int(sum(v < 0 for v in by_year.values())), by_year_pips=by_year))
                    bars_open = ends[:-1].astype(np.int64)
                    B, realized, fl, dd, min_eq, max_n, yr = grid(ts, o, h, l, c, bars_open, act, side, 5 * PIP, 5 * PIP,
                                                                  50 * PIP, 50, cost, swap)
                    tgt = B[:, 4] == 1
                    rows.append(dict(set="grid (not-open-orders set)", sym=sym, tf=tf, osc=kind, profile=prof,
                                     baskets=int(len(B)), baskets_per_year=round(len(B) / years),
                                     basket_win_rate=round(float(tgt.mean()), 3) if len(B) else None,
                                     avg_win_usd=round(float(B[tgt, 3].mean() / PIP * 0.1), 2) if tgt.any() else None,
                                     avg_stop_usd=round(float(B[~tgt, 3].mean() / PIP * 0.1), 2) if (~tgt).any() else None,
                                     max_orders_in_basket=int(max_n), net_usd_per_001lot=round((realized + fl) / PIP * 0.1),
                                     max_equity_dd_usd=round(dd / PIP * 0.1), worst_equity_usd=round(min_eq / PIP * 0.1),
                                     negative_years=int(sum(v < 0 for v in yr[:15])),
                                     by_year_usd={2011 + k: round(float(yr[k]) / PIP * 0.1) for k in range(15)}))
                    print(rows[-2]["set"], sym, tf, kind, prof, rows[-2]["net_pips_per_trade"], "|",
                          rows[-1]["net_usd_per_001lot"], rows[-1]["max_equity_dd_usd"], flush=True)
    json.dump(rows, open(os.path.join(OUT, "dark_mimas.json"), "w"), indent=1)
    return rows


if __name__ == "__main__":
    main()
