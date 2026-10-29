"""Run every liquidity variant on all four markets and judge it with the timeless funnel."""
import os, json, time
import numpy as np
import liquidity as LQ, gold_search as GS

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "trades", "liquidity"); os.makedirs(OUT, exist_ok=True)
SYMS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]


def main():
    res = {}
    for sym in SYMS:
        lab = LQ.Lab(sym); t0 = time.time()
        for name, kw in LQ.variants():
            key = f"{sym}_{name}"
            tr = lab.build(**kw); np.save(os.path.join(OUT, key + ".npy"), tr)
            j = GS.judge(tr, 0.53 if sym == "XAUUSD" else 0.0)
            if j: res[key] = j
        print(f"{sym}: {time.time()-t0:.0f}s", flush=True)
    fam = {}
    for k in res: fam.setdefault(k.rsplit("_tp", 1)[0], []).append(k)
    for k, v in res.items():
        v["G1"] = v["E_is"] > 0 and v["sh_is"] > 0.37
        v["G2"] = v["E_oos"] > 0 and v["E_oos"] >= 0.5 * v["E_is"]
        v["G3"] = v["t"] >= 1.96
        v["G4"] = all(x > 0 for x in v["regimes"].values())
        sib = [s for s in fam[k.rsplit("_tp", 1)[0]] if s != k]
        v["G5"] = (not sib) or any(res[s]["E"] > 0 for s in sib)
        v["pass"] = all(v[g] for g in ("G1", "G2", "G3", "G4", "G5"))
    json.dump(res, open(os.path.join(HERE, "results", "liquidity_lab.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    res = main()
    full = [k for k, v in res.items() if v["pass"]]
    print(f"{len(res)} variants | {len(full)} pass all five gates")
    print(f"{'variant':44s} {'/yr':>6s} {'win':>4s} {'E':>7s} {'IS':>7s} {'OOS':>7s} {'Sh':>5s} {'t':>5s} {'eras':>22s} gates")
    for k, v in sorted(res.items(), key=lambda kv: -kv[1]["sh_all"] if kv[1]["sh_all"] == kv[1]["sh_all"] else 9)[:35]:
        R = v["regimes"]; g = "".join("1" if v[x] else "." for x in ("G1", "G2", "G3", "G4", "G5"))
        print(f"{k:44s} {v['per_yr']:6.1f} {v['win']:4.0%} {v['E']:+7.3f} {v['E_is']:+7.3f} {v['E_oos']:+7.3f} "
              f"{v['sh_all']:5.2f} {v['t']:5.2f} {R['bear_2011_15']:+.3f}/{R['range_2016_18']:+.3f}/{R['bull_2019_25']:+.3f} {g}")
