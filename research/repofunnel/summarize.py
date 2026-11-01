"""Tables for the repo-funnel report from the Truth Lab grids (with swaps, and the low-cost swap-free view).

    python3 research/repofunnel/summarize.py   ->  research/results/repofunnel/cfd_table.csv (+ printed tables)
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results", "truth"); OUT = os.path.join(HERE, "..", "results", "repofunnel")
FILES = {"funnel_trustdan_v1": ["rule"], "funnel_sofus_v1": ["rule", "side"], "ath_trend_v1": ["side"], "payday_indices_v1": ["day"]}
DEV, E1, E2, VAL, OOS = range(2011, 2020), range(2011, 2016), range(2016, 2020), range(2020, 2023), range(2023, 2026)


def block(g, years):
    n = sum(g[f"n_{y}"].sum() for y in years); s = sum(g[f"s_{y}"].sum() for y in years)
    ss = sum(g[f"ss_{y}"].sum() for y in years); c = sum(g[f"c_{y}"].sum() for y in years); f = sum(g[f"f_{y}"].sum() for y in years)
    E = s / n.where(n > 0); sd = np.sqrt((ss / n.where(n > 0) - E ** 2).clip(lower=1e-12))
    return pd.DataFrame({"n": n, "E": E, "t": E / sd * np.sqrt(n), "E_sf": (s + 0.5 * c + f) / n.where(n > 0), "fin": f / n.where(n > 0)})


def table(name, keys):
    df = pd.read_csv(os.path.join(RES, name, "grid.csv.gz"))
    g = df.groupby(keys)
    T = pd.concat([block(g, DEV).add_prefix("dev_"), block(g, E1)[["E"]].add_prefix("e1_"), block(g, E2)[["E"]].add_prefix("e2_"),
                   block(g, VAL)[["n", "E", "E_sf"]].add_prefix("val_")], axis=1)
    gm = df.groupby(keys + ["sym"])
    M = block(gm, DEV)
    T["mk_pos"] = (M["E"] > 0).groupby(level=list(range(len(keys)))).sum()
    T["mk_pos_sf"] = (M["E_sf"] > 0).groupby(level=list(range(len(keys)))).sum()
    T["markets"] = df.sym.nunique()
    need = int(np.ceil(0.75 * T["markets"].iloc[0]))
    T["gate"] = (T.dev_n >= 200) & (T.e1_E > 0) & (T.e2_E > 0) & (T.mk_pos >= need)
    T["gate_sf_breadth"] = (T.mk_pos_sf >= need)
    best_sf = M["E_sf"].unstack("sym")
    T.insert(0, "file", name)
    return T.reset_index(), best_sf


def main():
    rows = []
    for name, keys in FILES.items():
        if not os.path.exists(os.path.join(RES, name, "grid.csv.gz")):
            continue
        T, M = table(name, keys)
        summ = json.load(open(os.path.join(RES, name, "summary.json")))
        T["lab_verdict"] = summ.get("verdict")
        rows.append(T)
        M.round(3).to_csv(os.path.join(OUT, f"{name}_dev_swapfree_by_market.csv"))
    A = pd.concat(rows, ignore_index=True)
    A.to_csv(os.path.join(OUT, "cfd_table.csv"), index=False, float_format="%.4f")
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
    cols = [c for c in ["file", "rule", "side", "day", "dev_n", "dev_E", "dev_t", "e1_E", "e2_E", "val_E", "mk_pos", "dev_E_sf", "val_E_sf", "mk_pos_sf", "gate"] if c in A.columns]
    print(A[cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
