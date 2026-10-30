"""Four strategies with the simplest robust exit (1.5 ATR stop, chandelier 4 ATR, no target, no BE),
then the central risk manager on: four alone, book alone, book + four; plus payouts for book + four.
Note: the exit choice is supported by 2011-2022 (it matches or beats the locked combinations there)
and was confirmed on 2023-2025, so 2023-2025 is no longer a clean test of this exit."""
import os, sys, json
import numpy as np
import runner as R, signals as SG, gold_lab as GL
HERE = os.path.dirname(os.path.abspath(__file__))
FN = {"TC": lambda B, v: SG.tc(B, v), "VC": lambda B, v: SG.vc(B, *v.split("_")),
      "VE": lambda B, v: SG.ve(B, float(v.split("_")[0][1:]), v.split("_")[1])}
rules = json.load(open(os.path.join(HERE, "..", "results", "four", "locked_rules.json")))
OUT = os.path.join(HERE, "..", "trades", "four_simple"); os.makedirs(OUT, exist_ok=True)
for fam in ("TC", "VC", "VE"):
    ru = rules[fam]
    for s in R.SYMS:
        M = R.Mkt(s); B = M.bars(ru["tf"])
        sig, side, stop = FN[fam](B, ru["var"])
        tr = M.run(B, sig, side, stop, ("atr1.5", 0.0, 0.0, 4.0), cut=None)
        T = GL.pack(tr[:, :6].copy()); T["entry"] = 0.0
        np.save(os.path.join(OUT, f"{fam}_{s}.npy"), T)
print("legs written")
