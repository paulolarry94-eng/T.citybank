"""North Star portfolio risk manager (PREREGISTRATION.md §6) and the comparison of sizing policies on
identical trades.

Policies:  FF      fixed fractional, no caps, no states
           FF+RED  caps + RED circuit breaker only (amendment 3; AMBER shadow-only)
           FF+CAPS fixed fractional with the exposure caps
           RAG     caps + GREEN/AMBER/RED states
           BRAKE   caps + the earlier drawdown brake (x1 at peak -> x0.3 at a 30% drawdown, linear)
Sizing never increases after strong returns: risk = base x leg weight x state multiplier x current equity.

Backtest limits (stated, not hidden): P&L is realised at exit (no intratrade mark-to-market); open risk
counts the initial stop risk (trailing never reduces it here); live-only triggers (slippage, stale feed,
order rejections, spread, margin) cannot be simulated and are AMBER/RED inputs only in the EA.
"""
import numpy as np
from numba import njit

USD_SHORT = {"XAUUSD": 1, "EURUSD": 1, "GBPUSD": 1, "USDJPY": -1, "GBPJPY": 0, "EURGBP": 0}
CAPS = dict(trade=0.02, total=0.10, instrument=0.04, same_dir=0.03, usd=0.06)
POLICIES = {"FF": 0, "FF+CAPS": 1, "RAG": 2, "BRAKE": 3, "FF+RED": 4}


@njit(cache=True)
def _sim(t_in, t_out, side, r, leg, inst, usd, w, base, policy, caps, n_inst, n_leg, brake_dd):
    """Event simulation. Returns equity after each event, per-trade taken risk fraction, state log."""
    n = len(t_in)
    order_out = np.argsort(t_out)
    eq = 1.0; peak = 1.0
    open_risk = np.zeros(n); is_open = np.zeros(n, np.bool_)
    risk_amt = np.zeros(n); taken = np.zeros(n)
    eq_path = np.zeros(2 * n + 1); eq_t = np.zeros(2 * n + 1, np.int64); m = 0
    eq_path[0] = 1.0; eq_t[0] = t_in[0] if n else 0
    state = 0                      # 0 green, 1 amber, 2 red
    red_until_day = -1; last_trigger_day = -10 ** 9; n_red = 0; n_amber_entries = 0; ack_eq = -1.0
    day_start_eq = 1.0; cur_day = -1
    day_eq = np.zeros(400000); day_seen = np.zeros(400000, np.bool_)    # equity at start of each UTC day
    leg_hist = np.zeros((n_leg, 30)); leg_cnt = np.zeros(n_leg, np.int64)
    j = 0                          # pointer into exits
    skipped = 0
    why = np.zeros(8, np.int64)     # entries seen in: green, amber, red; amber causes: dd, day, 5day, open-risk, leg
    for i in range(n):
        t = t_in[i]
        # process exits up to t
        while j < n and t_out[order_out[j]] <= t:
            k = order_out[j]; j += 1
            if not is_open[k]:
                continue
            is_open[k] = False
            pnl = risk_amt[k] * r[k]
            eq += pnl
            if eq > peak:
                peak = eq
            m += 1; eq_path[m] = eq; eq_t[m] = t_out[k]
            lg = leg[k]; leg_hist[lg, leg_cnt[lg] % 30] = r[k]; leg_cnt[lg] += 1
        d = t // 86400
        if d != cur_day:
            cur_day = d; day_start_eq = eq
            if d < 400000:
                day_eq[d] = eq; day_seen[d] = True
        # trading-day counting helper: weekdays only
        dd = 1.0 - eq / peak
        mult = 1.0
        if policy == 2 or policy == 4:
            day_loss = 1.0 - eq / day_start_eq
            d5 = d - 7                           # five trading days ~ seven calendar days
            loss5 = 0.0
            while d5 < d and (d5 < 0 or not day_seen[d5]):
                d5 += 1
            if d5 < d and day_seen[d5]:
                loss5 = 1.0 - eq / day_eq[d5]
            tot_open = 0.0
            for q in range(i):
                if is_open[q]:
                    tot_open += open_risk[q]
            red_dd = dd >= 0.20 and (ack_eq < 0 or eq <= 0.95 * ack_eq)      # amendment 2: re-arm after a further 5%
            red = red_dd or day_loss >= 0.06
            amber = dd >= 0.10 or day_loss >= 0.03 or loss5 >= 0.06 or tot_open > 0.8 * caps[1]
            if policy == 4:
                if amber:
                    n_amber_entries += 1                                 # shadow AMBER: counted, never changes size
                amber = False
                if dd < 0.10:
                    ack_eq = -1.0
            if state == 2 and d >= red_until_day:
                state = 1 if policy == 2 else 0                          # operator acknowledgement: RAG resumes in AMBER
                last_trigger_day = d; ack_eq = eq
            if state != 2:
                if red:
                    state = 2; red_until_day = d + 14                    # 10 trading days ~ 14 calendar days
                    last_trigger_day = d; n_red += 1
                elif amber:
                    state = 1; last_trigger_day = d
                elif state == 1 and dd < 0.10 and d - last_trigger_day >= 14:
                    state = 0; ack_eq = -1.0
            why[state] += 1
            if state == 1:
                if dd >= 0.10:
                    why[3] += 1
                if day_loss >= 0.03:
                    why[4] += 1
                if loss5 >= 0.06:
                    why[5] += 1
                if tot_open > 0.8 * caps[1]:
                    why[6] += 1
            if state == 2:
                skipped += 1
                continue
            if state == 1:
                mult = 0.5
            lg = leg[i]
            if policy == 2 and leg_cnt[lg] >= 30 and leg_hist[lg].mean() < -0.25:
                mult = 0.5; why[7] += 1
        elif policy == 3:
            mult = max(0.3, 1.0 - 0.7 * min(dd / brake_dd, 1.0))
        f = base * w[i] * mult
        if policy >= 1:
            f = min(f, caps[0])
            tot = 0.0; ins = 0.0; sdir = 0.0; usd_net = 0.0
            for q in range(i):
                if is_open[q]:
                    tot += open_risk[q]
                    if inst[q] == inst[i]:
                        ins += open_risk[q]
                        if side[q] == side[i]:
                            sdir += open_risk[q]
                    usd_net += open_risk[q] * usd[q] * side[q]
            nu = usd_net + f * usd[i] * side[i]
            if tot + f > caps[1] + 1e-12 or ins + f > caps[2] + 1e-12 or sdir + f > caps[3] + 1e-12 or abs(nu) > caps[4] + 1e-12:
                skipped += 1
                continue
        open_risk[i] = f; is_open[i] = True; risk_amt[i] = f * eq; taken[i] = f
        if policy == 2 and mult < 1.0:
            n_amber_entries += 1
    while j < n:
        k = order_out[j]; j += 1
        if is_open[k]:
            is_open[k] = False
            eq += risk_amt[k] * r[k]
            m += 1; eq_path[m] = eq; eq_t[m] = t_out[k]
    return eq_path[:m + 1], eq_t[:m + 1], taken, skipped, n_red, n_amber_entries, why


def simulate(T, base, policy="RAG", brake_dd=0.30):
    """T: dict of arrays t_in, t_out, side, r, leg, inst, usd, w (sorted by t_in)."""
    caps = np.array([CAPS["trade"], CAPS["total"], CAPS["instrument"], CAPS["same_dir"], CAPS["usd"]])
    ep, et, taken, skipped, n_red, n_amb, why = _sim(T["t_in"], T["t_out"], T["side"], T["r"], T["leg"], T["inst"], T["usd"], T["w"],
                                                 base, POLICIES[policy], caps, int(T["inst"].max()) + 1, int(T["leg"].max()) + 1, brake_dd)
    pk = np.maximum.accumulate(ep)
    years = (et[-1] - et[0]) / (365.25 * 86400) if len(et) > 1 else 1.0
    return dict(final=float(ep[-1]), cagr=float(ep[-1] ** (1 / years) - 1) if years >= 0.25 else float("nan"), max_dd=float((1 - ep / pk).max()),
                taken=int((taken > 0).sum()), skipped=int(skipped), red_episodes=int(n_red), amber_entries=int(n_amb),
                states=dict(zip(("green", "amber", "red", "amber_dd", "amber_day", "amber_5day", "amber_open", "leg_half"), map(int, why))),
                eq=ep, eq_t=et)


def quarter_shuffle(T, rng):
    """Reshuffle calendar-quarter blocks (trades keep their order inside a block; times are shifted)."""
    q = (T["t_in"] // (91 * 86400)).astype(np.int64)
    qs = np.unique(q); perm = rng.permutation(len(qs)); start = qs.min()
    shift = np.zeros(qs.max() + 1, np.int64)
    for new_pos, old in enumerate(qs[perm]):
        shift[old] = (start + new_pos - old) * 91 * 86400
    s = shift[q]
    U = {k: v.copy() for k, v in T.items()}
    U["t_in"] = T["t_in"] + s; U["t_out"] = T["t_out"] + s
    o = np.argsort(U["t_in"], kind="stable")
    return {k: v[o] for k, v in U.items()}


def drawdown_tail(T, base, policy, n=200, seed=7, q=0.95):
    rng = np.random.default_rng(seed)
    dds = [simulate(quarter_shuffle(T, rng), base, policy)["max_dd"] for _ in range(n)]
    return float(np.quantile(dds, q)), float(np.median(dds))
