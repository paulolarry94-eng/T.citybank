"""Diversified daily trend + carry with volatility targeting (Carver, "Systematic Trading" /
"Advanced Futures Trading Strategies"), on pysystemtrade's public futures data.

No parameter is fitted: EWMAC speeds, forecast scalars, caps, carry smoothing and the 60/40 trend/carry split
are the published defaults. Positions are in return space (fraction of capital), as with CFDs.

Costs: per trade = spread cost from pysystemtrade's spreadcosts.csv x CFD_SPREAD_MULT (CFD spreads are wider than
futures); plus a CFD financing markup per year on |position| (futures carry already contains the interest
differential, a CFD adds the broker's markup): FX 0.5%, everything else 2.5%.

    python3 carver.py -> ../results/multiasset/daily_returns.parquet-like CSVs + summary
"""
import os, sys, json, math
import numpy as np
import pandas as pd

PST = "/home/user/robcarver17/pysystemtrade/data/futures"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "multiasset")
UNIVERSE = {
    "FX": ["EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD", "MXP", "NOK", "SEK", "ZAR", "PLN", "GBPJPY", "AUDJPY", "CHFJPY",
           "EURAUD", "EURCAD", "EURCHF", "GBPCHF", "GBPEUR", "YENEUR"],
    "Metals": ["GOLD", "SILVER", "PLAT", "PALLAD", "COPPER"],
    "Energy": ["CRUDE_W", "BRENT-LAST", "GAS_US", "HEATOIL", "GASOILINE", "GASOIL"],
    "Equity": ["SP500", "NASDAQ", "DOW", "RUSSELL", "DAX", "EUROSTX", "CAC", "FTSE100", "NIKKEI", "HANG", "SPI200", "IBEX",
               "AEX", "SMI", "MIB"],
    "Bond": ["US10", "US5", "US2", "US30", "BUND", "BOBL", "SHATZ", "GILT", "OAT", "BTP", "JGB"],
    "Ags": ["CORN", "WHEAT", "SOYBEAN", "SOYOIL", "SOYMEAL", "SUGAR11", "COFFEE", "COCOA", "COTTON", "LIVECOW", "LEANHOG"],
    "Vol": ["VIX", "V2X"],
}
EWMAC = [(8, 32, 5.3), (16, 64, 3.75), (32, 128, 2.65), (64, 256, 1.87)]
CARRY_SCALAR, CAP = 30.0, 20.0
CFD_SPREAD_MULT = 2.0
MARKUP = {"FX": 0.005}
MARKUP_DEFAULT = 0.025
START = "2000-01-01"


def daily(path, cols):
    d = pd.read_csv(path, parse_dates=["DATETIME"])
    d["date"] = d.DATETIME.dt.normalize()
    return d.groupby("date")[cols].last()


def contract_years(c):
    c = pd.to_numeric(c, errors="coerce")
    y = (c // 10000); m = (c // 100) % 100
    return y + (m - 1) / 12.0


def load(inst):
    adj = daily(os.path.join(PST, "adjusted_prices_csv", f"{inst}.csv"), ["price"])["price"]
    mp = daily(os.path.join(PST, "multiple_prices_csv", f"{inst}.csv"), ["PRICE", "CARRY", "PRICE_CONTRACT", "CARRY_CONTRACT"])
    df = pd.concat([adj.rename("adj"), mp], axis=1).sort_index()
    df = df[df.index >= "1995-01-01"]
    df["PRICE"] = df.PRICE.ffill()
    return df


def signals(df):
    p = df.adj.ffill()
    dp = p.diff()
    vol_p = dp.ewm(span=35, min_periods=20).std()                         # daily price-unit vol
    vol_p = vol_p.clip(lower=vol_p.rolling(500, min_periods=20).quantile(0.05))  # floor (Carver: 5th pct)
    fc = []
    for f, s, sc in EWMAC:
        raw = (p.ewm(span=f, min_periods=f).mean() - p.ewm(span=s, min_periods=s).mean()) / vol_p
        fc.append((raw * sc).clip(-CAP, CAP))
    trend = sum(fc) / len(fc)
    dt = contract_years(df.CARRY_CONTRACT) - contract_years(df.PRICE_CONTRACT)
    raw_carry = (df.PRICE - df.CARRY) / dt.where(dt.abs() > 1e-6)              # price units per year, + = long earns roll
    carry = (raw_carry / (vol_p * 16)).ewm(span=90, min_periods=20).mean() * CARRY_SCALAR
    carry = carry.ffill().clip(-CAP, CAP)
    ret = dp / df.PRICE.shift(1)                                            # return on capital per unit notional
    vol_pct = vol_p * 16 / df.PRICE                                         # annualised % vol
    return trend, carry, ret, vol_pct


def build(trend_w=0.6, fdm=1.25, vol_target=0.20, start=START):
    sc = pd.read_csv(os.path.join(PST, "csvconfig", "spreadcosts.csv")).set_index("Instrument").SpreadCost
    data = {}
    for cls, insts in UNIVERSE.items():
        for i in insts:
            f = os.path.join(PST, "adjusted_prices_csv", f"{i}.csv")
            if not os.path.exists(f):
                continue
            df = load(i)
            if df.index[0] > pd.Timestamp("2012-01-01") or len(df) < 1500:
                continue
            tr, ca, r, v = signals(df)
            spread_pct = (sc.get(i, np.nan) * CFD_SPREAD_MULT) / df.PRICE
            data[i] = dict(cls=cls, trend=tr, carry=ca, ret=r, vol=v, spread=spread_pct)
    idx = pd.date_range(start, max(d["ret"].index.max() for d in data.values()), freq="B")
    F = lambda k: pd.DataFrame({i: d[k].reindex(idx).ffill(limit=5) for i, d in data.items()})
    T, C, R, V, S = F("trend"), F("carry"), pd.DataFrame({i: d["ret"].reindex(idx) for i, d in data.items()}).fillna(0.0), F("vol"), F("spread")
    cls = pd.Series({i: d["cls"] for i, d in data.items()})
    return dict(T=T, C=C, R=R, V=V, S=S, cls=cls)


def portfolio(D, trend_w=0.6, fdm=1.25, vol_target=0.20, idm=None, rules="both", buffer=0.10, markup=True):
    T, C, R, V, S, cls = D["T"], D["C"], D["R"], D["V"], D["S"], D["cls"]
    if rules == "trend":
        fc = T * fdm / 1.0
    elif rules == "carry":
        fc = C.fillna(0) * 1.0
    else:
        fc = (trend_w * T + (1 - trend_w) * C.fillna(0)) * fdm
    fc = fc.clip(-CAP, CAP)
    live = T.notna() & V.notna() & (V > 0)
    # instrument weights: equal across asset classes present that day, equal within class
    n_cls = live.T.groupby(cls).any().T.sum(axis=1)
    per_cls = live.T.groupby(cls).sum().T
    w = live.astype(float)
    for c in cls.unique():
        cols = cls.index[cls == c]
        w[cols] = live[cols].astype(float).div(per_cls[c].replace(0, np.nan), axis=0).div(n_cls, axis=0)
    w = w.fillna(0.0)
    if idm is None:
        idm = 2.0
    target = (fc / 10.0) * w * idm * vol_target / V.where(V > 0)
    target = target.where(live, 0.0).fillna(0.0)
    # buffering: trade only when the position drifts more than `buffer` x |average position| from target
    pos = np.zeros(target.shape); tv = target.values; avg = (w * idm * vol_target / V.where(V > 0)).fillna(0).values
    for t in range(1, len(tv)):
        p = pos[t - 1]; band = buffer * np.abs(avg[t])
        pos[t] = np.where(np.abs(tv[t] - p) > band, np.where(tv[t] > p, tv[t] - band, tv[t] + band), p)
        pos[t] = np.where(avg[t] == 0, 0.0, pos[t])
    P = pd.DataFrame(pos, index=target.index, columns=target.columns)
    gross = (P.shift(1) * R).sum(axis=1)
    trade_cost = (P.diff().abs() * S.fillna(S.median())).sum(axis=1)
    fin = 0.0
    if markup:
        mk = pd.Series({i: MARKUP.get(cls[i], MARKUP_DEFAULT) for i in cls.index})
        fin = (P.shift(1).abs() * mk).sum(axis=1) / 256.0
    net = gross - trade_cost - fin
    return dict(net=net, gross=gross, cost=trade_cost, fin=fin, pos=P, lev=P.abs().sum(axis=1))


def stats(r, label=""):
    r = r.dropna()
    if len(r) < 50:
        return {}
    ann = r.mean() * 256; vol = r.std() * 16
    eq = (1 + r).cumprod(); dd = (1 - eq / eq.cummax()).max()
    yrs = len(r) / 256
    down = r[r < 0]
    return dict(label=label, cagr=float(eq.iloc[-1] ** (1 / yrs) - 1), ann_mean=float(ann), vol=float(vol), sharpe=float(ann / vol) if vol else None,
                sortino=float(ann / (np.sqrt((down ** 2).mean()) * 16)) if len(down) else None, max_dd=float(dd),
                pos_years=f"{int((r.groupby(r.index.year).sum() > 0).sum())}/{r.index.year.nunique()}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    D = build()
    print("instruments:", len(D["cls"]), D["cls"].value_counts().to_dict())
    rows = []; series = {}
    for name, kw in (("trend+carry", {}), ("trend only", dict(rules="trend")), ("carry only", dict(rules="carry")),
                     ("trend+carry, no CFD markup", dict(markup=False)),
                     ("trend+carry ex Vol", None)):
        if kw is None:
            D2 = dict(D); keep = D["cls"].index[D["cls"] != "Vol"]
            D2 = {k: (v[keep] if isinstance(v, pd.DataFrame) else v[keep]) for k, v in D.items()}
            res = portfolio(D2)
        else:
            res = portfolio(D, **kw)
        series[name] = res["net"]
        for per, (a, b) in (("2000-2024Q1", ("2000", "2024")), ("2000-2009", ("2000", "2009")), ("2010-2018", ("2010", "2018")),
                            ("2019-2024Q1", ("2019", "2024"))):
            s = stats(res["net"][a:b], name); s["period"] = per
            s["cost_pa"] = float(res["cost"][a:b].mean() * 256); s["fin_pa"] = float((res["fin"][a:b] if not isinstance(res["fin"], float) else pd.Series(0)).mean() * 256)
            s["avg_leverage"] = float(res["lev"][a:b].mean())
            rows.append(s)
    S = pd.DataFrame(rows)
    S.to_csv(os.path.join(OUT, "carver_summary.csv"), index=False)
    pd.DataFrame(series).to_csv(os.path.join(OUT, "carver_daily_returns.csv.gz"))
    with pd.option_context("display.width", 200):
        print(S.round(3).to_string(index=False))
