"""Futures funnel v2: 16 cross-asset strategies from awesome-systematic-trading (research/repofunnel/PREREG.md section E,
fixed 2026-11-01 before any result; section E2: v2 trades ONE DAY AFTER each decision).

v1 (results/repofunnel/futures_funnel_v1_lookahead.json) earned on the day after the decision from the decision day's
close. With markets that close at different hours (Asia, Europe, US) and with stale prices on holidays that is a
look-ahead: the decision used the US close, then took e.g. the Hang Seng return measured from its own earlier close.
v2 fixes it for every strategy (weights decided at close t are held from close t+1). v1's final look (2023-01..2024-03)
was logged for F1, F4, F5, F10, F11, F13, so for those six the v2 final look is not fresh (disclosed in the report).

Data: pysystemtrade futures (local copy, ends 2024-03-28). Daily return = change in the adjusted price / the previous
price of the traded contract; levels for signals = the cumulative product of those returns. Weights decided at a
rebalance close apply from the next day. Costs per side = (spread cost x point size + commission per contract) /
(price x point size), times the change in weight.
Periods: development 2000-2019 (eras 2000-09, 2010-19), validation 2020-22, final look 2023-01..2024-03 (logged once per
strategy fingerprint). Gate: Sharpe > 0 in both eras and in validation (long-only timing strategies F10, F14, F15, F16 on
their return minus the equal-weight buy-and-hold of the same universe). Verdict: candidate (futures only) if the gate
passes and the final look is positive.

    python3 research/repofunnel/futures_funnel.py
"""
import os, sys, json, time, hashlib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "truth")); sys.path.insert(0, os.path.join(ROOT, "northstar")); sys.path.insert(0, ROOT)
PST = "/home/user/robcarver17/pysystemtrade/data/futures"
OUT = os.path.join(ROOT, "results", "repofunnel"); os.makedirs(OUT, exist_ok=True)
FINGERPRINT = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()

COMM = ["CORN", "WHEAT", "REDWHEAT", "SOYBEAN", "SOYMEAL", "SOYOIL", "OATIES", "RICE", "CANOLA", "LIVECOW", "FEEDCOW",
        "LEANHOG", "MILK", "GOLD", "SILVER", "PLAT", "PALLAD", "COPPER", "CRUDE_W", "BRENT_W", "GAS_US", "HEATOIL",
        "GASOILINE", "GASOIL", "COCOA", "COFFEE", "COTTON2", "SUGAR11", "OJ"]
FX = ["AUD", "CAD", "CHF", "EUR", "GBP", "JPY", "MXP", "NZD", "NOK", "SEK", "ZAR", "BRE"]
FX_DEV = ["EUR", "AUD", "CAD", "JPY", "NZD", "NOK", "SEK", "CHF", "GBP"]
EQ = ["SP500", "NASDAQ", "DOW", "SP400", "DAX", "CAC", "FTSE100", "AEX", "IBEX", "SMI", "EUROSTX", "NIKKEI", "TOPIX",
      "HANG", "KOSPI", "SPI200", "MIB"]
EQ_DEV9 = ["SP500", "NASDAQ", "DAX", "SMI", "EUROSTX", "CAC", "FTSE100", "NIKKEI", "SP400"]
EQ_FOREIGN = ["DAX", "FTSE100", "CAC", "AEX", "IBEX", "SMI", "EUROSTX", "NIKKEI", "TOPIX", "HANG", "SPI200"]
BOND = ["US2", "US5", "US10", "US20", "BUND", "BOBL", "SHATZ", "BTP", "OAT", "GILT", "JGB", "CAD10"]
ASYM22 = ["SOYOIL", "CORN", "COCOA", "COTTON2", "FEEDCOW", "GOLD", "COPPER", "HEATOIL", "COFFEE", "LIVECOW", "LEANHOG",
          "GAS_US", "OATIES", "OJ", "PALLAD", "PLAT", "SOYBEAN", "SUGAR11", "SILVER", "SOYMEAL", "WHEAT", "CRUDE_W"]
REV24 = ["AUD", "CAD", "EUR", "JPY", "SP500", "US2", "US5", "US10", "US20", "CORN", "WHEAT", "SOYBEAN", "SOYMEAL", "SOYOIL",
         "LIVECOW", "LEANHOG", "COTTON2", "GOLD", "SILVER", "COPPER", "CRUDE_W", "GAS_US", "HEATOIL", "PLAT"]
JAN6 = ["SP500", "DAX", "FTSE100", "HANG", "IBEX", "NASDAQ"]
ALL = sorted(set(COMM + FX + EQ + BOND + REV24 + JAN6))
START = "1998-01-01"
ERA1, ERA2, VAL, FINAL = ("2000", "2009"), ("2010", "2019"), ("2020", "2022"), ("2023", "2024")


# ----------------------------------------------------------------------------- data
def load():
    cfg = pd.read_csv(os.path.join(PST, "csvconfig", "instrumentconfig.csv")).set_index("Instrument")
    spr = pd.read_csv(os.path.join(PST, "csvconfig", "spreadcosts.csv")).set_index("Instrument")["SpreadCost"]
    R, PX, CAR = {}, {}, {}
    for i in ALL:
        fa = os.path.join(PST, "adjusted_prices_csv", f"{i}.csv"); fm = os.path.join(PST, "multiple_prices_csv", f"{i}.csv")
        if not (os.path.exists(fa) and os.path.exists(fm)):
            continue
        adj = pd.read_csv(fa, parse_dates=["DATETIME"]).set_index("DATETIME")["price"]
        mp = pd.read_csv(fm, parse_dates=["DATETIME"]).set_index("DATETIME")
        adj = adj.groupby(adj.index.normalize()).last(); mp = mp.groupby(mp.index.normalize()).last()
        adj = adj[adj.index >= START]; mp = mp[mp.index >= START]
        px = mp["PRICE"].reindex(adj.index).ffill()
        r = (adj.diff() / px.shift(1)).replace([np.inf, -np.inf], np.nan)
        r[(r.abs() >= 0.5) | (px.shift(1) <= 0)] = np.nan              # roll/data glitches and non-positive prices
        R[i] = r; PX[i] = px
        # annualised roll yield ln(near/far) / years apart, from the traded and the carry contract
        pc, cc = mp["PRICE_CONTRACT"], mp["CARRY_CONTRACT"]
        p, c = mp["PRICE"], mp["CARRY"]
        def ym(x):
            x = (x // 100).astype("float")
            return (x // 100) * 12 + (x % 100)
        dm = ym(cc) - ym(pc)
        near = np.where(dm > 0, p, c); far = np.where(dm > 0, c, p)
        with np.errstate(divide="ignore", invalid="ignore"):
            roll = np.log(near / far) / (np.abs(dm) / 12.0)
        roll = pd.Series(roll, index=mp.index).replace([np.inf, -np.inf], np.nan)
        roll[(dm == 0) | (near <= 0) | (far <= 0)] = np.nan
        CAR[i] = roll.reindex(adj.index).ffill(limit=10)
    R = pd.DataFrame(R).sort_index(); PX = pd.DataFrame(PX).reindex(R.index).ffill(); CAR = pd.DataFrame(CAR).reindex(R.index)
    R = R[R.index.day_of_week < 5]; PX = PX.reindex(R.index); CAR = CAR.reindex(R.index)
    cost = {}
    for i in R.columns:
        ps = float(cfg.loc[i, "Pointsize"]); com = float(cfg.loc[i, "PerBlock"]); pct = float(cfg.loc[i, "Percentage"])
        sc = float(spr.get(i, np.nan))
        c_i = (sc * ps + com) / (PX[i] * ps) + pct if np.isfinite(sc) else pd.Series(0.0005, index=PX.index)
        cost[i] = c_i.clip(upper=0.01)                                             # per side, fraction of notional
    C = pd.DataFrame(cost).reindex(R.index).ffill()
    LV = (1 + R.fillna(0)).cumprod().where(R.notna().cumsum() > 0)               # level index from the first return
    return R, LV, CAR, C


# ----------------------------------------------------------------------------- engine
def month_ends(idx):
    s = pd.Series(idx, index=idx)
    return list(s.groupby([idx.year, idx.month]).last())


LAG = 2                                                          # held from the close AFTER the decision day


def run_weights(R, C, W):
    """W: DataFrame of target weights on rebalance dates (index = decision dates). Weights apply from the next day.
    Returns daily net returns and daily cost."""
    W = W.reindex(columns=R.columns).fillna(0.0)
    full = W.reindex(R.index).ffill().fillna(0.0)
    held = full.shift(LAG).fillna(0.0)
    gross = (held * R.fillna(0.0)).sum(axis=1)
    dw = full.diff().abs().fillna(full.abs())
    cost = (dw * C.fillna(C.mean())).sum(axis=1).shift(1).fillna(0.0)
    return gross - cost, cost


def avail(LV, cols, t, look):
    """Instruments in cols with a full lookback window ending at t (and a return on t)."""
    out = []
    for i in cols:
        if i not in LV.columns:
            continue
        s = LV[i]
        j = LV.index.get_loc(t)
        if j - look < 0 or not np.isfinite(s.iloc[j]) or not np.isfinite(s.iloc[j - look]):
            continue
        out.append(i)
    return out


def mom(LV, i, t, look):
    j = LV.index.get_loc(t)
    return LV[i].iloc[j] / LV[i].iloc[j - look] - 1


def xs_quintiles(score, top_long=True):
    s = pd.Series(score).dropna().sort_values(ascending=False)
    q = len(s) // 5
    if q < 1:
        return {}
    lo, hi = list(s.index[-q:]), list(s.index[:q])
    L, S = (hi, lo) if top_long else (lo, hi)
    w = {i: 1.0 / len(L) for i in L}
    w.update({i: -1.0 / len(S) for i in S})
    return w


# ----------------------------------------------------------------------------- the 16 strategies
def F1(R, LV, CAR, C):
    U = [i for i in COMM + FX + EQ_DEV9 + BOND if i in R.columns]; rows = {}
    for t in month_ends(R.index):
        a = avail(LV, U, t, 252)
        j = R.index.get_loc(t); w = {}
        for i in a:
            vol = R[i].iloc[max(0, j - 59):j + 1].std() * np.sqrt(252)
            if not np.isfinite(vol) or vol <= 0:
                continue
            w[i] = np.sign(mom(LV, i, t, 252)) * 0.10 / vol
        n = len(w)
        if n:
            w = {k: v / n for k, v in w.items()}
            g = sum(abs(v) for v in w.values())
            if g > 4:
                w = {k: v * 4 / g for k, v in w.items()}
        rows[t] = w
    return pd.DataFrame(rows).T


def _monthly_xs(R, LV, U, look, scorer, top_long=True, k=None):
    rows = {}
    for t in month_ends(R.index):
        a = avail(LV, U, t, look)
        sc = {i: scorer(i, t) for i in a}
        sc = {i: v for i, v in sc.items() if np.isfinite(v)}
        if k is None:
            rows[t] = xs_quintiles(sc, top_long)
        else:
            s = pd.Series(sc).sort_values(ascending=False)
            if len(s) >= 2 * k:
                L, S = (list(s.index[:k]), list(s.index[-k:])) if top_long else (list(s.index[-k:]), list(s.index[:k]))
                w = {i: 1.0 / k for i in L}; w.update({i: -1.0 / k for i in S}); rows[t] = w
            else:
                rows[t] = {}
    return pd.DataFrame(rows).T


def F2(R, LV, CAR, C):
    return _monthly_xs(R, LV, [i for i in COMM if i in R.columns], 252, lambda i, t: mom(LV, i, t, 252))


def F3(R, LV, CAR, C):
    U = [i for i in COMM if i in R.columns]
    return _monthly_xs(R, LV, U, 5, lambda i, t: CAR[i].loc[t])


def F4(R, LV, CAR, C):
    U = [i for i in COMM if i in R.columns]
    def sk(i, t):
        j = R.index.get_loc(t); x = R[i].iloc[j - 251:j + 1].dropna()
        return float(x.skew()) if len(x) > 200 else np.nan
    return _monthly_xs(R, LV, U, 252, sk, top_long=False)


def F5(R, LV, CAR, C):
    U = [i for i in ASYM22 if i in R.columns]
    def ie(i, t):
        j = R.index.get_loc(t); x = R[i].iloc[j - 259:j + 1].dropna()
        if len(x) < 200:
            return np.nan
        m, s = x.mean(), x.std()
        return float((x > m + 2 * s).sum() - (x < m - 2 * s).sum())
    return _monthly_xs(R, LV, U, 260, ie, top_long=False, k=7)


def F6(R, LV, CAR, C):
    return _monthly_xs(R, LV, [i for i in FX if i in R.columns], 252, lambda i, t: mom(LV, i, t, 252), k=3)


def F7(R, LV, CAR, C):
    return _monthly_xs(R, LV, [i for i in FX if i in R.columns], 5, lambda i, t: CAR[i].loc[t], k=3)


def F8(R, LV, CAR, C):
    U = [i for i in FX_DEV if i in R.columns]; rows = {}
    for t in month_ends(R.index):
        a = [i for i in avail(LV, U, t, 5) if np.isfinite(CAR[i].loc[t])]
        if len(a) < 4:
            rows[t] = {}; continue
        sgn = 1.0 if np.mean([CAR[i].loc[t] for i in a]) > 0 else -1.0
        rows[t] = {i: sgn / len(a) for i in a}
    return pd.DataFrame(rows).T


def F9(R, LV, CAR, C):
    U = [i for i in REV24 if i in R.columns]; rows = {}
    idx = R.index
    weds = pd.Series(idx, index=idx)
    ends = list(weds.groupby(idx.to_period("W-WED")).last())                          # last trading day <= each Wednesday
    for t0, t in zip(ends[:-1], ends[1:]):
        a = [i for i in U if np.isfinite(LV[i].loc[t]) and np.isfinite(LV[i].loc[t0])]
        if len(a) < 6:
            rows[t] = {}; continue
        r = pd.Series({i: LV[i].loc[t] / LV[i].loc[t0] - 1 for i in a})
        d = -(r - r.mean())
        g = d.abs().sum()
        rows[t] = (d / g).to_dict() if g > 0 else {}
    return pd.DataFrame(rows).T


def F10(R, LV, CAR, C):
    rows, bench = {}, {}
    qe = [t for t in month_ends(R.index) if t.month in (3, 6, 9, 12)]
    for t0, t in zip(qe[:-1], qe[1:]):
        a = [i for i in ("SP500", "US20") if np.isfinite(LV[i].loc[t]) and np.isfinite(LV[i].loc[t0])]
        if len(a) < 2:
            rows[t] = {}; bench[t] = {}; continue
        win = max(a, key=lambda i: LV[i].loc[t] / LV[i].loc[t0])
        rows[t] = {win: 1.0}; bench[t] = {"SP500": 0.5, "US20": 0.5}
    return pd.DataFrame(rows).T, pd.DataFrame(bench).T


def F11(R, LV, CAR, C):
    U = [i for i in EQ if i in R.columns]; idx = R.index; n = len(idx)
    W = pd.DataFrame(0.0, index=idx, columns=U)
    for s0 in range(120, n - 1, 20):
        f0, f1 = s0 - 120, s0                                   # formation [f0, f1), trading [f1, f1 + 20)
        a = [i for i in U if R[i].iloc[f0:f1].notna().sum() >= 110 and R[i].iloc[f1:min(f1 + 20, n)].notna().any()]
        if len(a) < 4:
            continue
        P = (1 + R[a].iloc[f0:min(f1 + 20, n)].fillna(0)).cumprod()
        F = P.iloc[:120]
        pairs = []
        for x in range(len(a)):
            for y in range(x + 1, len(a)):
                d = float(((F[a[x]] - F[a[y]]) ** 2).sum()); pairs.append((d, a[x], a[y]))
        pairs.sort()
        for d, x, y in pairs[:5]:
            sp = P[x] - P[y]; sd = sp.iloc[:120].std()
            pos = 0
            for k in range(120, len(P)):
                t = P.index[k]; v = sp.iloc[k]
                if pos == 0 and abs(v) > 0.5 * sd:
                    pos = -1 if v > 0 else 1                     # +1 = long x / short y
                if pos != 0 and ((pos == -1 and v <= 0) or (pos == 1 and v >= 0)):
                    pos = 0                                      # converged: close
                if pos != 0 and k < len(P) - 1:
                    W.loc[t, x] += 0.2 * pos; W.loc[t, y] -= 0.2 * pos
        # positions are closed at the end of the trading period (the last day carries no weight)
    return W


def F12(R, LV, CAR, C):
    U = [i for i in EQ_FOREIGN + ["KOSPI", "MIB"] if i in R.columns]; rows = {}
    for t in month_ends(R.index):
        j = R.index.get_loc(t)
        m = R["SP500"].iloc[j - 251:j + 1]
        betas = {}
        for i in U:
            x = R[i].iloc[j - 251:j + 1]
            ok = x.notna() & m.notna()
            if ok.sum() < 200:
                continue
            betas[i] = np.cov(x[ok], m[ok])[0, 1] / np.var(m[ok], ddof=1)
        if len(betas) < 4:
            rows[t] = {}; continue
        b = pd.Series(betas); z = b.rank(); zb = z.mean()
        wl = (zb - z).clip(lower=0); wh = (z - zb).clip(lower=0)
        wl, wh = wl / wl.sum(), wh / wh.sum()
        bl, bh = float((wl * b).sum()), float((wh * b).sum())
        if bl <= 0 or bh <= 0:
            rows[t] = {}; continue
        rows[t] = (wl / bl - wh / bh).to_dict()
    return pd.DataFrame(rows).T


def F13(R, LV, CAR, C, PX=None):
    mp = {}
    for i in ("CRUDE_W", "BRENT_W"):
        d = pd.read_csv(os.path.join(PST, "multiple_prices_csv", f"{i}.csv"), parse_dates=["DATETIME"]).set_index("DATETIME")
        mp[i] = d.groupby(d.index.normalize()).last()["PRICE"]
    S = (mp["CRUDE_W"] - mp["BRENT_W"]).reindex(R.index).ffill()
    sma = S.rolling(20, min_periods=20).mean()
    pos = np.sign(sma - S)                                       # spread above its mean -> short the spread
    W = pd.DataFrame({"CRUDE_W": 0.5 * pos, "BRENT_W": -0.5 * pos}).fillna(0.0)
    return W


def F14(R, LV, CAR, C):
    rows, bench = {}, {}
    U = [i for i in JAN6 if i in R.columns]
    me = month_ends(R.index)
    for k, t in enumerate(me):
        w, b = {}, {}
        for i in U:
            if not np.isfinite(LV[i].loc[t]):
                continue
            b[i] = 1.0
            nxt = t.month % 12 + 1                               # the month this weight will be held in
            if nxt == 1:
                w[i] = 1.0
            else:
                jan_end = [x for x in me if x.year == (t.year if t.month >= 1 else t.year) and x.month == 1 and x <= t]
                dec_end = [x for x in me if x.year == t.year - 1 and x.month == 12]
                if jan_end and dec_end and np.isfinite(LV[i].loc[dec_end[0]]) and LV[i].loc[jan_end[0]] > LV[i].loc[dec_end[0]]:
                    w[i] = 1.0
        nb = len(b)
        rows[t] = {i: v / nb for i, v in w.items()} if nb else {}
        bench[t] = {i: 1.0 / nb for i in b} if nb else {}
    return pd.DataFrame(rows).T, pd.DataFrame(bench).T


def _classes(R):
    fx = [i for i in EQ_FOREIGN if i in R.columns]; cm = [i for i in COMM if i in R.columns]
    K = pd.DataFrame({"US": R["SP500"], "FOREIGN": R[fx].mean(axis=1), "BONDS": R["US10"], "COMM": R[cm].mean(axis=1)})
    return K


def _class_cost(R, C):
    fx = [i for i in EQ_FOREIGN if i in C.columns]; cm = [i for i in COMM if i in C.columns]
    return pd.DataFrame({"US": C["SP500"], "FOREIGN": C[fx].mean(axis=1), "BONDS": C["US10"], "COMM": C[cm].mean(axis=1)})


def F15(R, LV, CAR, C):
    K = _classes(R); L = (1 + K.fillna(0)).cumprod(); rows, bench = {}, {}
    for t in month_ends(K.index):
        j = K.index.get_loc(t)
        if j < 210:
            continue
        held = [c for c in K.columns if L[c].iloc[j] > L[c].iloc[j - 209:j + 1].mean()]
        rows[t] = {c: 1.0 / len(held) for c in held} if held else {}
        bench[t] = {c: 0.25 for c in K.columns}
    return pd.DataFrame(rows).T, pd.DataFrame(bench).T


def F16(R, LV, CAR, C):
    K = _classes(R); L = (1 + K.fillna(0)).cumprod(); rows, bench = {}, {}
    for t in month_ends(K.index):
        j = K.index.get_loc(t)
        if j < 252:
            continue
        m = (L.iloc[j] / L.iloc[j - 252] - 1).sort_values(ascending=False)
        rows[t] = {c: 1.0 / 3 for c in m.index[:3]}
        bench[t] = {c: 0.25 for c in K.columns}
    return pd.DataFrame(rows).T, pd.DataFrame(bench).T


STRATS = [("F1", "Time-series momentum", F1), ("F2", "Commodity momentum", F2), ("F3", "Commodity term structure", F3),
          ("F4", "Commodity skewness", F4), ("F5", "Commodity return asymmetry", F5), ("F6", "Currency momentum", F6),
          ("F7", "FX carry", F7), ("F8", "Dollar carry", F8), ("F9", "Short-term reversal (simplified)", F9),
          ("F10", "Paired switching (vs 50/50)", F10), ("F11", "Country index pairs", F11),
          ("F12", "Country betting-against-beta", F12), ("F13", "WTI-Brent spread", F13),
          ("F14", "January barometer (vs buy-and-hold)", F14), ("F15", "Asset-class trend (vs equal weight)", F15),
          ("F16", "Asset-class momentum (vs equal weight)", F16)]
TIMING = {"F10", "F14", "F15", "F16"}


# ----------------------------------------------------------------------------- statistics
def sharpe(x):
    x = x.dropna()
    return float(x.mean() / x.std() * np.sqrt(12)) if len(x) > 3 and x.std() > 0 else np.nan


def per(m, a, b):
    return m[(m.index.year >= int(a)) & (m.index.year <= int(b))]


def summary(m):
    out = {}
    for k, (a, b) in {"2000-09": ERA1, "2010-19": ERA2, "2020-22": VAL}.items():
        x = per(m, a, b)
        out[k] = dict(months=int(x.notna().sum()), sharpe=sharpe(x), ann_pct=float(x.mean() * 1200) if len(x) else np.nan)
    d = per(m, "2000", "2019").dropna()
    out["dev_t"] = float(d.mean() / d.std() * np.sqrt(len(d))) if len(d) > 3 and d.std() > 0 else np.nan
    return out


def main():
    t0 = time.time()
    R, LV, CAR, C = load()
    print(f"data: {R.shape[1]} instruments, {R.index.min().date()} -> {R.index.max().date()}  ({time.time() - t0:.0f}s)", flush=True)
    res = {}; monthly = {}
    Kc = None
    for sid, name, fn in STRATS:
        t1 = time.time()
        out = fn(R, LV, CAR, C)
        if sid in ("F15", "F16"):
            K = _classes(R); KC = _class_cost(R, C)
            (W, Bw) = out
            net, cost = run_weights(K, KC, W); bnet, _ = run_weights(K, KC, Bw)
        elif sid in TIMING:
            W, Bw = out
            net, cost = run_weights(R, C, W); bnet, _ = run_weights(R, C, Bw)
        else:
            W = out
            net, cost = run_weights(R, C, W); bnet = None
        mret = (1 + net).groupby([net.index.year, net.index.month]).prod() - 1
        mret.index = pd.to_datetime([f"{y}-{m:02d}-28" for y, m in mret.index])
        judged = mret
        if bnet is not None:
            bm = (1 + bnet).groupby([bnet.index.year, bnet.index.month]).prod() - 1
            bm.index = mret.index
            judged = mret - bm
            monthly[sid + "_bench"] = bm
        mret = mret[mret.index >= "2000-01-01"]; judged = judged[judged.index >= "2000-01-01"]
        monthly[sid] = mret; monthly[sid + "_judged"] = judged
        s = summary(judged)
        gate = all(np.isfinite(s[k]["sharpe"]) and s[k]["sharpe"] > 0 for k in ("2000-09", "2010-19", "2020-22"))
        res[sid] = dict(name=name, judged_on="return minus buy-and-hold" if bnet is not None else "return", gate=gate,
                        stats=s, absolute=summary(mret), cost_bp_per_year=float(cost[cost.index >= "2000"].sum() / max(1, len(set(cost.index.year[cost.index.year >= 2000]))) * 1e4))
        print(f"{sid:4s} {name:40s} gate {'PASS' if gate else 'fail'}  " +
              "  ".join(f"{k} SR {v['sharpe']:+.2f}" for k, v in s.items() if isinstance(v, dict)) + f"  ({time.time() - t1:.0f}s)", flush=True)
    # deflated Sharpe over the 16 (monthly, development 2000-2019)
    from confirm import deflated_sharpe
    dev = {sid: per(monthly[sid + "_judged"], "2000", "2019").dropna() for sid, _, _ in STRATS}
    trial = np.array([x.mean() / x.std() for x in dev.values() if len(x) > 3 and x.std() > 0])
    for sid in res:
        x = dev[sid]
        res[sid]["dsr"] = deflated_sharpe(x.values, trial, len(STRATS)) if len(x) > 3 else None
    # final look 2023-01..2024-03, logged once per fingerprint, only for strategies that passed the gate
    logp = os.path.join(OUT, "futures_oos_log.json"); log = json.load(open(logp)) if os.path.exists(logp) else []
    for sid in res:
        if not res[sid]["gate"]:
            res[sid]["verdict"] = "Rejected: failed the development/validation gate"; continue
        prior = [e for e in log if e["strategy"] == sid and e["fingerprint"] == FINGERPRINT]
        x = per(monthly[sid + "_judged"], *FINAL).dropna()
        e = prior[0] if prior else dict(strategy=sid, fingerprint=FINGERPRINT, time=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                                         months=int(len(x)), mean_pct=float(x.mean() * 100), sharpe=sharpe(x))
        if not prior:
            log.append(e)
        res[sid]["final_look"] = e
        res[sid]["final_period_seen_in_v1"] = any(x["strategy"] == sid and x["fingerprint"] != FINGERPRINT for x in log)
        res[sid]["verdict"] = "Candidate (futures only)" if e["mean_pct"] > 0 else "Rejected: negative final look"
    json.dump(log, open(logp, "w"), indent=1)
    json.dump(dict(fingerprint=FINGERPRINT, version="v2 (one-day execution lag)", data_end=str(R.index.max().date()), strategies=res), open(os.path.join(OUT, "futures_funnel_v2.json"), "w"), indent=1, default=float)
    pd.DataFrame(monthly).to_csv(os.path.join(OUT, "futures_funnel_v2_monthly.csv"), float_format="%.6f")
    print("\nverdicts:")
    for sid, v in res.items():
        print(f"  {sid:4s} {v['name']:40s} {v['verdict']}" + (f"  final {v['final_look']['mean_pct']:+.2f}%/month SR {v['final_look']['sharpe']:+.2f}" if 'final_look' in v else ""))


if __name__ == "__main__":
    main()
