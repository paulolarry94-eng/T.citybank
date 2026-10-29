import os, json, time, numpy as np
import liquidity2 as L2, liquidity as LQ, gold_lab as GL, gold_search as GS
HERE = os.path.dirname(__file__); OUT = os.path.join(HERE, "trades", "liquidity2"); os.makedirs(OUT, exist_ok=True)
FUN = {"daily_sweep": L2.daily_sweep, "turtle_soup_plus_one": L2.turtle_soup_plus_one, "nr_breakout": L2.nr_breakout}
res = {}
for sym in ("XAUUSD", "EURUSD", "GBPUSD", "USDJPY"):
    G = GL.Market(sym); Lb = LQ.Lab(sym); t0 = time.time(); gy = 0.53 if sym == "XAUUSD" else 0.0
    for name, (fn, kw) in L2.variants():
        tr = L2.trend_sweep(Lb, G, **kw) if fn == "trend_sweep" else FUN[fn](G, **kw)
        key = f"{sym}_{name}"; np.save(os.path.join(OUT, key + ".npy"), tr)
        j = GS.judge(tr, gy)
        if j: res[key] = j
    print(f"{sym}: {time.time()-t0:.0f}s", flush=True)
fam = {}
for k in res: fam.setdefault(k.rsplit("_tp", 1)[0], []).append(k)
for k, v in res.items():
    v["G1"] = v["E_is"] > 0 and v["sh_is"] > 0.37; v["G2"] = v["E_oos"] > 0 and v["E_oos"] >= 0.5 * v["E_is"]
    v["G3"] = v["t"] >= 1.96; v["G4"] = all(x > 0 for x in v["regimes"].values())
    sib = [s for s in fam[k.rsplit("_tp", 1)[0]] if s != k]; v["G5"] = (not sib) or any(res[s]["E"] > 0 for s in sib)
    v["pass"] = all(v[g] for g in ("G1", "G2", "G3", "G4", "G5"))
    v["cand"] = v["G1"] and v["G2"] and v["G4"] and v["G5"] and v["t"] >= 1.0
json.dump(res, open(os.path.join(HERE, "results", "liquidity2_lab.json"), "w"), indent=1, default=float)
print(f"{len(res)} variants | {sum(v['pass'] for v in res.values())} pass all gates | {sum(v['cand'] and not v['pass'] for v in res.values())} timeless candidates")
print(f"{'variant':40s} {'/yr':>6s} {'win':>4s} {'E':>7s} {'IS':>7s} {'OOS':>7s} {'t':>5s} {'eras':>22s} gates")
for k, v in sorted(res.items(), key=lambda kv: -kv[1]["t"] if kv[1]["t"] == kv[1]["t"] else 9)[:30]:
    R = v["regimes"]; g = "".join("1" if v[x] else "." for x in ("G1", "G2", "G3", "G4", "G5"))
    print(f"{k:40s} {v['per_yr']:6.1f} {v['win']:4.0%} {v['E']:+7.3f} {v['E_is']:+7.3f} {v['E_oos']:+7.3f} {v['t']:5.2f} {R['bear_2011_15']:+.3f}/{R['range_2016_18']:+.3f}/{R['bull_2019_25']:+.3f} {g}")
