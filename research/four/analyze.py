"""Four strategies: what management does, and timeless selection.

Periods: development 2011-2019 (selection), validation 2020-2022 (short list only), final
2023-2025 (masked from the grid; see final.py). Sub-eras inside development: 2011-15 and 2016-19.
"""
import os, sys, json, gzip, warnings
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
warnings.simplefilter("ignore")
DEV, VAL = list(range(2011, 2020)), list(range(2020, 2023))
ERA1, ERA2 = list(range(2011, 2016)), list(range(2016, 2020))
TGTS, BES, TRAILS = [0.0, 1.0, 1.5, 2.0, 3.0, 5.0], [0.0, 0.5, 1.0, 1.5, 2.0], [0.0, 2.0, 3.0, 4.0]
KEY = ["sym", "tf", "fam", "var", "stop"]


def stats(df, years, p=""):
    n = sum(df[f"n_{y}"] for y in years); s = sum(df[f"s_{y}"] for y in years); ss = sum(df[f"ss_{y}"] for y in years)
    c = sum(df[f"c_{y}"] for y in years)
    E = s / n.where(n > 0); var = (ss - n * E ** 2) / (n - 1).where(n > 1); sd = np.sqrt(var)
    return pd.DataFrame({f"{p}n": n, f"{p}E": E, f"{p}t": E / (sd / np.sqrt(n)), f"{p}sr": E / sd,
                         f"{p}Eg": (s + c) / n.where(n > 0)})


def load():
    df = pd.read_csv(os.path.join(HERE, "..", "results", "four", "grid.csv.gz"))
    df = pd.concat([df, stats(df, DEV), stats(df, VAL, "v_"), stats(df, ERA1, "e1_"), stats(df, ERA2, "e2_")], axis=1)
    return df


def effects(df):
    """Change from adding one management element to the plain version (no target, no BE, no trail),
    holding entry and stop fixed. Median over all entry sets of a family; share improved."""
    out = []
    base = df[(df.tgt == 0) & (df.be == 0) & (df.trail == 0)].set_index(KEY)
    tests = [("breakeven", "be", BES[1:], dict(tgt=0, trail=0)), ("target (R)", "tgt", TGTS[1:], dict(be=0, trail=0)),
             ("chandelier trail (ATR)", "trail", TRAILS[1:], dict(tgt=0, be=0))]
    for fam in ("TC", "FB", "VC", "VE"):
        for label, col, vals, fixed in tests:
            for v in vals:
                q = df[(df.fam == fam) & (df[col] == v)]
                for k, x in fixed.items():
                    q = q[q[k] == x]
                j = q.set_index(KEY).join(base[["E", "v_E", "sr", "v_sr", "n"]], rsuffix="_b", how="inner")
                j = j[j.n_b >= 50]
                out.append(dict(fam=fam, element=label, value=v, sets=len(j),
                                dE_dev=float((j.E - j.E_b).median()), better_dev=float((j.E > j.E_b).mean()),
                                dE_val=float((j.v_E - j.v_E_b).median()), better_val=float((j.v_E > j.v_E_b).mean()),
                                dSR_dev=float((j.sr - j.sr_b).median()), dSR_val=float((j.v_sr - j.v_sr_b).median())))
    return pd.DataFrame(out)


def combos(df):
    """Best and worst target x breakeven x trail combinations per family (median E over entry sets)."""
    g = df[df.n >= 50].groupby(["fam", "tgt", "be", "trail"]).agg(E_dev=("E", "median"), E_val=("v_E", "median"),
                                                                 SR_dev=("sr", "median"), SR_val=("v_sr", "median")).reset_index()
    return g


def neighbour(df):
    """Robust score = min(own dev t, median dev t of neighbours one step away in target, BE or trail)."""
    df = df.reset_index(drop=True)
    pos = {"tgt": TGTS, "be": BES, "trail": TRAILS}
    idx = {tuple(r): i for i, r in enumerate(df[KEY + ["tgt", "be", "trail"]].itertuples(index=False, name=None))}
    t = df["t"].values; n = df["n"].values
    sc = np.full(len(df), -np.inf)
    for i, r in enumerate(df[KEY + ["tgt", "be", "trail"]].itertuples(index=False, name=None)):
        if n[i] < 100 or not np.isfinite(t[i]):
            continue
        nb = []
        for d, (col, vals) in enumerate(pos.items()):
            k = vals.index(r[5 + d])
            for kk in (k - 1, k + 1):
                if 0 <= kk < len(vals):
                    rr = list(r); rr[5 + d] = vals[kk]
                    j = idx.get(tuple(rr))
                    if j is not None and np.isfinite(t[j]):
                        nb.append(t[j])
        sc[i] = min(t[i], np.median(nb)) if nb else t[i]
    df["score"] = sc
    return df


def select(df):
    """Timeless development gate, then best robust config per family and market."""
    d = df[(df.n >= 100) & (df.E > 0) & (df.t >= 2.0) & (df.e1_E > 0) & (df.e2_E > 0)].copy()
    d = neighbour(df).loc[d.index] if len(d) else d
    picks = []
    for (fam, sym), g in d.groupby(["fam", "sym"]):
        g = g.sort_values("score", ascending=False)
        if len(g) and np.isfinite(g.score.iloc[0]) and g.score.iloc[0] >= 1.5:
            picks.append(g.iloc[0])
    return pd.DataFrame(picks)


if __name__ == "__main__":
    df = load()
    print(f"{len(df):,} runs | share dev E>0 {np.mean(df.E > 0):.1%}")
    print("\nBy family (median over all runs with >=50 dev trades): dev E / val E / before-cost dev E")
    print(df[df.n >= 50].groupby("fam")[["E", "v_E", "Eg", "t"]].median().round(3))
    print(df[df.n >= 50].groupby(["fam", "tf"])[["E", "v_E"]].median().round(3).unstack())
    eff = effects(df); eff.to_csv(os.path.join(HERE, "..", "results", "four", "effects.csv"), index=False)
    pd.set_option("display.width", 220)
    print("\nManagement effects (vs no target / no BE / no trail; same entries and stop):")
    print(eff.round(3).to_string(index=False))
    cb = combos(df); cb.to_csv(os.path.join(HERE, "..", "results", "four", "combos.csv"), index=False)
    for fam, g in cb.groupby("fam"):
        print(f"\n{fam}: best 6 management combos by median dev E (val alongside)")
        print(g.sort_values("E_dev", ascending=False).head(6).round(3).to_string(index=False))
    sel = select(df)
    cols = ["fam", "sym", "tf", "var", "stop", "tgt", "be", "trail", "n", "E", "t", "e1_E", "e2_E", "score", "v_n", "v_E", "v_t"]
    print("\nTimeless development picks (dev E>0, t>=2, both dev eras positive, robust score>=1.5), with validation:")
    print(sel[cols].round(3).to_string(index=False) if len(sel) else "none")
    sel.to_csv(os.path.join(HERE, "..", "results", "four", "picks.csv"), index=False)
