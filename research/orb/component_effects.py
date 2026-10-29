"""ORB 50 — what each management element and each filter does (E4, E5), as the change in
expectancy against the same base without it. Development years decide; validation shown."""
import json, warnings
import numpy as np
import pandas as pd
import core, selection as SEL, refine as RF

warnings.simplefilter("ignore")


def tagged(stage, tasks_fn):
    B = RF.bases()
    tags = []
    for bi, b in enumerate(B):
        for t in tasks_fn([b]):
            tags.append((bi, b[0]))
    df = SEL.load([stage])
    k = df["id"].str.split("-").str[1].astype(int).values          # experiment id = position in the task list
    df["base"] = [tags[i][0] for i in k]; df["base_tag"] = [tags[i][1] for i in k]
    d = SEL.with_stats(df, SEL.DEV)
    v = SEL.period_stats(df, SEL.VAL, "v_")
    return pd.concat([d, v], axis=1)


def effect(d, ref_mask, var_mask, label):
    """Pairwise difference var - ref within each base (matching base), pooled by median."""
    ref = d[ref_mask].set_index("base")
    var = d[var_mask].set_index("base")
    j = var.join(ref[["E", "v_E", "n", "v_n"]], rsuffix="_ref", how="inner")
    j = j[(j["n_ref"] >= 100)]
    return dict(label=label, bases=int(len(j)), dE_dev_median=float((j["E"] - j["E_ref"]).median()),
                share_better_dev=float((j["E"] > j["E_ref"]).mean()),
                dE_val_median=float((j["v_E"] - j["v_E_ref"]).median()),
                share_better_val=float((j["v_E"] > j["v_E_ref"]).mean()),
                trades_kept=float((j["n"] / j["n_ref"]).median()))


def main():
    out = {}
    d4 = tagged("E4", RF.e4_tasks)
    base = (d4.be == 0) & (d4.trail == 0) & (d4.part_f == 0) & (d4.atr_p == 14)
    rows = []
    for tag in ("canon", "all"):
        dd = d4 if tag == "all" else d4[d4.base_tag == "canon"]
        b = base.loc[dd.index]
        for be in (0.75, 1.0, 1.25):
            rows.append(dict(set=tag, **effect(dd, b, (dd.be == be) & (dd.trail == 0) & (dd.part_f == 0) & (dd.atr_p == 14), f"break-even at {be}R")))
        for tr in (2.0, 2.5, 3.0, 3.5):
            for ap in (10, 14, 20):
                rows.append(dict(set=tag, **effect(dd, b, (dd.be == 0) & (dd.trail == tr) & (dd.part_f == 0) & (dd.atr_p == ap), f"chandelier {tr} x ATR{ap} (no target)")))
        rows.append(dict(set=tag, **effect(dd, b, (dd.be == 0) & (dd.trail == 3.0) & (dd.part_f == 0.5) & (dd.atr_p == 14), "50% at 1R + chandelier 3 x ATR14")))
        rows.append(dict(set=tag, **effect(dd, b, (dd.be == 1.0) & (dd.trail == 3.0) & (dd.part_f == 0.5) & (dd.atr_p == 14), "50% at 1R + BE 1R + chandelier 3")))
    out["management"] = rows
    d5 = tagged("E5", RF.e5_tasks)
    nofilt = (d5.filt == "") & (d5.imp == 0) & (d5.max_fails == -1) & (d5.vol == 0)
    rows = []
    for tag in ("canon", "all"):
        dd = d5 if tag == "all" else d5[d5.base_tag == "canon"]
        b = nofilt.loc[dd.index]
        for f in RF.FILTERS[1:]:
            rows.append(dict(set=tag, **effect(dd, b, (dd.filt == f) & (dd.imp == 0) & (dd.max_fails == -1) & (dd.vol == 0), f"filter {f}")))
        for imp in (1.5, 2.0, 3.0):
            rows.append(dict(set=tag, **effect(dd, b, (dd.filt == "") & (dd.imp == imp) & (dd.max_fails == -1), f"skip impulsive bar > {imp} ATR")))
        for mf in (0, 1, 2):
            rows.append(dict(set=tag, **effect(dd, b, (dd.filt == "") & (dd.imp == 0) & (dd.max_fails == mf), f"cancel after > {mf} failed attempts")))
        for v in (1.0, 1.5, 2.0):
            rows.append(dict(set=tag, **effect(dd, b, (dd.filt == "") & (dd.vol == v), f"breakout activity >= {v} x (USDJPY)")))
    out["filters"] = rows
    json.dump(out, open(f"{core.HERE}/../results/orb_component_effects.json", "w"), indent=1)
    for k in ("management", "filters"):
        print(f"\n{k.upper()}  (median change in R per trade vs same base without it)")
        print(pd.DataFrame(out[k]).round(3).to_string(index=False))
    # best robust management / filter per pick base, and its validation
    for nm, d in (("E4", d4), ("E5", d5)):
        print(f"\n{nm}: best robust variant per base (dev score) and its validation")
        res = []
        for bi, g in d.groupby("base"):
            if g.base_tag.iloc[0] == "canon":
                continue
            sc, nb = SEL.neighbour_score(g, g["t"].values, g["n"].values, 150)
            g = g.reset_index(drop=True); g["score"] = sc
            r = g.sort_values("score", ascending=False).iloc[0]
            res.append(dict(base=r.base_tag, sym=r.sym, session=r.session, orb=r.orb, be=r.be, trail=r.trail, part=r.part_f,
                            atr_p=r.atr_p, filt=r.filt, imp=r.imp, mf=r.max_fails, n=r.n, E=r.E, t=r.t, score=r.score,
                            v_n=r.v_n, v_E=r.v_E, v_t=r.v_t))
        print(pd.DataFrame(res).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
