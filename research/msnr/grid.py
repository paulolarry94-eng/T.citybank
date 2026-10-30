"""Full Malaysian SnR / engulfing grid on all four markets, judged by the timeless funnel."""
import os, sys, json, time, itertools
from multiprocessing import Pool
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import msnr_lab as M, gold_search as GS

SYMS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]


def configs(sym):
    C = []
    for tf, k, mode in itertools.product(("M15", "M30", "H1", "H4"), (1, 3), ("limit", "engulf", "failed", "rbs")):
        C.append((tf, None, k, mode))
    for (tf, htf), k, mode in itertools.product((("M15", "H4"), ("H1", "H4"), ("M15", "H1"), ("H1", "D1"), ("H4", "D1")), (1, 3),
                                                ("limit", "engulf", "failed", "rbs")):
        C.append((tf, htf, k, mode))
    for tf, mode in itertools.product(("M15", "M30", "H1", "H4"), ("engulf_any", "failed_any")):
        C.append((tf, None, 1, mode))
    out = []
    for c in C:
        for tgt, story in itertools.product((1.0, 2.0, 3.0), (False, True)):
            out.append(c + (tgt, story, None))
            if sym == "XAUUSD":
                out.append(c + (tgt, story, (17, 19)))
    return out


def work(sym):
    L = M.Lab(sym); res = {}; t0 = time.time()
    for tf, htf, k, mode, tgt, story, hours in configs(sym):
        tr = L.run(tf, k, mode, tgt, story=story, hours=hours, htf=htf)
        key = f"{sym}|{tf}{'<'+htf if htf else ''}|k{k}|{mode}|tp{tgt:g}|{'story' if story else 'nostory'}|{'WAT18-20' if hours else 'allday'}"
        j = GS.judge(tr, 0.53 if sym == "XAUUSD" else 0.0)
        if j:
            j["long_E"] = float(tr["r"][tr["side"] > 0].mean()) if (tr["side"] > 0).any() else None
            j["short_E"] = float(tr["r"][tr["side"] < 0].mean()) if (tr["side"] < 0).any() else None
            res[key] = j
    print(f"{sym}: {len(res)} configs in {time.time()-t0:.0f}s", flush=True)
    return res


if __name__ == "__main__":
    with Pool(4) as p:
        parts = p.map(work, SYMS)
    res = {k: v for d in parts for k, v in d.items()}
    fam = {}
    for k in res:
        fam.setdefault(k.rsplit("|", 3)[0], []).append(k)
    for k, v in res.items():
        v["G1"] = v["E_is"] > 0 and v["sh_is"] > 0.37
        v["G2"] = v["E_oos"] > 0 and v["E_oos"] >= 0.5 * v["E_is"]
        v["G3"] = v["t"] >= 1.96
        v["G4"] = all(x > 0 for x in v["regimes"].values() if x == x)
        sib = [s for s in fam[k.rsplit("|", 3)[0]] if s != k]
        v["G5"] = (not sib) or any(res[s]["E"] > 0 for s in sib)
        v["pass"] = bool(all(v[g] for g in ("G1", "G2", "G3", "G4", "G5")))
        v["timeless_candidate"] = bool(v["G1"] and v["G2"] and v["G4"] and v["G5"] and v["t"] >= 1.0)
    json.dump(res, open(os.path.join(HERE, "..", "results", "msnr_grid.json"), "w"), indent=1, default=float)
    E = np.array([v["E"] for v in res.values()])
    print(f"{len(res)} configs | share E>0 {np.mean(E > 0):.1%} | median E {np.median(E):+.3f} | "
          f"pass {sum(v['pass'] for v in res.values())} | timeless candidates {sum(v['timeless_candidate'] for v in res.values())}")
    for tag in ("pass", "timeless_candidate"):
        ks = sorted([k for k, v in res.items() if v[tag]], key=lambda k: -res[k]["t"])
        for k in ks[:25]:
            v = res[k]; R = v["regimes"]
            print(f"  {tag[:4]} {k:62s} {v['per_yr']:6.1f}/yr E {v['E']:+.3f} IS {v['E_is']:+.3f} OOS {v['E_oos']:+.3f} t {v['t']:.2f} "
                  f"eras {R['bear_2011_15']:+.3f}/{R['range_2016_18']:+.3f}/{R['bull_2019_25']:+.3f}")
