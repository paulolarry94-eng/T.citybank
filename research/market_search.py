"""All families x all timeframes x all four markets, judged by the timeless funnel.
Eras for the timeless gate: 2011-15, 2016-18, 2019-25 (the same three eras for every market)."""
import os, json, time, datetime as dt
import numpy as np
import gold_lab as GL, gold_search as GS

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "trades", "multi"); os.makedirs(OUT, exist_ok=True)
SYMS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]


def main():
    res = {}
    for sym in SYMS:
        G = GL.Market(sym); t0 = time.time()
        gy = 0.53 if sym == "XAUUSD" else 0.0
        for name, param, fn in GS.variants():
            key = f"{sym}_{name}"
            tr = fn(G); np.save(os.path.join(OUT, key + ".npy"), tr)
            j = GS.judge(tr, gy)
            if j: res[key] = {"param": param, **j}
        print(f"{sym}: {time.time()-t0:.0f}s", flush=True)
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
    json.dump(res, open(os.path.join(HERE, "results", "multi_lab.json"), "w"), indent=1, default=float)
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
