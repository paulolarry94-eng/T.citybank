"""Hunt 2, step 3: breadth. Build EURJPY, GBPJPY and EURGBP minute bars from the traded legs
and run the published families that survived on the majors (H1/H4/D1 only: lower timeframes
lose to the spread, and crosses cost more) through the same timeless funnel as the book.

Cross minute bars use only minutes where both legs have a bar. open/close are exact products
(ratios); high/low are bounded by the legs' extremes paired with the other leg's open/close,
which is close to, and slightly wider than, the true range. All-in costs (spread + commission +
slippage): EURJPY 2.0 pips, GBPJPY 3.0 pips, EURGBP 1.5 pips.
"""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import engine as E, gold_lab as GL, gold_search as GS

CROSSES = {"EURJPY": ("EURUSD", "USDJPY", "mul", 0.020), "GBPJPY": ("GBPUSD", "USDJPY", "mul", 0.030),
           "EURGBP": ("EURUSD", "GBPUSD", "div", 0.00015)}
OUT = os.path.join(HERE, "..", "trades", "crosses"); os.makedirs(OUT, exist_ok=True)


def synth(a, b, op):
    ta, oa, ha, la, ca = E.load_m1(a); tb, ob, hb, lb, cb = E.load_m1(b)
    common, ia, ib = np.intersect1d(ta, tb, assume_unique=True, return_indices=True)
    oa, ha, la, ca = oa[ia], ha[ia], la[ia], ca[ia]; ob, hb, lb, cb = ob[ib], hb[ib], lb[ib], cb[ib]
    if op == "mul":
        o, c = oa * ob, ca * cb
        hi = np.max([o, c, ha * cb, ca * hb, ha * ob, oa * hb], axis=0)
        lo = np.min([o, c, la * cb, ca * lb, la * ob, oa * lb], axis=0)
    else:
        o, c = oa / ob, ca / cb
        hi = np.max([o, c, ha / cb, ca / lb, ha / ob, oa / lb], axis=0)
        lo = np.min([o, c, la / cb, ca / hb, la / ob, oa / hb], axis=0)
    return common, o, hi, lo, c


class Cross(GL.Market):
    def __init__(self, sym):
        a, b, op, cost = CROSSES[sym]
        self.sym, self.cost = sym, cost
        self.m1 = synth(a, b, op)
        self.ts, self.o, self.h, self.l, self.c = self.m1
        self.gaps = E.data_gaps(self.ts)
        self.bars = {}


def variants():
    for name, param, fn in GS.variants():
        tf = name.split("_")[1]
        if tf in ("H1", "H4", "D1"):
            yield name, param, fn


def main():
    res = {}
    for sym in CROSSES:
        G = Cross(sym); t0 = time.time()
        for name, param, fn in variants():
            key = f"{sym}_{name}"
            tr = fn(G); np.save(os.path.join(OUT, key + ".npy"), tr)
            j = GS.judge(tr, 0.0)
            if j: res[key] = {"param": param, **j}
        print(f"{sym}: {len(G.ts):,} minutes, {time.time()-t0:.0f}s", flush=True)
    fam = {}
    for k in res: fam.setdefault(k.rsplit("_", 1)[0], []).append(k)
    for k, v in res.items():
        v["G1"] = v["E_is"] > 0 and v["sh_is"] > 0.37
        v["G2"] = v["E_oos"] > 0 and v["E_oos"] >= 0.5 * v["E_is"]
        v["G3"] = v["t"] >= 1.96
        v["G4"] = all(x > 0 for x in v["regimes"].values())
        sib = [s for s in fam[k.rsplit("_", 1)[0]] if s != k]
        v["G5"] = (not sib) or any(res[s]["E"] > 0 for s in sib)
        v["pass"] = all(v[g] for g in ("G1", "G2", "G3", "G4", "G5"))
        v["timeless_candidate"] = v["G1"] and v["G2"] and v["G4"] and v["G5"] and v["t"] >= 1.0
    json.dump(res, open(os.path.join(HERE, "..", "results", "crosses_lab.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    res = main()
    full = [k for k, v in res.items() if v["pass"]]
    cand = [k for k, v in res.items() if v["timeless_candidate"] and not v["pass"]]
    print(f"{len(res)} variants | {len(full)} pass all five gates | {len(cand)} more timeless candidates (t 1.0-1.96)")
    for tag, ks in (("PASS", full), ("cand", cand)):
        for k in sorted(ks, key=lambda k: -res[k]["sh_all"]):
            v = res[k]; R = v["regimes"]
            print(f"  {tag} {k:30s} {v['per_yr']:6.1f}/yr E {v['E']:+.3f} IS {v['E_is']:+.3f} OOS {v['E_oos']:+.3f} "
                  f"Sh {v['sh_all']:.2f} t {v['t']:.2f} | eras {R['bear_2011_15']:+.3f} {R['range_2016_18']:+.3f} {R['bull_2019_25']:+.3f}")
