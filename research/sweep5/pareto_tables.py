"""Owner-facing Pareto tables from research/results/sweep5/pareto.json -> research/results/sweep5/PARETO.md."""
import os, sys, json, pickle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "goal"))
import timeless_mix as TM   # noqa: E402

o = json.load(open(os.path.join(ROOT, "research", "results", "sweep5", "pareto.json")))
M = o["mixes"]


def mix_trades(name):
    L = TM.DQ.legs("zero_swaps")
    pk = os.path.join(ROOT, "research", "results", "sweep5", "v2_legs.pkl")
    extra = pickle.load(open(pk, "rb")) if os.path.exists(pk) else []
    allL = L + extra
    R = np.concatenate([g["r"][(g["t_out"] >= TM.T0) & (g["t_out"] < TM.Y23)] * g["w"] for g in allL if g["name"] in M[name]["legs"]])
    w, l = R[R > 0], R[R <= 0]
    return dict(win=(R > 0).mean(), aw=w.mean(), al=l.mean(), E=R.mean(), PF=w.sum() / -l.sum(), per_month=len(R) / (12 * 12))


lines = ["# Portfolio Pareto (owner, 2026-11-12) — pre-registered in research/sweep5/PREREGISTRATION.md", "",
         "Exness Zero costs + swaps for the 13 survivors; RoboForex Prime costs + swaps for the three pivot-sweep v2 legs. Risk per",
         "trade for each cap set on 2011-22 only (95% of bootstrapped 36-fortnight lifecycles = the cap); then kept for 2023-25 and",
         "Jan-Oct 2026. Integrity = share of calendar years 2011-2025 positive. Heat = average open risk. R figures are weighted R.", "",
         "## All mixes at the 3.6% envelope", "",
         "| Mix | integrity | two-week Sharpe 2011-22 / 2023-25 / 2026 | % a year 2011-22 / 2023-25 / Jan-Oct 2026 | worst drawdown 2011-22 / 2023-25 | heat | cap needed for 80% / 120% a year |",
         "|---|---|---|---|---|---|---|"]
for k, v in M.items():
    c = lambda p: v[p]["cap 0.036"]
    lines.append(f"| {k} | {v['integrity']:.0%} | {v['2011-22']['fortnight_sharpe']} / {v['2023-25']['fortnight_sharpe']} / {v['Jan-Oct 2026']['fortnight_sharpe']} | "
                 f"{c('2011-22')['pct_a_year']} / {c('2023-25')['pct_a_year']} / {c('Jan-Oct 2026')['pct_a_year']} (10 months) | "
                 f"{c('2011-22')['max_dd_pct']}% / {c('2023-25')['max_dd_pct']}% | {v['heat_avg_pct_at_3.6']}% | {v['cap_needed_for_80pct_a_year']:.0f}% / {v['cap_needed_for_120pct_a_year']:.0f}% |")
for tag, name, why in (("A. Max timelessness", o["A"], "rule: highest integrity, then the lowest 2011-22 drawdown"),
                       ("B. Balanced", o["B"], "rule: best two-week Sharpe on 2023-Oct 2026 among mixes with integrity >= 90%"),
                       ("C. Max return inside the walls", o["C"], "rule: highest % a year at 3.6% (2011-22) with integrity >= 90%")):
    v = M[name]; t = mix_trades(name)
    lines += ["", f"## {tag}: {name}", f"Chosen by the {why}.", "",
              f"Mix: {len(v['legs'])} legs, win rate {t['win']:.0%}, average win {t['aw']:.2f}R / loss {t['al']:.2f}R (weighted), expectancy "
              f"{t['E']:+.3f}R a trade, profit factor {t['PF']:.2f}, {t['per_month']:.0f} trades a month; integrity {v['integrity']:.0%}; heat "
              f"{v['heat_avg_pct_at_3.6']}% average open risk.", "",
              "| Cap (envelope) | base risk a trade | % per two weeks 2011-22 / 2023-25 / 2026 | % a year 2011-22 / 2023-25 / Jan-Oct 2026 | worst drawdown 2011-22 |",
              "|---|---|---|---|---|"]
    for cap in ("0.036", "0.08", "0.15", "0.25"):
        c = lambda p: v[p][f"cap {cap}"]
        lines.append(f"| {float(cap) * 100:g}% | {v['risk_per_trade_pct'][cap]}% x leg weight | {c('2011-22')['pct_per_fortnight']} / {c('2023-25')['pct_per_fortnight']} / "
                     f"{c('Jan-Oct 2026')['pct_per_fortnight']} | {c('2011-22')['pct_a_year']} / {c('2023-25')['pct_a_year']} / {c('Jan-Oct 2026')['pct_a_year']} | {c('2011-22')['max_dd_pct']}% |")
    lines += ["", "| Magic | Leg | Pair | Timeframe | weight | avg risk at 3.6% | win | avg win / loss R | expectancy R | PF | trades/month | 2023-25 expectancy (n) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for g in v["legs_detail"]:
        a, b = g["2011-22"], g["2023-25"]
        lines.append(f"| {g['magic']} | {g['name']} | {g['market']} | {g['timeframe']} | {g['weight']} | {g['avg_risk_pct_at_3p6']}% | {a['win']:.0%} | "
                     f"{a['avg_win_R']} / {a['avg_loss_R']} | {a['expectancy_R']:+.3f} | {a['PF']} | {a['per_month']} | {b.get('expectancy_R')} ({b.get('n')}) |")
lines += ["", "## Treatment common to A, B and C",
          "- Multiplier: none. Fixed fractional risk (base risk x leg weight, on current equity). No martingale, no ladder that",
          "  raises risk after wins or losses (P8, P24-P26). The envelope guard (pre-trade check: skip a trade if a full stop-out would",
          "  breach the cap from the lifecycle high-water mark) is what holds the envelope (P24).",
          "- Harvest: at each two-week close, pay out profit above the high-water mark minus a buffer of one envelope (3.6%); nothing",
          "  is paid in a losing fortnight (about 40-45% of fortnights).",
          "- 80-120% a year inside 3.6% is not possible with these edges: return is linear in the cap, and 80% a year needs a 44-61%",
          "  drawdown envelope (120%: 66-92%), where losing streaks and live edge decay (P11: 30-50% weaker) make ruin likely. The",
          "  maximum inside 3.6% is about 5-6.5% a year in backtest; about 1% in Jan-Oct 2026."]
open(os.path.join(ROOT, "research", "results", "sweep5", "PARETO.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines[:20]))
