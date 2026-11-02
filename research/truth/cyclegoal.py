"""Cycle goal: how far a strategy is from the owner's target (+2% to +7% per 10-trade cycle) inside a lifecycle drawdown cap.

Owner's units: cycle = 10 trades; lifecycle = 36 cycles = 360 trades; drawdown cap D = 3.6% of the starting balance
("higher but not too high": 5-8%), held in 95% of lifecycles; risk per trade is a fixed share of the start (no compounding).
R = the planned risk of a trade. Everything is AFTER costs and swaps.

The one number that decides it: edge quality s = mean R per trade / standard deviation of R per trade (per-trade Sharpe).
  cycle return C = n x r x mean      (n trades per cycle, r = risk per trade)
  drawdown       ~ r x (variance / mean), so with r fixed by C, drawdown / C depends on s alone.
Calculators:
  needed_s(C, D)        edge quality that target C needs for 95% of lifecycles to stay within D (10-trade cycles), from the
                        win/loss map of research/seesare/cycle_math_study.py (80 cells x 20,000 lifecycles): at C = 2% the
                        95th-percentile drawdown is about a x s^-k; drawdown scales with C because risk does.
  needed_s_sim(C, D, n) the same by direct simulation with normally distributed trades, for any trades-per-cycle n.
  score(R)              a strategy's own trades: s, and a block bootstrap (10 consecutive trades per cycle, 5,000 lifecycles)
                        giving the mean cycle at the risk where the 95th-percentile lifecycle drawdown equals each cap, the risk
                        and drawdown each target would need, and the gap to the needed s.
  cost_ladder(...)      the same trades at other prices: gross, RoboForex Prime, Exness Zero, lab standard.
CLI:
  python3 research/truth/cyclegoal.py --table                  needed edge quality for +2..7% x caps
  python3 research/truth/cyclegoal.py --trades <csv> [--col r] score any trade list (e.g. a lab parity_trades.csv)
  python3 research/truth/cyclegoal.py --survivors               score the verified strategies -> results/truth/cycle_goal_survivors.json
"""
import os
import sys
import json
import math
import functools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MAP = os.path.join(ROOT, "research", "results", "seesare", "cycle_math_study.json")
N_CYC, N_CYCLES = 10, 36
TARGETS = (0.02, 0.03, 0.04, 0.05, 0.06, 0.07)
CAPS = (0.036, 0.05, 0.06, 0.08)
SIMS, SEED = 5000, 11


@functools.lru_cache(maxsize=1)
def map_fit():
    """Fit of the 95th-percentile lifecycle drawdown (%) at +2% per cycle against s: dd95 = a * s**(-k)."""
    cells = [c for c in json.load(open(MAP))["cells"] if c.get("feasible") and 0.15 <= c["s"] <= 0.8]
    s = np.array([c["s"] for c in cells]); y = np.array([c["dd_p95"] for c in cells])
    slope, icpt = np.polyfit(np.log(s), np.log(y), 1)
    return dict(a=float(np.exp(icpt)), k=float(-slope), cells=len(cells))


def needed_s(C, D):
    """Edge quality needed for a mean of C per 10-trade cycle with 95% of 360-trade lifecycles inside drawdown D (fractions)."""
    f = map_fit()
    return ((C / 0.02) * f["a"] / (D * 100.0)) ** (1.0 / f["k"])


def map_table(C):
    """Exact for the win/loss model: 95th-percentile drawdown (%) of each win-rate x payoff cell at target C."""
    out = {}
    for c in json.load(open(MAP))["cells"]:
        out[(c["w"], c["b"])] = round(c["dd_p95"] * C / 0.02, 2) if c.get("feasible") else None
    return out


def lifecycle_dd(paths):
    eq = np.cumsum(paths, axis=-1)
    peak = np.maximum.accumulate(np.concatenate([np.zeros(eq.shape[:-1] + (1,)), eq], axis=-1), axis=-1)[..., 1:]
    return np.max(peak - eq, axis=-1)


def needed_s_sim(C, D, n=N_CYC, sims=4000, seed=SEED):
    """Direct simulation, normally distributed trades (sd 1 R): smallest s with the 95th-percentile drawdown <= D at mean C."""
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal((sims, N_CYCLES * n))
    lo, hi = 0.005, 3.0
    for _ in range(40):
        s = 0.5 * (lo + hi)
        dd95 = float(np.percentile(lifecycle_dd(Z + s), 95)) * C / (n * s)
        lo, hi = (s, hi) if dd95 > D else (lo, s)
    return hi


def trades_to_prove(s, t=3.0):
    """Trades needed before a true edge quality s shows a t-statistic of t on average."""
    return int(math.ceil((t / s) ** 2)) if s > 0 else None


def bootstrap(R, sims=SIMS, seed=SEED):
    """Blocks of 10 consecutive trades, 36 per lifecycle. Returns cycle sums (R) and lifecycle drawdowns (R)."""
    R = np.asarray(R, float)
    nb = len(R) - N_CYC + 1
    if nb < 1:
        return None, None
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, nb, size=(sims, N_CYCLES))
    paths = R[starts[..., None] + np.arange(N_CYC)].reshape(sims, N_CYCLES * N_CYC)
    return paths.reshape(sims, N_CYCLES, N_CYC).sum(axis=2), lifecycle_dd(paths)


def score(R):
    """Where a list of trade results (R, after costs) sits against the cycle goal."""
    R = np.asarray(R, float)
    R = R[np.isfinite(R)]
    if len(R) < 2 * N_CYC:
        return dict(trades=int(len(R)), note="too few trades")
    mu, sig = float(R.mean()), float(R.std(ddof=1))
    s = mu / sig if sig > 0 else 0.0
    cyc, dd = bootstrap(R)
    p95 = float(np.percentile(dd, 95))
    out = dict(trades=int(len(R)), mean_R=round(mu, 4), sd_R=round(sig, 4), s=round(s, 4), win_rate=round(float((R > 0).mean()), 3),
               trades_to_prove_t3=trades_to_prove(s),
               cycle_mean_pct_at_cap={f"{D * 100:g}": round(float(cyc.mean()) * D / p95 * 100, 3) for D in CAPS},
               risk_pct_at_cap={f"{D * 100:g}": round(D / p95 * 100, 4) for D in CAPS},
               needed_s={f"{C * 100:g}%/{D * 100:g}%": round(needed_s(C, D), 3) for C in TARGETS for D in CAPS[:2]})
    if mu > 0:
        out["for_target"] = {f"{C * 100:g}": dict(risk_pct=round(C / (N_CYC * mu) * 100, 3), dd95_pct=round(p95 * C / (N_CYC * mu) * 100, 1))
                             for C in TARGETS}
    out["gap_2pct_at_3.6"] = round(needed_s(0.02, 0.036) / s, 1) if s > 0 else None
    out["meets"] = [f"{C * 100:g}% at {D * 100:g}%" for C in TARGETS for D in CAPS
                    if out["cycle_mean_pct_at_cap"][f"{D * 100:g}"] >= C * 100]
    return out


def profiles():
    """Round-trip cost (price units) by profile and symbol."""
    lab = {k: v["cost"] for k, v in json.load(open(os.path.join(HERE, "costs.json"))).items() if isinstance(v, dict)}
    ex = json.load(open(os.path.join(HERE, "costs_exness_zero.json")))["realistic"]
    rf = json.load(open(os.path.join(HERE, "costs_roboforex_prime.json")))["realistic"]
    return {"gross": None, "roboforex_prime": rf, "exness_zero": ex, "lab_standard": lab}


def cost_ladder(T, markets, periods):
    """T: lab trade rows [t_in, t_out, side, net R, stop distance, cost R, nights, financing R, market index].
    periods: {name: boolean mask}. Returns mean R and t per period at each price list (swaps unchanged)."""
    out = {}
    for prof, table in profiles().items():
        R = T[:, 3] + T[:, 5]                                  # net R before trading costs
        if table is not None:
            c = np.array([table.get(markets[int(i)], np.nan) for i in T[:, 8]])
            R = R - c / T[:, 4]
        res = {}
        for name, m in periods.items():
            x = R[m]
            x = x[np.isfinite(x)]
            res[name] = dict(n=int(len(x)), E=round(float(x.mean()), 4) if len(x) else None,
                             t=round(float(x.mean() / x.std(ddof=1) * math.sqrt(len(x))), 2) if len(x) > 2 and x.std() > 0 else None)
        out[prof] = res
    return out


def table_text():
    f = map_fit()
    L = [f"Edge quality s needed (95% of 360-trade lifecycles inside the cap; fit dd95 = {f['a']:.3f}% x s^-{f['k']:.2f} at +2%):",
         "target/cycle " + " ".join(f"cap {D * 100:>4g}%" for D in CAPS)]
    for C in TARGETS:
        L.append(f"   +{C * 100:g}%      " + " ".join(f"{needed_s(C, D):9.3f}" for D in CAPS))
    return "\n".join(L)


def survivors():
    sys.path.insert(0, os.path.join(ROOT, "research", "seesare"))
    import daily_queue_study as DQ
    import universe_cap_study as U
    legs = DQ.legs("zero_swaps")
    book = {g["name"] for g in U.book_legs("zero_swaps")[0]}
    sets = {"book_11_legs_2011_25": [g for g in legs if g["name"] in book],
            "tokyo_fix_2011_25": [g for g in legs if g["name"] == "tokyo_fix_gotobi_v1"],
            "eurusd_reversal_2011_25": [g for g in legs if g["name"] == "eurusd_close_beyond_reversal_v1"],
            "all_13_2011_25": legs,
            "book_11_legs_2026_forward": DQ.legs("zero_swaps", y2026=True)}
    out = {}
    for k, gs in sets.items():
        R = [x[2] for x in DQ.signals(gs, {g["name"] for g in gs})]
        out[k] = score(R)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", action="store_true"); ap.add_argument("--trades"); ap.add_argument("--col", default="r")
    ap.add_argument("--survivors", action="store_true")
    a = ap.parse_args()
    if a.table or not (a.trades or a.survivors):
        print(table_text())
    if a.trades:
        import pandas as pd
        print(json.dumps(score(pd.read_csv(a.trades)[a.col].to_numpy()), indent=1))
    if a.survivors:
        res = dict(note="Exness Zero costs + swaps, every signal of each set at 1 R, 2011-25 seen before; 2026 is forward data.",
                   needed=table_text(), sets=survivors())
        p = os.path.join(ROOT, "research", "results", "truth", "cycle_goal_survivors.json")
        json.dump(res, open(p, "w"), indent=1)
        for k, v in res["sets"].items():
            print(k, {x: v[x] for x in ("trades", "s", "win_rate", "cycle_mean_pct_at_cap", "gap_2pct_at_3.6", "meets")})
