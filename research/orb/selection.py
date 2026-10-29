"""ORB 50 — reading the experiment log, period statistics and robust (neighbourhood) selection.

period_stats() turns the per-year aggregates of any set of years into n, E, t, PF, long/short E,
gross E and the share of positive years. Selection functions take a period argument and the
default is the development period only.
"""
import os, glob
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "..", "results", "orb_experiments")
DEV = list(range(2011, 2020))
VAL = list(range(2020, 2023))
PARAM_COLS = ["sym", "session", "orb", "filt", "bias_kind", "bias_ema", "bias_z", "side", "buf", "entry", "tol",
              "pb_k", "pb_atr", "disp", "ebuf", "stop", "stop_k", "sbuf", "tgt", "trail", "part_f", "part_r", "be",
              "imp", "max_fails", "vol", "bias", "inval", "min_risk", "delay", "pb_hi", "max_tr", "atr_p", "min_fails"]


def load(stages):
    parts = [pd.read_csv(os.path.join(LOG, f"{s}.csv.gz")) for s in stages]
    df = pd.concat(parts, ignore_index=True)
    df["filt"] = df["filt"].fillna("")
    df["bias_kind"] = df["bias_kind"].fillna("")
    return df


def period_stats(df, years, prefix=""):
    n = sum(df[f"n_{y}"] for y in years)
    s = sum(df[f"s_{y}"] for y in years)
    ss = sum(df[f"ss_{y}"] for y in years)
    pos = sum(df[f"pos_{y}"] for y in years)
    neg = sum(df[f"neg_{y}"] for y in years)
    c = sum(df[f"c_{y}"] for y in years)
    nl = sum(df[f"nl_{y}"] for y in years)
    sl = sum(df[f"sl_{y}"] for y in years)
    E = s / n.where(n > 0)
    var = (ss - n * E ** 2) / (n - 1).where(n > 1)
    t = E / np.sqrt(var / n)
    out = pd.DataFrame({
        f"{prefix}n": n, f"{prefix}E": E, f"{prefix}t": t,
        f"{prefix}pf": pos / neg.where(neg > 0),
        f"{prefix}Egross": (s + c) / n.where(n > 0),
        f"{prefix}El": sl / nl.where(nl > 0), f"{prefix}Es": (s - sl) / (n - nl).where(n - nl > 0),
        f"{prefix}nl": nl,
        f"{prefix}yrs_pos": sum(((df[f"s_{y}"] > 0) & (df[f"n_{y}"] > 0)).astype(int) for y in years)
                            / sum((df[f"n_{y}"] > 0).astype(int) for y in years).clip(lower=1),
        f"{prefix}per_yr": n / len(years),
    })
    return out


ORDINAL = ["orb", "buf", "tol", "tgt", "disp", "pb_k", "pb_atr", "bias_ema", "bias_z", "atr_p", "stop_k",
           "be", "trail", "ebuf", "sbuf", "imp", "max_fails", "vol", "part_r"]


def neighbour_score(df, t, n, min_n=150):
    """Robust score per row = min(own t, median t of its neighbours). A neighbour matches the row
    in every parameter except one ordinal parameter, which sits one grid step away (grid steps
    are the sorted distinct values present in df). Rows with fewer than min_n trades or no
    finite t score -inf; a row without neighbours keeps its own t."""
    df = df.reset_index(drop=True)
    t = np.asarray(t, float); n = np.asarray(n, float)
    cols = [c for c in PARAM_COLS if c in df.columns]
    ords = [c for c in ORDINAL if c in cols and df[c].nunique() > 1]
    base = df[cols].astype(str).copy()
    for c in ords:
        lv = {v: i for i, v in enumerate(sorted(df[c].unique()))}
        base[c] = df[c].map(lv).astype(int).astype(str)
    keys = [tuple(x) for x in base.values]
    index = {k: i for i, k in enumerate(keys)}
    pos = {c: cols.index(c) for c in ords}
    score = np.full(len(df), -np.inf); nbm = np.full(len(df), np.nan)
    for i, k in enumerate(keys):
        if n[i] < min_n or not np.isfinite(t[i]):
            continue
        nb = []
        for c, p in pos.items():
            for dlt in (-1, 1):
                kk = list(k); kk[p] = str(int(kk[p]) + dlt)
                j = index.get(tuple(kk))
                if j is not None and np.isfinite(t[j]) and n[j] >= min_n / 2:
                    nb.append(t[j])
        med = float(np.median(nb)) if nb else t[i]
        nbm[i] = med
        score[i] = min(t[i], med)
    return score, nbm


def with_stats(df, years=DEV, prefix=""):
    df = df.reset_index(drop=True)
    return pd.concat([df, period_stats(df, years, prefix)], axis=1).copy()


def pick(df, years=DEV, min_n=150, group=("sym", "session")):
    """Best robust configuration per group, using only `years`. Neighbour scores are computed
    within each sym/session so ORB length is a neighbour dimension."""
    d = with_stats(df, years)
    out = []
    for _, g in d.groupby(list(group)):
        sc, nb = neighbour_score(g, g["t"].values, g["n"].values, min_n)
        g = g.copy(); g["score"] = sc; g["nb_t"] = nb
        out.append(g.sort_values("score", ascending=False).head(1))
    return pd.concat(out, ignore_index=True)


def walk_forward(df, test_years=range(2014, 2023), train_len=3, min_n=None, group=("sym", "session")):
    """Each test year: choose per group the best robust config on the previous train_len years,
    then record that config's result in the test year (aggregates only, so this reads exactly
    one unseen year per selection). Returns one row per (group, test year)."""
    rows = []
    for Y in test_years:
        tr_years = list(range(Y - train_len, Y))
        mn = min_n or int(150 * train_len / 9)
        sel = pick(df, tr_years, mn, group)
        for _, r in sel.iterrows():
            if not np.isfinite(r["score"]):
                continue
            rows.append(dict(year=Y, sym=r["sym"], session=r["session"], id=r["id"], orb=r["orb"],
                             train_t=r["t"], train_E=r["E"], score=r["score"],
                             n=r[f"n_{Y}"], s=r[f"s_{Y}"], ss=r[f"ss_{Y}"]))
    return pd.DataFrame(rows)
