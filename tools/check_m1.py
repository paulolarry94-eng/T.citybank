"""Coverage and sanity check of data/{SYM}_M1_bid_{YEAR}.npz before any test uses it.

    python3 tools/check_m1.py US500,GER40,WTI,XAGUSD 2011 2025

Per year: bars, first and last day, weekday gaps longer than 3 days (holes), the share of bad bars (low above
open/close or high below), and jumps: one-minute moves larger than 15x the median absolute one-minute move of that year
(contract rolls on oil CFDs, bad ticks). Prints the 5 largest jumps per market so they can be inspected.
"""
import os, sys
import datetime as dt
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def day(t):
    return dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def main(syms, y0, y1):
    for s in syms:
        allj = []
        print(f"\n{s}")
        for y in range(y0, y1 + 1):
            f = os.path.join(DATA, f"{s}_M1_bid_{y}.npz")
            if not os.path.exists(f):
                print(f"  {y}: MISSING"); continue
            d = np.load(f); ts, o, h, l, c = d["ts"], d["o"], d["h"], d["l"], d["c"]
            gap_days = np.diff(ts) / 86400000
            holes = int((gap_days > 3).sum())
            bad = float(np.mean((l > np.minimum(o, c) + 1e-9) | (h < np.maximum(o, c) - 1e-9)))
            r = np.abs(np.diff(np.log(c)))
            med = np.median(r[r > 0]) if (r > 0).any() else 0
            big = np.flatnonzero(r > 15 * med) if med > 0 else np.array([], int)
            allj += [(float(r[i]), ts[i + 1], c[i], c[i + 1]) for i in big]
            print(f"  {y}: {len(ts):>7} bars  {day(ts[0])[:10]} -> {day(ts[-1])[:10]}  holes>3d {holes}  bad {bad:.2%}  "
                  f"jumps>15x {len(big)}  close {c[0]:g} -> {c[-1]:g}")
        for j in sorted(allj, reverse=True)[:5]:
            print(f"    largest jump {j[0]:.2%} at {day(j[1])}: {j[2]:g} -> {j[3]:g}")


if __name__ == "__main__":
    a = sys.argv[1:]
    main([x.strip().upper() for x in a[0].split(",")], int(a[1]), int(a[2]))
