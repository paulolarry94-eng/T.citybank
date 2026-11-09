"""Q26: payday_indices_v1's 2023-25 numbers recomputed on the clock-fixed HistData data (P29).

payday_indices_v1 had its one logged 2023-25 look on 2026-11-01 (research/results/truth/payday_indices_v1/oos_log.json),
on data whose US500 / NAS100 / UK100 / JP225 stamps were one hour late in daylight-saving periods. The lab replays a logged
look instead of recomputing it, so a re-run shows the old numbers. This script recomputes the same rule, same file, same
fingerprint, on the corrected data, for information only. It is not a new look of a new idea: the oos_log is left as it is.
Output: research/results/q26/payday_2023_25_corrected.json
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(R, "truth"))
import protocol as P
from grid import year_index
from confirm import stats

PATH = os.path.join(R, "truth", "strategies", "payday_indices_v1.py")
OUT = os.path.join(R, "results", "q26"); os.makedirs(OUT, exist_ok=True)


def main():
    S = P.load_strategy(PATH)
    log = json.load(open(os.path.join(R, "results", "truth", S.NAME, "oos_log.json")))
    assert all(e["fingerprint"] == S.FINGERPRINT for e in log), "strategy file changed since its logged look"
    e = log[0]; cfg = json.loads(e["config"])
    p = {k: cfg[k] for k in ["tf"] + list(S.GRID)}
    rows = []
    for i, s in enumerate(S.MARKETS):
        M = P.market(s, S)
        f = P.run_config(S, M, p, cfg["tgt"], cfg["trail"], cfg["bias"], cut=0)
        rows.append(np.c_[f, np.full(len(f), i)])
    F = np.vstack(rows); o = F[year_index(F[:, 0]) >= 2023]
    new = dict(oos=stats(o[:, 3]), per_market={s: stats(o[o[:, -1] == i, 3]) for i, s in enumerate(S.MARKETS)})
    res = dict(note=__doc__, fingerprint=S.FINGERPRINT, config=cfg, logged_look=dict(time=e["time"], oos=e["oos"],
               per_market=e["per_market"]), corrected_data=new)
    json.dump(res, open(os.path.join(OUT, "payday_2023_25_corrected.json"), "w"), indent=1, default=float)
    print("logged   ", {k: round(v, 4) for k, v in e["oos"].items()})
    print("corrected", {k: round(float(v), 4) for k, v in new["oos"].items()})
    for s in S.MARKETS:
        print(f"  {s:7s} logged E {e['per_market'][s]['E']:+.4f} n {e['per_market'][s]['n']}   corrected E "
              f"{new['per_market'][s]['E']:+.4f} n {new['per_market'][s]['n']}")


if __name__ == "__main__":
    main()
