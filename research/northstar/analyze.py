"""North Star selection on the grid (no final out-of-sample data is used here).

Per module, pooled over the four markets with identical parameters (PREREGISTRATION.md §5 + amendment 1):
development gate -> rank by development t -> candidate; then neighbours, validation 2020-2022,
walk-forward 2014-2022 and logged-sum cost/financing stress. Combination filters: paired increments.

    python3 analyze.py  -> results/northstar/selection.json, module_summary.csv
"""
import os, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results", "northstar")
SYMS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
DEV = list(range(2011, 2020)); ERA1 = list(range(2011, 2016)); ERA2 = list(range(2016, 2020)); VAL = [2020, 2021, 2022]
SD = ["tf", "k", "nb", "entry"]; QMP = ["tf", "qk", "m", "level", "entry", "t"]
FA = ["tf", "w", "d", "b", "g"]
PARAMS = {"SDC": SD, "SDR": SD, "FVG-A": FA, "FVG-B": ["tf", "w", "g"], "FVG-C": ["tf", "w"], "FVG-D": FA,
          "QM": QMP, "QM+FVG": QMP, "SDC+FVG": SD, "SDC+QM": SD}       # experiment order
COMMON = ["tgt", "trail", "bias"]
TFS = {"SD": ["M5", "M15", "M30", "H1", "H4"], "FVG": ["M5", "M15", "M30", "H1"], "QM": ["M15", "M30", "H1", "H4"]}
ORDERED = {"k": [1.0, 1.5], "nb": [1, 2, 3], "w": [0.1, 0.3], "d": [0.0, 0.5], "b": [0.0, 0.1], "g": [10, 30],
           "qk": [2, 3, 5], "m": [0.25, 0.5], "t": [0.0, 0.25], "tgt": [2.0, 3.0, 0.0], "trail": [0.0, 3.0]}
PRIMARY = {"SDC+FVG": "SDC", "SDC+QM": "SDC", "QM+FVG": "QM"}


def family(mod):
    return "SD" if mod.startswith("SD") else ("FVG" if mod.startswith("FVG") else "QM")


def load():
    df = pd.read_csv(os.path.join(RES, "grid.csv.gz"))
    for c in ("k", "nb", "w", "d", "b", "g", "qk", "m", "t"):
        df[c] = df[c].astype(float)
    D = df[(df.module == "FVG-A") & (df.bias == 1)].copy(); D["module"] = "FVG-D"     # model D = A with the H4 bias
    return pd.concat([df, D], ignore_index=True)


def keycols(mod):
    return PARAMS[mod] + COMMON


def summ(D, years, pre=""):
    """Vectorised pooled stats over the given years from per-year sufficient statistics."""
    n = sum(D[f"n_{y}"] for y in years); s = sum(D[f"s_{y}"] for y in years); ss = sum(D[f"ss_{y}"] for y in years)
    c = sum(D[f"c_{y}"] for y in years); f = sum(D[f"f_{y}"] for y in years)
    nl = sum(D[f"nl_{y}"] for y in years); sl = sum(D[f"sl_{y}"] for y in years)
    E = s / n.where(n > 0)
    sd = np.sqrt((ss / n.where(n > 0) - E ** 2).clip(lower=1e-12))
    out = pd.DataFrame({pre + "n": n, pre + "E": E, pre + "t": E / sd * np.sqrt(n), pre + "Es": (s - 0.5 * c - f) / n.where(n > 0),
                        pre + "fin": f / n.where(n > 0), pre + "nL": nl, pre + "EL": sl / nl.where(nl > 0),
                        pre + "nS": n - nl, pre + "ES": (s - sl) / (n - nl).where(n - nl > 0)})
    return out


def pooled(df, mod):
    d = df[df.module == mod]
    k = keycols(mod)
    num = [c for c in d.columns if c[:2] in ("n_", "s_", "ss", "c_", "f_", "nl", "sl")]
    P = d.groupby(k, dropna=False)[num].sum()
    per = {s: d[d.sym == s].set_index(k)[num] for s in SYMS}
    S = pd.concat([summ(P, DEV, "dev_"), summ(P, ERA1, "e1_"), summ(P, ERA2, "e2_"), summ(P, VAL, "val_"),
                   summ(P, DEV + VAL, "dv_")], axis=1)
    for s in SYMS:
        m = summ(per[s].reindex(P.index), DEV)
        S[f"devE_{s}"] = m["E"]; S[f"devn_{s}"] = m["n"]
        v = summ(per[s].reindex(P.index), VAL)
        S[f"valE_{s}"] = v["E"]
    S["mk_pos"] = sum((S[f"devE_{s}"] > 0).astype(int) for s in SYMS)
    S["gate"] = (S.dev_n >= 200) & (S.e1_E > 0) & (S.e2_E > 0) & (S.mk_pos >= 3)
    return P, per, S


def neighbours(mod, key, S):
    names = keycols(mod); cfg = dict(zip(names, key)); out = []
    lists = dict(ORDERED); lists["tf"] = TFS[family(mod)]
    for p in names:
        if p not in lists or (p == "t" and cfg.get("entry") != "retest"):
            continue
        L = lists[p]
        if cfg[p] not in L:
            continue
        i = L.index(cfg[p])
        for j in (i - 1, i + 1):
            if 0 <= j < len(L):
                c2 = dict(cfg); c2[p] = L[j]
                k2 = tuple(c2[x] for x in names)
                if k2 in S.index:
                    out.append(dict(param=p, value=L[j], dev_E=float(S.loc[k2, "dev_E"]), dev_t=float(S.loc[k2, "dev_t"]),
                                    dev_n=int(S.loc[k2, "dev_n"])))
    return out


def walk_forward(P, per, mod):
    """Re-select each year on the 3 preceding years (≥100 trades, E>0, ≥3 of 4 markets positive, max t)."""
    picks = []; n = s = 0.0
    for Y in range(2014, 2023):
        tr = [Y - 3, Y - 2, Y - 1]
        S = summ(P, tr)
        pos = sum((summ(per[x].reindex(P.index), tr)["E"] > 0).astype(int) for x in SYMS)
        ok = (S.n >= 100) & (S.E > 0) & (pos >= 3)
        if not ok.any():
            picks.append(dict(year=Y, pick=None, n=0, E=None)); continue
        k = S[ok].t.idxmax()
        ny, sy = float(P.loc[k, f"n_{Y}"]), float(P.loc[k, f"s_{Y}"])
        n += ny; s += sy
        picks.append(dict(year=Y, pick=[str(x) for x in k], n=int(ny), E=sy / ny if ny else None))
    return dict(E=s / n if n else None, n=int(n), picks=picks)


def jsonable(x):
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    return x


def main():
    df = load(); sel = {}; summary = []
    for mod in PARAMS:
        P, per, S = pooled(df, mod)
        n_cfg = len(S); n_gate = int(S.gate.sum())
        row = dict(module=mod, configs=n_cfg, passed_gate=n_gate,
                   share_dev_pos=float((S.dev_E > 0).mean()), share_dev_n200=float((S.dev_n >= 200).mean()),
                   median_dev_E=float(S.dev_E.median()))
        rec = dict(module=mod, configs=n_cfg, passed_gate=n_gate, candidate=None)
        if n_gate:
            G = S[S.gate].sort_values("dev_t", ascending=False)
            key = G.index[0]
            c = {k: jsonable(v) for k, v in zip(keycols(mod), key)}
            st = {k: jsonable(v) for k, v in S.loc[key].items() if k != "gate"}
            nb = neighbours(mod, key, S)
            nbt = [x["dev_t"] for x in nb]
            rec.update(candidate=c, stats=st, neighbours=nb,
                       neighbours_all_pos=bool(all(x["dev_E"] > 0 for x in nb)) if nb else False,
                       neighbours_median_t=float(np.median(nbt)) if nbt else None,
                       walk_forward=walk_forward(P, per, mod),
                       top5=[dict(cfg=[str(x) for x in k], dev_t=float(G.loc[k, "dev_t"]), dev_E=float(G.loc[k, "dev_E"]),
                                  dev_n=int(G.loc[k, "dev_n"]), val_E=jsonable(G.loc[k, "val_E"])) for k in G.index[:5]])
            row.update(cand=" ".join(f"{k}={v}" for k, v in c.items()), dev_n=st["dev_n"], dev_E=st["dev_E"], dev_t=st["dev_t"],
                       val_E=st["val_E"], val_t=st["val_t"], wf_E=rec["walk_forward"]["E"], nb_ok=rec["neighbours_all_pos"],
                       nb_med_t=rec["neighbours_median_t"], stress_dv_E=st["dv_Es"], fin_R=st["dev_fin"])
        if mod in PRIMARY:                                   # paired incremental value of the filter
            _, _, S0 = pooled(df, PRIMARY[mod])
            j = S.join(S0[["dev_E", "dev_t", "dev_n"]], rsuffix="_base")
            j = j[(j.dev_n >= 30) & (j.dev_n_base >= 30)]
            dE = j.dev_E - j.dev_E_base
            rec["increment"] = dict(pairs=int(len(j)), median_dE=jsonable(dE.median()), share_improved=jsonable((dE > 0).mean()),
                                    median_trade_share=jsonable((j.dev_n / j.dev_n_base).median()))
            row.update(inc_median_dE=rec["increment"]["median_dE"], inc_share_improved=rec["increment"]["share_improved"])
        sel[mod] = rec; summary.append(row)
        S.reset_index().to_csv(os.path.join(RES, f"pooled_{mod.replace('+', '_')}.csv.gz"), index=False)
    pd.DataFrame(summary).to_csv(os.path.join(RES, "module_summary.csv"), index=False)
    json.dump(sel, open(os.path.join(RES, "selection.json"), "w"), indent=1, default=jsonable)
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(pd.DataFrame(summary).drop(columns=["cand"], errors="ignore").round(3).to_string())
        for r in summary:
            print(r["module"], "->", r.get("cand"))


if __name__ == "__main__":
    main()
