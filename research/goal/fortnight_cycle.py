"""The cycle goal with a cycle = 2 weeks of trading instead of 10 trades (owner question, 2026-11-06).

    python3 research/goal/fortnight_cycle.py

Fortnights: 14-day blocks from Monday 2011-01-03 00:00 UTC; a trade counts in the fortnight of its exit. Lifecycle = 36
fortnights (about 17 months). Risk per trade r is set so that 95% of bootstrapped lifecycles (36 fortnights drawn with
replacement, trades inside a fortnight kept in order) stay inside the drawdown cap, measured trade by trade. Then the mean
return per fortnight at that risk. Survivor trades as in cyclegoal.py --survivors (Exness Zero costs + swaps; swap-free
separately). Also the fortnight Sharpe the goal needs (normal fortnights, drawdown measured at fortnight ends: lenient).
Output: research/results/goal/fortnight_cycle.json and FORTNIGHT_CYCLE.md
"""
import os, sys, json, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "seesare"))
import daily_queue_study as DQ        # noqa: E402
import universe_cap_study as U        # noqa: E402

OUT = os.path.join(ROOT, "research", "results", "goal")
T0 = int(dt.datetime(2011, 1, 3, tzinfo=dt.timezone.utc).timestamp())
F = 14 * 86400
N_LIFE, DRAWS, CAPS = 36, 5000, (0.036, 0.05, 0.08)


def fortnights(legs, weighted, t_lo, t_hi):
    rows = [(int(o), float(r) * (g["w"] if weighted else 1.0)) for g in legs for o, r in zip(g["t_out"], g["r"]) if t_lo <= o < t_hi]
    rows.sort()
    k0, k1 = (t_lo - T0) // F, (t_hi - T0) // F
    blocks = [[] for _ in range(int(k1 - k0))]
    for o, r in rows:
        k = int((o - T0) // F - k0)
        if 0 <= k < len(blocks):
            blocks[k].append(r)
    return [np.array(b) for b in blocks]


def max_dd(path):
    eq = np.r_[0.0, np.cumsum(path)]
    return float(np.max(np.maximum.accumulate(eq) - eq))


def score(blocks, seed=3):
    sums = np.array([b.sum() for b in blocks])
    rng = np.random.default_rng(seed)
    dd = np.array([max_dd(np.concatenate([blocks[i] for i in rng.integers(0, len(blocks), N_LIFE)]))
                   for _ in range(DRAWS)])
    q95 = float(np.quantile(dd, 0.95))
    out = dict(fortnights=len(blocks), trades_per_fortnight=round(float(np.mean([len(b) for b in blocks])), 1),
               sharpe_per_fortnight=round(float(sums.mean() / sums.std(ddof=1)), 3), mean_R_per_fortnight=round(float(sums.mean()), 3))
    for cap in CAPS:
        r = cap / q95
        f = sums * r * 100
        out[f"cap_{cap:g}"] = dict(risk_per_trade_pct=round(r * 100, 3), mean_pct=round(float(f.mean()), 3),
                                    median_pct=round(float(np.median(f)), 3), positive=round(float(np.mean(f > 0)), 3),
                                    at_least_2pct=round(float(np.mean(f >= 2)), 3), worst_pct=round(float(f.min()), 2),
                                    pct_a_year=round(float(f.mean() * 26.09), 1))
    return out


def needed_sharpe(C=2.0, cap=3.6, sims=4000, seed=5):
    """Smallest fortnight Sharpe with mean C % whose 95th-percentile lifecycle drawdown (36 fortnights) is <= cap %."""
    rng = np.random.default_rng(seed); z = rng.standard_normal((sims, N_LIFE))
    lo, hi = 0.05, 10.0
    for _ in range(40):
        S = (lo + hi) / 2
        x = C + (C / S) * z
        eq = np.concatenate([np.zeros((sims, 1)), np.cumsum(x, 1)], 1)
        q = np.quantile(np.max(np.maximum.accumulate(eq, 1) - eq, 1), 0.95)
        lo, hi = (lo, S) if q <= cap else (S, hi)
    return round(hi, 2)


def main():
    Y26 = int(dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc).timestamp())
    END26 = int(dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc).timestamp())
    res = dict(note=__doc__.split("\n\n")[1], needed={})
    for C in (2.0, 5.0, 7.0):
        for cap in (3.6, 5.0, 8.0):
            res["needed"][f"+{C:g}% inside {cap:g}%"] = needed_sharpe(C, cap)
    sets = {}
    for prof in ("zero_swaps", "zero_swapfree"):
        legs = DQ.legs(prof)
        book = {g["name"] for g in U.book_legs(prof)[0]}
        sets[prof] = {"All 13 survivors": legs, "11-leg book": [g for g in legs if g["name"] in book],
                      "Tokyo fix": [g for g in legs if g["name"] == "tokyo_fix_gotobi_v1"],
                      "EURUSD reversal": [g for g in legs if g["name"] == "eurusd_close_beyond_reversal_v1"]}
    res["sets"] = {}
    for prof, S in sets.items():
        for name, legs in S.items():
            for weighted in (False, True):
                key = f"{name} | {'leg weights' if weighted else 'every trade 1R'} | {'swaps' if prof == 'zero_swaps' else 'swap-free'}"
                res["sets"][key] = score(fortnights(legs, weighted, T0, Y26))
                print(key, res["sets"][key]["sharpe_per_fortnight"], res["sets"][key]["cap_0.036"], flush=True)
    L26 = DQ.legs("zero_swaps", y2026=True)
    for weighted in (False, True):
        key = f"11-leg book, Jan-Oct 2026 forward | {'leg weights' if weighted else 'every trade 1R'} | swaps"
        b = fortnights(L26, weighted, Y26 - 3 * 86400, END26)          # fortnight grid continues from 2011
        sums = np.array([x.sum() for x in b])
        res["sets"][key] = dict(fortnights=len(b), sharpe_per_fortnight=round(float(sums.mean() / sums.std(ddof=1)), 3),
                                mean_R_per_fortnight=round(float(sums.mean()), 3))
        print(key, res["sets"][key])
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "fortnight_cycle.json"), "w"), indent=1)
    print(json.dumps(res["needed"], indent=1))
    return res


if __name__ == "__main__":
    main()
