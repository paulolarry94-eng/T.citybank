"""ORB 50 — walk-forward test of the selection procedure (Part 6) inside 2011-2022.

Every test year Y in 2014..2022: for each market/session, choose the best robust config of a
model's grid on years Y-3..Y-1 (neighbourhood score, as in development selection), then trade
it blind in year Y. Two rules: 'always' trades every selection; 'gated' trades only when the
training score is >= 1.0 (abstains when nothing looks good). Pooled results show whether picking
ORB parameters from recent history has paid in the following year."""
import json, warnings
import numpy as np
import pandas as pd
import core, selection as SEL

warnings.simplefilter("ignore")
MODELS = {"A pure ORB": ["E1"], "B trend ORB": ["E2"], "C pullback ORB": ["E3"], "A+B+C pooled": ["E1", "E2", "E3"]}


def pooled(w):
    n, s, ss = w["n"].sum(), w["s"].sum(), w["ss"].sum()
    if n < 3:
        return dict(n=int(n), E=np.nan, t=np.nan)
    E = s / n; var = (ss - n * E * E) / (n - 1)
    return dict(n=int(n), E=float(E), t=float(E / np.sqrt(var / n)))


def main():
    out = {}
    for name, stages in MODELS.items():
        df = SEL.load(stages)
        w = SEL.walk_forward(df)
        w.to_csv(f"{core.HERE}/../results/orb_experiments/WF_{stages[0] if len(stages) == 1 else 'ALL'}.csv", index=False)
        res = dict(always=pooled(w), gated=pooled(w[w["score"] >= 1.0]))
        res["by_year"] = {int(y): pooled(g) for y, g in w.groupby("year")}
        res["by_session"] = {k: pooled(g) for k, g in w.groupby("session")}
        res["by_sym"] = {k: pooled(g) for k, g in w.groupby("sym")}
        out[name] = res
        print(f"{name:16s} always: n={res['always']['n']:5d} E={res['always']['E']:+.3f} t={res['always']['t']:+.2f} | "
              f"gated: n={res['gated']['n']:5d} E={res['gated']['E']:+.3f} t={res['gated']['t']:+.2f}", flush=True)
        print("   by year:", " ".join(f"{y}:{v['E']:+.3f}" for y, v in res["by_year"].items()))
        print("   by sym :", " ".join(f"{k}:{v['E']:+.3f}(t{v['t']:+.1f})" for k, v in res["by_sym"].items()))
    json.dump(out, open(f"{core.HERE}/../results/orb_walkforward.json", "w"), indent=1)


if __name__ == "__main__":
    main()
