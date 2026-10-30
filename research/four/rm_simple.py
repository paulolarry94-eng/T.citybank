import os, sys, glob, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import risk_manager as RM
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hunt"))
import risk_lab as RL, payout_lab as PL


def four_simple():
    out = []
    for f in sorted(glob.glob("trades/four_simple/*.npy")):
        fam, sym = os.path.basename(f)[:-4].split("_")
        out.append((f"{fam}s_{sym}", np.load(f), sym))
    return out


if __name__ == "__main__":
    sets = {"Four, simple exit (12 legs)": four_simple(), "Book (11 legs)": RM.legs_book(), "Book + Four simple (23 legs)": RM.legs_book() + four_simple()}
    res = {}
    for name, legs in sets.items():
        B = RM.Book(legs, npaths=400)
        base, s = B.solve(0.25)
        eq, mdd, ye = B.run_real(base)
        yr = RM.period_returns(ye)
        g = lambda a, b: float(np.prod([1 + yr[y] for y in yr if a <= y <= b]) ** (1 / (b - a + 1)) - 1)
        res[name] = dict(base=base, boot=s, real_cagr=float(eq ** (1 / B.span) - 1), real_dd=float(mdd), dev=g(2011, 2019), val=g(2020, 2022), oos=g(2023, 2025), years=yr)
        print(f"{name:30s} base {base:5.2%} | reshuffled CAGR med {s['cagr_med']:6.1%} p5 {s['cagr_p5']:6.1%} DD p95 {s['dd_p95']:5.1%} worst {s['dd_worst']:5.1%} | "
              f"real CAGR {res[name]['real_cagr']:6.1%} DD {mdd:5.1%} | dev {res[name]['dev']:+.0%}/yr val {res[name]['val']:+.0%}/yr 2023-25 {res[name]['oos']:+.0%}/yr", flush=True)
        if name.startswith("Book +"):
            print("   real yearly: " + " ".join(f"{y % 100:02d}:{v:+.0%}" for y, v in yr.items()))
            legs3 = [(n, tr, w) for (n, tr, sy), w in zip(legs, B.w)]
            rng = np.random.default_rng(11)
            paths = [RL.reshuffle(legs3, rng) for _ in range(400)]
            real = RL.merge(legs3)
            for tgt in (0.0125, 0.015, 0.0175, 0.02):
                p = PL.run(paths, real, base, 0.30, 0.25, tgt, 0.0, cap=0.04)
                res[name][f"pay_{tgt}"] = p
                print(f"   pay {tgt:.2%}/fn: {p['paid_med']:.0%}/yr, on time real {p['real_hit']:.0%} typical {p['hit_med']:.0%} 1-in-20 {p['hit_p5']:.0%} | DD typ {p['dd_med']:.0%} 1-in-20 {p['dd_p95']:.0%}")
    json.dump(res, open("results/four/rm_simple.json", "w"), indent=1, default=float)
