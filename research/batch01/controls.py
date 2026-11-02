"""Batch 01: control windows and the batch rule (fixed 2026-11-02 before any result; see PREREGISTRATION.md).

For each lab strategy of the batch, every configuration and market: the FLOW trades (exactly as the lab runs them) and the
CONTROL trades (the same rule with p['sample'] = 'control'), fills before 2023 (the lab's cut). Per period 2011-19 and
2020-22: n, mean R, t for flow and control, and the differential (flow minus control: difference of means, Welch t).
2023-25: only for the configuration the lab selected, and only if the lab logged its one look for this fingerprint.
Batch rule (stricter than the lab; the owner's Batch 01 protocol). A candidate is REAL only if all hold:
  1 lab verdict Tier A or B;
  2 the selected configuration's 2011-19 t >= 3 after costs;
  3 it beats its control in 2011-19: differential > 0 with Welch t >= 2;
  4 it replicates in a second slice: 2020-22 mean > 0 AND every market's 2011-19 mean > 0.
Tier B with 2-4 failing = MONITOR; otherwise REJECTED.
Output: research/results/batch01/controls.json and research/results/batch01/BATCH01_REPORT.md
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import protocol as P          # noqa: E402
import cyclegoal as G         # noqa: E402
from grid import year_index   # noqa: E402

STRATS = ("us_close_flow_v1", "monthend_rebalance_v1")
OUT = os.path.join(ROOT, "research", "results", "batch01")
PERIODS = (("2011-19", 0, 2019), ("2020-22", 2020, 2022))


def stats(x):
    x = np.asarray(x, float)
    if len(x) < 3:
        return dict(n=int(len(x)), E=None, t=None)
    return dict(n=int(len(x)), E=round(float(x.mean()), 4), t=round(float(x.mean() / x.std(ddof=1) * math.sqrt(len(x))), 2))


def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or len(b) < 3:
        return dict(diff=None, t=None)
    d = a.mean() - b.mean()
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return dict(diff=round(float(d), 4), t=round(float(d / se), 2) if se > 0 else None)


def run(name):
    S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", f"{name}.py"))
    summ_p = os.path.join(ROOT, "research", "results", "truth", name, "summary.json")
    summ = json.load(open(summ_p)) if os.path.exists(summ_p) else {}
    sel = (summ.get("selection") or {}).get("candidate")
    looked = bool(summ.get("final_look")) and summ.get("fingerprint") == S.FINGERPRINT
    res = dict(name=name, verdict=summ.get("verdict"), selected=sel, configs={})
    flows_sel, ctrls_sel, per_market_dev = [], [], {}
    for sym in S.MARKETS:
        M = P.market(sym, S)
        for p in P.param_sets(S):
            key = json.dumps({k: p[k] for k in S.GRID}, sort_keys=True)
            f = P.run_config(S, M, p, 0.0, 0.0, 0)
            c = P.run_config(S, M, dict(p, sample="control"), 0.0, 0.0, 0)
            yf, yc = year_index(f[:, 0]), year_index(c[:, 0])
            row = res["configs"].setdefault(key, {})
            for per, a, b in PERIODS:
                mf, mc = (yf >= a) & (yf <= b), (yc >= a) & (yc <= b)
                row.setdefault(per, {})[sym] = dict(flow=stats(f[mf, 3]), control=stats(c[mc, 3]), diff=welch(f[mf, 3], c[mc, 3]))
            if sel and all(sel.get(k) == p.get(k) for k in S.GRID):
                flows_sel.append(f); ctrls_sel.append(c)
                per_market_dev[sym] = stats(f[yf <= 2019, 3])
                if looked:
                    F = P.run_config(S, M, p, 0.0, 0.0, 0, cut=0); Cc = P.run_config(S, M, dict(p, sample="control"), 0.0, 0.0, 0, cut=0)
                    lf, lc = year_index(F[:, 0]) >= 2023, year_index(Cc[:, 0]) >= 2023
                    res.setdefault("late_2023_25", {})[sym] = dict(flow=stats(F[lf, 3]), control=stats(Cc[lc, 3]), diff=welch(F[lf, 3], Cc[lc, 3]))
    if sel:
        f = np.vstack(flows_sel); c = np.vstack(ctrls_sel)
        yf, yc = year_index(f[:, 0]), year_index(c[:, 0])
        dev, val = stats(f[yf <= 2019, 3]), stats(f[(yf >= 2020) & (yf <= 2022), 3])
        d = welch(f[yf <= 2019, 3], c[yc <= 2019, 3])
        rules = {"1_lab_tier_A_or_B": str(res["verdict"]).startswith("Tier"),
                 "2_dev_t_ge_3": dev["t"] is not None and dev["t"] >= 3,
                 "3_beats_control_t_ge_2": d["diff"] is not None and d["diff"] > 0 and (d["t"] or 0) >= 2,
                 "4_replicates": (val["E"] or 0) > 0 and all((v["E"] or 0) > 0 for v in per_market_dev.values())}
        res["selected_pooled"] = dict(dev=dev, val=val, control_dev=stats(c[yc <= 2019, 3]), diff_dev=d, per_market_dev=per_market_dev,
                                      cycle_goal_dev=G.score(f[yf <= 2019, 3]), rules=rules)
        res["batch_verdict"] = "REAL" if all(rules.values()) else ("MONITOR" if rules["1_lab_tier_A_or_B"] else "REJECTED")
    else:
        res["batch_verdict"] = "REJECTED (no configuration passed the lab's development gate)"
    return res


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    out = {n: run(n) for n in STRATS}
    json.dump(out, open(os.path.join(OUT, "controls.json"), "w"), indent=1, default=float)
    for n, r in out.items():
        print(n, r["verdict"], "->", r["batch_verdict"])
        for k, v in r["configs"].items():
            for per, mk in v.items():
                print("  ", k, per, {s: (m["flow"]["E"], m["flow"]["t"], m["control"]["E"], m["diff"]["t"]) for s, m in mk.items()})
        if r.get("selected_pooled"):
            print("   selected", r["selected_pooled"]["rules"], r["selected_pooled"]["dev"], r["selected_pooled"]["diff_dev"])
