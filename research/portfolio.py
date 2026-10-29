"""Portfolio replay + 20M-lifecycle envelope test for TimelessCity / SEESARE P26.

Inputs are real trade lists from engine.py (entry time, exit time, R after true fills).
Nothing here invents a trade: it only decides how much each real trade risked.

Sizing state (P26 hierarchy): one shared constraint level.
  win  -> up 1 level;  loss -> down 2 / 3 / 4 levels on the 1st / 2nd / 3rd+ consecutive loss
  |R| < 0.05 -> breakeven, level unchanged.  Level 0 = largest risk.
Per-leg weight = structural multiplier (ratio/3.5)^2.5, or 1.0 if exempted.
Heat wall: a new trade is refused if total open risk would exceed the cap (8%).
"""
import numpy as np
from numba import njit

USER_LADDER = np.array([3.0, 2.0, 1.33, 0.86, 0.56, 0.24]) / 100.0


def multiplier(ratio):
    return 1.0 if ratio >= 3.5 else (ratio / 3.5) ** 2.5


def merge(legs):
    """legs: list of (name, trades, weight). Returns time-ordered arrays."""
    t_in, t_out, r, leg, w = [], [], [], [], []
    for k, (name, tr, wt) in enumerate(legs):
        t_in.append(tr["t_in"]); t_out.append(tr["t_out"]); r.append(tr["r"])
        leg.append(np.full(len(tr), k)); w.append(np.full(len(tr), wt))
    t_in, t_out, r = np.concatenate(t_in), np.concatenate(t_out), np.concatenate(r)
    leg, w = np.concatenate(leg), np.concatenate(w)
    o = np.argsort(t_in, kind="stable")
    return t_in[o], t_out[o], r[o], leg[o], w[o]


@njit(cache=True)
def _step_level(level, consec, r, nlev, d1, d2, d3):
    if r > 0.05:
        level = max(level - 1, 0)
        consec = 0
    elif r < -0.05:
        consec += 1
        d = d1 if consec == 1 else (d2 if consec == 2 else d3)
        level = min(level + d, nlev - 1)
    return level, consec


@njit(cache=True)
def replay(t_in, t_out, r, leg, w, ladder, scale, heat_cap, d1, d2, d3, nleg,
           harvest_on, h_max, env_cap, cycle_len):
    """Chronological replay with real timestamps and concurrency.
    Returns equity path at each close, max DD (closed-equity), taken mask, risk used,
    banked harvest total, closes' timestamps."""
    n = len(r)
    # event list: entries and exits, exits first at equal times
    ev_t = np.empty(2 * n, np.int64); ev_k = np.empty(2 * n, np.int64); ev_e = np.empty(2 * n, np.int64)
    for i in range(n):
        ev_t[2 * i] = t_in[i]; ev_k[2 * i] = i; ev_e[2 * i] = 1
        ev_t[2 * i + 1] = t_out[i]; ev_k[2 * i + 1] = i; ev_e[2 * i + 1] = 0
    order = np.argsort(ev_t * 2 + ev_e, kind="mergesort")   # exits before entries at equal times
    eq = 1.0; peak = 1.0; mdd = 0.0
    level = 0; consec = 0
    open_risk = np.zeros(n); taken = np.zeros(n, np.bool_)
    risk_pct = np.zeros(n)
    heat = 0.0
    eq_path = np.empty(n); close_t = np.empty(n, np.int64); nclose = 0
    banked = 0.0; cyc_start = 1.0; ncyc = 0; env_used = 0.0
    nlev = len(ladder)
    for q in range(2 * n):
        j = order[q]
        i = ev_k[j]
        if ev_e[j] == 1:  # entry
            rp = ladder[level] * scale * w[i]
            if heat + rp > heat_cap + 1e-12:
                continue
            taken[i] = True
            risk_pct[i] = rp
            open_risk[i] = eq * rp
            heat += rp
        else:
            if not taken[i]:
                continue
            eq += open_risk[i] * r[i]
            heat -= risk_pct[i]
            if heat < 0: heat = 0.0
            level, consec = _step_level(level, consec, r[i], nlev, d1, d2, d3)
            if eq > peak: peak = eq
            dd = 1.0 - eq / peak
            if dd > mdd: mdd = dd
            if dd > env_used: env_used = dd
            eq_path[nclose] = eq; close_t[nclose] = t_out[i]; nclose += 1
            if harvest_on and nclose % cycle_len == 0:
                profit = eq - cyc_start
                if profit > 0 and eq >= peak - 1e-15:
                    frac = h_max * max(0.0, 1.0 - env_used / env_cap) * max(0.0, 1.0 - heat / 0.08)
                    amt = frac * profit
                    eq -= amt; peak -= amt; banked += amt
                cyc_start = eq
    return eq_path[:nclose], close_t[:nclose], mdd, taken, risk_pct, banked


@njit(cache=True)
def lifecycles(r_seq, w_seq, ladder, scale, d1, d2, d3, n_sims, n_events, block, seed,
               env):
    """Block-bootstrap lifecycles from the real resolved-trade sequence (keeps losing
    streaks and cross-leg clustering inside each block). Serial resolution, as P26 is
    defined. Returns per-sim final multiple and max DD, plus breach count."""
    np.random.seed(seed)
    m = len(r_seq)
    finals = np.empty(n_sims); mdds = np.empty(n_sims)
    breaches = 0
    nlev = len(ladder)
    for s in range(n_sims):
        eq = 1.0; peak = 1.0; mdd = 0.0; level = 0; consec = 0
        k = 0
        while k < n_events:
            start = np.random.randint(0, m)
            for b in range(block):
                if k >= n_events:
                    break
                idx = (start + b) % m
                rr = r_seq[idx]
                eq *= 1.0 + ladder[level] * scale * w_seq[idx] * rr
                if rr > 0.05:
                    level = max(level - 1, 0); consec = 0
                elif rr < -0.05:
                    consec += 1
                    d = d1 if consec == 1 else (d2 if consec == 2 else d3)
                    level = min(level + d, nlev - 1)
                if eq > peak: peak = eq
                dd = 1.0 - eq / peak
                if dd > mdd: mdd = dd
                k += 1
        finals[s] = eq; mdds[s] = mdd
        if mdd > env: breaches += 1
    return finals, mdds, breaches


def integrity(close_t):
    """Per event: >=15 min since previous close = 100%, 5-15 min = 85%, <5 min = 70%.
    Returns the average score and the share of events under 1h / 15m / 5m."""
    if len(close_t) < 2:
        return 1.0, 0, 0, 0
    g = np.diff(np.sort(close_t)) / 60.0
    score = np.where(g < 5, 0.70, np.where(g < 15, 0.85, 1.0))
    return float(np.r_[1.0, score].mean()), float((g < 60).mean()), float((g < 15).mean()), float((g < 5).mean())


@njit(cache=True)
def seq_dd(r, w, ladder, scale, d1, d2, d3):
    """Exact max drawdown of one given resolved-trade sequence (ladder starts at L0)."""
    eq = 1.0; peak = 1.0; mdd = 0.0; level = 0; consec = 0
    nlev = len(ladder)
    for i in range(len(r)):
        eq *= 1.0 + ladder[level] * scale * w[i] * r[i]
        if r[i] > 0.05:
            level = max(level - 1, 0); consec = 0
        elif r[i] < -0.05:
            consec += 1
            d = d1 if consec == 1 else (d2 if consec == 2 else d3)
            level = min(level + d, nlev - 1)
        if eq > peak: peak = eq
        dd = 1.0 - eq / peak
        if dd > mdd: mdd = dd
    return mdd, eq
