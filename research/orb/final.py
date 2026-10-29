"""ORB 50 — final evaluation of the four configurations named in Part 9D.

The four are fixed here BEFORE any 2023-2025 data is read:
  A  best pure ORB            = development robust pick of the Model A grid (E1)
  B  best trend-filtered ORB  = development robust pick of the Model B grid (E2)
  C  best pullback ORB        = development robust pick of the Model C grid (E3)
  X  best robust combined     = the only pick whose refinement held up in validation:
                                B + skip sessions whose OR is in the narrowest 20% (E5).
                                Chosen WITH knowledge of 2020-2022, so for X only 2023-2025
                                is a clean test.
Order of work: (1) robustness on 2011-2022 (deflated Sharpe on 2011-2019, cost and latency
stress, regimes, Monte Carlo); (2) one logged run over 2011-2025 per configuration; (3) one
logged batch run of the ablation table over 2023-2025.
"""
import os, json, warnings
import numpy as np
import pandas as pd
import core, strategy as S, selection as SEL, experiments as X, validate as V, metrics as MT, refine as RF, ablation as AB

warnings.simplefilter("ignore")
OUT = os.path.join(core.HERE, "..", "results", "orb_final")
FINAL = [("A", "Best pure ORB (Model A)", "E1", "E1-12484"),
         ("B", "Best trend-filtered ORB (Model B)", "E2", "E2-2166"),
         ("C", "Best pullback-continuation ORB (Model C)", "E3", "E3-385"),
         ("X", "Best robust combined (Model B + skip narrowest 20% of ORs)", "E5", "E5-1291")]
PERIODS = {"dev 2011-19": (2011, 2019), "val 2020-22": (2020, 2022), "oos 2023-25": (2023, 2025), "all 2011-25": (2011, 2025)}


def configs():
    out = []
    for key, name, st, eid in FINAL:
        r = SEL.load([st]).set_index("id").loc[eid]
        cfg, bias = RF.cfg_of(r)
        out.append(dict(key=key, name=name, id=eid, sym=r["sym"], session=r["session"], orb=int(r["orb"]),
                        cfg=cfg, bias=bias, filt=r["filt"] if isinstance(r["filt"], str) else ""))
    return out


def sr_trials():
    df = SEL.load(["E1", "E2", "E3", "E4", "E5", "E6"])
    p = SEL.period_stats(df, SEL.DEV)
    sr = (p["t"] / np.sqrt(p["n"]))[p["n"] >= 30]
    return sr.values, len(df)


def sub(tr, yrs, a, b):
    k = (yrs >= a) & (yrs <= b)
    return tr[k]


def main():
    os.makedirs(OUT, exist_ok=True)
    C = configs()
    srs, n_trials = sr_trials()
    mk = {}
    report = dict(n_trials=n_trials, configs=[])
    for c in C:
        M = mk.get(c["sym"]) or core.Market(c["sym"]); mk[c["sym"]] = M
        # ---------------------------------------------------- (1) everything before 2023
        tr, D = X.run_one(M, c["session"], c["orb"], c["cfg"], c["filt"], c["bias"])
        yrs = D["year"][tr["d"]]
        dev = sub(tr, yrs, 2011, 2019)
        pre = dict(dsr=V.deflated_sharpe(dev["r"], srs, n_trials),
                   bonferroni_t_all_trials=V.bonferroni_t(n_trials),
                   perturb=V.perturb(M, c["session"], c["orb"], c["cfg"], c["bias"], c["filt"]),
                   regimes=V.regime_table(M, tr),
                   monte_carlo=V.monte_carlo(tr, risk=0.005, years=3.0))
        # ---------------------------------------------------- (2) the one full run
        trf, yf = V.final_run(M, c["session"], c["orb"], c["cfg"], c["bias"], c["filt"], label=f"final {c['key']}")
        np.save(os.path.join(OUT, f"{c['key']}_trades.npy"), trf)
        np.save(os.path.join(OUT, f"{c['key']}_years.npy"), yf)
        per = {}
        for nm, (a, b) in PERIODS.items():
            t = sub(trf, yf, a, b)
            f = MT.full({c["sym"]: t}, risk=0.005)
            per[nm] = {k: v for k, v in f.items() if k not in ("monthly",)}
        post = dict(periods=per, regimes_oos=V.regime_table(M, sub(trf, yf, 2023, 2025)),
                    regimes_all=V.regime_table(M, trf), monte_carlo_all=V.monte_carlo(trf, risk=0.005, years=3.0),
                    monthly_all=MT.full({c["sym"]: trf}, risk=0.005)["monthly"])
        report["configs"].append(dict(c, pre_oos=pre, post=post))
        o = per["oos 2023-25"]; v = per["val 2020-22"]; d = per["dev 2011-19"]
        print(f"{c['key']} {c['sym']} {c['session']} ORB{c['orb']}: dev E={d['E']:+.3f} t={d['t']:+.2f} | "
              f"val E={v['E']:+.3f} t={v['t']:+.2f} | OOS E={o['E']:+.3f} t={o['t']:+.2f} n={o['n']} | "
              f"DSR={pre['dsr']['dsr']:.3f}", flush=True)
    json.dump(report, open(os.path.join(core.HERE, "..", "results", "orb_final.json"), "w"), indent=1, default=float)
    # -------------------------------------------------------- (3) ablation on 2023-2025, one batch
    T, labels = AB.tasks()
    rows = []
    for sym in core.SYMS:
        M = mk.get(sym) or core.Market(sym); mk[sym] = M
        for (s, sess, orb, cfg, filt, bias), lab in zip(T, labels):
            if s != sym:
                continue
            D = M.days(sess, orb)
            allow = (D["year"] >= 2023) & X.filter_mask(M, sess, orb, filt)
            t = S.run(M, sess, orb, allow=allow, bias_cfg=bias, **cfg)
            r = t["r"]
            rows.append(dict(sym=sym, session=sess, orb=orb, kind=lab[0], variant=lab[1], n=len(r), s=float(r.sum()),
                             ss=float((r ** 2).sum()), c=float((M.cost / t["dist"]).sum()) if len(t) else 0.0))
    log = json.load(open(V.LOG_OOS)) if os.path.exists(V.LOG_OOS) else []
    log.append(dict(label="ablation table 2023-2025 (one batch, reporting only)", runs=len(rows)))
    json.dump(log, open(V.LOG_OOS, "w"), indent=1)
    df = pd.DataFrame(rows)
    res = {}
    for scope, g0 in [("all 56 combos", df)] + [(f"session {s}", df[df.session == s]) for s in core.SESSIONS] + \
                     [("XAUUSD LDN", df[(df.sym == "XAUUSD") & (df.session == "LDN")])]:
        out = []
        for v in dict.fromkeys(df.variant):
            g = g0[g0.variant == v]
            n, s, ss, cc = g.n.sum(), g.s.sum(), g.ss.sum(), g.c.sum()
            E = s / n; var = (ss - n * E * E) / (n - 1)
            out.append(dict(variant=v, oos_n=int(n), oos_E=float(E), oos_t=float(E / np.sqrt(var / n)), oos_Egross=float((s + cc) / n)))
        res[scope] = out
    json.dump(res, open(os.path.join(core.HERE, "..", "results", "orb_ablation_oos.json"), "w"), indent=1)
    print(pd.DataFrame(res["all 56 combos"]).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
