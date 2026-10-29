import json, itertools, numpy as np, funnel as F
import pareto as PA, portfolio as P

from config import LADDERS, PORTS, weights

def main():
  # correlations between candidate legs (monthly R)
  cands = sorted(set(sum(PORTS.values(), [])))
  M = {}
  for c in cands:
      tr = np.load(f"trades/{c}_off120.npy"); mk = F.month_key(tr["t_out"]); s = np.zeros(180)
      ok = (mk >= 0) & (mk < 180); np.add.at(s, mk[ok], tr["r"][ok]); M[c] = s
  print("monthly-R correlation:")
  for a, b in itertools.combinations(cands, 2):
      print(f"  {a:26s} {b:26s} {np.corrcoef(M[a], M[b])[0,1]:+.2f}")

  rows = []
  for pn, names in PORTS.items():
      for ln, lad in LADDERS.items():
          for ws in ("formula", "exempt", "data"):
              if ln == "fixed" and ws == "formula": pass
              legs = PA.load_legs(names, weights(names, ws))
              sc = PA.max_scale_inside(legs, lad, n_boot=200_000)
              h = PA.run_hist(legs, lad, sc)
              rows.append({"port": pn, "ladder": ln, "weights": ws, "scale": sc, **{k: h[k] for k in
                           ("cagr", "mdd", "per_month", "avg_risk", "integrity", "trades")},
                           "life_max": max(h["life_dd"])})
              r = rows[-1]
              print(f"{pn:22s} {ln:7s} {ws:8s} L0={100*lad[0]*sc*max(weights(names,ws)):6.3f}% "
                    f"CAGR={100*r['cagr']:6.2f}% histDD={100*r['mdd']:5.2f}% lifeDDmax={100*r['life_max']:5.2f}% "
                    f"trades/mo={r['per_month']:4.2f} avgRisk={100*r['avg_risk']:.3f}% integ={r['integrity'][0]:.3f}", flush=True)
  json.dump(rows, open("results/inside_walls.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
