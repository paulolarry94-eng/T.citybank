"""Professional backtest of the recommended portfolio (research/sweep6/PREREGISTRATION.md, Phase 5; no new leg survived the
deep M1 study, so this is the current best mix: Timeless 10 + the three pivot-sweep v2 legs, research/results/sweep5/PARETO.md C).
Every trade carries gross R, cost R and swap R, so three profiles are exact: base (Exness Zero costs for the survivors,
RoboForex Prime for the v2 legs, + swaps), swap-free (no swaps), stress (costs x1.5, swaps x2). Fixed fractional risk on
equity: base risk a trade x leg weight; base risk for a 3.6% envelope (0.432%) and an 8% envelope (0.959%), set on 2011-22.
P&L booked on the exit day; compounded daily.
    python3 research/portfolio/build.py -> research/results/portfolio/portfolio.json, trades.csv
"""
import os, sys, json, pickle, datetime as dt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
for p in ("", "northstar", "exness", "seesare", "truth", "body4", "goal"):
    sys.path.insert(0, os.path.join(ROOT, p))
import gold_traits                     # noqa: E402,F401  (adds Jan-Oct 2026 to the price loader)
import core                            # noqa: E402
import ns_portfolio as PF              # noqa: E402
import rescore_book as RB              # noqa: E402
from rescore import COST, SWAP         # noqa: E402
import protocol as P                   # noqa: E402

OUT = os.path.join(ROOT, "results", "portfolio")
UTC = dt.timezone.utc
T = lambda y, m=1, d=1: int(dt.datetime(y, m, d, tzinfo=UTC).timestamp())
JAN26, END26 = T(2026), T(2026, 11, 1)
PARETO = json.load(open(os.path.join(ROOT, "results", "sweep5", "pareto.json")))["mixes"]["Timeless 10 + v2"]
WEIGHTS = {g["name"]: g["weight"] for g in PARETO["legs_detail"]}
RISK = {"3.6%": PARETO["risk_per_trade_pct"]["0.036"] / 100, "8%": PARETO["risk_per_trade_pct"]["0.08"] / 100}
META = {g["name"]: (g["market"], g["timeframe"]) for g in PARETO["legs_detail"]}
LAB = {"tokyo_fix_gotobi_v1": "USDJPY", "eurusd_close_beyond_reversal_v1": "EURUSD"}


def frame(name, sym, t_in, t_out, side, dist, entry, gross, cost_r, swap_r, src):
    return pd.DataFrame(dict(leg=name, sym=sym, t_in=np.asarray(t_in, np.int64), t_out=np.asarray(t_out, np.int64), side=np.asarray(side, float),
                             dist=np.asarray(dist, float), entry=np.asarray(entry, float), gross=np.asarray(gross, float),
                             cost_r=np.asarray(cost_r, float), swap_r=np.asarray(swap_r, float), source=src))


def book_trades():
    zc = RB.zero_costs(1.0)
    out = []
    for name, sym, x in PF.legs("BOOK"):
        if name not in WEIGHTS:
            continue
        x26 = np.load(os.path.join(ROOT, "trades", "champion_2026", f"{name}.npy"))
        x26 = x26[x26["t_in"] >= JAN26]
        for xx, src in ((x[x["t_in"] < JAN26], "backtest"), (x26, "2026 re-run")):
            nights = np.array([core.nights_held(int(a), int(b)) for a, b in zip(xx["t_in"], xx["t_out"])])
            gross = xx["r"] + COST[sym] / xx["dist"]
            out.append(frame(name, sym, xx["t_in"], xx["t_out"], xx["side"], xx["dist"], xx["entry"], gross, zc[sym] / xx["dist"],
                             nights * SWAP[sym] / xx["dist"], src))
    return out


def lab_trades():
    zc = RB.zero_costs(1.0)
    out = []
    for name, sym in LAB.items():
        Tt = pd.read_csv(os.path.join(ROOT, "results", "truth", name, "parity_trades.csv"))
        t_in = pd.to_datetime(Tt.t_in).to_numpy().astype("datetime64[s]").astype(np.int64)
        t_out = pd.to_datetime(Tt.t_out).to_numpy().astype("datetime64[s]").astype(np.int64)
        gross = Tt.r.to_numpy() + Tt.cost_r.to_numpy() + Tt.fin_r.to_numpy()
        out.append(frame(name, sym, t_in, t_out, Tt.side, Tt.dist, np.nan, gross, zc[sym] / Tt.dist.to_numpy(), Tt.fin_r, "backtest"))
        S = P.load_strategy(os.path.join(ROOT, "truth", "strategies", f"{name}.py"))
        cand = json.load(open(os.path.join(ROOT, "results", "truth", name, "summary.json")))["selection"]["candidate"]
        p = {k: v for k, v in cand.items() if k not in ("tgt", "trail", "bias")}
        X = np.asarray(P.run_config(S, P.market(sym, S), p, cand["tgt"], cand["trail"], cand["bias"], cut=2 ** 62))
        X = X[X[:, 0] >= JAN26]
        out.append(frame(name, sym, X[:, 0], X[:, 1], X[:, 2], X[:, 4], np.nan, X[:, 3] + X[:, 5] + X[:, 7], zc[sym] / X[:, 4], X[:, 7], "2026 re-run"))
    return out


def v2_trades():
    S = P.load_strategy(os.path.join(ROOT, "truth", "strategies", "sweep5_pivot_v2.py"))
    legs = pickle.load(open(os.path.join(ROOT, "results", "sweep5", "v2_legs.pkl"), "rb"))
    out = []
    for g in legs:
        sym, tf, cfg = [x.strip() for x in g["cell"].split("|", 2)]
        p = dict(kv.split("=") for kv in cfg.split("|")); p["life"] = int(p["life"]); p["tf"] = tf
        M = P.market(sym, S)
        D = S.detail(M, M.bars(tf), p)
        out.append(frame(g["name"], sym, D[:, 0], D[:, 1], D[:, 2], D[:, 4], D[:, 10], D[:, 3] + D[:, 5] + D[:, 7], D[:, 5], D[:, 7],
                         np.where(D[:, 0] >= JAN26, "2026 re-run", "backtest")))
    return out


def daily(Tr, risk, profile):
    r = {"base": Tr.net, "swap-free": Tr.net + Tr.swap_r, "stress": Tr.net - 0.5 * Tr.cost_r - Tr.swap_r, "no costs": Tr.gross}[profile]
    pnl = r * Tr.w * risk
    day = pd.to_datetime(Tr.t_out, unit="s", utc=True).dt.floor("D")
    s = pnl.groupby(day).sum()
    idx = pd.date_range("2011-01-03", "2026-10-31", freq="D", tz="UTC")
    return s.reindex(idx, fill_value=0.0)


def perf(d):
    eq = (1 + d).cumprod()
    yrs = (d.index[-1] - d.index[0]).days / 365.25
    dd = 1 - eq / eq.cummax()
    under = (dd > 1e-12).astype(int).to_numpy(); longest = cur = 0
    for u in under:
        cur = cur + 1 if u else 0; longest = max(longest, cur)
    wk = (1 + d).resample("W").prod() - 1
    mo = (1 + d).resample("ME").prod() - 1
    fn = (1 + d).groupby((d.index - pd.Timestamp("2011-01-03", tz="UTC")).days // 14).prod() - 1
    down = wk[wk < 0]
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    return dict(cagr_pct=round(cagr * 100, 2), total_pct=round((eq.iloc[-1] - 1) * 100, 1), vol_pct=round(float(wk.std() * np.sqrt(52)) * 100, 2),
                sharpe=round(float(wk.mean() / wk.std() * np.sqrt(52)), 2), sortino=round(float(wk.mean() / np.sqrt((down ** 2).sum() / len(wk)) * np.sqrt(52)), 2),
                max_dd_pct=round(float(dd.max()) * 100, 2), calmar=round(float(cagr / dd.max()), 2) if dd.max() > 0 else None,
                longest_dd_days=int(longest), pos_months_pct=round(float((mo > 0).mean()) * 100, 1), best_month_pct=round(float(mo.max()) * 100, 2),
                worst_month_pct=round(float(mo.min()) * 100, 2), pos_fortnights_pct=round(float((fn > 0).mean()) * 100, 1),
                mean_fortnight_pct=round(float(fn.mean()) * 100, 3), worst_fortnight_pct=round(float(fn.min()) * 100, 2),
                var95_day_pct=round(float(np.quantile(d[d != 0], 0.05)) * 100, 3) if (d != 0).any() else 0.0,
                cvar95_day_pct=round(float(d[d != 0][d[d != 0] <= np.quantile(d[d != 0], 0.05)].mean()) * 100, 3) if (d != 0).any() else 0.0,
                skew_weekly=round(float(wk.skew()), 2), kurt_weekly=round(float(wk.kurt()), 2))


def main():
    Tr = pd.concat(book_trades() + lab_trades() + v2_trades(), ignore_index=True)
    Tr = Tr[Tr.t_in < END26].copy()
    Tr["w"] = Tr.leg.map(WEIGHTS)
    Tr["net"] = Tr.gross - Tr.cost_r - Tr.swap_r
    assert Tr.w.notna().all(), Tr[Tr.w.isna()].leg.unique()
    os.makedirs(OUT, exist_ok=True)
    Tr.to_csv(os.path.join(OUT, "trades.csv"), index=False)
    periods = {"2011-2022 (in-sample)": ("2011-01-03", "2022-12-31"), "2023-2025 (seen)": ("2023-01-01", "2025-12-31"),
               "Jan-Oct 2026 (out-of-sample)": ("2026-01-01", "2026-10-31"), "2011-Oct 2026 (all)": ("2011-01-03", "2026-10-31")}
    res = dict(prereg="research/sweep6/PREREGISTRATION.md (Phase 5)", legs={}, profiles={}, yearly={}, monthly={}, equity_weekly={}, risk=RISK)
    for cap, rk in RISK.items():
        for prof in ("base", "swap-free", "stress", "no costs"):
            d = daily(Tr, rk, prof)
            res["profiles"][f"{cap} | {prof}"] = {pn: perf(d[a:b]) for pn, (a, b) in periods.items()}
            if prof == "base":
                res["yearly"][cap] = {str(k.year): round(float(v) * 100, 2) for k, v in ((1 + d).resample("YE").prod() - 1).items()}
                res["monthly"][cap] = {k.strftime("%Y-%m"): round(float(v) * 100, 2) for k, v in ((1 + d).resample("ME").prod() - 1).items()}
                eq = (1 + d).cumprod(); dd = 1 - eq / eq.cummax()
                res["equity_weekly"][cap] = {k.strftime("%Y-%m-%d"): [round(float(e), 5), round(float(x) * 100, 3)] for k, e, x in zip(eq.resample("W").last().index, eq.resample("W").last(), dd.resample("W").max())}
    for leg, g in Tr.groupby("leg"):
        bt = g[g.t_in < T(2023)]
        r = bt.net.to_numpy(); w_, l_ = r[r > 0], r[r <= 0]
        hold = (bt.t_out - bt.t_in).to_numpy() / 3600
        later = g[g.t_in >= T(2023)].net.to_numpy()
        res["legs"][leg] = dict(market=META[leg][0], timeframe=META[leg][1], weight=WEIGHTS[leg], trades_2011_22=int(len(r)),
                                per_month=round(len(r) / 144, 2), win=round(float((r > 0).mean()), 3), avg_win_R=round(float(w_.mean()), 2),
                                avg_loss_R=round(float(l_.mean()), 2), expectancy_R=round(float(r.mean()), 3), PF=round(float(w_.sum() / -l_.sum()), 2),
                                gross_R=round(float(bt.gross.mean()), 3), cost_R=round(float(bt.cost_r.mean()), 3), swap_R=round(float(bt.swap_r.mean()), 3),
                                median_hold_h=round(float(np.median(hold)), 1), later_expectancy_R=round(float(later.mean()), 3) if len(later) else None,
                                later_trades=int(len(later)), median_dist=float(np.median(bt.dist)), p75_dist=float(np.quantile(bt.dist, 0.75)))
    # correlation of monthly leg returns (weighted R), 2011-2025
    mo = Tr[Tr.t_out < T(2026)].assign(m=pd.to_datetime(Tr.t_out, unit="s").dt.to_period("M"), x=lambda z: z.net * z.w).pivot_table(index="m", columns="leg", values="x", aggfunc="sum").fillna(0)
    C = mo.corr()
    res["correlation"] = {a: {b: round(float(C.loc[a, b]), 3) for b in C.columns} for a in C.index}
    iu = np.triu_indices(len(C), 1)
    res["avg_pairwise_corr"] = round(float(C.to_numpy()[iu].mean()), 3)
    # Monte Carlo: fortnights of 2011-22 (3.6% risk), 10,000 one-year (26) and lifecycle (36) paths
    d = daily(Tr, RISK["3.6%"], "base")["2011-01-03":"2022-12-31"]
    fn = ((1 + d).groupby((d.index - pd.Timestamp("2011-01-03", tz="UTC")).days // 14).prod() - 1).to_numpy()
    rng = np.random.default_rng(11)
    out = {}
    for nm, k in (("one year (26 fortnights)", 26), ("lifecycle (36 fortnights)", 36)):
        X = fn[rng.integers(0, len(fn), (10000, k))]
        eq = np.cumprod(1 + X, axis=1); peak = np.maximum.accumulate(np.concatenate([np.ones((10000, 1)), eq], axis=1), axis=1)[:, 1:]
        mdd = np.max(1 - eq / peak, axis=1); ret = eq[:, -1] - 1
        out[nm] = dict(return_pct={q: round(float(np.quantile(ret, q)) * 100, 2) for q in (0.05, 0.25, 0.5, 0.75, 0.95)},
                       max_dd_pct={q: round(float(np.quantile(mdd, q)) * 100, 2) for q in (0.5, 0.95, 0.99)},
                       p_loss=round(float((ret < 0).mean()), 4), p_dd_over_3_6=round(float((mdd > 0.036).mean()), 4), p_dd_over_8=round(float((mdd > 0.08).mean()), 4))
    res["monte_carlo_3.6"] = out
    res["trades_total"] = int(len(Tr)); res["trades_by_source"] = Tr.source.value_counts().to_dict()
    json.dump(res, open(os.path.join(OUT, "portfolio.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    for k, v in r["profiles"].items():
        print(k); [print("   ", pn, x) for pn, x in v.items()]
    print("yearly 3.6", r["yearly"]["3.6%"]); print("avg corr", r["avg_pairwise_corr"]); print(json.dumps(r["monte_carlo_3.6"], indent=1))
