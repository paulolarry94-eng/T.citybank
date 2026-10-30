"""Exports every book leg's research trades as CSV, so an MT5 implementation can be checked trade by trade
(Strategy Tester, "every tick based on real ticks", same symbol) before any demo money is risked.

Columns: t_in_utc, t_out_utc, side, entry, stop, r_after_costs, financing_r. Parity target: >= 95% of trades
matched on entry time (+/- 1 bar) and side, and R within 0.1 for matched trades; differences explained.

    python3 parity_export.py -> results/northstar/parity/<leg>.csv
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rescore import ROOT, PFX, finance

OUT = os.path.join(ROOT, "results", "northstar", "parity")


def main():
    os.makedirs(OUT, exist_ok=True)
    book = json.load(open(os.path.join(ROOT, "results", "book_v3.json")))
    for leg in book["kept"]:
        x = np.load(os.path.join(ROOT, book["files"][leg])); sym = PFX[leg.split("_")[0]]
        df = pd.DataFrame(dict(t_in_utc=pd.to_datetime(x["t_in"], unit="s"), t_out_utc=pd.to_datetime(x["t_out"], unit="s"), side=x["side"],
                               entry=x["entry"], stop=x["entry"] - x["side"] * x["dist"], r_after_costs=x["r"], financing_r=finance(x, sym)))
        df.to_csv(os.path.join(OUT, f"{leg}.csv"), index=False, float_format="%.6f")
        print(f"{leg:34s} {sym}  {len(df):5d} trades  {df.t_in_utc.min():%Y-%m-%d} -> {df.t_in_utc.max():%Y-%m-%d}")


if __name__ == "__main__":
    main()
