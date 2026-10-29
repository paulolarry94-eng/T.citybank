"""Funnel search: same behaviours (S1 reversion, Donchian trend), any pair / timeframe /
direction. Every variant is replayed at two bar alignments (UTC and a GMT+2 broker clock)
so no result depends on where a chart's bars happen to start.

Usage: python3 search.py SYMBOL   -> research/results/{SYMBOL}.json + trade lists
"""
import sys, os, json, time
import numpy as np
import engine as E

OUT = os.path.join(os.path.dirname(__file__), "results")
TR = os.path.join(os.path.dirname(__file__), "trades")
os.makedirs(OUT, exist_ok=True); os.makedirs(TR, exist_ok=True)

S1_TFS = {"M15": (15,), "M20": (20,), "M30": (30,), "M20+M30": (30, 20), "H1": (60,),
          "H1+M30": (60, 30), "H4": (240,)}
TREND_TFS = {"H1": 60, "H4": 240, "D1": 1440}
SIDES = {"long": (1,), "short": (-1,), "both": (1, -1)}
OFFSETS = (0, 120)


def summarize(tr):
    s = E.stats(tr)
    if s["n"] == 0:
        return s
    r = tr["r"]
    # annualised Sharpe of the R stream at its own frequency, and t-stat of the mean
    sd = r.std(ddof=1) if len(r) > 1 else np.nan
    s["sharpe_ann"] = float(r.mean() / sd * np.sqrt(s["per_yr"])) if sd > 0 else np.nan
    s["t_stat"] = float(r.mean() / sd * np.sqrt(len(r))) if sd > 0 else np.nan
    return s


def main(sym):
    m1 = E.load_m1(sym)
    res = {}
    t0 = time.time()
    for off in OFFSETS:
        for tfn, tfs in S1_TFS.items():
            for sn, sides in SIDES.items():
                key = f"S1|{sym}|{tfn}|{sn}|off{off}"
                tr = E.run_s1(sym, m1, tfs=tfs, sides=sides, offset_min=off)
                np.save(os.path.join(TR, key.replace("|", "_") + ".npy"), tr)
                res[key] = summarize(tr)
        for tfn, tf in TREND_TFS.items():
            for mult in (2.0, 3.0):
                for sn, sides in SIDES.items():
                    key = f"TR|{sym}|{tfn}|atr{mult:g}|{sn}|off{off}"
                    tr = E.run_trend(sym, m1, tf=tf, atr_mult=mult, sides=sides, offset_min=off)
                    np.save(os.path.join(TR, key.replace("|", "_") + ".npy"), tr)
                    res[key] = summarize(tr)
        print(f"{sym} offset {off} done in {time.time()-t0:.0f}s", flush=True)
    json.dump(res, open(os.path.join(OUT, f"{sym}.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1])
