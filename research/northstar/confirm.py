"""Trade-level confirmation of each module candidate on development + validation (fills before 2023):
reproduces the grid numbers, runs the combined stress (costs x1.5, financing x2, +1 minute on market
entries), profit factors, and the deflated Sharpe ratio against the module's full grid.

    python3 confirm.py   (after analyze.py) -> results/northstar/confirm.json
"""
import os, sys, json, math
import numpy as np
import pandas as pd
from statistics import NormalDist
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import core, patterns as P
from grid import year_index, fvg_flags, qm_flags, SYMS
RES = os.path.join(HERE, "..", "results", "northstar")


def build(M, mod, cfg):
    """(B, candidates, keep) for one module configuration (same code path as grid.py)."""
    B = M.bars(cfg["tf"])
    if mod.startswith("SD"):
        kinds = ("DBR", "RBD") if mod == "SDR" else ("RBR", "DBD")
        C = P.sd_candidates(M, B, int(cfg["nb"]), float(cfg["k"]), kinds, cfg["entry"])
    elif mod == "FVG-A":
        C = P.fvg_candidates(M, B, "A", cfg["w"], cfg["d"], cfg["b"], int(cfg["g"]))
    elif mod == "FVG-B":
        C = P.fvg_candidates(M, B, "B", cfg["w"], age=int(cfg["g"]))
    elif mod == "FVG-C":
        C = P.fvg_candidates(M, B, "C", cfg["w"], 0.0, 0.0, 30, swings=P.swing_levels(B, 3))
    else:
        C = P.qm_candidates(M, B, int(cfg["qk"]), cfg["m"], cfg["level"], cfg["entry"], cfg["t"])
    keep = None
    if mod.endswith("+FVG"):
        keep = P.filter_keep(C, B, fvg_flags(B))
    elif mod.endswith("+QM"):
        keep = P.filter_keep(C, B, qm_flags(B))
    return B, C, keep


def run(M, mod, cfg, cut=core.CUT, **kw):
    B, C, keep = build(M, mod, cfg)
    return core.execute(M, B, C, cfg["tgt"], cfg["trail"], cut=cut, bias=bool(cfg["bias"]), keep=keep, **kw)


def stats(r):
    r = np.asarray(r, float)
    if len(r) < 2:
        return dict(n=int(len(r)), E=float(r.mean()) if len(r) else None)
    w, l = r[r > 0].sum(), -r[r < 0].sum()
    return dict(n=int(len(r)), E=float(r.mean()), t=float(r.mean() / r.std(ddof=1) * math.sqrt(len(r))),
                PF=float(w / l) if l > 0 else None, win=float((r > 0).mean()))


def deflated_sharpe(r, sr_trials, n_trials):
    """Bailey & Lopez de Prado (2014), per-trade Sharpe (same helper as research/orb/validate.py)."""
    r = np.asarray(r, float); T = len(r)
    sr = r.mean() / r.std(ddof=1)
    sk = ((r - r.mean()) ** 3).mean() / r.std() ** 3
    ku = ((r - r.mean()) ** 4).mean() / r.std() ** 4
    v = np.nanvar(sr_trials); g = 0.5772156649; N = NormalDist()
    sr0 = math.sqrt(v) * ((1 - g) * N.inv_cdf(1 - 1 / n_trials) + g * N.inv_cdf(1 - 1 / (n_trials * math.e)))
    z = (sr - sr0) * math.sqrt(T - 1) / math.sqrt(max(1 - sk * sr + (ku - 1) / 4 * sr ** 2, 1e-12))
    return dict(sr_trade=float(sr), sr0=float(sr0), dsr=float(N.cdf(z)), n_trials=int(n_trials), T=T)


def main():
    sel = json.load(open(os.path.join(RES, "selection.json")))
    mods = {m: r["candidate"] for m, r in sel.items() if r.get("candidate")}
    out = {}
    markets = {s: core.Mkt(s) for s in SYMS}
    for mod, cfg in mods.items():
        rows = {"base": [], "stress": []}
        for s, M in markets.items():
            for tag, kw in (("base", {}), ("stress", dict(cost_mult=1.5, swap_mult=2.0, delay=1))):
                tr = run(M, mod, cfg, **kw)
                rows[tag].append(np.c_[tr, np.full(len(tr), SYMS.index(s))])
        base = np.vstack(rows["base"]); st = np.vstack(rows["stress"])
        yb, ys = year_index(base[:, 0]), year_index(st[:, 0])
        dev, val = yb <= 2019, (yb >= 2020) & (yb <= 2022)
        pooled = pd.read_csv(os.path.join(RES, f"pooled_{mod.replace('+', '_')}.csv.gz"))
        srt = (pooled.dev_t / np.sqrt(pooled.dev_n)).replace([np.inf, -np.inf], np.nan).dropna()
        rec = dict(config=cfg, dev=stats(base[dev, 3]), val=stats(base[val, 3]), dev_val=stats(base[dev | val, 3]),
                   stress_dev_val=stats(st[ys <= 2022, 3]),
                   financing_R_per_trade=float(base[dev | val, 7].mean()), cost_R_per_trade=float(base[dev | val, 5].mean()),
                   per_market_dev={s: stats(base[dev & (base[:, 8] == i), 3]) for i, s in enumerate(SYMS)},
                   per_market_val={s: stats(base[val & (base[:, 8] == i), 3]) for i, s in enumerate(SYMS)},
                   long_dev=stats(base[dev & (base[:, 2] > 0), 3]), short_dev=stats(base[dev & (base[:, 2] < 0), 3]),
                   dsr=deflated_sharpe(base[dev, 3], srt.values, len(pooled)),
                   grid_check_dev_E=sel[mod]["stats"]["dev_E"], grid_check_dev_n=sel[mod]["stats"]["dev_n"])
        out[mod] = rec
        print(f"{mod:8s} dev n={rec['dev']['n']} E={rec['dev']['E']:.3f} t={rec['dev'].get('t', 0):.2f} | grid E={rec['grid_check_dev_E']:.3f} "
              f"n={rec['grid_check_dev_n']} | val E={rec['val'].get('E')} | stress E={rec['stress_dev_val'].get('E')} | DSR={rec['dsr']['dsr']:.3f}", flush=True)
    json.dump(out, open(os.path.join(RES, "confirm.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
