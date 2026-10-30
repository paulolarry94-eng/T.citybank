"""One-time final test of the four locked rules on every market, 2011-2025 (2023-2025 never seen by
any search). Saves each leg's trades for the central risk manager. Logged in orb_oos_log.json."""
import os, json, datetime as dt
import numpy as np
import runner as R, signals as SG
import gold_lab as GL

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
OUT = os.path.join(HERE, "..", "trades", "four"); os.makedirs(OUT, exist_ok=True)
FN = {"TC": lambda B, v: SG.tc(B, v), "VC": lambda B, v: SG.vc(B, *v.split("_")),
      "VE": lambda B, v: SG.ve(B, float(v.split("_")[0][1:]), v.split("_")[1]),
      "FB": lambda B, v: SG.fb(B, int(v.split("_")[0][1:]), v.split("_")[1], v.split("_")[2])}
PER = {"dev": (2011, 2019), "val": (2020, 2022), "oos": (2023, 2025)}


def st(r):
    if len(r) < 3:
        return dict(n=len(r), E=float(r.mean()) if len(r) else np.nan, t=np.nan)
    return dict(n=len(r), E=float(r.mean()), t=float(r.mean() / r.std(ddof=1) * np.sqrt(len(r))))


if __name__ == "__main__":
    rules = json.load(open(os.path.join(RES, "four", "locked_rules.json")))
    log_p = os.path.join(RES, "orb_oos_log.json")
    log = json.load(open(log_p)); log.append(dict(when=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                                                  label="four strategies: locked rules, 2011-2025 incl. final years", rules=rules))
    json.dump(log, open(log_p, "w"), indent=1)
    report = {}
    for fam, ru in rules.items():
        pooled = {p: [] for p in PER}
        for sym in R.SYMS:
            M = R.Mkt(sym); B = M.bars(ru["tf"])
            sig, side, stop = FN[fam](B, ru["var"])
            tr = M.run(B, sig, side, stop, (ru["stop"], ru["tgt"], ru["be"], ru["trail"]), cut=None)
            T = GL.pack(tr[:, :6].copy()) if len(tr) else np.zeros(0, dtype=GL.DT)
            T["entry"] = 0.0
            np.save(os.path.join(OUT, f"{fam}_{sym}.npy"), T)
            y = R.year_index(tr[:, 0].astype(np.int64))
            row = {}
            for p, (a, b) in PER.items():
                r = tr[(y >= a) & (y <= b), 3]; row[p] = st(r); pooled[p].append(r)
            report[f"{fam}|{sym}"] = row
            print(f"{fam} {sym}: " + " | ".join(f"{p} n {v['n']:4d} E {v['E']:+.3f} t {v['t']:+.2f}" for p, v in row.items()), flush=True)
        pr = {p: st(np.concatenate(v)) for p, v in pooled.items()}
        report[f"{fam}|ALL"] = pr
        print(f"{fam} ALL   : " + " | ".join(f"{p} n {v['n']:4d} E {v['E']:+.3f} t {v['t']:+.2f}" for p, v in pr.items()) + "\n", flush=True)
    json.dump(report, open(os.path.join(RES, "four", "final.json"), "w"), indent=1)
