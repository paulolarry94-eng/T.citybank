"""Exits judged the way a portfolio feels them: monthly Sharpe of each strategy's R summed over the
four markets (equal risk per trade), plus average holding time. Selected on 2011-2022; 2023-2025 shown."""
import os, json
import numpy as np
import runner as R, signals as SG
HERE = os.path.dirname(os.path.abspath(__file__))
FN = {"TC": lambda B, v: SG.tc(B, v), "VC": lambda B, v: SG.vc(B, *v.split("_")),
      "VE": lambda B, v: SG.ve(B, float(v.split("_")[0][1:]), v.split("_")[1])}
rules = json.load(open(os.path.join(HERE, "..", "results", "four", "locked_rules.json")))
M = {s: R.Mkt(s) for s in R.SYMS}
EXITS = [("plain (time exit 100 bars)", (0, 0, 0)), ("BE 0.5R", (0, 0.5, 0)), ("BE 1R", (0, 1, 0)), ("BE 2R", (0, 2, 0)),
         ("target 1R", (1, 0, 0)), ("target 1.5R", (1.5, 0, 0)), ("target 2R", (2, 0, 0)), ("target 3R", (3, 0, 0)), ("target 5R", (5, 0, 0)),
         ("trail 2 ATR", (0, 0, 2)), ("trail 3 ATR", (0, 0, 3)), ("trail 4 ATR", (0, 0, 4)),
         ("target 2R + BE 1R", (2, 1, 0)), ("target 3R + trail 3", (3, 0, 3)), ("target 2R + trail 2", (2, 0, 2)), ("target 3R + BE 1R", (3, 1, 0))]


def monthly(trs):
    s = np.zeros(180)
    for tr in trs:
        y = R.year_index(tr[:, 1].astype(np.int64))
        mo = ((tr[:, 1].astype(np.int64) // 86400) * 12 // 365.2425).astype(np.int64)
        import datetime as dt
        k = np.array([(dt.datetime.utcfromtimestamp(int(t)).year - 2011) * 12 + dt.datetime.utcfromtimestamp(int(t)).month - 1 for t in tr[:, 1]])
        ok = (k >= 0) & (k < 180); np.add.at(s, k[ok], tr[ok, 3])
    return s


out = {}
for fam in ("TC", "VC", "VE"):
    ru = rules[fam]; ents = {}
    for s in R.SYMS:
        B = M[s].bars(ru["tf"]); ents[s] = (B, *FN[fam](B, ru["var"]))
    rows = []
    for lab, (tg, be, tl) in EXITS + [("locked combination", (ru["tgt"], ru["be"], ru["trail"]))]:
        trs = [M[s].run(ents[s][0], *ents[s][1:], ("atr1.5", float(tg), float(be), float(tl)), cut=None) for s in R.SYMS]
        mon = monthly(trs)
        a, b = mon[:144], mon[144:]
        sh = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(12)
        allr = np.concatenate([t[:, 3] for t in trs]); hold = np.concatenate([(t[:, 1] - t[:, 0]) / 86400 for t in trs]).mean()
        rows.append((lab, sh(a), sh(b), float(allr.mean()), hold))
    rows.sort(key=lambda r: -r[1])
    out[fam] = rows
    print(f"\n{fam}: monthly Sharpe 2011-22 | 2023-25 | R per trade | avg hold (days)   [sorted by 2011-22 Sharpe]")
    for lab, s1, s2, e, h in rows:
        print(f"  {lab:28s} {s1:5.2f}  {s2:5.2f}  {e:+.3f}  {h:5.1f}")
json.dump(out, open(os.path.join(HERE, "..", "results", "four", "exit_sharpe.json"), "w"), indent=1)
