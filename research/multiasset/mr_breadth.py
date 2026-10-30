"""Breadth for the book's short-term mean-reversion families on every daily market (pysystemtrade data).
Parameters are the book's, unchanged: RSI(2) < 5 above SMA200 (long) / > 95 below SMA200 (short), exit on a close
across SMA5 or after 10 days; Bollinger(20, 1.5): close below/above the band, exit at SMA20 or after 20 days.
Entry at the signal day's close (MOC) or, as a check, the next day's close. Vol-scaled positions, CFD costs and
financing markups. Close-only data: no intraday stop (exit rules only).

    python3 mr_breadth.py -> ../results/multiasset/mr_breadth.json
"""
import os, sys, json
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import carver as CV
from combine import CFD, ann

OUT = os.path.join(HERE, "..", "results", "multiasset")


def rsi(c, n=2):
    d = c.diff(); up = d.clip(lower=0); dn = (-d).clip(lower=0)
    ru = up.ewm(alpha=1 / n, adjust=False).mean(); rd = dn.ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + ru / rd.replace(0, np.nan))


def positions(px, kind):
    c = px
    if kind == "RSI2":
        r = rsi(c); m200 = c.rolling(200).mean(); m5 = c.rolling(5).mean()
        L = (r < 5) & (c > m200); S = (r > 95) & (c < m200); xl = c > m5; xs = c < m5; cap = 10
    else:
        m = c.rolling(20).mean(); sd = c.rolling(20).std()
        L = c < m - 1.5 * sd; S = c > m + 1.5 * sd; xl = c >= m; xs = c <= m; cap = 20
    pos = np.zeros(len(c)); cur = 0; age = 0
    Lv, Sv, xlv, xsv = L.values, S.values, xl.values, xs.values
    for t in range(len(c)):
        if cur != 0:
            age += 1
            if (cur > 0 and xlv[t]) or (cur < 0 and xsv[t]) or age >= cap:
                cur = 0
        if cur == 0:
            if Lv[t]:
                cur, age = 1, 0
            elif Sv[t]:
                cur, age = -1, 0
        pos[t] = cur
    return pd.Series(pos, index=c.index)


def run(D, kind, delay=0, vol_target=0.20):
    R, V, cls, S = D["R"], D["V"], D["cls"], D["S"]
    keep = cls.index[~cls.isin(["Vol"])]
    out = {}; per_inst = {}
    for i in keep:
        px = (1 + R[i]).cumprod()
        p = positions(px, kind).shift(delay)
        size = (vol_target / V[i].where(V[i] > 0)).clip(upper=20)
        P = (p * size).fillna(0)
        gross = P.shift(1) * R[i]
        cost = P.diff().abs() * S[i].fillna(S[i].median())
        fin = P.shift(1).abs() * CFD[cls[i]] / 256
        per_inst[i] = (gross - cost - fin).fillna(0)
    X = pd.DataFrame(per_inst)
    # equal weight across classes, equal within class, diversification credit 2 (as for trend+carry)
    w = pd.Series({i: 1.0 / (cls[keep] == cls[i]).sum() / cls[keep].nunique() for i in keep})
    port = (X * w).sum(axis=1) * 2.0
    by_cls = {c: ann((X[cls.index[cls == c].intersection(keep)].mean(axis=1))["2001":"2024"]) for c in cls[keep].unique()}
    return port, by_cls, X


def main():
    D = CV.build()
    res = {}
    src = pd.read_csv(os.path.join(OUT, "sources_daily.csv.gz"), index_col=0, parse_dates=True)
    for kind in ("RSI2", "BB"):
        for delay in (0, 1):
            port, by_cls, X = run(D, kind, delay)
            key = f"{kind} delay{delay}"
            eras = {e: ann(port[a:b]) for e, (a, b) in {"2001-2010": ("2001", "2010"), "2011-2018": ("2011", "2018"),
                                                       "2019-2024Q1": ("2019", "2024")}.items()}
            j = pd.concat([port.rename("MR"), src], axis=1).loc["2011":"2024-03"].dropna()
            res[key] = dict(full=ann(port["2001":"2024"]), eras=eras, by_class=by_cls, corr_with=j.corr()["MR"].drop("MR").round(3).to_dict())
            print(f"{key:12s} full SR {res[key]['full']['sharpe']:+.2f} | " + " | ".join(f"{e} {v['sharpe']:+.2f}" for e, v in eras.items()) +
                  " | by class " + " ".join(f"{c}:{v['sharpe']:+.2f}" for c, v in by_cls.items()) + f" | corr BOOK {res[key]['corr_with'].get('BOOK')}")
            if delay == 0:
                port.rename(key).to_csv(os.path.join(OUT, f"mr_{kind}_daily.csv.gz"))
    json.dump(res, open(os.path.join(OUT, "mr_breadth.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
