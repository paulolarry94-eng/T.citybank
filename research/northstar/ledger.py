"""North Star Part 1: master experiment ledger.

Reads every saved result artifact of this research project and writes one row per tested
configuration with a common schema. Nothing is re-estimated from memory: a field that the original
study did not save is written as empty and listed in the missing-artifact report.

Split schemes used by the earlier studies (recorded per row):
  IS/OOS-2019  in-sample 2011-2018, out-of-sample 2019-2025 (labs, liquidity, crosses, MSnR, funnel)
  DEV/VAL/OOS  development 2011-2019, validation 2020-2022, final 2023-2025 (ORB, four, FVG, North Star)
"""
import os, json, gzip, csv, glob
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
OUT = os.path.join(RES, "northstar"); os.makedirs(OUT, exist_ok=True)
DEV, VAL = range(2011, 2020), range(2020, 2023)
COST = "all-in round trip: XAU $0.45, EUR 1.5p, GBP 1.8p, JPY 1.2p; no financing"
COLS = ["study", "config_id", "instrument", "timeframe", "family", "params", "entry_rule", "exit_rule", "cost_model",
        "split", "n_total", "E_total", "t_total", "pf_total", "win", "n_insample", "E_insample", "t_insample", "pf_insample",
        "n_val", "E_val", "t_val", "n_oos", "E_oos", "t_oos", "pf_oos", "max_dd", "walk_forward", "status", "reason", "source"]
MISSING = []


def per_year_stats(df, years, has_pf):
    n = sum(df[f"n_{y}"] for y in years); s = sum(df[f"s_{y}"] for y in years); ss = sum(df[f"ss_{y}"] for y in years)
    E = s / n.where(n > 0); var = (ss - n * E ** 2) / (n - 1).where(n > 1)
    t = E / np.sqrt(var / n)
    pf = None
    if has_pf:
        pos = sum(df[f"pos_{y}"] for y in years); neg = sum(df[f"neg_{y}"] for y in years)
        pf = pos / neg.where(neg > 0)
    return n, E, t, pf


def grid_rows(path, study, cfg_cols, family_col, split_note, has_pf, reason_fn, source):
    df = path if isinstance(path, pd.DataFrame) else pd.read_csv(path)
    nD, ED, tD, pfD = per_year_stats(df, DEV, has_pf)
    nV, EV, tV, pfV = per_year_stats(df, VAL, has_pf)
    yrs = [int(c[2:]) for c in df.columns if c.startswith("n_") and c[2:].isdigit()]
    nT, ET, tT, pfT = per_year_stats(df, [y for y in yrs if y <= 2022], has_pf)
    out = pd.DataFrame({
        "study": study, "config_id": df.get("id", pd.Series(range(len(df)))).astype(str),
        "instrument": df["sym"], "timeframe": df["tf"] if "tf" in df else df.get("session", ""),
        "family": df[family_col] if family_col in df else study,
        "params": df[cfg_cols].fillna("").astype(str).agg("|".join, axis=1), "entry_rule": "", "exit_rule": "", "cost_model": COST,
        "split": split_note, "n_total": nT, "E_total": ET, "t_total": tT, "pf_total": pfT if has_pf else np.nan, "win": np.nan,
        "n_insample": nD, "E_insample": ED, "t_insample": tD, "pf_insample": pfD if has_pf else np.nan,
        "n_val": nV, "E_val": EV, "t_val": tV, "n_oos": np.nan, "E_oos": np.nan, "t_oos": np.nan, "pf_oos": np.nan,
        "max_dd": np.nan, "walk_forward": "", "source": source})
    out["status"], out["reason"] = zip(*[reason_fn(r) for r in out.itertuples()])
    return out


def basic_reason(r, min_n=100):
    if not (r.n_insample >= min_n):
        return "rejected", "too few development trades"
    if not (r.E_insample > 0):
        return "rejected", "development expectancy <= 0"
    if not (r.t_insample >= 2.0):
        return "rejected", "development t < 2"
    if not (r.E_val > 0):
        return "rejected", "validation expectancy <= 0"
    return "not selected", "passed development and validation but not the study's top robust pick"


def judge_rows(d, study, source, split="IS/OOS-2019"):
    rows = []
    for k, v in d.items():
        if not isinstance(v, dict) or "E" not in v:
            continue
        parts = k.replace("|", "_").split("_")
        sym = next((p for p in parts if p in ("XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "EURJPY", "GBPJPY", "EURGBP")), "")
        tf = next((p for p in parts if p in ("M5", "M15", "M20", "M30", "H1", "H4", "D1") or p.startswith(("M15<", "H1<", "H4<", "M30<"))), "")
        gates = [g for g in ("G1", "G2", "G3", "G4", "G5") if g in v]
        if "pass" in v:
            if v["pass"]:
                st, rs = "passed study gates", ""
            else:
                names = {"G1": "in-sample E/Sharpe", "G2": "out-of-sample E", "G3": "t < 1.96", "G4": "not positive in every era", "G5": "no positive neighbour"}
                rs = "failed: " + ", ".join(names[g] for g in gates if not v[g])
                st = "rejected"
        else:
            st, rs = ("candidate" if v.get("E_is", -1) > 0 and v.get("E_oos", -1) > 0 else "rejected"), "study had no gate flags; status from IS/OOS sign"
        rows.append(dict(study=study, config_id=k, instrument=sym, timeframe=tf, family=k.split("_")[1] if "_" in k else "",
                         params=json.dumps(v.get("param", "")), entry_rule="", exit_rule="", cost_model=COST, split=split,
                         n_total=v.get("n"), E_total=v.get("E"), t_total=v.get("t"), pf_total=v.get("pf"), win=v.get("win"),
                         n_insample=v.get("n_is"), E_insample=v.get("E_is"), t_insample=np.nan, pf_insample=np.nan,
                         n_val=np.nan, E_val=np.nan, t_val=np.nan, n_oos=v.get("n_oos"), E_oos=v.get("E_oos"), t_oos=np.nan, pf_oos=np.nan,
                         max_dd=np.nan, walk_forward="", status=st, reason=rs, source=source))
    return pd.DataFrame(rows)


def main():
    parts = []
    # ---------------------------------------------------------------- ORB 50 grids (per-year aggregates)
    orb_cfg = ["sym", "session", "orb", "entry", "buf", "tol", "pb_k", "pb_atr", "disp", "stop", "stop_k", "tgt", "trail",
               "part_f", "be", "imp", "max_fails", "vol", "bias", "bias_kind", "bias_ema", "bias_z", "filt", "atr_p"]
    fin = json.load(open(os.path.join(RES, "orb_final.json")))
    finmap = {c["id"]: c for c in fin["configs"]}
    for st in ("E0", "E1", "E2", "E3", "E4", "E5", "E6", "AB"):
        p = os.path.join(RES, "orb_experiments", f"{st}.csv.gz")
        df = pd.read_csv(p)
        df["filt"] = df["filt"].fillna(""); df["bias_kind"] = df["bias_kind"].fillna("")
        df["tf"] = df["session"] + "_ORB" + df["orb"].astype(str)
        df["fam"] = "ORB-" + st
        g = grid_rows(df, f"ORB50 {st}", [c for c in orb_cfg if c in df.columns], "fam", "DEV/VAL/OOS (OOS masked)", True, basic_reason,
                      f"results/orb_experiments/{st}.csv.gz")
        for i, cid in enumerate(df["id"]):
            if cid in finmap:
                c = finmap[cid]["post"]["periods"]
                g.loc[i, ["n_oos", "E_oos", "t_oos", "pf_oos", "max_dd"]] = [c["oos 2023-25"]["n"], c["oos 2023-25"]["E"], c["oos 2023-25"]["t"],
                                                                            c["oos 2023-25"]["pf"], c["all 2011-25"]["max_dd"]]
                g.loc[i, ["status", "reason"]] = ["rejected", f"ORB finalist {finmap[cid]['key']}: final 2023-25 expectancy negative"]
        parts.append(g)
    wf = json.load(open(os.path.join(RES, "orb_walkforward.json")))
    parts.append(pd.DataFrame([dict(study="ORB50 walk-forward", config_id=k, instrument="all", timeframe="all", family="ORB",
                                    params="3y train -> 1y test, 2014-2022", cost_model=COST, split="walk-forward",
                                    n_total=v["always"]["n"], E_total=v["always"]["E"], t_total=v["always"]["t"],
                                    walk_forward=f"E {v['always']['E']:+.3f} t {v['always']['t']:+.2f}; gated E {v['gated']['E']:+.3f}",
                                    status="rejected", reason="walk-forward negative", source="results/orb_walkforward.json") for k, v in wf.items()]))
    # ---------------------------------------------------------------- four strategies grid
    p4 = os.path.join(RES, "four", "grid.csv.gz")
    g4 = grid_rows(p4, "Four strategies grid", ["sym", "tf", "fam", "var", "stop", "tgt", "be", "trail"], "fam",
                   "DEV/VAL/OOS (OOS masked)", False, basic_reason, "results/four/grid.csv.gz")
    lr = json.load(open(os.path.join(RES, "four", "locked_rules.json")))
    ff = json.load(open(os.path.join(RES, "four", "final.json")))
    rows = []
    for fam, ru in lr.items():
        for sym in ("XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "ALL"):
            v = ff[f"{fam}|{sym}"]
            rows.append(dict(study="Four strategies locked rule", config_id=f"{fam}_{sym}", instrument=sym, timeframe=ru["tf"], family=fam,
                             params=json.dumps(ru), cost_model=COST, split="DEV/VAL/OOS", n_insample=v["dev"]["n"], E_insample=v["dev"]["E"],
                             t_insample=v["dev"]["t"], n_val=v["val"]["n"], E_val=v["val"]["E"], t_val=v["val"]["t"], n_oos=v["oos"]["n"],
                             E_oos=v["oos"]["E"], t_oos=v["oos"]["t"],
                             status=("rejected" if fam == "FB" else "baseline (locked)"),
                             reason=("failed validation" if fam == "FB" else "locked universal rule; weaker in 2023-25"),
                             source="results/four/final.json"))
    parts += [g4, pd.DataFrame(rows)]
    # ---------------------------------------------------------------- FVG grid
    gf = grid_rows(os.path.join(RES, "fvg", "grid.csv.gz"), "FVG grid", ["sym", "tf", "mode", "disp", "gmin", "stop", "tgt", "trail", "bias", "kill"],
                   "mode", "DEV/VAL/OOS (OOS masked)", False, basic_reason, "results/fvg/grid.csv.gz")
    parts.append(gf)
    fc = json.load(open(os.path.join(RES, "fvg", "final_check.json")))
    parts.append(pd.DataFrame([dict(study="FVG final check", config_id=k, instrument="pooled", timeframe="H4", family="FVG", params=k, cost_model=COST,
                                    split="DEV/VAL/OOS", n_insample=v["pooled"]["dev"][0], E_insample=v["pooled"]["dev"][1], t_insample=v["pooled"]["dev"][2],
                                    n_val=v["pooled"]["val"][0], E_val=v["pooled"]["val"][1], t_val=v["pooled"]["val"][2],
                                    n_oos=v["pooled"]["oos"][0], E_oos=v["pooled"]["oos"][1], t_oos=v["pooled"]["oos"][2],
                                    status="watch-list" if v["pooled"]["oos"][1] > 0 else "rejected",
                                    reason="weakly positive in every period" if v["pooled"]["oos"][1] > 0 else "final 2023-25 expectancy negative",
                                    source="results/fvg/final_check.json") for k, v in fc.items()]))
    # ---------------------------------------------------------------- labs on the IS/OOS-2019 split
    for f, study in (("multi_lab.json", "Multi-market family lab"), ("liquidity_lab.json", "Liquidity sweeps"), ("liquidity2_lab.json", "Daily structure round 2"),
                     ("crosses_lab.json", "Cross pairs lab"), ("msnr_grid.json", "Malaysian SnR grid")):
        parts.append(judge_rows(json.load(open(os.path.join(RES, f))), study, f"results/{f}"))
    gl = json.load(open(os.path.join(RES, "gold_lab.json")))
    parts.append(judge_rows(gl["results"], "Gold lab", "results/gold_lab.json"))
    for sym in ("XAUUSD", "EURUSD", "GBPUSD", "USDJPY"):
        d = json.load(open(os.path.join(RES, f"{sym}.json")))
        parts.append(judge_rows(d, f"S1/TR search {sym}", f"results/{sym}.json"))
    fu = json.load(open(os.path.join(RES, "funnel.json")))
    parts.append(judge_rows(fu.get("report", {}), "Funnel (P26 era)", "results/funnel.json"))
    # ---------------------------------------------------------------- portfolios
    port = []
    for k, v in json.load(open(os.path.join(RES, "final_pareto.json"))).items():
        port.append(dict(study="P26 Pareto (inside 3.6% walls)", config_id=k, instrument="book", family="portfolio", params=json.dumps(v.get("weights", ""))[:300],
                         cost_model=COST, split="2011-2025", E_total=np.nan, max_dd=v.get("hist_mdd"), walk_forward="",
                         status="superseded", reason=f"CAGR {v.get('cagr', 0):.2%} inside the walls; walls later removed by the user",
                         source="results/final_pareto.json"))
    rm = json.load(open(os.path.join(RES, "four", "risk_manager.json")))
    for k, v in rm.items():
        port.append(dict(study="Central risk manager (four study)", config_id=k, instrument="portfolio", family="portfolio", params=f"base {v['base']:.4f}",
                         cost_model=COST, split="2011-2025 real + reshuffled", E_total=np.nan, max_dd=v["real"]["mdd"],
                         walk_forward="", status="baseline", reason=f"real CAGR {v['real']['cagr']:.1%}; 2023-25 {v['real']['oos']:+.1%}/yr",
                         source="results/four/risk_manager.json"))
    parts.append(pd.DataFrame(port))
    # ---------------------------------------------------------------- 11-leg book: computed from the saved trades
    bk = json.load(open(os.path.join(RES, "book_v3.json")))
    rows = []
    for k in bk["kept"]:
        tr = np.load(os.path.join(RES, "..", bk["files"][k]))
        y = np.array([pd.Timestamp(int(t), unit="s").year for t in tr["t_in"]]); r = tr["r"]
        def st(m):
            x = r[m]
            return (len(x), float(x.mean()) if len(x) else np.nan,
                    float(x.mean() / x.std(ddof=1) * np.sqrt(len(x))) if len(x) > 2 else np.nan,
                    float(x[x > 0].sum() / -x[x < 0].sum()) if (x < 0).any() else np.nan)
        a, d, v, o = st(np.ones(len(r), bool)), st(y <= 2019), st((y >= 2020) & (y <= 2022)), st(y >= 2023)
        cum = np.cumsum(r[np.argsort(tr["t_out"])]); mdd = float((np.maximum.accumulate(np.r_[0, cum])[1:] - cum).max())
        rows.append(dict(study="11-leg book (Hunt 2)", config_id=k, instrument=k.split("_")[0], family="book leg", params=f"weight {bk['weights'][k]:.3f}",
                         cost_model=COST, split="DEV/VAL/OOS recomputed from trades", n_total=a[0], E_total=a[1], t_total=a[2], pf_total=a[3],
                         n_insample=d[0], E_insample=d[1], t_insample=d[2], pf_insample=d[3], n_val=v[0], E_val=v[1], t_val=v[2],
                         n_oos=o[0], E_oos=o[1], t_oos=o[2], pf_oos=o[3], max_dd=f"{mdd:.1f}R (cumulative R, equal size)",
                         status="baseline (in book)", reason="selected with 2019-2025 visible (see Hunt 2 caveats)", source=bk["files"][k]))
    parts.append(pd.DataFrame(rows))
    L = pd.concat(parts, ignore_index=True)
    for c in COLS:
        if c not in L:
            L[c] = np.nan
    L = L[COLS]
    L.to_csv(os.path.join(OUT, "ledger.csv.gz"), index=False)
    # ---------------------------------------------------------------- missing artifacts
    MISSING.extend([
        ("Hour-of-day seasonality scan and window searches (hunt/seasonal_scan.py, windows.py, windows2.py)", "printed only, no result file", "re-run the scripts (deterministic)"),
        ("Gold 18:00-20:00 WAT test (msnr/gold_wat.py)", "printed only", "re-run the script"),
        ("MSnR robustness probe (msnr/probe.py)", "printed only", "re-run the script"),
        ("Euro European-hours variants (hunt/euro_hours.py)", "printed only; trades saved for 2 variants", "re-run the script"),
        ("Cross-pair trade files (trades/crosses)", "169 of 171 not committed (regenerable)", "re-run hunt/crosses.py"),
        ("Per-configuration maximum drawdown for every grid run", "never computed (grids log per-year sums only)", "recompute per configuration if needed"),
        ("Profit factor for four-strategy and FVG grid runs", "wins/losses sums not logged", "re-run grid with pos/neg sums"),
        ("Walk-forward results for the four-strategy, FVG and MSnR studies", "not run in those studies", "run North Star walk-forward on their candidates"),
        ("Per-trade logs of grid configurations", "not saved by design (aggregates only); saved for finalists and book legs", "re-run a configuration to regenerate"),
        ("P26 / TimelessCity early studies (search.py, search2.py, strategies2.py)", "partly summarised in results/*.json; some early outputs recovered from transcript only", "see recovered/README.md"),
        ("Financing (swap) costs in all pre-North Star studies", "not modelled", "North Star re-scores baselines with financing"),
    ])
    with open(os.path.join(OUT, "missing_artifacts.md"), "w") as f:
        f.write("# Missing or incomplete artifacts\n\n| artifact | state | how to recover |\n|---|---|---|\n")
        for a, b, c in MISSING:
            f.write(f"| {a} | {b} | {c} |\n")
    summ = L.groupby("study").agg(configs=("config_id", "count"), passed=("status", lambda s: int(s.isin(["passed study gates", "candidate", "baseline (locked)", "watch-list", "baseline"]).sum())))
    summ.to_csv(os.path.join(OUT, "ledger_summary.csv"))
    print(summ.to_string()); print("total rows", len(L))


if __name__ == "__main__":
    main()
