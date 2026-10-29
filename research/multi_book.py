"""Four-market timeless book. Candidates = every strategy that is positive in all three eras
and out-of-sample (full passes first). Greedy correlation filter < 0.30 on monthly R.
Weights = inverse monthly-R volatility measured on 2011-2018 only (risk balance, no
return-chasing), so 2019-2025 stays a fair test."""
import numpy as np, json, datetime as dt
import gold_search as GS

CANDS = {  # name: (file, full_pass)
 "XAU_S1_reversion_H1M30M20": ("trades/S1_XAUUSD_H1+M30+M20_long_off120.npy", True),
 "XAU_Donchian20_H4_turtle":  ("trades/multi/XAUUSD_DON_H4_n20_turtle.npy", True),
 "JPY_VolBreakout_D1_k0.7":   ("trades/multi/USDJPY_VBO_D1_k0.7.npy", True),
 "JPY_S2_Donchian20_H4_long": ("trades/TR_USDJPY_H4_atr2_long_off120.npy", True),
 "XAU_EMA20-50_H4":           ("trades/multi/XAUUSD_MAX_H4_20-50.npy", False),
 "XAU_VolBreakout_D1_k0.5":   ("trades/multi/XAUUSD_VBO_D1_k0.5.npy", False),
 "JPY_Donchian55_D1_trail":   ("trades/multi/USDJPY_DON_D1_n55_trail.npy", False),
 "JPY_RSI2_D1_lo5":           ("trades/multi/USDJPY_RSI2_D1_lo5.npy", False),
 "XAU_Donchian55_H4_turtle":  ("trades/multi/XAUUSD_DON_H4_n55_turtle.npy", False),
 "XAU_S3_Donchian20_H4_3atr": ("trades/TR_XAUUSD_H4_atr3_both_off120.npy", False),
}


def monthly(tr):
    mk = np.array([(dt.datetime.utcfromtimestamp(int(t)).year - 2011) * 12 + dt.datetime.utcfromtimestamp(int(t)).month - 1 for t in tr["t_out"]])
    s = np.zeros(180); ok = (mk >= 0) & (mk < 180); np.add.at(s, mk[ok], tr["r"][ok]); return s


def build(verbose=True):
    T = {k: np.load(p) for k, (p, _) in CANDS.items()}
    J = {k: GS.judge(T[k], 0.53 if k.startswith("XAU") else 0.0) for k in T}
    M = {k: monthly(T[k]) for k in T}
    order = sorted(T, key=lambda k: (not CANDS[k][1], -J[k]["t"]))     # full passes first, then t
    kept = []
    for k in order:
        timeless = all(x > 0 for x in J[k]["regimes"].values()) and J[k]["E_oos"] > 0
        cs = {q: float(np.corrcoef(M[k], M[q])[0, 1]) for q in kept}
        ok = timeless and all(abs(c) < 0.30 for c in cs.values())
        if verbose:
            R = J[k]["regimes"]
            print(f"  {'KEEP' if ok else 'drop'} {k:28s} {J[k]['per_yr']:6.1f}/yr E {J[k]['E']:+.3f} t {J[k]['t']:.2f} "
                  f"eras {R['bear_2011_15']:+.3f}/{R['range_2016_18']:+.3f}/{R['bull_2019_25']:+.3f} "
                  f"{'' if timeless else '(not timeless) '}maxcorr {max([abs(c) for c in cs.values()] or [0]):.2f}")
        if ok: kept.append(k)
    vol = np.array([M[k][:96].std(ddof=1) for k in kept])
    w = (1 / vol); w = w / w.max()
    return kept, dict(zip(kept, map(float, w))), T, M, J


if __name__ == "__main__":
    kept, W, T, M, J = build()
    print("\nweights (2011-2018 risk balance):", {k: round(v, 2) for k, v in W.items()})
    mon = sum(W[k] * M[k] for k in kept)
    nz = np.count_nonzero(mon)
    sh = mon.mean() / mon.std(ddof=1) * np.sqrt(12); t = mon.mean() / mon.std(ddof=1) * np.sqrt(nz)
    isv, oos = mon[:96], mon[96:]
    yrs = [mon[i*12:(i+1)*12].sum() for i in range(15)]
    eras = (mon[:60].mean(), mon[60:96].mean(), mon[96:].mean())
    print(f"BOOK: {sum(J[k]['per_yr'] for k in kept):.0f} trades/yr ({sum(J[k]['per_yr'] for k in kept)/26:.1f} per fortnight) | "
          f"monthly Sharpe {sh:.2f} (IS {isv.mean()/isv.std(ddof=1)*np.sqrt(12):.2f}, OOS {oos.mean()/oos.std(ddof=1)*np.sqrt(12):.2f}) | t {t:.2f}")
    print(f"      eras (mean monthly R): {eras[0]:+.3f} / {eras[1]:+.3f} / {eras[2]:+.3f} | positive months {(mon>0).mean():.0%} | "
          f"positive years {sum(y>0 for y in yrs)}/15")
    print("      per-year R: " + " ".join(f"{11+i:02d}:{y:+.1f}" for i, y in enumerate(yrs)))
    json.dump({"kept": kept, "weights": W}, open("results/multi_book.json", "w"), indent=1)
