"""Replay of the Gold Hunter V9 settings (hedged constant-lot averaging grid) on XAUUSD M1 2011-2025.

The Truth Lab cannot express multi-order baskets, so this is a separate study (recorded in the project memory).
The .ex5 is compiled and protected: the logic below is the standard grid reading of its .set file, not its code.

Per side (buy basket / sell basket, independent, always one basket open per side):
  open 1 order (Lot_start); each time price moves Pip_step against the LAST order, add an order (lot x multiplier)
  up to Max_orders; close ALL orders of the side when price reaches average entry +/- Take_profit_combined; reopen.
  No stop-loss in the original. Bounded variants (declared before any run): max orders N in {5, 10, 20} and the whole
  basket is closed at a loss when the next add would have triggered (one step beyond the N-th order).
Costs: all-in $0.45/oz per order (our research cost; x0.5 profile for a raw-spread account); swap $0.20/oz per night
on every open order (x3 Wednesday) or swap-free. Size: 0.01 lot = 1 oz per order. Intrabar path: O->L->H->C if the
bar closes up, else O->H->L->C. Equity is marked at the worse of the bar's high/low (conservative).

    python3 research/gridbot/gold_hunter_sim.py -> research/results/gridbot/gold_hunter.json
"""
import os, sys, json
import numpy as np
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import engine as E

OUT = os.path.join(HERE, "..", "results", "gridbot")


@njit(cache=True)
def simulate(ts, o, h, l, c, step, tp, max_orders, mult, cost, swap, bounded):
    n = len(ts)
    # per side: entries, lots
    be = np.zeros(max_orders); bl = np.zeros(max_orders); nb = 0
    se = np.zeros(max_orders); sl = np.zeros(max_orders); ns = 0
    realized = 0.0; peak = 0.0; maxdd = 0.0; min_eq = 0.0
    yr = np.zeros(20); yr_closes = np.zeros(20); yr_stops = np.zeros(20)
    max_nb = 0; max_ns = 0; swap_paid = 0.0; cost_paid = 0.0
    last_day = -1
    # open the first orders
    be[0] = o[0]; bl[0] = 1.0; nb = 1; se[0] = o[0]; sl[0] = 1.0; ns = 1
    realized -= 2 * cost; cost_paid += 2 * cost
    for i in range(n):
        y = int((ts[i] // 86400 + 0) // 365.2425) + 1970 - 2011
        if y < 0: y = 0
        if y > 19: y = 19
        # swap at 22:00 UTC rollover
        d = ts[i] // 86400
        if (ts[i] % 86400) >= 79200 and d != last_day:
            last_day = d
            wd = (d + 3) % 7
            if wd < 5:
                oz = 0.0
                for k in range(nb): oz += bl[k]
                for k in range(ns): oz += sl[k]
                m = 3.0 if wd == 2 else 1.0
                realized -= swap * oz * m; swap_paid += swap * oz * m; yr[y] -= swap * oz * m
        up = c[i] >= o[i]
        for leg in range(2):
            price = l[i] if ((leg == 0) == up) else h[i]      # first extreme, then the other
            # ---- buy basket: adds on the way down, TP on the way up
            while nb > 0:
                last = be[nb - 1]
                if price <= last - step:
                    if nb < max_orders:
                        lot = bl[nb - 1] * mult
                        be[nb] = last - step; bl[nb] = lot; nb += 1
                        realized -= cost * lot; cost_paid += cost * lot; yr[y] -= cost * lot
                        if nb > max_nb: max_nb = nb
                        continue
                    elif bounded:
                        px = last - step; pnl = 0.0
                        for k in range(nb): pnl += (px - be[k]) * bl[k]
                        realized += pnl; yr[y] += pnl; yr_stops[y] += 1
                        be[0] = px; bl[0] = 1.0; nb = 1; realized -= cost; cost_paid += cost; yr[y] -= cost
                        continue
                lots = 0.0; avg = 0.0
                for k in range(nb): lots += bl[k]; avg += be[k] * bl[k]
                avg /= lots
                if price >= avg + tp:
                    px = avg + tp; pnl = 0.0
                    for k in range(nb): pnl += (px - be[k]) * bl[k]
                    realized += pnl; yr[y] += pnl; yr_closes[y] += 1
                    be[0] = px; bl[0] = 1.0; nb = 1; realized -= cost; cost_paid += cost; yr[y] -= cost
                    continue
                break
            # ---- sell basket: adds on the way up, TP on the way down
            while ns > 0:
                last = se[ns - 1]
                if price >= last + step:
                    if ns < max_orders:
                        lot = sl[ns - 1] * mult
                        se[ns] = last + step; sl[ns] = lot; ns += 1
                        realized -= cost * lot; cost_paid += cost * lot; yr[y] -= cost * lot
                        if ns > max_ns: max_ns = ns
                        continue
                    elif bounded:
                        px = last + step; pnl = 0.0
                        for k in range(ns): pnl += (se[k] - px) * sl[k]
                        realized += pnl; yr[y] += pnl; yr_stops[y] += 1
                        se[0] = px; sl[0] = 1.0; ns = 1; realized -= cost; cost_paid += cost; yr[y] -= cost
                        continue
                lots = 0.0; avg = 0.0
                for k in range(ns): lots += sl[k]; avg += se[k] * sl[k]
                avg /= lots
                if price <= avg - tp:
                    px = avg - tp; pnl = 0.0
                    for k in range(ns): pnl += (se[k] - px) * sl[k]
                    realized += pnl; yr[y] += pnl; yr_closes[y] += 1
                    se[0] = px; sl[0] = 1.0; ns = 1; realized -= cost; cost_paid += cost; yr[y] -= cost
                    continue
                break
        # equity marked at the worse of high / low
        worst = 1e18
        for px in (l[i], h[i]):
            fl = 0.0
            for k in range(nb): fl += (px - be[k]) * bl[k]
            for k in range(ns): fl += (se[k] - px) * sl[k]
            if realized + fl < worst: worst = realized + fl
        if realized > peak: peak = realized
        if worst < min_eq: min_eq = worst
        if peak - worst > maxdd: maxdd = peak - worst
    fl_end = 0.0
    for k in range(nb): fl_end += (c[n - 1] - be[k]) * bl[k]
    for k in range(ns): fl_end += (se[k] - c[n - 1]) * sl[k]
    return realized, fl_end, maxdd, min_eq, max_nb, max_ns, swap_paid, cost_paid, yr, yr_closes, yr_stops


def main():
    os.makedirs(OUT, exist_ok=True)
    ts, o, h, l, c = E.load_m1("XAUUSD")
    ts = ts.astype(np.int64)
    years = (ts[-1] - ts[0]) / (365.25 * 86400)
    rows = []
    for label, pip in (("pip=$0.01 (step $10.20, TP $4.20)", 0.01), ("pip=$0.10 (step $102, TP $42)", 0.10)):
        for name, mo, bounded in (("original: 99 orders, no stop", 99, False), ("bounded: 20 orders + basket stop", 20, True),
                                  ("bounded: 10 orders + basket stop", 10, True), ("bounded: 5 orders + basket stop", 5, True)):
            for prof, cost, swap in (("research costs + swaps", 0.45, 0.20), ("low-cost, swap-free", 0.225, 0.0)):
                R = simulate(ts, o, h, l, c, 1020 * pip, 420 * pip, mo, 1.0, cost, swap, bounded)
                realized, fl_end, maxdd, min_eq, mnb, mns, swp, cst, yr, ycl, yst = R
                net = realized + fl_end
                row = dict(interpretation=label, variant=name, profile=prof, per="0.01 lot start (1 oz per order)",
                           realized_usd=round(realized), floating_at_end_usd=round(fl_end), net_usd=round(net),
                           max_drawdown_usd=round(maxdd), lowest_equity_usd=round(min_eq), max_buy_orders=int(mnb), max_sell_orders=int(mns),
                           swaps_paid_usd=round(swp), costs_paid_usd=round(cst),
                           capital_needed_usd=round(maxdd * 1.2), annual_return_on_needed_capital=(net / years) / (maxdd * 1.2) if maxdd > 0 else None,
                           yearly_usd={str(2011 + k): round(float(yr[k])) for k in range(15)},
                           basket_wins_per_year=round(float(ycl[:15].sum()) / years, 1), basket_stops_per_year=round(float(yst[:15].sum()) / years, 1))
                rows.append(row)
                print(f"{label:34s} | {name:34s} | {prof:23s} | net ${net:>10,.0f} (realised {realized:>10,.0f}, floating {fl_end:>10,.0f}) | "
                      f"max DD ${maxdd:>9,.0f} | orders max {mnb}/{mns} | swaps ${swp:,.0f} | return on capital {row['annual_return_on_needed_capital'] if row['annual_return_on_needed_capital'] is None else round(row['annual_return_on_needed_capital'] * 100, 1)}%/yr", flush=True)
    json.dump(rows, open(os.path.join(OUT, "gold_hunter.json"), "w"), indent=1)


if __name__ == "__main__" and len(sys.argv) == 1:
    main()


@njit(cache=True)
def from_start(ts, o, h, l, c, i0, step, tp, max_orders, cost, swap, capital, horizon):
    """Original grid (no stop) on one account from bar i0: returns (blown_bar or -1, realised at 3/6/12 months, min equity)."""
    be = np.zeros(max_orders); nb = 1; se = np.zeros(max_orders); ns = 1
    be[0] = o[i0]; se[0] = o[i0]; realized = -2 * cost; last_day = -1
    marks = np.zeros(3); mark_t = np.array([ts[i0] + 91 * 86400, ts[i0] + 182 * 86400, ts[i0] + 365 * 86400]); mi = 0
    min_eq = capital
    for i in range(i0, min(len(ts), i0 + horizon)):
        while mi < 3 and ts[i] >= mark_t[mi]:
            marks[mi] = realized; mi += 1
        d = ts[i] // 86400
        if (ts[i] % 86400) >= 79200 and d != last_day:
            last_day = d; wd = (d + 3) % 7
            if wd < 5:
                realized -= swap * (nb + ns) * (3.0 if wd == 2 else 1.0)
        up = c[i] >= o[i]
        for leg in range(2):
            price = l[i] if ((leg == 0) == up) else h[i]
            while True:
                if price <= be[nb - 1] - step and nb < max_orders:
                    be[nb] = be[nb - 1] - step; nb += 1; realized -= cost; continue
                avg = 0.0
                for k in range(nb): avg += be[k]
                avg /= nb
                if price >= avg + tp:
                    for k in range(nb): realized += avg + tp - be[k]
                    be[0] = avg + tp; nb = 1; realized -= cost; continue
                break
            while True:
                if price >= se[ns - 1] + step and ns < max_orders:
                    se[ns] = se[ns - 1] + step; ns += 1; realized -= cost; continue
                avg = 0.0
                for k in range(ns): avg += se[k]
                avg /= ns
                if price <= avg - tp:
                    for k in range(ns): realized += se[k] - (avg - tp)
                    se[0] = avg - tp; ns = 1; realized -= cost; continue
                break
        worst = 1e18
        for px in (l[i], h[i]):
            fl = 0.0
            for k in range(nb): fl += px - be[k]
            for k in range(ns): fl += se[k] - px
            if fl < worst: worst = fl
        eq = capital + realized + worst
        if eq < min_eq: min_eq = eq
        if eq <= 0:
            return i, marks, min_eq
    while mi < 3:
        marks[mi] = realized; mi += 1
    return -1, marks, min_eq


def accounts():
    ts, o, h, l, c = E.load_m1("XAUUSD"); ts = ts.astype(np.int64)
    starts = [int(np.searchsorted(ts, int(np.datetime64(f"{y}-{m:02d}-01").astype("datetime64[s]").astype(np.int64)))) for y in range(2011, 2025) for m in range(1, 13)]
    starts = [s for s in starts if s < len(ts) - 1]
    horizon = 3 * 365 * 1440
    out = []
    for label, pip in (("pip=$0.01", 0.01), ("pip=$0.10", 0.10)):
        for cap in (1000, 5000, 10000, 50000):
            blown12 = blown36 = looked_good_3m = looked_good_then_blown = 0; n = 0
            for s in starts:
                b, marks, mn = from_start(ts, o, h, l, c, s, 1020 * pip, 420 * pip, 99, 0.45, 0.20, cap, horizon)
                n += 1
                dt = (ts[b] - ts[s]) / 86400 if b >= 0 else 1e9
                blown12 += dt <= 365; blown36 += dt <= 3 * 365
                good = marks[0] > 0; looked_good_3m += good; looked_good_then_blown += good and dt <= 3 * 365
            r = dict(interpretation=label, capital_per_001_lot=cap, starts=n, blown_within_1y=blown12 / n, blown_within_3y=blown36 / n,
                     profitable_after_3_months=looked_good_3m / n, profitable_at_3m_but_blown_within_3y=looked_good_then_blown / n)
            out.append(r)
            print(f"{label:10s} ${cap:>6,} per 0.01 lot | blown within 1y {r['blown_within_1y']:.0%} | within 3y {r['blown_within_3y']:.0%} | "
                  f"realised profit after 3 months {r['profitable_after_3_months']:.0%} | looked profitable at 3m, then blown within 3y {r['profitable_at_3m_but_blown_within_3y']:.0%}", flush=True)
    json.dump(out, open(os.path.join(OUT, "gold_hunter_accounts.json"), "w"), indent=1)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--accounts":
    accounts()
