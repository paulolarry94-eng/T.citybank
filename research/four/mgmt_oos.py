"""Do the management findings hold in 2023-2025? Locked TC / VC / VE entries, all four markets
pooled; one element changed at a time from the plain exit (no target, no BE, no trail).
Reporting only (logged as a look at the final years)."""
import os, json, datetime as dt
import numpy as np
import runner as R
import signals as SG
FN = {"TC": lambda B, v: SG.tc(B, v), "VC": lambda B, v: SG.vc(B, *v.split("_")),
      "VE": lambda B, v: SG.ve(B, float(v.split("_")[0][1:]), v.split("_")[1])}

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "..", "results")
rules = json.load(open(os.path.join(RES, "four", "locked_rules.json")))
log = json.load(open(os.path.join(RES, "orb_oos_log.json")))
log.append(dict(when=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), label="four: management variants on 2023-2025 (reporting)"))
json.dump(log, open(os.path.join(RES, "orb_oos_log.json"), "w"), indent=1)
M = {s: R.Mkt(s) for s in R.SYMS}
out = {}
for fam in ("TC", "VC", "VE"):
    ru = rules[fam]
    ents = {}
    for s in R.SYMS:
        B = M[s].bars(ru["tf"]); ents[s] = (B, *FN[fam](B, ru["var"]))
    def pooled(mg):
        rs = {"dev": [], "val": [], "oos": []}
        for s in R.SYMS:
            B, sig, side, stop = ents[s]
            tr = M[s].run(B, sig, side, stop, mg, cut=None)
            y = R.year_index(tr[:, 0].astype(np.int64))
            for p, (a, b) in (("dev", (2011, 2019)), ("val", (2020, 2022)), ("oos", (2023, 2025))):
                rs[p].append(tr[(y >= a) & (y <= b), 3])
        return {p: float(np.concatenate(v).mean()) for p, v in rs.items()}
    plain = pooled((ru["stop"], 0.0, 0.0, 0.0))
    rows = [("plain (no target, BE or trail)", plain)]
    for be in (0.5, 1.0, 1.5, 2.0):
        rows.append((f"breakeven {be}R", pooled((ru["stop"], 0.0, be, 0.0))))
    for tg in (1.0, 1.5, 2.0, 3.0, 5.0):
        rows.append((f"target {tg}R", pooled((ru["stop"], tg, 0.0, 0.0))))
    for tl in (2.0, 3.0, 4.0):
        rows.append((f"chandelier {tl} ATR", pooled((ru["stop"], 0.0, 0.0, tl))))
    rows.append(("locked combination", pooled((ru["stop"], ru["tgt"], ru["be"], ru["trail"]))))
    out[fam] = rows
    print(f"\n{fam} ({ru['tf']} {ru['var']}, stop {ru['stop']}): R per trade dev / val / 2023-25")
    for lab, v in rows:
        print(f"  {lab:32s} {v['dev']:+.3f}  {v['val']:+.3f}  {v['oos']:+.3f}")
json.dump(out, open(os.path.join(RES, "four", "mgmt_oos.json"), "w"), indent=1)
