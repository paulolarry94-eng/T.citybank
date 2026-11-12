"""Owner-facing tables for Phase 2 and Phases 3-4 of the deep M1 study -> research/results/sweep6/PHASE2.md, PHASE3.md"""
import os, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
R = os.path.join(ROOT, "research", "results", "sweep6")
p2 = json.load(open(os.path.join(R, "phase2.json"))); p3 = json.load(open(os.path.join(R, "phase3.json")))
rc = json.load(open(os.path.join(R, "phase2_rechoice.json")))
f3 = lambda x: "-" if x is None else f"{x:+.3f}"


def table(title, tab, other=None, note=""):
    out = [f"### {title}", note, "", "| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |",
           "|---|---|---|---|---|---|"]
    for b, v in tab.items():
        L, C, V = v["LEARN"], v["CONFIRM"], v["VALIDATE"]
        o = " / ".join(f3(other["3R"][b][p]) for p in ("LEARN", "CONFIRM", "VALIDATE")) if other and b in other["3R"] else "-"
        flag = "loses less (both periods)" if v["IMPROVE"] else "loses more (both periods)" if v["WORSE"] else "edge" if v["EDGE"] else "no"
        out.append(f"| {b} | {L['n']:,} / {C['n']:,} | {f3(L['E'])} / {f3(C['E'])} / {f3(V['E'])} | {L['win']:.1%} | {o} | {flag} |")
    return out + [""]


lines = ["# Phase 2: what separates winners from losers (frictionless, M1, 12 markets)", "",
         f"Superset: every four-candle setup (bodies >= 40%, with or without a sweep): {p2['n']['LEARN']:,} trades in 2011-15 (LEARN),",
         f"{p2['n']['CONFIRM']:,} in 2016-19 (CONFIRM), {p2['n']['VALIDATE']:,} in 2020-22 (VALIDATE), each simulated alone with no costs.",
         f"Outcome: R a trade with the Phase 1 payout ({p2['structure']}). Overall: {p2['overall']['LEARN']['E']:+.3f} / {p2['overall']['CONFIRM']['E']:+.3f} / "
         f"{p2['overall']['VALIDATE']['E']:+.3f}R a trade. A condition counts only if it holds in 2011-15 (t >= 3) AND 2016-19 (t >= 2).",
         f"Tests: {p2['tests']['single_bins']} single conditions + {p2['tests']['pair_cells']:,} pairs; expected false passes by luck: {p2['tests']['expected_false_passes']}.", "",
         "## Outcome", "- **No condition and no pair makes money in both 2011-15 and 2016-19** (0 of 1,142).",
         "- **Winners and losers look the same.** For every feature the difference between winners' and losers' averages is under",
         "  0.1 standard deviations (Kolmogorov-Smirnov distance under 0.04). There is no trait the winners have and the losers lack.",
         "- A few conditions consistently LOSE LESS: a sweep present (vs none), 12-16 UTC (vs 16-21 UTC), not Monday, no sweep on the",
         "  target side, candle bodies under 100%. None turns positive.", "",
         "## Your questions", ""]
O = p2["single_other_structures"]
lines += table("Which candle swept the pivot (the latest sweep before candle 4 closed)", p2["single"]["sweeping candle"], O["sweeping candle"],
               "Candles since the sweep = this category (candle 4 = 0, candle 1 = 3, 'before 1' = 4, ...).")
lines += table("Sweep depth beyond the pivot, FX pairs, in pips", p2["owner_tables"]["sweep depth (FX pairs, pips)"])
lines += table("Sweep depth in ATR units (all markets)", p2["single"]["depth_atr"], O["depth_atr"])
lines += table("Smaller body of candles 2 and 4 (your 40% / 50% / 60% question)", p2["single"]["smaller body of candles 2 and 4"], O["smaller body of candles 2 and 4"])
lines += table("Stop versus the sweep extreme ('a range from the sweep')", p2["single"]["stop vs the sweep extreme"], O["stop vs the sweep extreme"])
lines += table("Pull-back from the sweep extreme to candle 4's close (ATR units)", p2["single"]["pullback_atr"], O["pullback_atr"])
lines += table("Sweep candle closed back inside the pivot", p2["single"]["sweep candle closed back inside"], O["sweep candle closed back inside"])
lines += table("Pivots swept", p2["single"]["pivots swept"], O["pivots swept"])
lines += table("Engulfing type", p2["single"]["engulfing"], O["engulfing"])
lines += table("Hour candle 4 closes (UTC)", p2["single"]["hour (UTC, candle 4 close)"], O["hour (UTC, candle 4 close)"])
lines += table("Weekday", p2["single"]["weekday"], O["weekday"])
lines += table("Minutes until the limit filled", p2["single"]["fill_delay"], O["fill_delay"])
lines += ["## Winners vs losers (2011-15; 2016-19 in brackets)", "", "| Feature | winners' average | losers' average | standardized difference | KS distance |", "|---|---|---|---|---|"]
for f, v in sorted(p2["winners_vs_losers"].items(), key=lambda kv: -abs(kv[1]["LEARN"]["smd"] or 0)):
    L, C = v["LEARN"], v["CONFIRM"]
    lines.append(f"| {f} | {L['winners_mean']:.3g} | {L['losers_mean']:.3g} | {L['smd']:+.3f} ({C['smd']:+.3f}) | {L['ks']:.3f} ({C['ks']:.3f}) |")
la = p2["loser_anatomy"]
lines += ["", "## Why the losers lose (stopped trades, 20R payout)", "", "| | 2011-15 | 2016-19 | 2020-22 |", "|---|---|---|---|"]
for k in ("immediate failure (best < 0.3R)", "middle (0.3-1R)", "reversal (reached >= 1R first)"):
    lines.append(f"| {k} | {la['LEARN']['shares'][k]:.0%} | {la['CONFIRM']['shares'][k]:.0%} | {la['VALIDATE']['shares'][k]:.0%} |")
for k, lab in (("wick_stop", "wick stop (stop exceeded by < 0.2R, then +1R within an hour)"), ("breakout_3R_past_stop", "breakout (ran >= 3R past the stop first)"),
               ("reached_TP1_within_a_day", "reached TP1 later the same day"), ("reached_TP2_within_a_day", "reached TP2 later the same day")):
    lines.append(f"| {lab} | {la['LEARN'][k]:.0%} | {la['CONFIRM'][k]:.0%} | {la['VALIDATE'][k]:.0%} |")
lines += ["", "Most losers are not stop hunts: half never move 0.3R in favour, and two thirds keep going 3R or more past the stop (the",
          "sweep was the start of a real move). Only 5-6% are wick stops that a slightly bigger stop would have saved. That most later",
          "reach TP1 anyway (after running far past the stop) is what a random walk does, not a sign the stop is too tight.", "",
          "## The scanner rule built from these results (greedy, 2011-15, checked on 2016-19)", ""]
for s in p2["scanner"]["steps"]:
    lines.append(f"- add `{s['condition']}`: 2011-15 {s['LEARN_E']:+.3f}R (+{s['gain']:.3f}, t {s['t']}), 2016-19 {s['CONFIRM_E']:+.3f}R, 2020-22 {s['VALIDATE_E']:+.3f}R")
lines += [f"- payout re-chosen on 2011-15: {rc['scanner_rechoice'][0]} ({rc['scanner_rechoice'][1]['LEARN']:+.3f} / {rc['scanner_rechoice'][1]['CONFIRM']:+.3f} / "
          f"{rc['scanner_rechoice'][1]['VALIDATE']:+.3f}R). Keeping the sweep requirement too: {rc['scanner_plus_sweep_rechoice'][1]['LEARN']:+.3f} / "
          f"{rc['scanner_plus_sweep_rechoice'][1]['CONFIRM']:+.3f} / {rc['scanner_plus_sweep_rechoice'][1]['VALIDATE']:+.3f}R (information only).",
          "", "Positive only in the years it was chosen on: the signature of fitting noise."]
open(os.path.join(R, "PHASE2.md"), "w").write("\n".join(lines) + "\n")

L3 = ["# Phases 3-4: the scanner on every timeframe and market, without and with costs; Monte Carlo", "",
      "Strategy `sweep6_scanner_v1` (Truth Lab: 0 of 6 pass, 0% positive in development). One trade at a time per market and",
      "timeframe; trades entered before 2023. Costs: RoboForex Prime + swaps (lab standard for markets without a Prime price).", "",
      "## 12 markets pooled", "", "| Timeframe | trades 2011-19 | no costs: R a trade 2011-19 / 2020-22 | with costs: R a trade 2011-19 / 2020-22 | cells positive with costs 2011-19 |", "|---|---|---|---|---|"]
for tf in ("M1", "M5", "M15", "M30", "H1", "H4"):
    z1, z2 = p3["pooled"][f"{tf} | zero | 2011-19"], p3["pooled"][f"{tf} | zero | 2020-22"]
    c1, c2 = p3["pooled"][f"{tf} | cost | 2011-19"], p3["pooled"][f"{tf} | cost | 2020-22"]
    L3.append(f"| {tf} | {z1['n']:,} | {z1['E']:+.3f} / {z2['E']:+.3f} | {c1['E']:+.3f} / {c2['E']:+.3f} | {c1['positive_cells']} of 12 |")
L3 += ["", "## Every market x timeframe (R a trade 2011-19, no costs -> with costs; 2020-22 with costs)", "",
       "| Market | " + " | ".join(("M1", "M5", "M15", "M30", "H1", "H4")) + " |", "|---|" + "---|" * 6]
for m in ("XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"):
    cells = []
    for tf in ("M1", "M5", "M15", "M30", "H1", "H4"):
        v = p3["cells"][f"{m} {tf}"]
        cells.append(f"{f3(v['zero']['2011-19'].get('E'))} -> {f3(v['cost']['2011-19'].get('E'))}; {f3(v['cost']['2020-22'].get('E'))} ({v['cost']['2011-19'].get('n', 0)})")
    L3.append(f"| {m} | " + " | ".join(cells) + " |")
L3 += ["", f"## Candidates (with costs positive in each of 2011-14, 2015-18, 2019-22) and Monte Carlo", "",
       "| Cell | trades a year | chance of a losing year | median year | 5th percentile year | median worst drawdown in a year | survives |", "|---|---|---|---|---|---|---|"]
for k, v in p3["mc"].items():
    L3.append(f"| {k} | {v['trades_per_year']} | {v['p_losing_year']:.0%} | {v['median_year_pct']:+.1f}% | {v['p5_year_pct']:+.1f}% | {v['median_maxdd_pct']:.1f}% | {'yes' if k in p3['survivors'] else 'no'} |")
L3 += ["", f"3 of 72 cells pass the era test (about what luck gives: each era is positive for 7-25% of cells); none survives the",
       "Monte Carlo rule (losing year <= 20%, median worst drawdown <= 10%). No cell reaches the logged 2023-26 look, and no new leg",
       "joins the portfolio."]
open(os.path.join(R, "PHASE3.md"), "w").write("\n".join(L3) + "\n")
print("ok")
