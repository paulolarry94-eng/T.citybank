"""Fill ORB_REPORT.template.md with tables built from the saved results -> ORB_REPORT.md."""
import os, json, re, warnings
import numpy as np
import pandas as pd
import core, selection as SEL

warnings.simplefilter("ignore")
RES = os.path.join(core.HERE, "..", "results")
J = lambda f: json.load(open(os.path.join(RES, f)))


def md(df, floatfmt="{:+.3f}"):
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                cells.append("" if not np.isfinite(v) else floatfmt.format(v))
            else:
                cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def t_stage_summary():
    rows = []
    for st, name in (("E1", "A pure ORB"), ("E2", "B trend-filtered ORB"), ("E3", "C pullback ORB"), ("E6", "failed-breakout reversal")):
        d = SEL.with_stats(SEL.load([st]))
        k = d.n >= 150
        rows.append(dict(model=name, configs=f"{len(d):,}", **{"with >=150 dev trades": f"{k.sum():,}",
                    "share E>0": f"{(d.E[k] > 0).mean():.1%}", "t>2": int((d.t[k] > 2).sum()),
                    "median E": float(d.E[k].median()), "best E": float(d.E[k].max()), "best t": float(d.t[k].max()),
                    "median E before costs": float(d.Egross[k].median())}))
    return md(pd.DataFrame(rows))


def t_sessions():
    d = SEL.load(["E0"]); a = SEL.period_stats(d, SEL.DEV); v = SEL.period_stats(d, SEL.VAL, "v_")
    x = pd.concat([d[["sym", "session", "orb", "tgt"]], a, v], axis=1)
    x = x[x.tgt == 2.0]
    g = x.groupby("session").agg(dev_E=("E", "mean"), dev_E_before_costs=("Egross", "mean"), dev_long=("El", "mean"),
                                 dev_short=("Es", "mean"), val_E=("v_E", "mean")).reset_index()
    g2 = x.groupby("sym").agg(dev_E=("E", "mean"), dev_E_before_costs=("Egross", "mean"), dev_long=("El", "mean"),
                              dev_short=("Es", "mean"), val_E=("v_E", "mean")).reset_index().rename(columns={"sym": "session"})
    g2["session"] = "all sessions, " + g2["session"]
    return md(pd.concat([g, g2]))


def t_components():
    C = J("orb_component_effects.json")
    out = []
    for k in ("management", "filters"):
        df = pd.DataFrame(C[k]); df = df[df.set == "canon"].drop(columns=["set"])
        df = df.rename(columns={"label": "component", "dE_dev_median": "change dev (R)", "share_better_dev": "bases better dev",
                                "dE_val_median": "change val (R)", "share_better_val": "bases better val", "trades_kept": "trades kept"})
        for c in ("bases better dev", "bases better val", "trades kept"):
            df[c] = df[c].map(lambda v: f"{v:.0%}")
        out.append(md(df))
    return out


def t_ablation():
    dv = J("orb_ablation.json"); oo = J("orb_ablation_oos.json")
    out = {}
    for scope in ("all 56 combos", "session LDN", "XAUUSD LDN"):
        om = {r["variant"]: r for r in oo[scope]}
        rows = []
        for r in dv[scope]:
            o = om[r["variant"]]
            rows.append({"variant": r["variant"].replace(" ladder", "") + (" (cumulative)" if r["kind"] == "ladder" else ""),
                         "dev n": f"{r['dev_n']:,}", "dev E": r["dev_E"], "dev t": r["dev_t"], "val E": r["val_E"], "val t": r["val_t"],
                         "OOS n": f"{o['oos_n']:,}", "OOS E": o["oos_E"], "OOS t": o["oos_t"], "OOS E before costs": o["oos_Egross"]})
        out[scope] = md(pd.DataFrame(rows))
    return out


def t_walkforward():
    W = J("orb_walkforward.json")
    rows = []
    for k, v in W.items():
        rows.append({"model": k, "trades": f"{v['always']['n']:,}", "E (always trade)": v["always"]["E"], "t": v["always"]["t"],
                     "trades (gated, score>=1)": f"{v['gated']['n']:,}", "E (gated)": v["gated"]["E"], "t (gated)": v["gated"]["t"],
                     "positive years": f"{sum(1 for y in v['by_year'].values() if y['E'] > 0)}/9"})
    return md(pd.DataFrame(rows))


def t_validation():
    v = pd.read_csv(os.path.join(RES, "orb_experiments", "validation_shortlist.csv"))
    v = v.rename(columns={"score": "dev robust score", "E": "dev E", "t": "dev t", "v_n": "val n", "v_E": "val E", "v_t": "val t"})
    return md(v[["model", "sym", "session", "orb", "dev robust score", "dev E", "dev t", "val n", "val E", "val t"]])


def t_final():
    R = J("orb_final.json")
    rows, rows2, st, rg = [], [], [], []
    for c in R["configs"]:
        for p, s in c["post"]["periods"].items():
            rows.append({"cfg": c["key"], "period": p, "trades": s["n"], "net profit $": f"{s['net_profit']:,.0f}",
                         "CAGR": f"{s['cagr']:+.1%}", "PF": f"{s['pf']:.2f}", "win": f"{s['win']:.0%}",
                         "avg win R": f"{s['avg_win_R']:.2f}", "avg loss R": f"{s['avg_loss_R']:.2f}", "E (R)": s["E"],
                         "E before costs": s["E_gross"], "t": s["t"], "max DD": f"{s['max_dd']:.1%}",
                         "recovery": f"{s['recovery']:.2f}", "Sharpe": f"{s['sharpe']:.2f}", "Sortino": f"{s['sortino']:.2f}",
                         "max losing streak": s["max_consec_losses"], "avg hold (min)": f"{s['hold_min_avg']:.0f}",
                         "long E": s["long_E"], "short E": s["short_E"], "% months up": f"{s['pct_months_positive']:.0%}"})
        p = c["pre_oos"]
        st.append({"cfg": c["key"], **{k: f"{v['E']:+.3f} (t {v['t']:+.2f})" for k, v in p["perturb"].items()},
                   "DSR (dev)": f"{p['dsr']['dsr']:.3f}", "trade Sharpe": f"{p['dsr']['sr_trade']:.3f}",
                   "Sharpe needed (SR0)": f"{p['dsr']['sr0']:.3f}",
                   "MC 3y median DD": f"{p['monte_carlo']['max_dd']['p50']:.1%}", "MC 3y 95% DD": f"{p['monte_carlo']['max_dd']['p95']:.1%}",
                   "MC 3y P(loss)": f"{p['monte_carlo']['p_loss']:.0%}"})
        r1 = p["regimes"]; r2 = c["post"]["regimes_oos"]
        for k in ("trend:bull", "trend:bear", "trend:sideways", "vol:high", "vol:normal", "vol:low", "shock"):
            a = r1.get(k, {"n": 0, "E": np.nan}); b = r2.get(k, {"n": 0, "E": np.nan})
            rg.append({"cfg": c["key"], "regime": k, "2011-22 n": a["n"], "2011-22 E": a["E"], "2023-25 n": b["n"], "2023-25 E": b["E"]})
        rows2.append({"cfg": c["key"], "name": c["name"], "market": f"{c['sym']} {c['session']} ORB{c['orb']}", "experiment id": c["id"],
                      "filter": c["filt"] or "-", "bias": (f"H4 EMA{c['bias']['period']} {c['bias']['kind']}" + (f" z={c['bias']['z']}" if c['bias']['kind'] == "neutral" else "")) if c["bias"] else "-"})
    return md(pd.DataFrame(rows2)), md(pd.DataFrame(rows)), md(pd.DataFrame(st)), md(pd.DataFrame(rg))


def main():
    T = open(os.path.join(core.HERE, "ORB_REPORT.template.md")).read()
    comp = t_components(); ab = t_ablation(); f_names, f_tab, f_stress, f_reg = t_final()
    isoos = J("orb_is_oos.json")
    fill = {"STAGES": t_stage_summary(), "SESSIONS": t_sessions(), "MANAGEMENT": comp[0], "FILTERS": comp[1],
            "ABL_ALL": ab["all 56 combos"], "ABL_LDN": ab["session LDN"], "ABL_XAU": ab["XAUUSD LDN"],
            "WALKFORWARD": t_walkforward(), "VALIDATION": t_validation(), "FINAL_NAMES": f_names, "FINAL": f_tab,
            "STRESS": f_stress, "REGIMES": f_reg, "ISOOS_CORR": f"{isoos['is_oos_corr']:+.2f}",
            "ISOOS_TOP": f"{isoos['top1pct_val_E']:+.3f}", "ISOOS_N": f"{isoos['top1pct_n']:,}"}
    for k, v in fill.items():
        T = T.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", T)
    assert not left, left
    open(os.path.join(core.HERE, "ORB_REPORT.md"), "w").write(T)
    print("ORB_REPORT.md written", len(T), "chars")


if __name__ == "__main__":
    main()
