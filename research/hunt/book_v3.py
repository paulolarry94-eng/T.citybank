"""Hunt 2, step 5: does anything new earn a place in the book? Same rules as multi_book.py:
timeless (positive in all three eras and out-of-sample), greedy correlation < 0.30 on monthly R,
weights = inverse monthly-R volatility on 2011-2018 only."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
os.environ["BOOK_FILTERED"] = "1"
os.chdir(os.path.join(HERE, ".."))
import numpy as np
import multi_book as MB
import euro_hours as EH

NEW = {
    "EUR_EuroHours_short_TueThu": ("trades/hunt/EUR_EuroHours_short_0913_TueThu.npy", True),
    "GBPJPY_Donchian20_H4_trail": ("trades/crosses/GBPJPY_DON_H4_n20_trail.npy", False),
    "EURGBP_Bollinger_D1_k1.5": ("trades/crosses/EURGBP_BB_D1_k1.5.npy", False),
}

if __name__ == "__main__":
    np.save("trades/hunt/EUR_EuroHours_short_0913_TueThu.npy", EH.build(k=0.5, days=(1, 2, 3)))
    MB.CANDS.update(NEW)
    kept, W, T, M, J = MB.build()
    mon = sum(W[k] * M[k] for k in kept)
    nz = np.count_nonzero(mon)
    sh = mon.mean() / mon.std(ddof=1) * np.sqrt(12); t = mon.mean() / mon.std(ddof=1) * np.sqrt(nz)
    isv, oos = mon[:96], mon[96:]
    yrs = [mon[i*12:(i+1)*12].sum() for i in range(15)]
    print("\nweights:", {k: round(v, 2) for k, v in W.items()})
    print(f"BOOK v3: {len(kept)} legs, {sum(J[k]['per_yr'] for k in kept):.0f} trades/yr | monthly Sharpe {sh:.2f} "
          f"(IS {isv.mean()/isv.std(ddof=1)*np.sqrt(12):.2f}, OOS {oos.mean()/oos.std(ddof=1)*np.sqrt(12):.2f}) | t {t:.2f} | "
          f"positive months {(mon>0).mean():.0%} | positive years {sum(y>0 for y in yrs)}/15")
    json.dump({"kept": kept, "weights": W, "files": {k: MB.CANDS[k][0] for k in kept}},
              open("results/book_v3.json", "w"), indent=1)
