"""Export the data behind the portfolio report page (Data artifact) as CSV files: research/results/portfolio/report/*.csv.
Every number the page shows comes from one of these files."""
import os, sys, json, glob, datetime as dt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
import engine as EN   # noqa: E402

R = os.path.join(ROOT, "results"); OUT = os.path.join(R, "portfolio", "report"); os.makedirs(OUT, exist_ok=True)
PF = json.load(open(os.path.join(R, "portfolio", "portfolio.json"))); EX = json.load(open(os.path.join(R, "portfolio", "extras.json")))
P1 = json.load(open(os.path.join(R, "sweep6", "phase1.json"))); P2 = json.load(open(os.path.join(R, "sweep6", "phase2.json")))
P3 = json.load(open(os.path.join(R, "sweep6", "phase3.json"))); TK = json.load(open(os.path.join(R, "sweep6", "tickcheck.json")))["pooled"]
PER = {"2011-2022 (in-sample)": "insample", "2023-2025 (seen)": "seen", "Jan-Oct 2026 (out-of-sample)": "oos", "2011-Oct 2026 (all)": "all"}
PROF = {"base": "base", "swap-free": "swapfree", "stress": "stress", "no costs": "nocosts"}
ENV = {"3.6%": "3.6", "8%": "8"}

rows = []
for key, v in PF["profiles"].items():
    env, prof = key.split(" | ")
    for pn, s in v.items():
        rows.append(dict(envelope=ENV[env], profile=PROF[prof], period=PER[pn], **{k: s[k] for k in ("cagr_pct", "total_pct", "sharpe", "sortino",
                         "max_dd_pct", "calmar", "longest_dd_days", "pos_months_pct", "pos_fortnights_pct", "mean_fortnight_pct", "worst_fortnight_pct", "worst_month_pct", "vol_pct")}))
pd.DataFrame(rows).to_csv(os.path.join(OUT, "kpis.csv"), index=False)

rows = []
for env, d in PF["equity_weekly"].items():
    for date, (eq, dd) in d.items():
        rows.append(dict(date=date, envelope=ENV[env], equity=eq, drawdown_pct=dd))
pd.DataFrame(rows).to_csv(os.path.join(OUT, "equity.csv"), index=False)

per_of = lambda y: "oos" if y >= 2026 else "seen" if y >= 2023 else "insample"
pd.DataFrame([dict(year=int(y), period=per_of(int(y)), ret_36=PF["yearly"]["3.6%"][y], ret_8=PF["yearly"]["8%"][y]) for y in PF["yearly"]["3.6%"]]).to_csv(os.path.join(OUT, "yearly.csv"), index=False)
pd.DataFrame([dict(month=m, year=int(m[:4]), mon=int(m[5:]), ret_36=v, ret_8=PF["monthly"]["8%"][m]) for m, v in PF["monthly"]["3.6%"].items()]).to_csv(os.path.join(OUT, "monthly.csv"), index=False)

legs = []
for leg, v in PF["legs"].items():
    legs.append(dict(leg=leg, market=v["market"], timeframe=v["timeframe"], weight=v["weight"], trades=v["trades_2011_22"], per_month=v["per_month"],
                     win_pct=round(v["win"] * 100, 1), avg_win_R=v["avg_win_R"], avg_loss_R=v["avg_loss_R"], expectancy_R=v["expectancy_R"], pf=v["PF"],
                     gross_R=v["gross_R"], cost_R=v["cost_R"], swap_R=v["swap_R"], hold_h=v["median_hold_h"], later_R=v["later_expectancy_R"],
                     later_trades=v["later_trades"], contribution_R=EX["examples"]["contribution_R"][leg],
                     risk_pct_36=round(PF["risk"]["3.6%"] * v["weight"] * 100, 3)))
pd.DataFrame(legs).sort_values("contribution_R", ascending=False).to_csv(os.path.join(OUT, "legs.csv"), index=False)

pd.DataFrame([dict(leg_a=a, leg_b=b, corr=c) for a, row in PF["correlation"].items() for b, c in row.items()]).to_csv(os.path.join(OUT, "correlation.csv"), index=False)

rows = []
for hz, v in PF["monte_carlo_3.6"].items():
    h = "year" if hz.startswith("one") else "lifecycle"
    rows.append(dict(horizon=h, ret_p5=v["return_pct"]["0.05"], ret_p25=v["return_pct"]["0.25"], ret_p50=v["return_pct"]["0.5"], ret_p75=v["return_pct"]["0.75"],
                     ret_p95=v["return_pct"]["0.95"], dd_p50=v["max_dd_pct"]["0.5"], dd_p95=v["max_dd_pct"]["0.95"], dd_p99=v["max_dd_pct"]["0.99"],
                     p_loss_pct=round(v["p_loss"] * 100, 2), p_dd_36_pct=round(v["p_dd_over_3_6"] * 100, 2), p_dd_8_pct=round(v["p_dd_over_8"] * 100, 2)))
pd.DataFrame(rows).to_csv(os.path.join(OUT, "montecarlo.csv"), index=False)

rows = []
for env, a in EX["account"].items():
    for leg, v in a["legs"].items():
        rows.append(dict(envelope=ENV[env], leg=leg, market=v["market"], usd_per_001_lot=v["usd_per_001_lot_p75"], risk_pct=v["risk_pct"],
                         min_account=v["min_account_usd"], min_account_cent=v["min_account_cent_usd"]))
pd.DataFrame(rows).to_csv(os.path.join(OUT, "account.csv"), index=False)
rows = []
for env, a in EX["payouts"].items():
    for amt, per in a["account_for_usd_per_fortnight"].items():
        for pn, acc in per.items():
            rows.append(dict(envelope=ENV[env], payout=int(amt), period=PER[{"2011-2022 (in-sample)": "2011-2022 (in-sample)", "2023-2025 (seen)": "2023-2025 (seen)", "Jan-Oct 2026 (out-of-sample)": "Jan-Oct 2026 (out-of-sample)"}[pn]],
                             fortnight_pct=a["mean_fortnight_pct"][pn], account=acc))
pd.DataFrame(rows).to_csv(os.path.join(OUT, "payouts.csv"), index=False)

L, C, V = (P1["periods"][k] for k in ("LEARN 2011-15", "CONFIRM 2016-19", "VALIDATE 2020-22"))
order = ["1R", "2R", "3R", "5R", "7R", "10R", "15R", "20R", "5R-BE75", "10R-BE75", "TP1", "TP2", "TP2-BE75", "P60"]
rows = []
for nm in order:
    T_ = float(nm.split("R")[0]) if nm[0].isdigit() and "BE" not in nm else (float(nm.split("R")[0]) if nm[0].isdigit() else None)
    rows.append(dict(structure=nm, wins_per_10=L[nm]["wins_per_10"], chance_per_10=round(10 / (1 + T_), 2) if T_ else None, avg_win_R=L[nm]["avg_win"],
                     E_learn=L[nm]["E"], E_confirm=C[nm]["E"], E_validate=V[nm]["E"], R_per_10=L[nm]["R_per_10"], losing_streak=L[nm]["longest_losing_streak"]))
pd.DataFrame(rows).to_csv(os.path.join(OUT, "study_payout.csv"), index=False)
pd.DataFrame([dict(structure=k, win_m1_pct=round(v["win_m1"] * 100, 1), win_tick_pct=round(v["win_tick"] * 100, 1), n=v["n"]) for k, v in TK.items()]).to_csv(os.path.join(OUT, "study_tick.csv"), index=False)

pd.DataFrame([dict(tf=tf, trades=P3["pooled"][f"{tf} | zero | 2011-19"]["n"], zero_dev=P3["pooled"][f"{tf} | zero | 2011-19"]["E"], zero_val=P3["pooled"][f"{tf} | zero | 2020-22"]["E"],
                    cost_dev=P3["pooled"][f"{tf} | cost | 2011-19"]["E"], cost_val=P3["pooled"][f"{tf} | cost | 2020-22"]["E"],
                    positive_cells=P3["pooled"][f"{tf} | cost | 2011-19"]["positive_cells"]) for tf in ("M1", "M5", "M15", "M30", "H1", "H4")]).to_csv(os.path.join(OUT, "study_timeframes.csv"), index=False)

FN = {"vol_regime": "Volatility regime", "range_atr": "Range size (ATR)", "risk_atr": "Stop size (ATR)", "depth_R": "Sweep depth (R)", "room2": "Room to TP2 (R)",
      "mom60": "Momentum, last hour", "room1": "Room to TP1 (R)", "fill_delay": "Minutes to fill", "body4": "Candle 4 body", "depth_atr": "Sweep depth (ATR)",
      "daypos": "Place in the day's range", "pullback_atr": "Pull-back from the sweep", "c4pos": "Candle 4 close in range", "mom1440": "Momentum, last day",
      "ratio2": "Candle 2 / candle 1 size", "body2": "Candle 2 body", "ratio4": "Candle 4 / candle 3 size", "pivot_age": "Pivot age"}
pd.DataFrame([dict(feature=FN[f], smd_learn=v["LEARN"]["smd"], smd_confirm=v["CONFIRM"]["smd"], ks_learn=v["LEARN"]["ks"]) for f, v in P2["winners_vs_losers"].items()]).sort_values("smd_learn", key=lambda s: -s.abs()).to_csv(os.path.join(OUT, "study_features.csv"), index=False)

rows = []
for q, src in (("Which candle swept the pivot", P2["single"]["sweeping candle"]), ("Smaller body of candles 2 and 4", P2["single"]["smaller body of candles 2 and 4"]),
               ("Stop versus the sweep extreme", P2["single"]["stop vs the sweep extreme"]), ("Sweep depth, FX pairs (pips)", P2["owner_tables"]["sweep depth (FX pairs, pips)"]),
               ("Hour candle 4 closes (UTC)", P2["single"]["hour (UTC, candle 4 close)"])):
    for b, v in src.items():
        rows.append(dict(question=q, condition=b, trades_learn=v["LEARN"]["n"], E_learn=v["LEARN"]["E"], E_confirm=v["CONFIRM"]["E"], E_validate=v["VALIDATE"]["E"],
                         verdict="loses less" if v["IMPROVE"] else "loses more" if v["WORSE"] else "edge" if v["EDGE"] else "no consistent effect"))
pd.DataFrame(rows).to_csv(os.path.join(OUT, "study_questions.csv"), index=False)
la = P2["loser_anatomy"]
cats = [("Never reached +0.3R", "immediate failure (best < 0.3R)"), ("Reached +0.3 to +1R, then stopped", "middle (0.3-1R)"), ("Reached +1R or more, then stopped", "reversal (reached >= 1R first)")]
rows = [dict(category=a, learn=round(la["LEARN"]["shares"][b] * 100, 1), confirm=round(la["CONFIRM"]["shares"][b] * 100, 1), validate=round(la["VALIDATE"]["shares"][b] * 100, 1)) for a, b in cats]
for a, b in (("Wick stop (saved by a slightly wider stop)", "wick_stop"), ("Ran 3R or more past the stop first", "breakout_3R_past_stop"), ("Reached TP1 later that day", "reached_TP1_within_a_day")):
    rows.append(dict(category=a, learn=round(la["LEARN"][b] * 100, 1), confirm=round(la["CONFIRM"][b] * 100, 1), validate=round(la["VALIDATE"][b] * 100, 1)))
pd.DataFrame(rows).to_csv(os.path.join(OUT, "study_losers.csv"), index=False)

# examples: candles around each rule-chosen trade, on the leg's own timeframe
Tr = pd.read_csv(os.path.join(R, "portfolio", "trades.csv"))
TFMIN = {"EUR_EuroHours_short_TueThu": 15, "tokyo_fix_gotobi_v1": 5, "eurusd_close_beyond_reversal_v1": 240, "XAU_S1_reversion_H1M30M20": 30}
meta, candles = [], []
for i, ch in enumerate(EX["examples"]["charts"]):
    if "error" in ch:
        continue
    leg = ch["leg"]; t0 = int(dt.datetime.strptime(ch["t_in"], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc).timestamp())
    r = Tr[(Tr.leg == leg) & (Tr.t_in == t0)].iloc[0]
    tf = TFMIN[leg]; span = max(int(r.t_out - r.t_in), tf * 600)
    a, b = int(r.t_in) - max(span, tf * 60 * 40), int(r.t_out) + max(span // 3, tf * 600)
    ts, o, h, l, c = EN.load_m1(r.sym, dt.datetime.utcfromtimestamp(a).year, dt.datetime.utcfromtimestamp(b).year)
    m = (ts >= a) & (ts <= b)
    bt, bo, bh, bl, bc, _ = EN.resample(ts[m], o[m], h[m], l[m], c[m], tf)
    i_in = int(np.searchsorted(ts, int(r.t_in))); i_out = int(np.searchsorted(ts, int(r.t_out)))
    entry = r.entry if np.isfinite(r.entry) else c[max(i_in - 1, 0)]
    ex_id = f"ex{i + 1}"
    meta.append(dict(example=ex_id, leg=leg, market=r.sym, kind=ch["kind"], side="buy" if r.side > 0 else "sell", tf_min=tf,
                     t_in=dt.datetime.utcfromtimestamp(int(r.t_in)).strftime("%Y-%m-%d %H:%M"), t_out=dt.datetime.utcfromtimestamp(int(r.t_out)).strftime("%Y-%m-%d %H:%M"),
                     entry=round(float(entry), 5), stop=round(float(entry - r.side * r.dist), 5), exit=round(float(c[min(i_out, len(c) - 1)]), 5), R=round(float(r.net), 2)))
    for k in range(len(bt)):
        candles.append(dict(example=ex_id, t=dt.datetime.utcfromtimestamp(int(bt[k])).strftime("%Y-%m-%d %H:%M"), o=round(float(bo[k]), 5), h=round(float(bh[k]), 5), l=round(float(bl[k]), 5), c=round(float(bc[k]), 5)))
pd.DataFrame(meta).to_csv(os.path.join(OUT, "examples.csv"), index=False)
pd.DataFrame(candles).to_csv(os.path.join(OUT, "candles.csv"), index=False)
for f in sorted(glob.glob(os.path.join(OUT, "*.csv"))):
    print(os.path.basename(f), os.path.getsize(f), sum(1 for _ in open(f)) - 1, "rows")

# ---- additions for the page: keys, plain names, chance with breakeven, headline facts, scanner steps and Monte Carlo
kp = pd.read_csv(os.path.join(OUT, "kpis.csv"), dtype={"envelope": str}); kp.insert(0, "key", kp.envelope.astype(str) + "-" + kp.profile + "-" + kp.period)
kp.to_csv(os.path.join(OUT, "kpis.csv"), index=False)
eq = pd.read_csv(os.path.join(OUT, "equity.csv"), dtype={"envelope": str}); eq["period"] = eq.date.str[:4].astype(int).map(per_of); eq.to_csv(os.path.join(OUT, "equity.csv"), index=False)
NAMES = {"EUR_EuroHours_short_TueThu": ("EURUSD Euro-hours short", "EUR hours"), "tokyo_fix_gotobi_v1": ("USDJPY Tokyo fix, gotobi days", "Tokyo fix"),
         "eurusd_close_beyond_reversal_v1": ("EURUSD close-beyond reversal", "EUR reversal"), "XAU_S1_reversion_H1M30M20": ("Gold dip reversion (S1)", "Gold dip"),
         "v2_EURGBP_H1": ("EURGBP pivot-sweep v2", "EURGBP v2"), "GBP_WeeklySweep_FollowThrough": ("GBPUSD weekly sweep follow-through", "GBP sweep"),
         "XAU_EMA20-50_H4": ("Gold EMA 20/50 trend", "Gold EMA"), "GBPJPY_Donchian20_H4_trail": ("GBPJPY Donchian 20 trend", "GJ Donchian"),
         "JPY_RSI2_D1_lo5": ("USDJPY RSI(2) dip", "JPY RSI2"), "JPY_S2_Donchian20_H4_long": ("USDJPY Donchian 20 long (S2)", "JPY Donchian"),
         "XAU_Donchian20_H4_turtle": ("Gold Donchian 20 trend", "Gold Donchian"), "v2_NAS100_H1": ("NAS100 pivot-sweep v2", "NAS v2"),
         "v2_GBPUSD_M15": ("GBPUSD pivot-sweep v2", "GBP v2")}
lg = pd.read_csv(os.path.join(OUT, "legs.csv")); lg.insert(1, "name", lg.leg.map(lambda x: NAMES[x][0])); lg.insert(2, "short", lg.leg.map(lambda x: NAMES[x][1]))
lg.to_csv(os.path.join(OUT, "legs.csv"), index=False)
sp = pd.read_csv(os.path.join(OUT, "study_payout.csv"))
def chance(nm):   # driftless random walk: P(target before stop) = 1/(1+T); with the stop moved to entry at 75% of the way: 0.75/(1+0.75T)
    if not nm[0].isdigit():
        return None
    T = float(nm.split("R")[0])
    return round(10 * (0.75 / (1 + 0.75 * T) if "BE75" in nm else 1 / (1 + T)), 2)
sp["chance_per_10"] = sp.structure.map(chance); sp.to_csv(os.path.join(OUT, "study_payout.csv"), index=False)
st = pd.read_csv(os.path.join(OUT, "study_timeframes.csv")); st = st.rename(columns={"positive_cells": "markets_positive_after_costs"}); st.to_csv(os.path.join(OUT, "study_timeframes.csv"), index=False)
acc = pd.read_csv(os.path.join(OUT, "account.csv"), dtype={"envelope": str})
H = [("legs", len(PF["legs"]), "legs in the mix"), ("avg_corr", PF["avg_pairwise_corr"], "average correlation between legs (daily P&L, 2011-22)"),
     ("risk_36", round(PF["risk"]["3.6%"] * 100, 3), "base risk a trade at the 3.6% envelope, % of equity"),
     ("risk_8", round(PF["risk"]["8%"] * 100, 3), "base risk a trade at the 8% envelope, % of equity"),
     ("trades_2011_22", int(lg.trades.sum()), "trades 2011-22, all legs"), ("trades_per_month", round(float(lg.per_month.sum()), 1), "trades a month, all legs"),
     ("min_acc_36", float(acc[acc.envelope == "3.6"].min_account.max()), "minimum standard account at 3.6%, USD"),
     ("min_acc_cent_36", float(acc[acc.envelope == "3.6"].min_account_cent.max()), "minimum cent account at 3.6%, USD"),
     ("min_acc_8", float(acc[acc.envelope == "8"].min_account.max()), "minimum standard account at 8%, USD"),
     ("min_acc_cent_8", float(acc[acc.envelope == "8"].min_account_cent.max()), "minimum cent account at 8%, USD"),
     ("study_setups", int(P1["periods"]["LEARN 2011-15"]["1R"]["n"] + P1["periods"]["CONFIRM 2016-19"]["1R"]["n"] + P1["periods"]["VALIDATE 2020-22"]["1R"]["n"]), "pattern study: filled setups 2011-22 (M1, 12 markets)"),
     ("study_tests", int(P2["tests"]["single_bins"] + P2["tests"]["pair_cells"]), "pattern study: condition tests (single conditions + pairs)"),
     ("study_tests_edge", int(sum(v["EDGE"] for g in P2["single"].values() for v in g.values()) + sum(v["EDGE"] for v in P2["pairs"].values())),
      "pattern study: tests with an edge in both LEARN and CONFIRM"),
     ("study_tests_lose_less", int(sum(v["IMPROVE"] for g in P2["single"].values() for v in g.values()) + sum(v["IMPROVE"] for v in P2["pairs"].values())),
      "pattern study: conditions that lose less in both LEARN and CONFIRM")]
THIS_REPORT = ("sweep6-prereg-9305332", "portfolio-report-2026-11-12")           # this study and this report are not "before this report"
LED = [e for e in (json.loads(x) for x in open(os.path.join(ROOT, "truth", "memory", "ledger.jsonl")) if x.strip()) if e.get("fingerprint") not in THIS_REPORT]
H += [("ideas_tested", len(LED), "ideas tested in the project before this report (research memory ledger)"),
      ("configs_tried", int(sum(int(e.get("configs") or e.get("configurations") or 0) for e in LED)), "configurations tested in the project before this report"),
      ("v2_cells", 1440, "pivot-sweep v2 cells the 3 v2 legs were picked from (research/results/sweep5)"),
      ("mc_paths", 10000, "Monte Carlo paths per horizon")]
pd.DataFrame(H, columns=["metric", "value", "meaning"]).to_csv(os.path.join(OUT, "headline.csv"), index=False)
sc = P2["scanner"]
rows = [dict(step=i + 1, condition=s["condition"].replace("hour (UTC, candle 4 close) = ", "candle 4 closes ").replace("weekday != Mon", "not Monday"),
             E_learn=s["LEARN_E"], E_confirm=s["CONFIRM_E"], E_validate=s["VALIDATE_E"], trades_learn=s["n"]["LEARN"]) for i, s in enumerate(sc["steps"])]
pd.DataFrame(rows).to_csv(os.path.join(OUT, "study_scanner.csv"), index=False)
pd.DataFrame([dict(cell=k, trades_per_year=v["trades_per_year"], p_losing_year_pct=round(v["p_losing_year"] * 100, 1), median_year_pct=v["median_year_pct"],
                    p5_year_pct=v["p5_year_pct"], median_maxdd_pct=v["median_maxdd_pct"], survives="no") for k, v in P3["mc"].items()]).to_csv(os.path.join(OUT, "study_mc.csv"), index=False)
print(open(os.path.join(OUT, "headline.csv")).read()); print(open(os.path.join(OUT, "study_scanner.csv")).read()); print(open(os.path.join(OUT, "study_mc.csv")).read())
print(sp.to_string())
# plain ids for tables whose names hold commas (row keys on the page)
for fn, prefix in (("study_questions.csv", "q"), ("study_losers.csv", "l"), ("study_features.csv", "f")):
    d = pd.read_csv(os.path.join(OUT, fn)); d.insert(0, "id", [f"{prefix}{i + 1}" for i in range(len(d))]); d.to_csv(os.path.join(OUT, fn), index=False)
