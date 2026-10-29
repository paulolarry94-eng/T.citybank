"""Apply the funnel (research/FUNNEL.md) to every variant searched.

Gate 1  in-sample 2011-2018 only:  E_is > +0.15R  and  Sharpe_is > 0.37 (benchmark median)
Gate 2  out-of-sample 2019-2025:   E_oos > 0  and  E_oos >= 0.5 * E_is
Gate 3  whole record:              t-stat >= 1.96  (i.e. distinguishable from luck)
Gate 4  bar-clock robustness:      H4/D1 variants must pass at BOTH alignments
Gate 5  diversification:           monthly-R correlation < 0.20 with every leg already kept
                                   (greedy, strongest in-sample Sharpe first)
"""
import json, glob, os, datetime as dt
import numpy as np

HERE = os.path.dirname(__file__)
SPLIT = 2019


def year_of(ts):
    return np.array([dt.datetime.utcfromtimestamp(int(t)).year for t in ts])


def month_key(ts):
    return np.array([(dt.datetime.utcfromtimestamp(int(t)).year - 2011) * 12 +
                     dt.datetime.utcfromtimestamp(int(t)).month - 1 for t in ts])


def sharpe_t(r, years):
    if len(r) < 3 or r.std(ddof=1) == 0:
        return np.nan, np.nan
    m, s = r.mean(), r.std(ddof=1)
    return m / s * np.sqrt(len(r) / years), m / s * np.sqrt(len(r))


def evaluate(path):
    tr = np.load(path)
    if len(tr) < 20:
        return None
    y = year_of(tr["t_in"])
    r = tr["r"]
    span_is = 8.0 - (4.4 / 12 if "XAUUSD" in path else 0.0)   # gold record starts 2011-05
    ins, oos = r[y < SPLIT], r[y >= SPLIT]
    sh_is, t_is = sharpe_t(ins, span_is)
    sh_all, t_all = sharpe_t(r, span_is + 7.0)
    return {"n": len(r), "per_yr": len(r) / (span_is + 7.0), "win": float((r > 0).mean()),
            "E": float(r.mean()), "E_is": float(ins.mean()) if len(ins) else np.nan,
            "E_oos": float(oos.mean()) if len(oos) else np.nan, "sh_is": sh_is,
            "sh_all": sh_all, "t_all": t_all,
            "pf": float(r[r > 0].sum() / -r[r <= 0].sum()) if (r <= 0).any() else np.inf}


def main():
    rows = {}
    for p in sorted(glob.glob(os.path.join(HERE, "trades", "*.npy"))):
        name = os.path.basename(p)[:-4]
        ev = evaluate(p)
        if ev:
            rows[name] = ev
    # collapse bar alignments: key without the _offN suffix
    groups = {}
    for k, v in rows.items():
        base, off = k.rsplit("_off", 1)
        groups.setdefault(base, {})[off] = v
    passed = []
    report = {}
    for base, offs in groups.items():
        g1 = all(v["E_is"] > 0.15 and v["sh_is"] > 0.37 for v in offs.values())
        g2 = all(v["E_oos"] > 0 and v["E_oos"] >= 0.5 * v["E_is"] for v in offs.values())
        g3 = all(v["t_all"] >= 1.96 for v in offs.values())
        v = offs.get("120", offs.get("0"))
        report[base] = {**v, "g1_in_sample": g1, "g2_out_of_sample": g2, "g3_tstat": g3}
        if g1 and g2 and g3:
            passed.append(base)
    # Gate 5: greedy correlation filter on monthly R (broker clock variant)
    monthly = {}
    for b in passed:
        p = os.path.join(HERE, "trades", b + "_off120.npy")
        tr = np.load(p)
        mk = month_key(tr["t_out"])
        s = np.zeros(15 * 12)
        np.add.at(s, mk[(mk >= 0) & (mk < 180)], tr["r"][(mk >= 0) & (mk < 180)])
        monthly[b] = s
    order = sorted(passed, key=lambda b: -report[b]["sh_is"])
    kept, corr_note = [], {}
    for b in order:
        cs = {k: float(np.corrcoef(monthly[b], monthly[k])[0, 1]) for k in kept}
        if all(abs(c) < 0.20 for c in cs.values()):
            kept.append(b)
        corr_note[b] = cs
    json.dump({"report": report, "passed_g1_g3": passed, "kept": kept, "corr": corr_note},
              open(os.path.join(HERE, "results", "funnel.json"), "w"), indent=1, default=float)
    return report, passed, kept, corr_note


if __name__ == "__main__":
    rep, passed, kept, corr = main()
    print(f"{len(rep)} variants | {len(passed)} pass gates 1-3 | {len(kept)} kept after correlation")
    for b in passed:
        v = rep[b]
        print(f"  {'KEEP' if b in kept else 'corr'} {b:34s} n={v['n']:4d} {v['per_yr']:5.1f}/yr "
              f"E={v['E']:+.3f} IS={v['E_is']:+.3f} OOS={v['E_oos']:+.3f} ShIS={v['sh_is']:.2f} "
              f"t={v['t_all']:.2f}  corr={ {k: round(c, 2) for k, c in corr[b].items()} }")
