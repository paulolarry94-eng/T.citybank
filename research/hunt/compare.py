"""Attribution and robustness of the brake result: old book vs new book, plain euro leg vs
Tue-Thu, without the two weak cross legs, and heat cap 10/20/30%."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import risk_lab as RL

B3 = json.load(open("results/book_v3.json"))
OLD = ["XAU_S1_reversion_H1M30M20", "JPY_VolBreakout_D1_k0.7", "XAU_Donchian20_H4_turtle", "JPY_S2_Donchian20_H4_long",
       "XAU_EMA20-50_H4", "GBP_WeeklySweep_FollowThrough", "JPY_Donchian55_D1_trail", "JPY_RSI2_D1_lo5"]


def legs_of(names, swap=None):
    out = []
    for k in names:
        f = B3["files"][k]
        if swap and k in swap:
            f = swap[k]
        out.append((k, np.load(f), B3["weights"][k]))
    return out


if __name__ == "__main__":
    n = int(os.environ.get("NPATHS", "600"))
    sets = {
        "old 8-leg book": legs_of(OLD),
        "new 11-leg book": legs_of(B3["kept"]),
        "new book, euro leg every weekday": legs_of(B3["kept"], {"EUR_EuroHours_short_TueThu": "trades/hunt/EUR_EuroHours_short_0913.npy"}),
        "new book without the two cross legs": legs_of([k for k in B3["kept"] if not k.startswith(("GBPJPY", "EURGBP"))]),
    }
    res = {}
    for name, legs in sets.items():
        P = RL.Paths(legs, n=n)
        for pol in ("fixed", "ddbrake"):
            r = P.solve(pol, 0.25, **({"dd_full": 0.25} if pol == "ddbrake" else {}))
            res[f"{name} | {pol}"] = r
            print(f"{name:38s} {pol:8s} base {r['base']:5.2%} CAGR med {r['cagr_med']:6.1%} p5 {r['cagr_p5']:6.1%} | "
                  f"DD p95 {r['dd_p95']:5.1%} worst {r['dd_worst']:5.1%} | real CAGR {r['real_cagr']:6.1%} DD {r['real_dd']:5.1%}", flush=True)
    P = RL.Paths(sets["new 11-leg book"], n=n)
    for hc in (0.10, 0.30):
        r = P.solve("ddbrake", 0.25, heat_cap=hc, dd_full=0.25)
        res[f"heat {hc}"] = r
        print(f"new book ddbrake heat cap {hc:.0%}: base {r['base']:5.2%} CAGR med {r['cagr_med']:6.1%} p5 {r['cagr_p5']:6.1%} | "
              f"DD p95 {r['dd_p95']:5.1%} worst {r['dd_worst']:5.1%} | real CAGR {r['real_cagr']:6.1%} DD {r['real_dd']:5.1%}", flush=True)
    json.dump(res, open("results/risk_compare.json", "w"), indent=1)
