"""Crude oil predicts equity returns, checked on real futures (pysystemtrade data, no CFD financing) and on years this study
never touched. Fixed 2026-11-01 BEFORE running, after the CFD tests (oil_equity_v2: rejected after CFD financing;
calendar_study: right direction in 2011-19 and 2023-25, wrong in 2020-22).

Data: pysystemtrade adjusted futures prices (/home/user/robcarver17/pysystemtrade/data/futures): CRUDE_W (WTI) and six
  equity index futures SP500, NASDAQ, DAX, FTSE100, NIKKEI, EUROSTX. Daily return = change in the adjusted price / the
  previous day's traded contract price (multiple_prices PRICE); monthly return = sum of daily returns in the month.
Signal: the sign of WTI's monthly return. Test: next-month equity return after oil FELL minus after it ROSE, per index and
  for an equal-weight basket; t-statistics. Trading versions (no costs: futures costs are ~0.01% a month here):
  long_short = long the basket after oil fell, short after it rose; long_cash = long after oil fell, flat after it rose,
  against buy-and-hold. Periods: 2000-2010 (fresh: no test in this project used these months), 2011-latest (overlaps
  the CFD tests).
Output: research/results/flows/oil_equity_futures.json
"""
import os, json
import numpy as np
import pandas as pd

PST = "/home/user/robcarver17/pysystemtrade/data/futures"
EQ = ["SP500", "NASDAQ", "DAX", "FTSE100", "NIKKEI", "EUROSTX"]
OIL = "CRUDE_W"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "flows")


def monthly(inst):
    adj = pd.read_csv(os.path.join(PST, "adjusted_prices_csv", f"{inst}.csv"), parse_dates=["DATETIME"]).set_index("DATETIME")["price"]
    mp = pd.read_csv(os.path.join(PST, "multiple_prices_csv", f"{inst}.csv"), parse_dates=["DATETIME"]).set_index("DATETIME")["PRICE"]
    adj = adj.groupby(adj.index.normalize()).last(); mp = mp.groupby(mp.index.normalize()).last()
    px = mp.reindex(adj.index).ffill()
    r = (adj.diff() / px.shift(1)).replace([np.inf, -np.inf], np.nan).dropna()
    r = r[(r.abs() < 0.5)]                                        # drop roll/data glitches larger than 50% in a day
    return r.resample("ME").sum()


def stats(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    if len(x) < 3:
        return dict(n=int(len(x)))
    return dict(n=int(len(x)), mean_pct=round(float(x.mean() * 100), 2), t=round(float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))), 2),
                sharpe_ann=round(float(x.mean() / x.std(ddof=1) * np.sqrt(12)), 2))


def diff(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return dict(n_fell=int(len(a)), n_rose=int(len(b)), diff_pct=round(float((a.mean() - b.mean()) * 100), 2), t=round(float((a.mean() - b.mean()) / se), 2))


def main():
    oil = monthly(OIL); s = np.sign(oil).shift(1)                 # sign of LAST month's oil return, aligned to this month
    E = pd.DataFrame({i: monthly(i) for i in EQ})
    D = E.join(s.rename("oil_prev"), how="inner").dropna(subset=["oil_prev"])
    D["basket"] = D[EQ].mean(axis=1, skipna=True)
    periods = {"2000-2010 (fresh)": (2000, 2010), "2011-latest": (2011, 2100), "all": (1990, 2100)}
    res = {"first_month": str(D.index.min().date()), "last_month": str(D.index.max().date()), "by_period": {}}
    for pn, (y0, y1) in periods.items():
        g = D[(D.index.year >= y0) & (D.index.year <= y1)]
        fell, rose = g[g.oil_prev < 0], g[g.oil_prev > 0]
        row = {i: diff(fell[i].dropna(), rose[i].dropna()) for i in EQ + ["basket"]}
        ls = np.where(g.oil_prev < 0, g.basket, -g.basket)
        lc = np.where(g.oil_prev < 0, g.basket, 0.0)
        row["trade long_short basket"] = stats(ls)
        row["trade long_cash basket"] = stats(lc)
        row["buy_and_hold basket"] = stats(g.basket)
        res["by_period"][pn] = row
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "oil_equity_futures.json"), "w"), indent=1)
    print("months", res["first_month"], "->", res["last_month"])
    for pn, row in res["by_period"].items():
        print(f"\n== {pn}")
        for k, v in row.items():
            print(f"  {k:26s} {v}")


if __name__ == "__main__":
    main()
