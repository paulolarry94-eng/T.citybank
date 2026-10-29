import json, itertools, numpy as np, funnel as F
import pareto as PA, portfolio as P

U6 = np.array([3.0, 2.0, 1.33, 0.86, 0.56, 0.24]) / 100
U12 = np.r_[U6, 0.24 / 100 * 0.6 ** np.arange(1, 7)]
FIX = np.array([1.0]) / 100
LADDERS = {"user6": U6, "user12": U12, "fixed": FIX}

PORTS = {
  "P1_strict": ["S1_XAUUSD_H1+M30_long", "TR_USDJPY_H4_atr2_long"],
  "P2_original": ["S1_XAUUSD_M20+M30_long", "S1_EURUSD_M20+M30_long", "TR_USDJPY_H4_atr2_long",
                  "TR_XAUUSD_H4_atr3_both"],
  "P3_strict+gold_trend": ["S1_XAUUSD_H1+M30_long", "TR_USDJPY_H4_atr2_long", "TR_XAUUSD_H4_atr3_long"],
}
def weights(names, scheme):
    out = []
    for n in names:
        s1 = n.startswith("S1")
        if scheme == "formula": out.append(P.multiplier(1.0) if s1 else P.multiplier(1.5))
        elif scheme == "exempt": out.append(1.0 if s1 else P.multiplier(1.5))
        elif scheme == "data": out.append(1.0 if s1 else 0.4)
        elif scheme == "equal": out.append(1.0)
    return out

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
