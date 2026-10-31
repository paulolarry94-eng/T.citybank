"""Professional tearsheet of the champion (11-leg book), 2011-2025 backtest + Jan-Oct 2026 true out-of-sample.
Primary profile: Exness Zero realistic costs + swaps; lab costs and swap-free shown alongside. 1% risk per trade x
frozen leg weight, P&L booked at exit. Output: research/results/champion/tearsheet.json"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
for p in (R, os.path.join(R, "northstar"), os.path.join(R, "exness")):
    sys.path.insert(0, p)
import core
import ns_portfolio as PF
import rescore_book as RB
from rescore import COST, SWAP

OUT = os.path.join(R, "results", "champion")


def series(cost, swap, cmult=1.0, smult=1.0):
    _, names = PF.build("BOOK"); w = np.array([n["weight"] for n in names])
    rows = []; legs = {}
    for i, (name, sym, x) in enumerate(PF.legs("BOOK")):
        nights = np.array([core.nights_held(int(a), int(b)) for a, b in zip(x["t_in"], x["t_out"])])
        r = x["r"] + COST[sym] / x["dist"] - cmult * cost[sym] / x["dist"] - smult * nights * swap[sym] / x["dist"]
        df = pd.DataFrame(dict(t_out=x["t_out"].astype(np.int64), r=r, w=w[i], leg=name, sym=sym))
        rows.append(df); legs[name] = df
    D = pd.concat(rows)
    return RB.daily(D, D["w"].to_numpy()), D, legs, {n["leg"]: n["weight"] for n in names}


def perf(p):
    eq = (1 + p).cumprod(); yrs = len(p) / 252
    dd = 1 - eq / eq.cummax()
    under = (dd > 0).astype(int); longest = 0; cur = 0
    for u in under:
        cur = cur + 1 if u else 0; longest = max(longest, cur)
    mon = p.resample("ME").sum(); yr = p.resample("YE").sum()
    down = p[p < 0]
    return dict(cagr=round(float(eq.iloc[-1] ** (1 / yrs) - 1) * 100, 2), vol=round(float(p.std() * np.sqrt(252)) * 100, 2),
                sharpe=round(float(p.mean() / p.std() * np.sqrt(252)), 2),
                sortino=round(float(p.mean() / np.sqrt((down ** 2).sum() / len(p)) * np.sqrt(252)), 2),
                max_dd=round(float(dd.max()) * 100, 2), calmar=round(float((eq.iloc[-1] ** (1 / yrs) - 1) / dd.max()), 2),
                longest_dd_days=int(longest), pos_months=round(float((mon > 0).mean()) * 100, 1),
                best_month=round(float(mon.max()) * 100, 2), worst_month=round(float(mon.min()) * 100, 2),
                pos_years=f"{int((yr > 0).sum())}/{len(yr)}")


def main():
    zc = RB.zero_costs(1.0); nos = {k: 0.0 for k in SWAP}
    prof = {"Exness Zero + swaps": (zc, SWAP), "lab costs + swaps": (COST, SWAP), "Exness Zero swap-free": (zc, nos)}
    res = {"profiles": {}}
    for lab, (c, s) in prof.items():
        p, D, legs, W = series(c, s)
        res["profiles"][lab] = {"2011-2025": perf(p), "2011-2019": perf(p[p.index < "2020"]), "2020-2022": perf(p[(p.index >= "2020") & (p.index < "2023")]),
                                "2023-2025": perf(p[p.index >= "2023"])}
        if lab == "Exness Zero + swaps":
            res["yearly_pct"] = {str(k.year): round(float(v) * 100, 2) for k, v in p.resample("YE").sum().items()}
            mon = p.resample("ME").sum()
            res["monthly_pct"] = {k.strftime("%Y-%m"): round(float(v) * 100, 2) for k, v in mon.items()}
            eq = (1 + p).cumprod()
            res["equity_monthly"] = {k.strftime("%Y-%m"): round(float(v), 4) for k, v in eq.resample("ME").last().items()}
            dd = 1 - eq / eq.cummax()
            res["drawdown_monthly"] = {k.strftime("%Y-%m"): round(float(v) * 100, 2) for k, v in dd.resample("ME").max().items()}
            roll = p.rolling(252).mean() / p.rolling(252).std() * np.sqrt(252)
            res["rolling_12m_sharpe"] = {k.strftime("%Y-%m"): round(float(v), 2) for k, v in roll.resample("ME").last().dropna().items()}
            r10 = (1 + p).rolling(210).apply(np.prod, raw=True) - 1                 # ~10 months of business days
            r10 = r10.dropna()
            v26 = json.load(open(os.path.join(OUT, "book_2026.json")))["book_2026"]["Exness Zero + swaps"]["return_pct_at_1pct"] / 100
            res["ten_month_returns"] = dict(median=round(float(r10.median()) * 100, 2), p5=round(float(r10.quantile(0.05)) * 100, 2),
                                            p10=round(float(r10.quantile(0.10)) * 100, 2), value_2026=round(v26 * 100, 2),
                                            share_at_or_below_2026=round(float((r10 <= v26).mean()) * 100, 1),
                                            share_negative=round(float((r10 < 0).mean()) * 100, 1), windows=int(len(r10)))
            edges = np.arange(np.floor(r10.min() * 100), np.ceil(r10.max() * 100) + 1, 1.0)
            cnt, _ = np.histogram(r10 * 100, bins=edges)
            res["ten_month_hist"] = dict(bins=edges.tolist(), counts=cnt.tolist())
            # legs
            lt = {}
            M = {}
            for name, df in legs.items():
                d = pd.DatetimeIndex(pd.to_datetime(df.t_out.to_numpy(), unit="s"))
                m = pd.Series(df.r.to_numpy(), index=d).resample("ME").sum()
                M[name] = m
                yrs = 15
                lt[name] = dict(sym=df.sym.iloc[0], weight=round(W[name], 2), trades_per_year=round(len(df) / yrs),
                                mean_R=round(float(df.r.mean()), 3), win=round(float((df.r > 0).mean()), 3),
                                sum_R=round(float(df.r.sum()), 1), share_of_book_pnl=None)
            tot = sum(lt[n]["sum_R"] * W[n] for n in lt)
            for n in lt:
                lt[n]["share_of_book_pnl"] = round(lt[n]["sum_R"] * W[n] / tot * 100, 1)
            Mdf = pd.DataFrame(M).fillna(0.0)
            cc = Mdf.corr().values; iu = np.triu_indices(len(cc), 1)
            res["legs"] = lt; res["avg_pairwise_monthly_corr"] = round(float(np.nanmean(cc[iu])), 3)
            res["trades_total"] = int(len(D)); res["trades_per_year"] = round(len(D) / 15)
    # stress (Exness profile): costs x1.5, swaps x2
    p, *_ = series(zc, SWAP, 1.5, 2.0)
    res["stress_costs1.5_swaps2"] = perf(p)
    # 2026 out-of-sample (from regen_2026.py)
    res["oos_2026"] = json.load(open(os.path.join(OUT, "book_2026.json")))
    json.dump(res, open(os.path.join(OUT, "tearsheet.json"), "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("profiles", "ten_month_returns", "avg_pairwise_monthly_corr", "trades_per_year", "stress_costs1.5_swaps2", "yearly_pct")}, indent=1)[:6000])


if __name__ == "__main__":
    main()
