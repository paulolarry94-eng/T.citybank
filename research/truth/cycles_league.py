"""Cycle league: every configuration of a lab strategy scored in the owner's units (cycles and lifecycles).

    python3 research/truth/cycles_league.py <strategy_name>

For every configuration, the trades of all markets (fills before 2023, the lab's cut: the 2023-25 holdout stays closed)
are put in time order and scored per period (2011-19 development, 2020-22 validation) with research/truth/cyclegoal.py:
edge quality s, the mean return per 10-trade cycle at a 3.6% / 5% lifecycle drawdown cap (block bootstrap), and the actual
sequence at the 3.6%-cap risk: trades and cycles a year, months per 360-trade lifecycle, share of positive cycles, median and
worst cycle, lifecycles completed, their returns and worst drawdown. Ranked by 2011-19 edge quality.
Output: research/results/truth/<NAME>/cycles_league.json and CYCLES_LEAGUE.md
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import protocol as P          # noqa: E402
import cyclegoal as G         # noqa: E402
from grid import year_index   # noqa: E402


def league(name):
    S = P.load_strategy(os.path.join(HERE, "strategies", f"{name}.py"))
    per_cfg = {}
    for sym in S.MARKETS:
        M = P.market(sym, S)
        for p in P.param_sets(S):
            key = json.dumps({k: p[k] for k in S.GRID}, sort_keys=True)
            tr = P.run_config(S, M, p, 0.0, 0.0, 0)
            per_cfg.setdefault(key, []).append(np.c_[tr[:, :4], np.full(len(tr), S.MARKETS.index(sym))])
    rows = []
    for key, parts in per_cfg.items():
        T = np.vstack(parts) if parts else np.zeros((0, 5))
        T = T[np.argsort(T[:, 0], kind="stable")]
        y = year_index(T[:, 0]) if len(T) else np.zeros(0)
        row = dict(config=json.loads(key))
        for per, m in (("2011-19", y <= 2019), ("2020-22", (y >= 2020) & (y <= 2022))):
            row[per] = G.score(T[m, 3], T[m, 0])
            mk = {}
            for i, sym in enumerate(S.MARKETS):
                x = T[m & (T[:, 4] == i), 3]
                mk[sym] = round(float(x.mean()), 4) if len(x) else None
            row[per]["per_market_E"] = mk
        rows.append(row)
    rows.sort(key=lambda r: -(r["2011-19"].get("s") or -9))
    out = os.path.join(ROOT, "research", "results", "truth", name)
    os.makedirs(out, exist_ok=True)
    json.dump(rows, open(os.path.join(out, "cycles_league.json"), "w"), indent=1, default=float)
    open(os.path.join(out, "CYCLES_LEAGUE.md"), "w").write(markdown(S, rows))
    return rows


def _c(v, k, fmt="{:+.2f}%"):
    return fmt.format(v[k]) if v and v.get(k) is not None else "-"


def markdown(S, rows):
    L = [f"# Cycle league — {S.NAME}", "",
         "Every configuration, all markets in time order, fills before 2023 (the 2023-25 holdout stays closed). A cycle = 10 trades, "
         "a lifecycle = 360 trades. 'At 3.6%' = risk set so 95% of bootstrapped lifecycles stay inside a 3.6% drawdown. "
         f"Edge quality needed for +2% per cycle inside 3.6%: {G.needed_s(0.02, 0.036):.2f}.", "",
         "| # | Configuration | Trades/yr | Win rate | Edge quality s (2011-19) | Cycle at 3.6% | at 5% | Positive cycles | Worst cycle | "
         "Months per lifecycle | Lifecycles | Lifecycle returns | s 2020-22 | Cycle at 3.6% 2020-22 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        d, v = r["2011-19"], r["2020-22"]
        q = d.get("sequence") or {}
        cfg = ", ".join(f"{k} {v_}" for k, v_ in r["config"].items())
        cm, cv = d.get("cycle_mean_pct_at_cap", {}), v.get("cycle_mean_pct_at_cap", {})
        L.append(f"| {i} | {cfg} | {q.get('trades_per_year', '-')} | {d.get('win_rate', 0):.0%} | {d.get('s', 0):+.3f} | "
                 f"{cm.get('3.6', 0):+.3f}% | {cm.get('5', 0):+.3f}% | {q.get('cycles_positive', 0):.0%} | {_c(q, 'cycle_worst_pct')} | "
                 f"{q.get('months_per_lifecycle', '-')} | {q.get('lifecycles', 0)} | "
                 f"{', '.join(f'{x:+.1f}%' for x in q.get('lifecycle_returns_pct', [])) or '-'} | {v.get('s', 0):+.3f} | {cv.get('3.6', 0):+.3f}% |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    for n in sys.argv[1:]:
        rows = league(n)
        for r in rows[:10]:
            d = r["2011-19"]; v = r["2020-22"]
            print(r["config"], "s", d.get("s"), "cycle@3.6", d.get("cycle_mean_pct_at_cap", {}).get("3.6"), "| 2020-22 s", v.get("s"))
