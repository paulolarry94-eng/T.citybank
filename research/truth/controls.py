"""Control windows for any lab strategy whose signals() honour p['sample'] = 'control' (owner's protocol, 2026-11-02).

    python3 research/truth/controls.py <strategy_name> [<strategy_name> ...]

For every configuration and market: the FLOW trades (exactly as the lab runs them) and the CONTROL trades, fills before
2023 (the lab's cut). Per period 2011-19 and 2020-22: n, mean R, t for flow and control, and the differential (Welch t).
For the configuration the lab selected (if any): long/short split, the trades at RoboForex Prime's published side-specific
swaps (where published), and 2023-25 only if the lab already logged its one look for this fingerprint.
Owner's rule (stricter than the lab): REAL only if (1) lab Tier A/B, (2) 2011-19 t >= 3 after costs, (3) beats its control
in 2011-19 (differential > 0, Welch t >= 2), (4) replicates (2020-22 > 0 and every market > 0 in 2011-19).
Tier B failing 2-4 = MONITOR; otherwise REJECTED. Also every configuration pooled across markets (flow vs control, per
period). Output: research/results/truth/<NAME>/controls.json
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import protocol as P          # noqa: E402
import cyclegoal as G         # noqa: E402
from grid import year_index   # noqa: E402

PERIODS = (("2011-19", 0, 2019), ("2020-22", 2020, 2022))


def stats(x):
    x = np.asarray(x, float)
    if len(x) < 3:
        return dict(n=int(len(x)), E=None, t=None)
    sd = x.std(ddof=1)
    return dict(n=int(len(x)), E=round(float(x.mean()), 4), t=round(float(x.mean() / sd * math.sqrt(len(x))), 2) if sd > 0 else None)


def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or len(b) < 3:
        return dict(diff=None, t=None)
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return dict(diff=round(float(d), 4), t=round(float(d / se), 2) if se > 0 else None)


def prime_swaps(T, sym):
    """Net R with the lab's swap replaced by RoboForex Prime's published side-specific swap (credit > 0), if published."""
    sw = json.load(open(os.path.join(HERE, "costs_roboforex_prime.json"))).get("published_swaps_pips_per_night", {}).get(sym)
    if not sw or "pip" not in sw:
        return None
    credit = np.where(T[:, 2] > 0, sw["long"], sw["short"]) * sw["pip"]
    return T[:, 3] + T[:, 7] + T[:, 6] * credit / T[:, 4]


def run(name):
    S = P.load_strategy(os.path.join(HERE, "strategies", f"{name}.py"))
    summ_p = os.path.join(ROOT, "research", "results", "truth", name, "summary.json")
    summ = json.load(open(summ_p)) if os.path.exists(summ_p) else {}
    sel = (summ.get("selection") or {}).get("candidate")
    looked = bool(summ.get("final_look")) and summ.get("fingerprint") == S.FINGERPRINT
    res = dict(name=name, fingerprint=S.FINGERPRINT, verdict=summ.get("verdict"), selected=sel, configs={})
    fs, cs, per_mkt = [], [], {}
    pool = {}                                                    # config -> period -> ([flow R], [control R]) across markets
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
                pf, pc = pool.setdefault(key, {}).setdefault(per, ([], []))
                pf.append(f[mf, 3]); pc.append(c[mc, 3])
            if sel and all(sel.get(k) == p.get(k) for k in S.GRID):
                fs.append((sym, f)); cs.append(c)
                per_mkt[sym] = stats(f[yf <= 2019, 3])
                dev = yf <= 2019
                side = {("long" if s > 0 else "short"): stats(f[dev & (f[:, 2] == s), 3]) for s in (1, -1)}
                ps = prime_swaps(f, sym)
                res.setdefault("selected_by_market", {})[sym] = dict(by_side_2011_19=side,
                    prime_swaps_2011_19=stats(ps[dev]) if ps is not None else None,
                    prime_swaps_2020_22=stats(ps[(yf >= 2020) & (yf <= 2022)]) if ps is not None else None)
                if looked:
                    F = P.run_config(S, M, p, 0.0, 0.0, 0, cut=0); Cc = P.run_config(S, M, dict(p, sample="control"), 0.0, 0.0, 0, cut=0)
                    lf, lc = year_index(F[:, 0]) >= 2023, year_index(Cc[:, 0]) >= 2023
                    res.setdefault("late_2023_25", {})[sym] = dict(flow=stats(F[lf, 3]), control=stats(Cc[lc, 3]), diff=welch(F[lf, 3], Cc[lc, 3]))
    res["pooled"] = {k: {per: dict(flow=stats(np.concatenate(pf)), control=stats(np.concatenate(pc)),
                                   diff=welch(np.concatenate(pf), np.concatenate(pc))) for per, (pf, pc) in v.items()}
                     for k, v in pool.items()}
    if sel:
        f = np.vstack([x for _, x in fs]); c = np.vstack(cs)
        yf, yc = year_index(f[:, 0]), year_index(c[:, 0])
        dev, val = stats(f[yf <= 2019, 3]), stats(f[(yf >= 2020) & (yf <= 2022), 3])
        d = welch(f[yf <= 2019, 3], c[yc <= 2019, 3])
        rules = {"1_lab_tier_A_or_B": str(res["verdict"]).startswith("Tier"),
                 "2_dev_t_ge_3": dev["t"] is not None and dev["t"] >= 3,
                 "3_beats_control_t_ge_2": d["diff"] is not None and d["diff"] > 0 and (d["t"] or 0) >= 2,
                 "4_replicates": (val["E"] or 0) > 0 and all((v["E"] or 0) > 0 for v in per_mkt.values())}
        res["selected_pooled"] = dict(dev=dev, val=val, control_dev=stats(c[yc <= 2019, 3]), diff_dev=d, per_market_dev=per_mkt,
                                      cycle_goal_dev=G.score(f[yf <= 2019, 3]), rules=rules)
        res["owner_rule_verdict"] = "REAL" if all(rules.values()) else ("MONITOR" if rules["1_lab_tier_A_or_B"] else "REJECTED")
    else:
        res["owner_rule_verdict"] = "REJECTED (no configuration passed the lab's development gate)"
    out = os.path.join(ROOT, "research", "results", "truth", name)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "controls.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    for n in sys.argv[1:]:
        r = run(n)
        print(n, r["verdict"], "->", r["owner_rule_verdict"])
        for k, v in r["configs"].items():
            for per, mk in v.items():
                print("  ", k, per, {s: dict(flow=(m["flow"]["n"], m["flow"]["E"], m["flow"]["t"]), control=(m["control"]["n"], m["control"]["E"]),
                                         diff_t=m["diff"]["t"]) for s, m in mk.items()})
        for k in ("selected_pooled", "selected_by_market", "late_2023_25"):
            if r.get(k):
                print("  ", k, r[k] if k != "selected_pooled" else {x: r[k][x] for x in ("dev", "val", "control_dev", "diff_dev", "rules")})
