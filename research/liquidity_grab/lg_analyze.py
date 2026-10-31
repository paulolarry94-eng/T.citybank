"""Liquidity-grab selection, confirmation and the one logged 2023-25 look, with the North Star machinery.

    python3 lg_analyze.py -> ../results/liquidity_grab/{summary.csv, selection.json, confirm.json, oos_log.json, tiers.json}
"""
import os, sys, json, time
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "northstar"))
import analyze as A
import core
from confirm import stats, deflated_sharpe
from grid import year_index, SYMS
from oos import tier
import lg

RES = os.path.join(HERE, "..", "results", "liquidity_grab")
A.PARAMS.clear()
A.PARAMS.update({"LG1": ["tf", "k", "age", "depth"], "LG2": ["tf", "k", "tol"], "LG3": ["tf", "k", "win"], "LG4": ["tf"]})
A.ORDERED.update({"k": [3, 5], "age": [5, 20], "depth": [0.5, 1.0], "tol": [0.1, 0.25], "win": [5, 10]})
A.TFS["LG"] = lg.TFS
A.family = lambda mod: "LG"


def load():
    df = pd.read_csv(os.path.join(RES, "grid.csv.gz"))
    for c in ("k", "age", "depth", "tol", "win"):
        df[c] = df[c].astype(float)
    return df


def main():
    df = load(); sel = {}; rows = []
    for mod in A.PARAMS:
        P, per, S = A.pooled(df, mod)
        r = dict(module=mod, configs=len(S), passed_gate=int(S.gate.sum()), share_dev_pos=float((S.dev_E > 0).mean()),
                 median_dev_E=float(S.dev_E.median()), best_dev_E_n200=float(S[S.dev_n >= 200].dev_E.max()) if (S.dev_n >= 200).any() else None,
                 share_pos_exness_dev=float(((2 * S.dev_E - S.dev_Es) > 0).mean()),            # costs x0.5, no swap: E + (E - Es - fin) + fin
                 share_pos_exness_dev_and_val=float((((2 * S.dev_E - S.dev_Es) > 0) & ((2 * S.val_E - S.val_Es) > 0)).mean()))
        rec = dict(module=mod, configs=len(S), passed_gate=int(S.gate.sum()), candidate=None)
        if S.gate.any():
            G = S[S.gate].sort_values("dev_t", ascending=False); key = G.index[0]
            c = {k: A.jsonable(v) for k, v in zip(A.keycols(mod), key)}
            st = {k: A.jsonable(v) for k, v in S.loc[key].items() if k != "gate"}
            nb = A.neighbours(mod, key, S); nbt = [x["dev_t"] for x in nb]
            rec.update(candidate=c, stats=st, neighbours=nb, neighbours_all_pos=bool(all(x["dev_E"] > 0 for x in nb)) if nb else False,
                       neighbours_median_t=float(np.median(nbt)) if nbt else None, walk_forward=A.walk_forward(P, per, mod))
            r.update(cand=" ".join(f"{k}={v}" for k, v in c.items()), dev_n=st["dev_n"], dev_E=st["dev_E"], dev_t=st["dev_t"], val_E=st["val_E"],
                     wf_E=rec["walk_forward"]["E"], nb_ok=rec["neighbours_all_pos"])
        sel[mod] = rec; rows.append(r)
        S.reset_index().to_csv(os.path.join(RES, f"pooled_{mod}.csv.gz"), index=False)
    pd.DataFrame(rows).to_csv(os.path.join(RES, "summary.csv"), index=False)
    json.dump(sel, open(os.path.join(RES, "selection.json"), "w"), indent=1, default=A.jsonable)
    with pd.option_context("display.width", 250, "display.max_columns", 20):
        print(pd.DataFrame(rows).round(3).to_string(index=False))
    # ---- trade-level confirmation + one logged look, for module candidates only
    cands = {m: r["candidate"] for m, r in sel.items() if r.get("candidate")}
    if not cands:
        print("no module passed the development gate"); return
    markets = {s: core.Mkt(s) for s in SYMS}
    conf, tiers = {}, {}
    logp = os.path.join(RES, "oos_log.json"); log = json.load(open(logp)) if os.path.exists(logp) else []
    for mod, cfg in cands.items():
        base, strs, full = [], [], []
        for i, s in enumerate(SYMS):
            b = lg.run(markets[s], mod, cfg); base.append(np.c_[b, np.full(len(b), i)])
            x = lg.run(markets[s], mod, cfg, cost_mult=1.5, swap_mult=2.0, delay=1); strs.append(x)
            f = lg.run(markets[s], mod, cfg, cut=0); full.append(np.c_[f, np.full(len(f), i)])
        B = np.vstack(base); X = np.vstack(strs); F = np.vstack(full)
        yb = year_index(B[:, 0]); dev, val = yb <= 2019, (yb >= 2020) & (yb <= 2022)
        pooled = pd.read_csv(os.path.join(RES, f"pooled_{mod}.csv.gz"))
        srt = (pooled.dev_t / np.sqrt(pooled.dev_n)).replace([np.inf, -np.inf], np.nan).dropna()
        conf[mod] = dict(dev=stats(B[dev, 3]), val=stats(B[val, 3]), stress_dev_val=stats(X[year_index(X[:, 0]) <= 2022, 3]),
                         dsr=deflated_sharpe(B[dev, 3], srt.values, len(pooled)))
        key = mod + " " + json.dumps(cfg, sort_keys=True)
        prior = [e for e in log if e["key"] == key]
        o = F[year_index(F[:, 0]) >= 2023]
        e = prior[0] if prior else dict(key=key, time=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), oos=stats(o[:, 3]),
                                         per_market={s: stats(o[o[:, 8] == i, 3]) for i, s in enumerate(SYMS)},
                                         exness_like=dict(dev=stats(B[dev, 3] + 0.5 * B[dev, 5] + B[dev, 7]), val=stats(B[val, 3] + 0.5 * B[val, 5] + B[val, 7]),
                                                          oos=stats(o[:, 3] + 0.5 * o[:, 5] + o[:, 7])))
        if not prior:
            log.append(e)
        t, crit = tier(sel[mod], conf[mod], e)
        tiers[mod] = dict(tier=t, criteria=crit, config=cfg, oos=e["oos"], per_market=e["per_market"], exness_like=e["exness_like"], dsr=conf[mod]["dsr"]["dsr"])
        print(f"\n{mod} {cfg}\n  dev {conf[mod]['dev']}\n  val {conf[mod]['val']}\n  stress {conf[mod]['stress_dev_val']}\n  DSR {conf[mod]['dsr']['dsr']:.3f}"
              f"\n  2023-25 {e['oos']}\n  per market " + str({s: (v['n'], round(v.get('E') or 0, 3)) for s, v in e['per_market'].items()}) +
              f"\n  Exness-like (costs x0.5, no swap): dev {e['exness_like']['dev'].get('E')}, val {e['exness_like']['val'].get('E')}, 2023-25 {e['exness_like']['oos'].get('E')}"
              f"\n  -> {t} {crit}")
    json.dump(log, open(logp, "w"), indent=1, default=float)
    json.dump(conf, open(os.path.join(RES, "confirm.json"), "w"), indent=1, default=float)
    json.dump(tiers, open(os.path.join(RES, "tiers.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
