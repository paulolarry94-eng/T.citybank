"""Part 11 master comparison: the earlier ledger (27 studies) + every North Star configuration (pooled over
the four markets) + the financed re-score of the baselines.

    python3 master.py -> results/northstar/master_comparison.csv.gz, master_summary.csv
"""
import os, json
import numpy as np
import pandas as pd
from analyze import RES, PARAMS, keycols

COST = "all-in round trip: XAU $0.45, EUR 1.5p, GBP 1.8p, JPY 1.2p; + financing per rollover (x3 Wed)"


def northstar_rows():
    tiers = json.load(open(os.path.join(RES, "tiers.json")))
    rows = []
    for mod in PARAMS:
        S = pd.read_csv(os.path.join(RES, f"pooled_{mod.replace('+', '_')}.csv.gz"))
        cand = tiers.get(mod, {}).get("config")
        for i, r in S.iterrows():
            cfg = {k: r[k] for k in keycols(mod)}
            is_cand = cand is not None and all(str(cfg[k]) == str(cand[k]) or (isinstance(cand[k], float) and float(cfg[k]) == cand[k]) for k in cand)
            if is_cand:
                status, reason = tiers[mod]["tier"].lower(), "module candidate; failed: " + ", ".join(k for k, v in tiers[mod]["criteria"].items() if not v)
            elif r["gate"]:
                status, reason = "rejected", "passed development gate, not top-ranked"
            else:
                why = []
                if r["dev_n"] < 200: why.append("dev trades < 200")
                if not r["e1_E"] > 0: why.append("2011-15 E <= 0")
                if not r["e2_E"] > 0: why.append("2016-19 E <= 0")
                if r["mk_pos"] < 3: why.append("< 3 markets positive")
                status, reason = "rejected", "; ".join(why)
            o = tiers[mod]["oos"] if is_cand else {}
            rows.append(dict(study=f"North Star {mod}", config_id=f"NS-{mod}-{i}", instrument="4 markets pooled", timeframe=cfg["tf"],
                             family=mod, params="|".join(f"{k}={v}" for k, v in cfg.items()), entry_rule=str(cfg.get("entry", "limit" if mod.startswith("FVG-") and mod != "FVG-B" else "market")),
                             exit_rule=f"tgt={cfg['tgt']} trail={cfg['trail']} time=50 bars", cost_model=COST, split="DEV/VAL (OOS masked except candidate)",
                             n_insample=r["dev_n"], E_insample=r["dev_E"], t_insample=r["dev_t"], n_val=r["val_n"], E_val=r["val_E"], t_val=r["val_t"],
                             n_oos=o.get("n"), E_oos=o.get("E"), t_oos=o.get("t"), pf_oos=o.get("PF"), status=status, reason=reason,
                             source=f"results/northstar/pooled_{mod.replace('+', '_')}.csv.gz"))
    return rows


def baseline_rows():
    b = json.load(open(os.path.join(RES, "baselines_financed.json"))); rows = []
    for k, v in b.items():
        study = "Book (financed re-score)" if k.startswith("book") else ("Four strategies (financed re-score)" if k.startswith("four") else "ORB finalists (financed re-score)")
        d, va, o = v["dev"]["after"], v["val"]["after"], v["oos"]["after"]
        rows.append(dict(study=study, config_id=f"FIN-{k}", instrument="see name", family=k, cost_model=COST, split="DEV/VAL/OOS (OOS seen in earlier studies)",
                         n_insample=d["n"], E_insample=d.get("E"), t_insample=d.get("t"), pf_insample=d.get("PF"),
                         n_val=va["n"], E_val=va.get("E"), t_val=va.get("t"), n_oos=o["n"], E_oos=o.get("E"), t_oos=o.get("t"), pf_oos=o.get("PF"),
                         status="forward-test candidate" if k == "book_all_unweighted" else "reference",
                         reason="; ".join(f"{c}={'pass' if x else 'fail'}" for c, x in v["criteria"].items()), source="results/northstar/baselines_financed.json"))
    return rows


def main():
    L = pd.read_csv(os.path.join(RES, "ledger.csv.gz"), low_memory=False)
    N = pd.DataFrame(northstar_rows() + baseline_rows())
    M = pd.concat([L, N], ignore_index=True)
    M.to_csv(os.path.join(RES, "master_comparison.csv.gz"), index=False)
    g = M.groupby("study", sort=False)
    S = pd.DataFrame(dict(configs=g.size(), dev_positive_share=g.apply(lambda d: (d.E_insample > 0).mean()),
                          best_dev_E_n30=g.apply(lambda d: d.E_insample[d.n_insample.fillna(d.n_total) >= 30].max()),
                          median_dev_E=g.E_insample.median(),
                          looked_oos=g.apply(lambda d: int(d.E_oos.notna().sum())), oos_positive=g.apply(lambda d: int((d.E_oos > 0).sum())),
                          not_rejected=g.apply(lambda d: int((~d.status.astype(str).str.startswith("rejected")).sum()))))
    S.to_csv(os.path.join(RES, "master_summary.csv"))
    print(f"master rows: {len(M):,}  studies: {len(S)}")
    with pd.option_context("display.width", 200, "display.max_rows", 100):
        print(S.round(3).to_string())


if __name__ == "__main__":
    main()
