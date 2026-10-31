"""Combine every return source into one portfolio and map the return / drawdown frontier.

Sources (daily returns on capital, overlapping period 2011 to 2024-03):
  BOOK      the 11-leg book (costs + financing), 1% base risk x leg weight, P&L booked at exit
  TC_FUT    trend + carry on futures, all classes except Vol (no CFD markup)
  TC_CFD    trend + carry as CFDs (class markups), excluding bonds and Vol
  XSMOM     cross-sectional momentum: within each asset class, long the top third / short the bottom third
            by 12-month return skipping the last month, vol-scaled, rebalanced monthly (CFD markups)
  PAIRS     stat-arb: z-score mean reversion of log price ratios of 10 economically linked pairs (CFD markups)
Then: correlations, inverse-vol and equal-risk mixes, and a Monte Carlo (quarter-block bootstrap) frontier of
CAGR / max drawdown / ruin probabilities at portfolio vol targets 10%-60%, plus the Kelly fraction.

    python3 combine.py -> ../results/multiasset/combine.json
"""
import os, sys, json, math
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "northstar"))
import carver as CV

OUT = os.path.join(HERE, "..", "results", "multiasset")
CFD = {"FX": 0.005, "Equity": 0.02, "Bond": 0.02, "Metals": 0.01, "Energy": 0.003, "Ags": 0.003, "Vol": 0.003}
PAIRS = [("AUD", "NZD"), ("EUR", "CHF"), ("GOLD", "SILVER"), ("SP500", "NASDAQ"), ("DAX", "EUROSTX"), ("CRUDE_W", "BRENT-LAST"),
         ("CORN", "WHEAT"), ("SOYBEAN", "SOYMEAL"), ("FTSE100", "EUROSTX"), ("HEATOIL", "GASOIL")]


def book_daily():
    import ns_portfolio as PF
    T, names = PF.build("BOOK")
    d = pd.to_datetime(T["t_out"], unit="s").normalize() + pd.offsets.BDay(0)  # Sunday-open exits count on Monday
    pnl = pd.Series(0.01 * T["w"] * T["r"], index=d).groupby(level=0).sum()
    idx = pd.date_range("2011-01-03", pnl.index.max(), freq="B")
    return pnl.reindex(idx, fill_value=0.0)


def subset(D, keep):
    return {k: (v[keep] if isinstance(v, (pd.DataFrame, pd.Series)) else v) for k, v in D.items()}


def tc(D, keep, markup):
    CV.MARKUP.clear(); CV.MARKUP_DEFAULT = 0.0
    if markup:
        CV.MARKUP.update(CFD)
    return CV.portfolio(subset(D, keep))["net"]


def xsmom(D, vol_target=0.20):
    R, V, cls, S = D["R"], D["V"], D["cls"], D["S"]
    keep = cls.index[(cls != "Vol") & (cls != "Bond")]
    R, V, cls, S = R[keep], V[keep], cls[keep], S[keep]
    px = (1 + R).cumprod()
    mom = px.shift(21) / px.shift(252) - 1
    me = mom.resample("BME").last()
    sig = pd.DataFrame(0.0, index=me.index, columns=keep)
    for c in cls.unique():
        cols = cls.index[cls == c]
        rk = me[cols].rank(axis=1, pct=True)
        n = me[cols].notna().sum(axis=1)
        sig[cols] = np.where(rk >= 2 / 3, 1.0, np.where(rk <= 1 / 3, -1.0, 0.0)) * (n >= 3).values[:, None]
    sig = sig.reindex(R.index, method="ffill").shift(1).fillna(0)
    n_cls = cls.nunique()
    per = sig.abs().T.groupby(cls).sum().T.replace(0, np.nan)
    w = sig.copy()
    for c in cls.unique():
        cols = cls.index[cls == c]
        w[cols] = sig[cols].div(per[c], axis=0) / n_cls
    P = (w.fillna(0) * 2.0 * vol_target / V.where(V > 0)).fillna(0)
    gross = (P.shift(1) * R).sum(axis=1)
    cost = (P.diff().abs() * S.fillna(S.median())).sum(axis=1)
    fin = (P.shift(1).abs() * pd.Series({i: CFD[cls[i]] for i in keep})).sum(axis=1) / 256
    return gross - cost - fin


def pairs(D, vol_target=0.20, look=60, entry=1.5, exit_=0.25):
    R, V, cls, S = D["R"], D["V"], D["cls"], D["S"]
    out = []
    for a, b in PAIRS:
        if a not in R or b not in R:
            continue
        la, lb = np.log((1 + R[a]).cumprod()), np.log((1 + R[b]).cumprod())
        beta = la.diff().rolling(250).cov(lb.diff()) / lb.diff().rolling(250).var()
        spread = la - beta * lb
        z = (spread - spread.rolling(look).mean()) / spread.rolling(look).std()
        pos = pd.Series(0.0, index=z.index); cur = 0.0
        zv = z.values; pv = np.zeros(len(zv))
        for t in range(len(zv)):
            if not np.isfinite(zv[t]):
                cur = 0.0
            elif cur == 0 and zv[t] > entry:
                cur = -1.0
            elif cur == 0 and zv[t] < -entry:
                cur = 1.0
            elif cur != 0 and abs(zv[t]) < exit_:
                cur = 0.0
            pv[t] = cur
        pos = pd.Series(pv, index=z.index)
        sret = R[a] - beta.shift(1) * R[b]
        svol = sret.ewm(span=60).std() * 16
        lev = (vol_target / svol).clip(upper=10).shift(1)
        r = pos.shift(1) * lev * sret
        notional = pos.shift(1).abs() * lev * (1 + beta.abs().shift(1))
        cost = pos.diff().abs() * lev * (S[a].fillna(0) + beta.abs() * S[b].fillna(0))
        fin = notional * CFD.get(cls[a], 0.01) / 256
        out.append((r - cost - fin).rename(f"{a}/{b}"))
    P = pd.concat(out, axis=1).fillna(0)
    return P.mean(axis=1) * math.sqrt(len(out)) / 2       # ~ equal risk, partial diversification credit


def ann(r):
    r = r.dropna(); eq = (1 + r).cumprod()
    return dict(sharpe=float(r.mean() / r.std() * 16), vol=float(r.std() * 16), cagr=float(eq.iloc[-1] ** (256 / len(r)) - 1),
                max_dd=float((1 - eq / eq.cummax()).max()))


def frontier(r, targets=(0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60), n=1000, seed=3, horizon_years=3):
    """Scale the combined series to each vol target; quarter-block bootstrap of 3-year paths."""
    r = r.dropna(); r = r / (r.std() * 16)               # unit annual vol
    q = r.groupby([r.index.year, r.index.quarter]).apply(lambda x: x.values)
    blocks = list(q.values); rng = np.random.default_rng(seed)
    nb = horizon_years * 4
    rows = []
    for tv in targets:
        cagr, mdd = [], []
        for _ in range(n):
            path = np.concatenate([blocks[i] for i in rng.integers(0, len(blocks), nb)]) * tv
            eq = np.cumprod(1 + path); cagr.append(eq[-1] ** (1 / horizon_years) - 1); mdd.append((1 - eq / np.maximum.accumulate(eq)).max())
        cagr, mdd = np.array(cagr), np.array(mdd)
        full = r * tv; eqf = (1 + full).cumprod()
        rows.append(dict(vol_target=tv, hist_cagr=float(eqf.iloc[-1] ** (256 / len(full)) - 1), hist_max_dd=float((1 - eqf / eqf.cummax()).max()),
                         cagr_p10=float(np.quantile(cagr, 0.10)), cagr_median=float(np.median(cagr)), cagr_p90=float(np.quantile(cagr, 0.90)),
                         dd_median=float(np.median(mdd)), dd_p95=float(np.quantile(mdd, 0.95)),
                         p_dd_over_30=float((mdd > 0.30).mean()), p_dd_over_50=float((mdd > 0.50).mean()),
                         p_cagr_over_60=float((cagr > 0.60).mean()), p_loss_3y=float((cagr < 0).mean())))
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    D = CV.build()
    cls = D["cls"]
    src = {"BOOK": book_daily(),
           "TC_FUT": tc(D, cls.index[cls != "Vol"], False),
           "TC_CFD": tc(D, cls.index[~cls.isin(["Vol", "Bond"])], True),
           "XSMOM": xsmom(D),
           "PAIRS": pairs(D)}
    X = pd.DataFrame(src)
    X = X.loc["2011-01-03":"2024-03-28"].fillna(0.0)
    res = {"period": "2011-01-03 to 2024-03-28", "sources": {k: ann(X[k]) for k in X},
           "sources_by_era": {k: {e: ann(X[k][a:b]) for e, (a, b) in {"2011-2016": ("2011", "2016"), "2017-2020": ("2017", "2020"), "2021-2024Q1": ("2021", "2024")}.items()} for k in X},
           "corr": X.corr().round(3).to_dict()}
    # mixes: inverse-vol weights estimated on 2011-2016 only, then held fixed
    est = X["2011":"2016"]; iv = 1 / est.std()
    mixes = {"BOOK alone": ["BOOK"], "BOOK + TC_CFD": ["BOOK", "TC_CFD"], "BOOK + TC_FUT": ["BOOK", "TC_FUT"],
             "BOOK + TC_CFD + XSMOM + PAIRS": ["BOOK", "TC_CFD", "XSMOM", "PAIRS"], "BOOK + TC_FUT + XSMOM + PAIRS": ["BOOK", "TC_FUT", "XSMOM", "PAIRS"]}
    res["mixes"] = {}
    for name, ks in mixes.items():
        w = iv[ks] / iv[ks].sum()
        m = (X[ks] * w).sum(axis=1)
        res["mixes"][name] = dict(weights=w.round(3).to_dict(), full=ann(m), by_era={e: ann(m[a:b]) for e, (a, b) in
                                  {"2011-2016 (weights fitted)": ("2011", "2016"), "2017-2024Q1 (after)": ("2017", "2024")}.items()},
                                  frontier=frontier(m))
    json.dump(res, open(os.path.join(OUT, "combine.json"), "w"), indent=1, default=float)
    X.to_csv(os.path.join(OUT, "sources_daily.csv.gz"))
    print("sources 2011-2024Q1:")
    for k, v in res["sources"].items():
        print(f"  {k:7s} SR {v['sharpe']:+.2f} vol {v['vol']:.3f} cagr {v['cagr']:+.3f} dd {v['max_dd']:.2f} | eras " +
              " ".join(f"{e}:{x['sharpe']:+.2f}" for e, x in res["sources_by_era"][k].items()))
    print(pd.DataFrame(res["corr"]).to_string())
    for name, v in res["mixes"].items():
        print(f"\n{name}: weights {v['weights']}  SR full {v['full']['sharpe']:.2f} | " + " | ".join(f"{e} SR {x['sharpe']:.2f}" for e, x in v["by_era"].items()))
        F = pd.DataFrame(v["frontier"])
        print(F.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
