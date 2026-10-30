"""Ablation over the full grids (development 2011-2019 only): for every ingredient, the paired change in
pooled expectancy when that one ingredient is switched and everything else is held fixed. Also the
per-side split asked for in experiment 1 / 2 (RBR vs DBD, DBR vs RBD).

    python3 ablation.py -> results/northstar/ablation.csv, sides.json
"""
import os, json
import numpy as np
import pandas as pd
from analyze import RES, PARAMS, keycols, ORDERED, TFS, family

SWITCHES = {"tf": None, "k": None, "nb": None, "entry": ["break", "retest"], "w": None, "d": None, "b": None, "g": None,
            "qk": None, "m": None, "level": ["near", "far"], "tgt": None, "trail": None, "bias": [0, 1]}


def main():
    rows = []
    for mod in PARAMS:
        S = pd.read_csv(os.path.join(RES, f"pooled_{mod.replace('+', '_')}.csv.gz"))
        keys = keycols(mod)
        for p in keys:
            if p not in SWITCHES or (p == "t"):
                continue
            vals = SWITCHES[p] or (TFS[family(mod)] if p == "tf" else ORDERED[p])
            others = [k for k in keys if k != p]
            base = S[S[p] == vals[0]].set_index(others)
            for v in vals[1:]:
                alt = S[S[p] == v].set_index(others)
                j = base[["dev_E", "dev_n"]].join(alt[["dev_E", "dev_n"]], rsuffix="_alt", how="inner")
                j = j[(j.dev_n >= 30) & (j.dev_n_alt >= 30)]
                if not len(j):
                    continue
                d = j.dev_E_alt - j.dev_E
                rows.append(dict(module=mod, ingredient=p, change=f"{vals[0]} -> {v}", pairs=len(j), median_dE=d.median(),
                                 share_better=(d > 0).mean(), median_trade_ratio=(j.dev_n_alt / j.dev_n).median()))
    A = pd.DataFrame(rows)
    A.to_csv(os.path.join(RES, "ablation.csv"), index=False)
    sides = {}
    for mod, names in (("SDC", ("RBR long", "DBD short")), ("SDR", ("DBR long", "RBD short"))):
        S = pd.read_csv(os.path.join(RES, f"pooled_{mod}.csv.gz"))
        for col_n, col_e, name in (("dev_nL", "dev_EL", names[0]), ("dev_nS", "dev_ES", names[1])):
            ok = S[S[col_n] >= 100]
            best = ok.sort_values(col_e, ascending=False).head(1)
            sides[name] = dict(configs_with_100_trades=int(len(ok)), share_positive=float((ok[col_e] > 0).mean()) if len(ok) else None,
                               median_E=float(ok[col_e].median()) if len(ok) else None,
                               best=best[keycols(mod) + [col_n, col_e]].to_dict("records")[0] if len(best) else None)
    json.dump(sides, open(os.path.join(RES, "sides.json"), "w"), indent=1, default=float)
    with pd.option_context("display.width", 200):
        print(A.round(3).to_string(index=False))
    print(json.dumps(sides, indent=1, default=float))


if __name__ == "__main__":
    main()
