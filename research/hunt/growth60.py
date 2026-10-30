"""Payouts at the 'Growth 60' profile (brake budget 30%, heat cap 40%, per-trade cap 6%), and the
effect of the probationary failed-engulfing legs (gold, USDJPY) on the book if they are real."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "msnr"))
import risk_lab as RL, payout_lab as PL

if __name__ == "__main__":
    legs = RL.load_book(); real = RL.merge(legs)
    rng = np.random.default_rng(11)
    paths = [RL.reshuffle(legs, rng) for _ in range(600)]
    F = json.load(open("results/frontier.json"))["0.3_0.4_0.06"]
    base = F["base"]
    print(f"Growth 60: base {base:.2%}, heat 40%, cap 6%, brake 30% | salary mode")
    out = {}
    for tgt in (0.01, 0.0125, 0.015, 0.0175, 0.02, 0.025):
        s = PL.run(paths, real, base, 0.40, 0.30, tgt, 0.0, cap=0.06)
        out[tgt] = s
        print(f"  {tgt:6.2%}/fn  paid/yr {s['paid_med']:6.1%}  on time real {s['real_hit']:.0%} typical {s['hit_med']:.0%} 1-in-20 {s['hit_p5']:.0%} | "
              f"DD real {s['real_dd']:.0%} typ {s['dd_med']:.0%} 1-in-20 {s['dd_p95']:.0%}")
    for dcy in (0.02, 0.05):
        s = PL.run(paths, real, base, 0.40, 0.30, 0.015, 0.0, decay=dcy, cap=0.06)
        print(f"  decay -{dcy}R at 1.50%/fn: on time typical {s['hit_med']:.0%} 1-in-20 {s['hit_p5']:.0%}, DD typ {s['dd_med']:.0%} 1-in-20 {s['dd_p95']:.0%}")
    json.dump({str(k): v for k, v in out.items()}, open("results/growth60_payouts.json", "w"), indent=1)

    # probationary legs
    import msnr_lab as M
    import multi_book as MB
    os.makedirs("trades/msnr", exist_ok=True)
    np.save("trades/msnr/XAU_failed_engulf_M15H1_k3_story_tp3.npy", M.Lab("XAUUSD").run("M15", 3, "failed", 3.0, story=True, htf="H1"))
    np.save("trades/msnr/JPY_failed_engulf_M15H1_k3_story_tp3.npy", M.Lab("USDJPY").run("M15", 3, "failed", 3.0, story=True, htf="H1"))
    B3 = json.load(open("results/book_v3.json"))
    MB.CANDS.clear()
    for k in B3["kept"]:
        MB.CANDS[k] = (B3["files"][k], True)
    MB.CANDS["XAU_FailedEngulf_M15H1"] = ("trades/msnr/XAU_failed_engulf_M15H1_k3_story_tp3.npy", False)
    MB.CANDS["JPY_FailedEngulf_M15H1"] = ("trades/msnr/JPY_failed_engulf_M15H1_k3_story_tp3.npy", False)
    kept, W, T, Mo, J = MB.build(verbose=True)
    mon = sum(W[k] * Mo[k] for k in kept)
    sh = mon.mean() / mon.std(ddof=1) * np.sqrt(12)
    print(f"book + probationary legs: {len(kept)} legs, monthly Sharpe {sh:.2f} (IS {mon[:96].mean()/mon[:96].std(ddof=1)*np.sqrt(12):.2f}, "
          f"OOS {mon[96:].mean()/mon[96:].std(ddof=1)*np.sqrt(12):.2f}) vs 1.52 without")
