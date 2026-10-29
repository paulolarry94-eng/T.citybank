"""Final Pareto points, each verified on 20,000,000 bootstrapped 360-trade lifecycles."""
import json, numpy as np, datetime as dt
import pareto as PA, portfolio as P, engine as E
from config import LADDERS, PORTS, weights

N20M = 20_000_000
SPECS = {
  "A_max_timelessness": ("P1_strict", "fixed", "data", 0.018),
  "B_balanced":         ("P1_strict", "fixed", "data", 0.036),
  "C_max_inside_walls": ("P3_strict+gold_trend", "fixed", "data", 0.036),
  "ref_user_hierarchy": ("P1_strict", "user6", "data", 0.036),
}

def verified_scale(legs, lad, env):
    sc = 1.0
    # start from the 200k-search answer, then tighten until 20M lifecycles hold
    lo, hi = 0.0, 2.0
    for _ in range(16):
        mid = (lo + hi) / 2
        h = PA.run_hist(legs, lad, mid)
        ok = max(h["life_dd"]) <= env and PA.run_boot(legs, lad, mid, 200_000)["worst"] <= env
        lo, hi = (mid, hi) if ok else (lo, mid)
    sc = lo
    while True:
        b = PA.run_boot(legs, lad, sc, N20M, seed=2026)
        if b["worst"] <= env:
            return sc, b
        sc *= env / b["worst"] * 0.995

out = {}
for name, (pn, ln, ws, env) in SPECS.items():
    names = PORTS[pn]; w = weights(names, ws); lad = LADDERS[ln]
    legs = PA.load_legs(names, w)
    sc, b = verified_scale(legs, lad, env)
    h = PA.run_hist(legs, lad, sc)
    hv = PA.run_hist(legs, lad, sc, harvest=True)
    leg_rows = []
    for n, wt in zip(names, w):
        tr = np.load(f"trades/{n}_off120.npy"); s = E.stats(tr); s.pop("per_year")
        leg_rows.append({"leg": n, "risk_pct": float(lad[0] * sc * wt), **{k: s[k] for k in
                         ("n", "per_yr", "win", "avg_w", "avg_l", "E", "pf", "E_is", "E_oos",
                          "max_consec_loss")}})
    yr = h["cagr"]
    out[name] = {"portfolio": pn, "ladder": ln, "weights": ws, "envelope_target": env,
                 "scale": sc, "legs": leg_rows, "cagr": yr, "biweekly": (1 + yr) ** (1 / 26) - 1,
                 "hist_mdd": h["mdd"], "life_dd_max": max(h["life_dd"]),
                 "trades_per_month": h["per_month"], "months_for_360": 360 / h["per_month"],
                 "avg_risk": h["avg_risk"], "integrity": h["integrity"],
                 "boot20M": b, "harvest_banked_15y": hv["banked"], "harvest_cagr_left": hv["cagr"]}
    o = out[name]
    print(f"\n{name}  [{pn} | {ln} | {ws}]  20M lifecycles: breaches={b['breaches']} worst={100*b['worst']:.2f}%")
    for L in leg_rows:
        print(f"   {L['leg']:26s} risk {100*L['risk_pct']:.3f}%  {L['per_yr']:.1f}/yr win {L['win']:.0%} "
              f"avgW {L['avg_w']:+.2f} avgL {L['avg_l']:+.2f} E {L['E']:+.3f} PF {L['pf']:.2f}")
    print(f"   CAGR {100*yr:.2f}%  bi-weekly {100*o['biweekly']:.3f}%  hist DD {100*o['hist_mdd']:.2f}%  "
          f"trades/mo {o['trades_per_month']:.2f}  360 trades = {o['months_for_360']:.0f} months  "
          f"avg risk {100*o['avg_risk']:.3f}%  integrity {o['integrity'][0]:.3f} "
          f"(<15min {100*o['integrity'][2]:.1f}%)  lifecycle median {100*b['med_life']:+.2f}% p5 {100*b['p5_life']:+.2f}%",
          flush=True)
json.dump(out, open("results/final_pareto.json", "w"), indent=1, default=float)
