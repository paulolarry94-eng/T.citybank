"""FVG grid: overall picture, what each ingredient does, universal rules (pooled over markets) with
the development gate, validation for the top rules. Development 2011-2019, validation 2020-2022."""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.simplefilter("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "four"))
import analyze as A

df = pd.read_csv(os.path.join(HERE, "..", "results", "fvg", "grid.csv.gz"))
df = pd.concat([df, A.stats(df, A.DEV), A.stats(df, A.VAL, "v_"), A.stats(df, A.ERA1, "e1_"), A.stats(df, A.ERA2, "e2_")], axis=1)
pd.set_option("display.width", 220)
ok = df[df.n >= 50]
print(f"{len(df):,} runs | dev E>0: {np.mean(ok.E > 0):.1%} | dev t>2: {(ok.t > 2).sum()}")
print("\nMedian R per trade by mode x timeframe (dev | val | dev before costs):")
print(ok.groupby(["mode", "tf"])[["E", "v_E", "Eg"]].median().round(3).unstack())

print("\nWhat each ingredient does (median change in dev / val R per trade, same everything else):")
cfg = ["sym", "tf", "mode", "disp", "gmin", "stop", "tgt", "trail", "bias", "kill"]
def eff(col, a, b, q=ok):
    x = q[q[col] == a].set_index([c for c in cfg if c != col])[["E", "v_E"]]
    y = q[q[col] == b].set_index([c for c in cfg if c != col])[["E", "v_E"]]
    j = y.join(x, rsuffix="_a", how="inner")
    return len(j), (j.E - j.E_a).median(), (j.E > j.E_a).mean(), (j.v_E - j.v_E_a).median(), (j.v_E > j.v_E_a).mean()
for lab, col, a, b in (("displacement >= 1.0 ATR vs none", "disp", 0.0, 1.0), ("displacement >= 1.5 ATR vs none", "disp", 0.0, 1.5),
                       ("gap >= 0.3 ATR vs 0.1", "gmin", 0.1, 0.3), ("daily bias vs none", "bias", 0, 1),
                       ("killzones vs all day (M15)", "kill", 0, 1), ("stop at gap vs ICT origin", "stop", "origin", "gap"),
                       ("chandelier 3 ATR vs none", "trail", 0.0, 3.0), ("target 3R vs 1.5R", "tgt", 1.5, 3.0), ("no target vs 2R", "tgt", 2.0, 0.0)):
    n, d1, b1, d2, b2 = eff(col, a, b)
    print(f"  {lab:34s} sets {n:5d}  dev {d1:+.3f} ({b1:.0%} better)  val {d2:+.3f} ({b2:.0%} better)")
x = ok[ok["mode"] == "edge"].set_index([c for c in cfg if c != "mode"])[["E", "v_E"]]
y = ok[ok["mode"] == "ce"].set_index([c for c in cfg if c != "mode"])[["E", "v_E"]]
j = y.join(x, rsuffix="_a", how="inner")
print(f"  {'midpoint (CE) vs gap edge':34s} sets {len(j):5d}  dev {(j.E - j.E_a).median():+.3f} ({(j.E > j.E_a).mean():.0%} better)  val {(j.v_E - j.v_E_a).median():+.3f}")

ucfg = [c for c in cfg if c != "sym"]
num = [c for c in df.columns if c[:2] in ("n_", "s_", "ss", "c_", "nl", "sl")]
P = df.groupby(ucfg)[num].sum().reset_index()
P = pd.concat([P, A.stats(P, A.DEV), A.stats(P, A.VAL, "v_"), A.stats(P, A.ERA1, "e1_"), A.stats(P, A.ERA2, "e2_")], axis=1)
per = pd.concat([df[cfg], A.stats(df, A.DEV), A.stats(df, A.VAL, "v_")], axis=1)
P = P.merge(per.assign(p=per.E > 0).groupby(ucfg).p.sum().rename("mk_pos").reset_index(), on=ucfg)
P = P.merge(per.assign(p=per.v_E > 0).groupby(ucfg).p.sum().rename("mk_vpos").reset_index(), on=ucfg)
gate = P[(P.n >= 200) & (P.E > 0) & (P.e1_E > 0) & (P.e2_E > 0) & (P.mk_pos >= 3)]
print(f"\nUniversal rules passing the development gate: {len(gate)} of {len(P)}")
print(gate.sort_values("t", ascending=False)[ucfg + ["n", "E", "t", "e1_E", "e2_E", "mk_pos", "v_n", "v_E", "v_t", "mk_vpos"]].head(12).round(3).to_string(index=False))
print("\nBest per-market rules by dev t (dev gate: n>=100, E>0 in both eras), with validation:")
pm = df[(df.n >= 100) & (df.E > 0) & (df.e1_E > 0) & (df.e2_E > 0)]
for sym, g in pm.groupby("sym"):
    r = g.sort_values("t", ascending=False).head(2)
    print(r[cfg + ["n", "E", "t", "v_n", "v_E", "v_t"]].round(3).to_string(index=False, header=(sym == pm.sym.min())))
P.to_csv(os.path.join(HERE, "..", "results", "fvg", "universal.csv.gz"), index=False)
