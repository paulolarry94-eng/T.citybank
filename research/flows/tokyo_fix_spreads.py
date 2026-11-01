"""Exness Zero USDJPY spread at the Tokyo fix trade's minutes (entry 23:00 UTC, exit 00:55 UTC) vs the rest of the day.
The cost study (research/exness/exness_costs.py) excluded 20:30-23:00 UTC, so the entry minute needs its own measurement.
Sample fixed before measuring: the same 6 months as the cost study (2021-03, 2022-06, 2023-09, 2024-01, 2024-07, 2025-04)
plus 2026-03 and 2026-09. Per minute: the spread of the last tick (pips). Reports the mean and the 90th percentile at
23:00, 23:01-23:05, 00:55, and over all other minutes outside 20:30-23:00.
Output: research/results/flows/tokyo_fix_spreads.json
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(R, "exness"))
import exness_costs as XC

MONTHS = [(2021, 3), (2022, 6), (2023, 9), (2024, 1), (2024, 7), (2025, 4), (2026, 3), (2026, 9)]


def main():
    out = {}; allm = []
    for y, m in MONTHS:
        s = XC.minute_spreads("USDJPY", y, m)[0] / 0.01                    # pips
        s = s[s.index.dayofweek < 5]
        hm = s.index.hour * 60 + s.index.minute
        rows = {"23:00": s[hm == 23 * 60], "23:01-23:05": s[(hm > 23 * 60) & (hm <= 23 * 60 + 5)], "00:55": s[hm == 55],
                "other minutes": s[~((hm >= 20 * 60 + 30) & (hm < 23 * 60))]}
        out[f"{y}-{m:02d}"] = {k: dict(mean=round(float(v.mean()), 3), p90=round(float(v.quantile(0.9)), 3), n=int(len(v))) for k, v in rows.items()}
        print(y, m, out[f"{y}-{m:02d}"], flush=True)
        allm.append(out[f"{y}-{m:02d}"])
    out["average over months"] = {k: round(float(np.mean([x[k]["mean"] for x in allm])), 3) for k in allm[0]}
    os.makedirs(os.path.join(R, "results", "flows"), exist_ok=True)
    json.dump(out, open(os.path.join(R, "results", "flows", "tokyo_fix_spreads.json"), "w"), indent=1)
    print(out["average over months"])


if __name__ == "__main__":
    main()
