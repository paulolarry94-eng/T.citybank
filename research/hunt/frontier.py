"""What does 60%+ a year cost? The expanded book with the drawdown brake at higher budgets and
open-risk caps (per-trade cap 4% and 6%), 600 reshuffled histories each."""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import risk_lab as RL
legs = RL.load_book(); P = RL.Paths(legs, n=600)
res = {}
print(f"{'budget':>6s} {'heat':>5s} {'cap':>4s} {'base':>6s} {'CAGR med':>8s} {'CAGR p5':>8s} {'DD p95':>7s} {'worst':>6s} {'P(DD>40%)':>9s} {'real CAGR':>9s} {'real DD':>7s}")
for budget, heat, cap in ((0.25, 0.30, 0.04), (0.30, 0.30, 0.04), (0.30, 0.40, 0.06), (0.35, 0.40, 0.06), (0.35, 0.50, 0.08), (0.40, 0.50, 0.08), (0.45, 0.60, 0.10)):
    r = P.solve("ddbrake", budget, heat_cap=heat, dd_full=budget, trade_cap=cap)
    res[f"{budget}_{heat}_{cap}"] = r
    print(f"{budget:6.0%} {heat:5.0%} {cap:4.0%} {r['base']:6.2%} {r['cagr_med']:8.1%} {r['cagr_p5']:8.1%} {r['dd_p95']:7.1%} {r['dd_worst']:6.1%} "
          f"{r['p_dd40']:9.1%} {r['real_cagr']:9.1%} {r['real_dd']:7.1%}", flush=True)
json.dump(res, open("results/frontier.json", "w"), indent=1)
