"""Pool the ablation runs across all market/session/ORB combinations (and per session)."""
import json, warnings
import numpy as np
import pandas as pd
import core, selection as SEL

warnings.simplefilter("ignore")


def pool(g, years):
    n = sum(g[f"n_{y}"].sum() for y in years); s = sum(g[f"s_{y}"].sum() for y in years)
    ss = sum(g[f"ss_{y}"].sum() for y in years); c = sum(g[f"c_{y}"].sum() for y in years)
    E = s / n; var = (ss - n * E * E) / (n - 1)
    return dict(n=int(n), E=float(E), t=float(E / np.sqrt(var / n)), Egross=float((s + c) / n))


def main(years_sets=(("dev", SEL.DEV), ("val", SEL.VAL))):
    df = SEL.load(["AB"]).merge(pd.read_csv(f"{core.HERE}/../results/orb_experiments/AB_labels.csv"), on="id")
    out = {}
    order = list(dict.fromkeys(df["variant"]))
    for scope, sub in [("all 56 combos", df)] + [(f"session {s}", df[df.session == s]) for s in core.SESSIONS] + \
                      [("XAUUSD LDN", df[(df.sym == "XAUUSD") & (df.session == "LDN")])]:
        rows = []
        for v in order:
            g = sub[sub.variant == v]
            r = dict(variant=v, kind=g.kind.iloc[0])
            for nm, yrs in years_sets:
                p = pool(g, yrs)
                r.update({f"{nm}_{k}": p[k] for k in p})
            rows.append(r)
        out[scope] = rows
        print(f"\n== {scope}")
        print(pd.DataFrame(rows).round(3).to_string(index=False))
    json.dump(out, open(f"{core.HERE}/../results/orb_ablation.json", "w"), indent=1)


if __name__ == "__main__":
    main()
