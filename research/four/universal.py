"""Universal rules: one configuration per family applied to all four markets. Development stats
are pooled across markets (sums of trades, R and R^2); a rule must be positive in development in
each era AND have at least 3 of 4 markets positive in development. Ranked by pooled development t;
validation shown per market only for the top rules."""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.simplefilter("ignore")
import analyze as A

df = pd.read_csv(os.path.join(A.HERE, "..", "results", "four", "grid.csv.gz"))
cfg = ["tf", "fam", "var", "stop", "tgt", "be", "trail"]
num = [c for c in df.columns if c[:2] in ("n_", "s_", "ss", "c_", "nl", "sl")]
P = df.groupby(cfg)[num].sum().reset_index()
P = pd.concat([P, A.stats(P, A.DEV), A.stats(P, A.VAL, "v_"), A.stats(P, A.ERA1, "e1_"), A.stats(P, A.ERA2, "e2_")], axis=1)
per = pd.concat([df[cfg + ["sym"]], A.stats(df, A.DEV), A.stats(df, A.VAL, "v_")], axis=1)
pos = per.assign(p=per.E > 0).groupby(cfg).p.sum().rename("mkts_pos").reset_index()
vpos = per.assign(p=per.v_E > 0).groupby(cfg).p.sum().rename("mkts_vpos").reset_index()
P = P.merge(pos, on=cfg).merge(vpos, on=cfg)
ok = P[(P.n >= 200) & (P.E > 0) & (P.e1_E > 0) & (P.e2_E > 0) & (P.mkts_pos >= 3)]
pd.set_option("display.width", 220)
for fam in ("TC", "FB", "VC", "VE"):
    g = ok[ok.fam == fam].sort_values("t", ascending=False)
    print(f"\n{fam}: {len(g)} universal rules pass the development gate. Top 8 by pooled dev t (validation pooled and markets positive):")
    print(g[cfg + ["n", "E", "t", "e1_E", "e2_E", "mkts_pos", "v_n", "v_E", "v_t", "mkts_vpos"]].head(8).round(3).to_string(index=False))
P.to_csv(os.path.join(A.HERE, "..", "results", "four", "universal.csv.gz"), index=False)
