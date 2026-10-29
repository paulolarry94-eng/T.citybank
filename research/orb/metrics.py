"""ORB 50 — performance statistics (Part 7) and account simulation with contract specifications.

R-level statistics come straight from the trade list (net of the all-in cost). Money-level
statistics replay the trades on an account: risk a fixed fraction of current equity per trade,
lots = floor(risk$ / (stop distance x contract x USD per price unit) / 0.01) x 0.01, minimum
0.01 lot (trades that cannot be sized are skipped and counted). Every position is closed within
its session, before the 17:00 New York rollover, so no swap is ever paid or received.
"""
import datetime as dt
import numpy as np
import core

LOT_STEP = 0.01


def quick(tr):
    """Fast summary used in the parameter search."""
    r = tr["r"]
    n = len(r)
    if n < 2:
        return dict(n=n, E=np.nan, t=np.nan, win=np.nan, pf=np.nan, sd=np.nan)
    sd = r.std(ddof=1)
    pos, neg = r[r > 0].sum(), -r[r < 0].sum()
    return dict(n=n, E=float(r.mean()), t=float(r.mean() / sd * np.sqrt(n)) if sd > 0 else np.nan,
                win=float((r > 0).mean()), pf=float(pos / neg) if neg > 0 else np.inf, sd=float(sd))


def year_of(t):
    return np.array([dt.datetime.fromtimestamp(int(x), dt.timezone.utc).year for x in t])


def gross_r(tr, cost):
    return tr["r"] + cost / tr["dist"]


def max_streak(neg):
    best = cur = 0
    for x in neg:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return best


def account(trades_by_sym, risk=0.005, start=100_000.0, cost_mult=1.0):
    """Replay one or more trade lists (dict sym -> TR array) on a single account in time order.
    Equity is marked at trade exits; risk is a fraction of equity at entry. cost_mult > 1
    charges extra cost (perturbation) on top of what the trade already paid."""
    ev = []
    for sym, tr in trades_by_sym.items():
        for t in tr:
            ev.append((int(t["t_in"]), int(t["t_out"]), sym, float(t["r"]), float(t["dist"]), float(t["entry"])))
    ev.sort()
    eq = start
    open_pos = []                     # (t_out, pnl)
    curve_t, curve_e, pnl_list, skipped = [], [], [], 0
    for t_in, t_out, sym, r, dist, entry in ev:
        open_pos.sort()
        while open_pos and open_pos[0][0] <= t_in:
            to, p = open_pos.pop(0); eq += p; curve_t.append(to); curve_e.append(eq)
        usd_per_unit = 1.0 / entry if sym == "USDJPY" else 1.0
        per_lot = dist * core.CONTRACT[sym] * usd_per_unit
        lots = np.floor(eq * risk / per_lot / LOT_STEP + 1e-9) * LOT_STEP
        if lots < LOT_STEP:
            skipped += 1
            continue
        extra = (cost_mult - 1.0) * core.COST[sym] / dist
        pnl = lots * per_lot * (r - extra)
        pnl_list.append((t_out, pnl, eq))
        open_pos.append((t_out, pnl))
    for to, p in sorted(open_pos):
        eq += p; curve_t.append(to); curve_e.append(eq)
    return np.array(curve_t, np.int64), np.array(curve_e), pnl_list, skipped


def drawdown(e, start):
    peak = np.maximum.accumulate(np.r_[start, e])[1:]
    return (e - peak) / peak


def daily_returns(curve_t, curve_e, start):
    if len(curve_t) == 0:
        return np.zeros(0), np.zeros(0)
    day = curve_t // 86400
    last = np.r_[np.flatnonzero(day[1:] != day[:-1]), len(day) - 1]
    d, e = day[last], curve_e[last]
    allday = np.arange(d[0], d[-1] + 1)
    wk = ((allday + 3) % 7) < 5
    eq = np.interp(allday, d, e, left=start)
    idx = np.searchsorted(d, allday, side="right") - 1
    eq = np.where(idx >= 0, e[np.clip(idx, 0, None)], start)
    ret = np.diff(np.r_[start, eq]) / np.r_[start, eq][:-1]
    return allday[wk], ret[wk]


def full(trades_by_sym, risk=0.005, start=100_000.0, sessions_of=None):
    """All Part 7 statistics for one trade list or a combined book."""
    allt = np.concatenate([tr for tr in trades_by_sym.values()]) if trades_by_sym else np.zeros(0)
    if len(allt) < 2:
        return dict(n=len(allt))
    r = allt["r"]
    q = quick(allt)
    ct, ce, pnl, skipped = account(trades_by_sym, risk, start)
    dd = drawdown(ce, start)
    days, dr = daily_returns(ct, ce, start)
    yrs = max((allt["t_out"].max() - allt["t_in"].min()) / (365.25 * 86400), 1e-9)
    net = ce[-1] - start if len(ce) else 0.0
    sh = dr.mean() / dr.std() * np.sqrt(252) if dr.std() > 0 else np.nan
    down = dr[dr < 0]
    so = dr.mean() / np.sqrt((down ** 2).mean()) * np.sqrt(252) if len(down) else np.nan
    # monthly and annual returns (compounded from equity marks)
    mon, ann = {}, {}
    eq_prev = start
    for t, e in zip(ct, ce):
        d = dt.datetime.fromtimestamp(int(t), dt.timezone.utc)
        mon[(d.year, d.month)] = e; ann[d.year] = e
    mk = sorted(mon); mret = {}
    prev = start
    for k in mk:
        mret[f"{k[0]}-{k[1]:02d}"] = mon[k] / prev - 1; prev = mon[k]
    ak = sorted(ann); aret = {}
    prev = start
    for k in ak:
        aret[k] = ann[k] / prev - 1; prev = ann[k]
    cost_by = {}
    gross = np.concatenate([tr["r"] + core.COST[s] / tr["dist"] for s, tr in trades_by_sym.items()])
    out = dict(
        n=int(len(r)), per_year=float(len(r) / yrs), years=float(yrs),
        E=q["E"], t=q["t"], win=q["win"], pf=q["pf"],
        avg_win_R=float(r[r > 0].mean()) if (r > 0).any() else 0.0,
        avg_loss_R=float(r[r <= 0].mean()) if (r <= 0).any() else 0.0,
        E_gross=float(gross.mean()), cost_R_per_trade=float((gross - r).mean()),
        max_consec_losses=int(max_streak(r[np.argsort(allt["t_in"])] <= 0)),
        hold_min_avg=float(((allt["t_out"] - allt["t_in"]) / 60).mean()),
        long_n=int((allt["side"] > 0).sum()), long_E=float(r[allt["side"] > 0].mean()) if (allt["side"] > 0).any() else np.nan,
        short_n=int((allt["side"] < 0).sum()), short_E=float(r[allt["side"] < 0].mean()) if (allt["side"] < 0).any() else np.nan,
        risk=risk, start=start, net_profit=float(net), end_equity=float(ce[-1]) if len(ce) else start,
        cagr=float((ce[-1] / start) ** (1 / yrs) - 1) if len(ce) else 0.0,
        max_dd=float(-dd.min()) if len(dd) else 0.0,
        recovery=float(net / (-dd.min() * start)) if len(dd) and dd.min() < 0 else np.inf,
        sharpe=float(sh), sortino=float(so), skipped_unsizable=int(skipped),
        monthly=mret, annual=aret,
        pct_months_positive=float(np.mean([v > 0 for v in mret.values()])) if mret else np.nan,
        worst_month=float(min(mret.values())) if mret else np.nan,
        best_month=float(max(mret.values())) if mret else np.nan,
    )
    return out
