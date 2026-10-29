"""Size the kept legs and find the Pareto points.

Inside the walls (A/B/C): the envelope must hold on the real 2011-2025 replay (every
360-trade lifecycle, ladder reset at each) AND in 20,000,000 bootstrapped lifecycles.
Outside the walls (D): the smallest drawdown that still delivers >= 120%/yr on the
real replay.
"""
import json, os, sys, itertools, datetime as dt
import numpy as np
import portfolio as P

HERE = os.path.dirname(__file__)
ENV = 0.036


def load_legs(names, weights):
    return [(n, np.load(os.path.join(HERE, "trades", n + "_off120.npy")), w)
            for n, w in zip(names, weights)]


def run_hist(legs, ladder, scale, harvest=False, d=(2, 3, 4), heat=0.08):
    t_in, t_out, r, leg, w = P.merge(legs)
    eq, ct, mdd, taken, rp, banked = P.replay(t_in, t_out, r, leg, w, ladder, scale, heat,
                                              d[0], d[1], d[2], len(legs), harvest, 0.8, ENV, 10)
    yrs = (ct[-1] - ct[0]) / (365.25 * 86400)
    cagr = eq[-1] ** (1 / yrs) - 1
    # per-lifecycle: replay each consecutive block of 360 resolved trades with a reset ladder
    order = np.argsort(t_out[taken], kind="stable")
    rr, ww = r[taken][order], w[taken][order]
    life_dd = []
    starts = range(0, max(1, len(rr) - 359), 30) if len(rr) >= 360 else [0]
    for s in starts:          # every 360-trade lifecycle start, stepped by 30 trades
        m, _ = P.seq_dd(rr[s:s + 360], ww[s:s + 360], ladder, scale, d[0], d[1], d[2])
        life_dd.append(m)
    integ = P.integrity(ct)
    return {"cagr": float(cagr), "mdd": float(mdd), "life_dd": [float(x) for x in life_dd],
            "trades": int(taken.sum()), "per_month": float(taken.sum() / (yrs * 12)),
            "avg_risk": float(rp[taken].mean()), "skipped_heat": int((~taken).sum()),
            "integrity": integ, "banked": float(banked), "years": float(yrs)}


def run_boot(legs, ladder, scale, n_sims, d=(2, 3, 4), block=20, seed=7):
    t_in, t_out, r, leg, w = P.merge(legs)
    o = np.argsort(t_out, kind="stable")
    f, m, b = P.lifecycles(r[o], w[o], ladder, scale, d[0], d[1], d[2], n_sims, 360, block,
                           seed, ENV)
    return {"breaches": int(b), "worst": float(m.max()), "p99": float(np.percentile(m, 99)),
            "med_dd": float(np.median(m)), "med_life": float(np.median(f) - 1),
            "p5_life": float(np.percentile(f, 5) - 1), "p_loss": float((f < 1).mean())}


def max_scale_inside(legs, ladder, d=(2, 3, 4), env=ENV, n_boot=1_000_000):
    """Largest ladder scale whose real replay AND bootstrap stay inside `env`."""
    lo, hi = 0.0, 1.0
    for _ in range(18):
        mid = (lo + hi) / 2
        h = run_hist(legs, ladder, mid, d=d)
        ok = max(h["life_dd"] + [0]) <= env
        if ok:
            b = run_boot(legs, ladder, mid, n_boot, d=d)
            ok = b["breaches"] == 0
        lo, hi = (mid, hi) if ok else (lo, mid)
    return lo


def scale_for_cagr(legs, ladder, target, d=(2, 3, 4), heat=0.08):
    lo, hi = 0.0, 20.0
    for _ in range(40):
        mid = (lo + hi) / 2
        c = run_hist(legs, ladder, mid, d=d, heat=heat)["cagr"]
        lo, hi = (mid, hi) if c < target else (lo, mid)
    return hi
