"""Hunt 2, step 7: fortnightly payouts on top of the drawdown-braked book.

Every 14 days: profit above the trading base is swept to a bank (a share `grow` of it may stay
in the account so the base compounds), then the payout = min(bank, target x base) is paid out.
A loss is therefore always rebuilt by later profit before anything else leaves, and a flat
fortnight can still pay from the bank. The brake measures drawdown on the trading account; a
sweep is not a drawdown.

Profiles (all: drawdown brake, floor 0.3 at the budget):
  Steady    budget 15%, heat cap 20%
  Balanced  budget 25%, heat cap 20%
  Max       budget 25%, heat cap 30%
Also run with every trade's result cut by 0.05R (edge decay stress).
"""
import os, sys, json
import numpy as np
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import risk_lab as RL

FN = 14 * 86400


@njit(cache=True)
def sim_pay(t_in, t_out, r, w, base, heat_cap, dd_full, floor, target, grow, pays, trade_cap=1.0):
    n = len(r)
    ev_t = np.empty(2 * n, np.int64); ev_i = np.empty(2 * n, np.int64); ev_e = np.empty(2 * n, np.int64)
    for i in range(n):
        ev_t[2 * i] = t_in[i]; ev_i[2 * i] = i; ev_e[2 * i] = 1
        ev_t[2 * i + 1] = t_out[i]; ev_i[2 * i + 1] = i; ev_e[2 * i + 1] = 0
    order = np.argsort(ev_t * 2 + ev_e, kind="mergesort")
    eq = 1.0; hwm = 1.0; peak = 1.0; mdd = 0.0; bank = 0.0
    amt = np.zeros(n); pct = np.zeros(n); taken = np.zeros(n, np.bool_); heat = 0.0
    nxt = ev_t[order[0]] + 14 * 86400; f = 0
    for q in range(2 * n):
        j = order[q]; t = ev_t[j]; i = ev_i[j]
        while t >= nxt and f < len(pays):
            if eq > hwm:
                ex = eq - hwm
                sweep = (1.0 - grow) * ex
                eq -= sweep; bank += sweep; hwm = eq
                peak = max(peak - sweep, eq)
            pay = min(bank, target * hwm)
            bank -= pay; pays[f] = pay; f += 1
            nxt += 14 * 86400
        if ev_e[j] == 1:
            dd = 1.0 - eq / peak
            m = 1.0 - (1.0 - floor) * min(1.0, dd / dd_full)
            p = min(base * w[i] * m, trade_cap)
            if heat + p > heat_cap + 1e-12:
                continue
            taken[i] = True; pct[i] = p; amt[i] = eq * p; heat += p
        else:
            if not taken[i]:
                continue
            heat -= pct[i]; eq += amt[i] * r[i]
            if eq > peak:
                peak = eq
            dd = 1.0 - eq / peak
            if dd > mdd:
                mdd = dd
            if eq <= 0:
                return f, mdd, 0.0, bank
    return f, mdd, eq, bank


def run(paths, real, base, heat, budget, target, grow, decay=0.0, cap=0.04):
    out = []
    for p in [real] + paths:
        t_in, t_out, r, w = p
        pays = np.zeros(400)
        f, mdd, eq, bank = sim_pay(t_in, t_out, r - decay, w, base, heat, budget, 0.3, target, grow, pays, cap)
        pays = pays[:f]
        full = pays >= target * 0.999 * 1.0 if grow == 0 else None
        hit = float((pays >= 0.999 * target).mean()) if grow == 0 else float((pays > 0).mean())
        streak = cur = 0
        for x in pays:
            cur = 0 if x >= 0.999 * target else cur + 1
            streak = max(streak, cur)
        out.append((hit, pays.sum() / (f / 26.0), mdd, eq, streak))
    A = np.array(out)
    real_row, sims = A[0], A[1:]
    return dict(real_hit=real_row[0], real_paid_yr=real_row[1], real_dd=real_row[2], real_end=real_row[3], real_streak=real_row[4],
                hit_med=float(np.median(sims[:, 0])), hit_p5=float(np.percentile(sims[:, 0], 5)),
                paid_med=float(np.median(sims[:, 1])), dd_med=float(np.median(sims[:, 2])), dd_p95=float(np.percentile(sims[:, 2], 95)),
                end_med=float(np.median(sims[:, 3])), streak_p95=float(np.percentile(sims[:, 4], 95)))


if __name__ == "__main__":
    legs = RL.load_book()
    rng = np.random.default_rng(11)
    paths = [RL.reshuffle(legs, rng) for _ in range(int(os.environ.get("NPATHS", "600")))]
    real = RL.merge(legs)
    R = json.load(open("results/risk_lab.json"))
    C = json.load(open("results/risk_cap.json"))
    prof = {"Steady": (R["ddbrake@0.15"]["base"], 0.20, 0.15), "Balanced": (C["heat0.2_cap0.04"]["base"], 0.20, 0.25),
            "Max": (C["heat0.3_cap0.04"]["base"], 0.30, 0.25)}
    res = {}
    for name, (base, heat, budget) in prof.items():
        print(f"\n{name}: base {base:.2%} per unit weight, heat cap {heat:.0%}, brake budget {budget:.0%} | salary mode (no compounding)")
        print("  pay/fn   paid/yr  on-time real  on-time typical  on-time 1-in-20  longest miss 1-in-20  trading DD real/typ/1-in-20  end base typ")
        best = None
        for tgt in (0.005, 0.0075, 0.01, 0.0125, 0.015, 0.0175, 0.02, 0.025):
            s = run(paths, real, base, heat, budget, tgt, 0.0)
            ok = s["hit_med"] >= 0.90 and s["hit_p5"] >= 0.75
            print(f"  {tgt:6.2%}  {s['paid_med']:7.1%}  {s['real_hit']:12.0%}  {s['hit_med']:15.0%}  {s['hit_p5']:15.0%}  "
                  f"{s['streak_p95']:20.0f}  {s['real_dd']:6.1%}/{s['dd_med']:5.1%}/{s['dd_p95']:5.1%}  {s['end_med']:12.2f}{'  <= highest that holds' if ok else ''}", flush=True)
            if ok:
                best = (tgt, s)
        dec = {}
        for dcy in (0.02, 0.05):
            d = run(paths, real, base, heat, budget, best[0], 0.0, decay=dcy)
            dec[dcy] = d
            print(f"  edge-decay stress (every trade -{dcy:.2f}R) at {best[0]:.2%}/fn: on-time typical {d['hit_med']:.0%}, 1-in-20 {d['hit_p5']:.0%}, "
                  f"paid/yr {d['paid_med']:.1%}, trading DD typ {d['dd_med']:.1%} / 1-in-20 {d['dd_p95']:.1%}, end base {d['end_med']:.2f}")
        res[name] = dict(base=base, heat=heat, budget=budget, cap=0.04, target=best[0], stats=best[1], decay=dec)
    json.dump(res, open("results/payout_v3.json", "w"), indent=1)
