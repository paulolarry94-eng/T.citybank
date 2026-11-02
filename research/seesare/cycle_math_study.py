"""Cycle math (owner, 2026-11-02): without a backtest, what does +2% per 10-trade cycle need, and what lifecycle drawdown
(360 trades) comes with it? "Within 3.6%, it can be higher but not too high, still safe." Fixed before any result.

Model: trades are independent; each wins +b R with probability w, otherwise loses 1 R (R = the planned risk; all numbers
are AFTER costs). Risk per trade is a fixed share r of the starting balance (no compounding, like the ledger's fixed $1,000
State Value). Cycle = 10 trades; lifecycle = 36 cycles = 360 trades. Mean per trade mu = w*b - (1-w), spread
sigma = (b+1)*sqrt(w(1-w)), per-trade Sharpe s = mu / sigma.

A  Closed form. For a random walk with drift, the chance of ever falling D below where it starts is about exp(-2 mu D / sigma^2)
   (D in R). With r = C / (10 mu) for a cycle target C this is exp(-20 s^2 D / C): only the per-trade Sharpe s matters.
   Needed s for chance p: sqrt(C ln(1/p) / (20 D)). Table: C = 2%; D = 3.6, 5, 6, 8, 10%; p = 5%, 1%. (One fall from one
   peak; a lifecycle has many peaks, so the Monte Carlo below is the real answer and will need a somewhat higher s.)
B  Monte Carlo, exact for the model: w = 0.35 ... 0.80 (step 0.05) x b in 0.5, 0.75, 1, 1.5, 2, 3, 4, 5 = 80 cells,
   20,000 lifecycles per cell, the same random numbers in every cell. Risk r = 0.2% / mu, so the mean cycle is exactly +2%.
   Reported per cell: mu, s, r, lifecycle max drawdown (median, 95th percentile), chance it exceeds 3.6 / 5 / 6 / 8 / 10%,
   share of positive cycles, 10th-percentile cycle, median lifecycle return, 95th-percentile longest losing streak; and the
   mean cycle at the risk where the 95th-percentile drawdown is exactly 3.6 / 5 / 6 / 8%.
C  The drawdown-keyed ladder (ledger format 2) at weight 1.00 (the engine's maximum), same cells: level = floor(drawdown /
   $2.25) on $1,000, risk = 0.30 x 1.00 x $2.25 x (15 - level) rounded down to 4 decimals, lifecycle stops at L15. The
   drawdown cannot pass 3.6% by construction. Reported: median / mean cycle, share positive, chance a lifecycle stops,
   median lifecycle return.
D  Our verified strategies on the same map (descriptive; every period was seen before except Jan-Oct 2026): per-trade
   mu, sigma, s after Exness Zero costs + swaps for the 11-leg book (all signals), the Tokyo fix, the EURUSD reversal and all
   13 together (2011-2025), and the book Jan-Oct 2026 (forward data); then a block bootstrap (10 consecutive trades per
   cycle, 5,000 lifecycles, as daily_queue_study.py): the mean cycle at the risk where the 95th-percentile drawdown is
   3.6 / 5 / 6 / 8%, and the risk that a +2% mean cycle would need with its 95th-percentile drawdown.
Output: research/results/seesare/cycle_math_study.json
"""
import os
import sys
import json
import math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

C_TARGET, N_CYC, N_LIFE = 0.02, 10, 360
CAPS = (0.036, 0.05, 0.06, 0.08, 0.10)
WS = [round(0.35 + 0.05 * i, 2) for i in range(10)]
BS = (0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0)
SIMS, SEED = 20000, 20261102
OUT = os.path.join(HERE, "..", "results", "seesare", "cycle_math_study.json")


def max_dd(eq):
    """eq: (sims, n) cumulative P&L; drawdown measured from the running peak including the start (0)."""
    peak = np.maximum.accumulate(np.concatenate([np.zeros((eq.shape[0], 1)), eq], axis=1), axis=1)[:, 1:]
    return (peak - eq).max(axis=1)


def longest_loss_run(win):
    best = np.zeros(win.shape[0], int); cur = np.zeros(win.shape[0], int)
    for j in range(win.shape[1]):
        cur = np.where(win[:, j], 0, cur + 1); best = np.maximum(best, cur)
    return best


def part_a():
    out = {}
    for D in CAPS:
        for p in (0.05, 0.01):
            out[f"D{D * 100:g}%/p{p * 100:g}%"] = round(math.sqrt(C_TARGET * math.log(1 / p) / (20 * D)), 3)
    return out


def ladder_run(win, b):
    """Drawdown-keyed ladder, weight 1.00, $1,000 State Value. Returns cycle P&L in % (sims, 36) and stopped flags."""
    sims, n = win.shape
    net = np.zeros(sims); peak = np.zeros(sims); stopped = np.zeros(sims, bool)
    cyc = np.zeros((sims, n // N_CYC))
    for j in range(n):
        dd = peak - net
        u = np.maximum(np.round(dd * 10000.0).astype(np.int64), 0)
        lvl = np.minimum(u // 22500, 15)
        plan = np.floor(0.30 * 1.0 * 2.25 * (15 - lvl) * 10000.0 + 1e-6) / 10000.0
        plan = np.where(stopped, 0.0, plan)
        pnl = np.where(win[:, j], plan * b, -plan)
        net = net + pnl; peak = np.maximum(peak, net)
        stopped |= (np.minimum(np.maximum(np.round((peak - net) * 10000.0).astype(np.int64), 0) // 22500, 15) >= 15)
        cyc[:, j // N_CYC] += pnl / 10.0                      # $ on $1,000 -> %
    return cyc, stopped, (peak - net)


def part_bc():
    rng = np.random.default_rng(SEED)
    U = rng.random((SIMS, N_LIFE))
    rows = []
    for w in WS:
        win = U < w
        streak = int(np.percentile(longest_loss_run(win), 95))
        for b in BS:
            mu = w * b - (1 - w)
            sig = (b + 1) * math.sqrt(w * (1 - w))
            row = dict(w=w, b=b, mu=round(mu, 4), s=round(mu / sig, 4), loss_streak_p95=streak)
            if mu <= 0:
                row["feasible"] = False
                rows.append(row); continue
            R = np.where(win, b, -1.0)
            eq = np.cumsum(R, axis=1)
            dd_r = max_dd(eq)
            cyc_r = R.reshape(SIMS, N_LIFE // N_CYC, N_CYC).sum(axis=2)
            r = C_TARGET / (N_CYC * mu)
            dd = dd_r * r * 100; cyc = cyc_r * r * 100; life = eq[:, -1] * r * 100
            p95 = float(np.percentile(dd_r, 95))
            row.update(feasible=True, risk_pct=round(r * 100, 4), dd_median=round(float(np.median(dd)), 2), dd_p95=round(float(np.percentile(dd, 95)), 2),
                       **{f"p_dd_over_{c * 100:g}": round(float((dd > c * 100).mean()), 4) for c in CAPS},
                       cycle_positive=round(float((cyc > 0).mean()), 3), cycle_p10=round(float(np.percentile(cyc, 10)), 3),
                       life_median=round(float(np.median(life)), 2),
                       cycle_mean_at_cap={f"{c * 100:g}": round(float(N_CYC * mu * (c / p95) * 100), 3) for c in CAPS[:4]})
            lc, stopped, _ = ladder_run(win, b)
            row["ladder"] = dict(cycle_median=round(float(np.median(lc)), 3), cycle_mean=round(float(lc.mean()), 3),
                                 cycle_positive=round(float((lc > 0).mean()), 3), p_stopped=round(float(stopped.mean()), 4),
                                 life_median=round(float(np.median(lc.sum(axis=1))), 2))
            rows.append(row)
    return rows


def part_d():
    import daily_queue_study as D
    import universe_cap_study as U
    legs = D.legs("zero_swaps")
    book_names = {g["name"] for g in U.book_legs("zero_swaps")[0]}
    sets = {"book_11_legs_2011_25": [g for g in legs if g["name"] in book_names],
            "tokyo_fix_2011_25": [g for g in legs if g["name"] == "tokyo_fix_gotobi_v1"],
            "eurusd_reversal_2011_25": [g for g in legs if g["name"] == "eurusd_close_beyond_reversal_v1"],
            "all_13_2011_25": legs,
            "book_11_legs_2026_forward": D.legs("zero_swaps", y2026=True)}
    out = {}
    for name, gs in sets.items():
        R = np.array([x[2] for x in D.signals(gs, {g["name"] for g in gs})])
        mu, sig = float(R.mean()), float(R.std(ddof=1))
        cyc, dd = D.monte_carlo(R)
        p95 = float(np.percentile(dd, 95))
        res = dict(trades=len(R), mu=round(mu, 4), sigma=round(sig, 4), s=round(mu / sig, 4),
                   cycle_mean_at_cap={f"{c * 100:g}": round(float(cyc.mean()) * (c / p95) * 100, 3) for c in CAPS[:4]})
        if mu > 0:
            r = C_TARGET / (N_CYC * mu)
            res.update(risk_for_2pct=round(r * 100, 3), dd_p95_at_2pct=round(p95 * r * 100, 1))
        out[name] = res
    return out


if __name__ == "__main__":
    res = dict(design=__doc__, closed_form_s_needed=part_a())
    print("A needed per-trade Sharpe:", res["closed_form_s_needed"])
    res["cells"] = part_bc()
    for r in res["cells"]:
        if r["feasible"]:
            print(f"w {r['w']:.2f} b {r['b']:4.2f} mu {r['mu']:+.3f} s {r['s']:.3f} risk {r['risk_pct']:.3f}% DD med {r['dd_median']:5.2f} "
                  f"p95 {r['dd_p95']:6.2f} P>3.6 {r['p_dd_over_3.6']:.3f} P>5 {r['p_dd_over_5']:.3f} cyc+ {r['cycle_positive']:.2f} "
                  f"p10 {r['cycle_p10']:+.2f} | ladder med {r['ladder']['cycle_median']:+.3f} mean {r['ladder']['cycle_mean']:+.3f} "
                  f"stop {r['ladder']['p_stopped']:.3f}")
    res["ours"] = part_d()
    for k, v in res["ours"].items():
        print(k, v)
    with open(OUT, "w") as f:
        json.dump(res, f, indent=1)
