"""Q26: old vs new results of the intraday studies that used HistData markets, before and after the clock fix (P29).

HistData's M1 stamps were one hour late in daylight-saving periods (EURGBP, XAGUSD, US500, NAS100, UK100, JP225 all years;
GER40 to 2020-01-29; WTI to 2023-12-01). The data was fixed in place in commit e68f660. The studies below were re-run on
2026-11-03 with the same code and the same strategy files (same fingerprints); nothing about the rules changed.

Old results are read from git at OLD (the last commit before the re-runs); new results from the working tree.
Control: XAUUSD, EURUSD, GBPUSD and USDJPY were never HistData; their numbers must be identical, which shows that every
difference comes from the data fix and not from code changes since the studies were first run.

    python3 research/q26/compare.py            # prints the tables, writes research/results/q26/rerun_compare.json
"""
import os, io, json, subprocess
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OLD = "76d7dfe"
OUT = os.path.join(ROOT, "research", "results", "q26"); os.makedirs(OUT, exist_ok=True)
CLEAN = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
HIST = ["XAGUSD", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
LAB = ["tom_indices_v2", "opex_week_indices_v2", "oil_equity_v2", "payday_indices_v1"]


def old_bytes(path):
    return subprocess.check_output(["git", "-C", ROOT, "show", f"{OLD}:{path}"])


def both_json(path):
    return json.loads(old_bytes(path)), json.load(open(os.path.join(ROOT, path)))


def both_csv(path):
    comp = "gzip" if path.endswith(".gz") else None
    return pd.read_csv(io.BytesIO(old_bytes(path)), compression=comp), pd.read_csv(os.path.join(ROOT, path), compression=comp)


def pocket():
    o, n = both_json("research/results/hunter5m/pocket_scan.json")
    co, cn = both_csv("research/results/hunter5m/pocket_cells.csv")
    key = ["sym", "tf", "session", "exit"]
    m = co.merge(cn, on=key, suffixes=("_old", "_new"))
    num = [c for c in co.columns if c not in key]
    changed = np.zeros(len(m), bool)
    for c in num:
        a, b = m[c + "_old"], m[c + "_new"]
        changed |= ~((a == b) | (a.isna() & b.isna()))
    m["changed"] = changed
    ctrl = m[m.sym.isin(CLEAN)]
    head = lambda d: dict(discovery_pass=d["discovery_pass"], confirmed=d["confirmed"], survivors=len(d["survivors"]),
                          discovery_cells=[f"{x['sym']} {x['tf']} {x['session']} {x['exit']} (dev {x['dev_E']:+.3f} t {x['dev_t']}, "
                                           f"val {x['val_E']:+.3f})" for x in d["discovery_passes"]],
                          persistence_after=d["persistence after costs"], persistence_before=d["persistence before costs"],
                          share_pos_after=d["share_cells_positive_after_costs"], share_pos_before=d["share_cells_positive_before_costs"],
                          median_after_by_tf=d["median_E_after_costs_by_tf"], median_before_by_tf=d["median_E_before_costs_by_tf"],
                          median_after_by_session=d["median_E_after_costs_by_session"],
                          hint={ex: {p: v[p].get("E") for p in ("2011-19", "2020-22", "2023-25")} for ex, v in d["hint_M30_16_20_other_markets"].items()},
                          hint_by_market={ex: {s: v["by market 2011-25"][s].get("E") for s in v["by market 2011-25"]}
                                          for ex, v in d["hint_M30_16_20_other_markets"].items()})
    by_mkt = {s: dict(cells=int((m.sym == s).sum()), changed=int(m[m.sym == s].changed.sum()),
                      dev_Egross_median_old=round(float(m[m.sym == s].dev_Egross_old.median()), 3),
                      dev_Egross_median_new=round(float(m[m.sym == s].dev_Egross_new.median()), 3),
                      dev_E_median_old=round(float(m[m.sym == s].dev_E_old.median()), 3),
                      dev_E_median_new=round(float(m[m.sym == s].dev_E_new.median()), 3))
              for s in CLEAN + HIST}
    sess = {}
    for s in ("asia", "london", "newyork"):
        g = m[(m.session == s) & m.sym.isin(HIST)]
        sess[s] = dict(dev_Egross_old=round(float(g.dev_Egross_old.median()), 3), dev_Egross_new=round(float(g.dev_Egross_new.median()), 3),
                       dev_E_old=round(float(g.dev_E_old.median()), 3), dev_E_new=round(float(g.dev_E_new.median()), 3))
    mad = float(np.nanmedian(np.abs(m[m.sym.isin(HIST)].dev_Egross_new - m[m.sym.isin(HIST)].dev_Egross_old)))
    return dict(old=head(o), new=head(n), control_cells=int(len(ctrl)), control_changed=int(ctrl.changed.sum()),
                hist_cells=int(m.sym.isin(HIST).sum()), hist_changed=int(m[m.sym.isin(HIST)].changed.sum()),
                hist_median_abs_change_dev_Egross=round(mad, 4), by_market=by_mkt, hist_markets_by_session=sess)


def anatomy():
    o, n = both_json("research/results/hunter5m/winner_anatomy.json")
    pick = lambda d, k, ex="ladder": d.get(k, {}).get(ex, {}).get("E")
    base = {}
    for s in HIST + CLEAN:
        for per in ("2011-19", "2020-22", "2023-25"):
            k = f"{s} {per}"
            if k in o["baseline"]:
                base[k] = dict(old=pick(o["baseline"], k), new=pick(n["baseline"], k),
                               old_gross=pick(o["baseline"], k, "ladder_gross"), new_gross=pick(n["baseline"], k, "ladder_gross"),
                               n_old=o["baseline"][k]["ladder"]["n"], n_new=n["baseline"][k]["ladder"]["n"])
    rr = {k: dict(old=pick(o["rule_results"], k), new=pick(n["rule_results"], k), n_old=o["rule_results"][k]["ladder"].get("n"),
                  n_new=n["rule_results"][k]["ladder"].get("n")) for k in o["rule_results"]}
    return dict(rule_same=o["rule"] == n["rule"], kept_old=o["kept"], kept_new=n["kept"],
                learning_same=o["anatomy"] == n["anatomy"] and o["rule_halves"] == n["rule_halves"],
                baseline_ladder=base, rule_results_ladder=rr)


def runner():
    o, n = both_json("research/results/hunter5m/runner_profile.json")
    g = lambda d, k, sel: d["results"][k][sel]["ladder"].get("E")
    return dict(cuts_same=o["cut_points"] == n["cut_points"],
                groups={k: dict(all_old=g(o, k, "all setups"), all_new=g(n, k, "all setups"),
                                s3_old=g(o, k, "score>=3"), s3_new=g(n, k, "score>=3"),
                                s3_n_old=o["results"][k]["score>=3"]["ladder"].get("n"), s3_n_new=n["results"][k]["score>=3"]["ladder"].get("n"))
                        for k in o["results"]})


def q21():
    path = "research/results/q21/velocity_diagnostic.json"
    return dict(identical=old_bytes(path) == open(os.path.join(ROOT, path), "rb").read(),
                why="GER40 is studied 2020-25 only (no tick volume before 2020); its HistData part ends 2020-01-29, in winter, "
                    "when the stamps were already right; USDJPY was never HistData.")


def lab():
    res = {}
    for s in LAB:
        base = f"research/results/truth/{s}"
        so, sn = both_json(base + "/summary.json")
        po, pn = both_csv(base + "/pooled.csv.gz")
        assert so["fingerprint"] == sn["fingerprint"], s
        rows = []
        for (_, a), (_, b) in zip(po.iterrows(), pn.iterrows()):
            cfg = {c: a[c] for c in po.columns[:5]}
            rows.append(dict(config=" ".join(str(v) for v in cfg.values()),
                             dev_old=dict(n=int(a.dev_n), E=round(a.dev_E, 4), t=round(a.dev_t, 2)),
                             dev_new=dict(n=int(b.dev_n), E=round(b.dev_E, 4), t=round(b.dev_t, 2)),
                             val_old=dict(n=int(a.val_n), E=round(a.val_E, 4), t=round(a.val_t, 2)),
                             val_new=dict(n=int(b.val_n), E=round(b.val_E, 4), t=round(b.val_t, 2)),
                             gate_old=bool(a.gate), gate_new=bool(b.gate)))
        res[s] = dict(fingerprint=sn["fingerprint"][:12], verdict_old=so["verdict"], verdict_new=sn["verdict"], configs=rows)
    p = json.load(open(os.path.join(OUT, "payday_2023_25_corrected.json")))
    res["payday_indices_v1"]["2023-25"] = dict(logged=p["logged_look"]["oos"], corrected=p["corrected_data"]["oos"])
    return res


def main():
    R = dict(note=__doc__, old_commit=OLD, pocket_scan=pocket(), winner_anatomy=anatomy(), runner_profile=runner(), q21=q21(), lab=lab())
    json.dump(R, open(os.path.join(OUT, "rerun_compare.json"), "w"), indent=1, default=float)
    P = R["pocket_scan"]
    print(f"pocket scan: control cells changed {P['control_changed']}/{P['control_cells']}; HistData cells changed "
          f"{P['hist_changed']}/{P['hist_cells']} (median |change| before costs 2011-19 {P['hist_median_abs_change_dev_Egross']} R)")
    for k in ("discovery_pass", "confirmed", "survivors", "discovery_cells", "persistence_after", "persistence_before",
              "share_pos_after", "share_pos_before", "median_after_by_session", "hint"):
        print(f"  {k}: old {P['old'][k]}\n  {' ' * len(k)}  new {P['new'][k]}")
    for s, v in P["by_market"].items():
        print(f"  {s:7s} changed {v['changed']:>2}/{v['cells']}  median 2011-19 gross {v['dev_Egross_median_old']:+.3f} -> "
              f"{v['dev_Egross_median_new']:+.3f}  net {v['dev_E_median_old']:+.3f} -> {v['dev_E_median_new']:+.3f}")
    print("  HistData markets by session (median 2011-19):", P["hist_markets_by_session"])
    A = R["winner_anatomy"]
    print(f"winner anatomy: rule same {A['rule_same']}, learning same {A['learning_same']}, kept {A['kept_old']} -> {A['kept_new']}")
    for k, v in A["rule_results_ladder"].items():
        print(f"  rule {k:36s} {v['old']} -> {v['new']}  (n {v['n_old']} -> {v['n_new']})")
    for k, v in A["baseline_ladder"].items():
        if v["old"] != v["new"]:
            print(f"  all setups {k:16s} net {v['old']} -> {v['new']}  gross {v['old_gross']} -> {v['new_gross']}  n {v['n_old']} -> {v['n_new']}")
    U = R["runner_profile"]
    print(f"runner profile: cut points same {U['cuts_same']}")
    for k, v in U["groups"].items():
        print(f"  {k:36s} all {v['all_old']} -> {v['all_new']}   score>=3 {v['s3_old']} -> {v['s3_new']} (n {v['s3_n_old']} -> {v['s3_n_new']})")
    print("Q21:", R["q21"])
    for s, v in R["lab"].items():
        print(f"{s} [{v['fingerprint']}] {v['verdict_old']}  ->  {v['verdict_new']}")
        for c in v["configs"]:
            print(f"  {c['config']}: dev {c['dev_old']} -> {c['dev_new']}; val {c['val_old']} -> {c['val_new']}; gate {c['gate_old']} -> {c['gate_new']}")
        if "2023-25" in v:
            print("  2023-25 logged", v["2023-25"]["logged"], "\n  2023-25 corrected", v["2023-25"]["corrected"])


if __name__ == "__main__":
    main()
