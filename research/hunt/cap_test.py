import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import risk_lab as RL
legs = RL.load_book(); P = RL.Paths(legs, n=600)
res = {}
for heat in (0.20, 0.30):
    for cap in (1.0, 0.04, 0.03, 0.02):
        r = P.solve("ddbrake", 0.25, heat_cap=heat, dd_full=0.25, trade_cap=cap)
        res[f"heat{heat}_cap{cap}"] = r
        print(f"heat {heat:.0%} per-trade cap {('none' if cap == 1 else f'{cap:.0%}'):>4s}: base {r['base']:6.2%} CAGR med {r['cagr_med']:6.1%} p5 {r['cagr_p5']:6.1%} | "
              f"DD p95 {r['dd_p95']:5.1%} worst {r['dd_worst']:5.1%} | real CAGR {r['real_cagr']:6.1%} DD {r['real_dd']:5.1%}", flush=True)
json.dump(res, open("results/risk_cap.json", "w"), indent=1)
