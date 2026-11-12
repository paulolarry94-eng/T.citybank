"""Owner-facing Phase 1 tables: research/results/sweep6/phase1.json + tickcheck.json -> PHASE1.md"""
import os, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
R = os.path.join(ROOT, "research", "results", "sweep6")
p1 = json.load(open(os.path.join(R, "phase1.json"))); tk = json.load(open(os.path.join(R, "tickcheck.json")))["pooled"]
L, C, V = (p1["periods"][k] for k in ("LEARN 2011-15", "CONFIRM 2016-19", "VALIDATE 2020-22"))
order = ["1R", "2R", "3R", "4R", "5R", "6R", "7R", "8R", "9R", "10R", "15R", "20R", "3R-BE75", "4R-BE75", "5R-BE75", "6R-BE75",
         "7R-BE75", "8R-BE75", "9R-BE75", "10R-BE75", "TP1", "TP2", "TP2-BE75", "P60"]
lines = ["# Phase 1: payout structure, frictionless, M1, 12 markets (pre-registered: research/sweep6/PREREGISTRATION.md)", "",
         f"Base = the owner's current rule (bodies >= 50%, a sweep from 6 candles before candle 1 through candle 2), every setup",
         f"simulated alone with no spread, commission, slippage or swaps. Same trades for every structure: {L['1R']['n']:,} (LEARN),",
         f"{C['1R']['n']:,} (CONFIRM), {V['1R']['n']:,} (VALIDATE). TP2 sits a median {L['_tp2_distance_R']['0.5']}R from the entry "
         f"(10-90%: {L['_tp2_distance_R']['0.1']}-{L['_tp2_distance_R']['0.9']}R).", "",
         "| Structure | wins per 10 trades | chance level per 10 (1/(1+T)) | avg win | R a trade LEARN / CONFIRM / VALIDATE | R per 10 trades (LEARN) | 10-trade blocks positive | longest losing streak |",
         "|---|---|---|---|---|---|---|---|"]
for nm in order:
    a, b, c = L[nm], C[nm], V[nm]
    T = float(nm.split("R")[0]) if nm[0].isdigit() else None
    chance = f"{10 / (1 + T):.2f}" if T else "-"
    lines.append(f"| {nm} | {a['wins_per_10']:.2f} | {chance} | {a['avg_win']:+.2f}R | {a['E']:+.3f} / {b['E']:+.3f} / {c['E']:+.3f} | "
                 f"{a['R_per_10']:+.2f}R | {a['block_pos']:.0%} | {a['longest_losing_streak']} |")
lines += ["", f"Rule choice (highest LEARN R a trade): **{p1['choice']}** ({L[p1['choice']]['E']:+.3f}R); every structure is below zero",
          "before costs in LEARN and CONFIRM, and the best ones are statistically tied (differences < 0.01R, t < 1).", "",
          "## One-minute resolution (tick check, 9 months of Exness ticks in 2021-22, 585 trades)", "",
          "| Structure | win rate M1 bars | win rate ticks | R a trade M1 (pessimistic) | M1 (optimistic) | ticks |", "|---|---|---|---|---|---|"]
for nm in ["1R", "2R", "3R", "5R", "10R", "20R", "TP1", "TP2", "TP2-BE75", "P60"]:
    t_ = tk[nm]
    lines.append(f"| {nm} | {t_['win_m1']:.1%} | {t_['win_tick']:.1%} | {t_['m1_pessimistic']:+.3f} | {t_['m1_optimistic']:+.3f} | {t_['tick']:+.3f} |")
lines += ["", "Win rates on M1 bars equal the tick truth from 5R up and are 0.3-1.7 points low at 1-3R; the remaining R gap comes",
          "from tick-level fill prices (a limit filled on a tick jump gets a better price than the level), not from ordering."]
open(os.path.join(R, "PHASE1.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
