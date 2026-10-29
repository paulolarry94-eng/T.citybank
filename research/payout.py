"""Fortnightly payout engine, replayed on the real trade record (real timestamps).

Trading account: fixed-fractional risk per leg (optional drawdown throttle).
Every 14 days (the cycle):
  1. SWEEP  - beta x (equity above the high-water mark) moves to the internal BANK
              (cash that never trades again); the high-water mark resets to equity.
  2. PAY    - the broker withdrawal = min(bank, target x reference capital).
The payout therefore depends on the bank, not on that fortnight's result, so a flat or
losing fortnight can still pay. Nothing here changes a trade; it only sizes and banks.
"""
import numpy as np
import pareto as PA, portfolio as P

FORTNIGHT = 14 * 86400


def simulate(legs, risk, target, beta=1.0, throttle=None, capital=1.0, start=None,
             mode="base", grow=0.0, heat_cap=None):
    """risk: base risk fraction for weight 1.0. throttle: (dd_level, factor) halves risk
    once trading drawdown exceeds dd_level. Returns a dict of payout statistics."""
    t_in, t_out, r, leg, w = P.merge(legs)
    ev = sorted([(t_in[i], 1, i) for i in range(len(r))] + [(t_out[i], 0, i) for i in range(len(r))])
    t0 = ev[0][0] if start is None else start
    next_pay = t0 + FORTNIGHT
    eq = capital; hwm = capital; peak_tr = capital; mdd = 0.0
    bank = 0.0; paid = []; open_amt = {}; open_pct = {}; blocked = 0
    for t, kind, i in ev:
        while t >= next_pay:                          # cycle boundary(ies) before this event
            # base mode: only profit above the trading base is banked, so a loss is always
            # repaid by later profit before anything leaves. grow>0 lets the base (and so
            # the trade size) compound by that share of each sweep.
            ref = hwm
            if eq > ref:
                sweep = beta * (eq - ref); eq -= sweep; bank += sweep
                hwm = ref + grow * sweep / max(beta, 1e-9) * beta if mode == "base" else eq
                peak_tr = max(peak_tr - sweep, eq)
            elif mode != "base":
                hwm = eq
            pay = min(bank, target * capital)
            bank -= pay; paid.append(pay)
            next_pay += FORTNIGHT
        if kind == 1:
            dd = 1 - eq / peak_tr
            f = throttle[1] if (throttle and dd > throttle[0]) else 1.0
            pct = risk * w[i] * f
            if heat_cap is not None and sum(open_pct.values()) + pct > heat_cap + 1e-12:
                blocked += 1
                continue                       # the shared heat wall refuses this trade
            open_amt[i] = eq * pct; open_pct[i] = pct
        else:
            if i not in open_amt:
                continue
            open_pct.pop(i)
            eq += open_amt.pop(i) * r[i]
            peak_tr = max(peak_tr, eq)
            mdd = max(mdd, 1 - eq / peak_tr)
    paid = np.array(paid)
    years = len(paid) / 26.0
    return {"fortnights": len(paid), "hit_rate": float((paid >= target * capital * 0.999).mean()),
            "any_rate": float((paid > 0).mean()), "avg_pay": float(paid.mean()),
            "total_paid": float(paid.sum()), "per_year_paid": float(paid.sum() / years),
            "end_equity": float(eq), "end_bank": float(bank), "trading_mdd": float(mdd),
            "worst_dry_spell": int(_longest_zero(paid >= target * capital * 0.999)),
            "blocked_by_heat": blocked}


def _longest_zero(hit):
    best = cur = 0
    for h in hit:
        cur = 0 if h else cur + 1
        best = max(best, cur)
    return best


def bootstrap(legs, risk, target, n=2000, seed=11, beta=1.0, throttle=None, block_days=91):
    """Synthetic 15-year histories built from randomly re-ordered calendar quarters of the
    real trade record (trades keep their real within-quarter timing and clustering)."""
    rng = np.random.default_rng(seed)
    names = [l[0] for l in legs]
    t0 = min(int(l[1]["t_in"].min()) for l in legs)
    B = block_days * 86400
    nblk = int((max(int(l[1]["t_out"].max()) for l in legs) - t0) // B) + 1
    out = []
    for _ in range(n):
        pick = rng.integers(0, nblk, nblk)
        new = []
        for name, tr, w in legs:
            k = (tr["t_in"] - t0) // B
            parts = []
            for j, src in enumerate(pick):
                sel = tr[k == src].copy()
                if len(sel):
                    shift = (j - src) * B
                    sel["t_in"] += shift; sel["t_out"] += shift
                    parts.append(sel)
            new.append((name, np.concatenate(parts) if parts else tr[:0], w))
        out.append(simulate(new, risk, target, beta=beta, throttle=throttle))
    keys = ("hit_rate", "per_year_paid", "trading_mdd", "end_equity", "worst_dry_spell")
    return {k: np.array([o[k] for o in out]) for k in keys}
