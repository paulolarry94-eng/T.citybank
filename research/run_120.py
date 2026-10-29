import json, numpy as np, pareto as PA, portfolio as P
from config import PORTS, weights, LADDERS
out = []
print("Growth curve on the real 2011-2025 record (no heat cap, outside the walls):")
for pn, names in PORTS.items():
    for ln in ("fixed", "user6"):
        lad = LADDERS[ln]
        legs = PA.load_legs(names, weights(names, "data"))
        best = (-1, None)
        for sc in np.r_[np.arange(0.5, 10, 0.5), np.arange(10, 41, 2)]:
            h = PA.run_hist(legs, lad, sc, heat=10.0)
            out.append({"port": pn, "ladder": ln, "scale": float(sc), "l0": float(lad[0]*sc),
                        "cagr": h["cagr"], "mdd": h["mdd"], "life_max": max(h["life_dd"])})
            if h["cagr"] > best[0]: best = (h["cagr"], (sc, h["mdd"]))
        hit = [o for o in out if o["port"] == pn and o["ladder"] == ln and o["cagr"] >= 1.2]
        if hit:
            o = min(hit, key=lambda o: o["mdd"])
            print(f"  {pn:22s} {ln:6s} 120%/yr REACHED at S1 risk {100*o['l0']:.1f}%/trade: max DD {100*o['mdd']:.1f}%")
        else:
            print(f"  {pn:22s} {ln:6s} 120%/yr NOT reachable. Peak CAGR {100*best[0]:.1f}% "
                  f"(S1 risk {100*lad[0]*best[1][0]:.1f}%/trade, max DD {100*best[1][1]:.1f}%)")
        for target in (0.2, 0.4, 0.6, 0.8):
            hit = [o for o in out if o["port"] == pn and o["ladder"] == ln and o["cagr"] >= target]
            if hit:
                o = min(hit, key=lambda o: o["mdd"])
                print(f"        {int(target*100):3d}%/yr needs max DD {100*o['mdd']:5.1f}% (S1 risk {100*o['l0']:.1f}%)")
json.dump(out, open("results/growth_curve.json", "w"), indent=1, default=float)
