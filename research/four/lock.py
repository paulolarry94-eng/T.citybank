"""Lock one universal rule per family: the highest pooled development t among rules that pass the
development gate (pooled n >= 200, E > 0 in both development eras, >= 3 of 4 markets positive).
Prints the neighbourhood (one step in target / BE / trail) to show the rule sits in a stable region."""
import os, json, warnings
import numpy as np, pandas as pd
warnings.simplefilter("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
P = pd.read_csv(os.path.join(HERE, "..", "results", "four", "universal.csv.gz"))
ok = P[(P.n >= 200) & (P.E > 0) & (P.e1_E > 0) & (P.e2_E > 0) & (P.mkts_pos >= 3)]
TG, BE, TR = [0.0, 1.0, 1.5, 2.0, 3.0, 5.0], [0.0, 0.5, 1.0, 1.5, 2.0], [0.0, 2.0, 3.0, 4.0]
rules = {}
for fam in ("TC", "FB", "VC", "VE"):
    r = ok[ok.fam == fam].sort_values("t", ascending=False).iloc[0]
    rules[fam] = dict(tf=r.tf, var=r["var"], stop=r.stop, tgt=float(r.tgt), be=float(r.be), trail=float(r.trail))
    same = P[(P.fam == fam) & (P.tf == r.tf) & (P["var"] == r["var"]) & (P.stop == r.stop)]
    nb = []
    for col, vals in (("tgt", TG), ("be", BE), ("trail", TR)):
        k = vals.index(float(r[col]))
        for kk in (k - 1, k + 1):
            if 0 <= kk < len(vals):
                q = same.copy()
                for c2 in ("tgt", "be", "trail"):
                    q = q[q[c2] == (vals[kk] if c2 == col else float(r[c2]))]
                if len(q):
                    nb.append((col, vals[kk], float(q.t.iloc[0]), float(q.E.iloc[0]), float(q.v_E.iloc[0])))
    print(f"\n{fam} locked: {rules[fam]} | dev E {r.E:+.3f} t {r.t:.2f} | val E {r.v_E:+.3f} t {r.v_t:.2f}")
    for col, v, t, E, vE in nb:
        print(f"   neighbour {col}={v:<4g}: dev t {t:+.2f}  dev E {E:+.3f}  val E {vE:+.3f}")
json.dump(rules, open(os.path.join(HERE, "..", "results", "four", "locked_rules.json"), "w"), indent=1)
