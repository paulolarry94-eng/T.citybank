"""Data files behind the champion report page (11-leg book: 2011-2025 backtest + Jan-Oct 2026 untouched test).

Reads research/results/champion/{tearsheet,book_2026}.json, research/results/probability/odds.json and the 2026 trade
files, and rebuilds the daily P&L (Exness Zero realistic costs + swaps, 1% risk x frozen leg weight) so the 2026
months continue the backtest curve. Adds two perspective checks (fixed before looking at their result):
  - how often a 10-month stretch as bad as 2026 happens if the live edge is 30% or 50% weaker than the backtest (P11);
  - whether 2026's average trade is statistically different from the backtest's (z-score, one-sided p).
Output: research/results/champion/dashboard/*.csv (references_recalled.csv holds recalled public figures, not data)
"""
import os, sys, json, glob, math
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
for p in (R, os.path.join(R, "northstar"), os.path.join(R, "exness"), HERE):
    sys.path.insert(0, p)
import core
import ns_portfolio as PF
import rescore_book as RB
import tearsheet as TS
from rescore import COST, SWAP

RES = os.path.join(R, "results", "champion"); OUT = os.path.join(RES, "dashboard"); os.makedirs(OUT, exist_ok=True)
NAMES = {
    "EUR_EuroHours_short_TueThu": ("EUR/USD European-hours short, Tue-Thu", "EURUSD"),
    "XAU_S1_reversion_H1M30M20": ("Gold dip reversion (S1)", "XAUUSD"),
    "JPY_VolBreakout_D1_k0.7": ("USD/JPY daily volatility breakout", "USDJPY"),
    "XAU_Donchian20_H4_turtle": ("Gold H4 Donchian 20, turtle exit", "XAUUSD"),
    "JPY_S2_Donchian20_H4_long": ("USD/JPY H4 trend, long only (S2)", "USDJPY"),
    "XAU_EMA20-50_H4": ("Gold H4 EMA 20/50 cross", "XAUUSD"),
    "GBP_WeeklySweep_FollowThrough": ("GBP/USD weekly-level sweep, follow-through", "GBPUSD"),
    "JPY_Donchian55_D1_trail": ("USD/JPY daily Donchian 55", "USDJPY"),
    "JPY_RSI2_D1_lo5": ("USD/JPY daily RSI(2) dip", "USDJPY"),
    "GBPJPY_Donchian20_H4_trail": ("GBP/JPY H4 Donchian 20", "GBPJPY"),
    "EURGBP_Bollinger_D1_k1.5": ("EUR/GBP daily Bollinger reversion", "EURGBP"),
}


def daily_2026(swap):
    _, names = PF.build("BOOK"); W = {n["leg"]: n["weight"] for n in names}; SYM = {n["leg"]: n["sym"] for n in names}
    zc = RB.zero_costs(1.0); rows = []
    for f in sorted(glob.glob(os.path.join(R, "trades", "champion_2026", "*.npy"))):
        leg = os.path.basename(f)[:-4]; x = np.load(f); sym = SYM[leg]
        if not len(x):
            continue
        nights = np.array([core.nights_held(int(a), int(b)) for a, b in zip(x["t_in"], x["t_out"])])
        r = x["r"] + COST[sym] / x["dist"] - zc[sym] / x["dist"] - nights * swap[sym] / x["dist"]
        rows.append(pd.DataFrame(dict(t_out=x["t_out"].astype(np.int64), r=r, w=W[leg])))
    D = pd.concat(rows)
    d = pd.DatetimeIndex(pd.to_datetime(D.t_out.to_numpy(), unit="s")).normalize() + pd.offsets.BDay(0)
    p = pd.Series(0.01 * D.w.to_numpy() * D.r.to_numpy(), index=d).groupby(level=0).sum()
    return p.reindex(pd.date_range("2026-01-01", "2026-10-30", freq="B"), fill_value=0.0), D


def z_one_sided(m_new, n_new, m_ref, sd_ref):
    z = (m_new - m_ref) / (sd_ref / math.sqrt(n_new))
    return round(z, 2), round(0.5 * (1 + math.erf(z / math.sqrt(2))), 3)


def main():
    T = json.load(open(os.path.join(RES, "tearsheet.json"))); B = json.load(open(os.path.join(RES, "book_2026.json")))
    odds = json.load(open(os.path.join(R, "results", "probability", "odds.json")))
    zc = RB.zero_costs(1.0); nos = {k: 0.0 for k in SWAP}
    p_bt, Dbt, _, Wl = TS.series(zc, SWAP); p_sf, Dsf, _, _ = TS.series(zc, nos)
    p26, D26 = daily_2026(SWAP); p26_sf, _ = daily_2026(nos)
    P = pd.concat([p_bt, p26]); Psf = pd.concat([p_sf, p26_sf])
    eq = (1 + P).cumprod(); dd = 1 - eq / eq.cummax()
    roll = (P.rolling(252).mean() / P.rolling(252).std() * np.sqrt(252)).resample("ME").last()
    mon = pd.DataFrame(dict(ret_pct=((1 + P).resample("ME").prod() - 1) * 100, cum_pct=(eq.resample("ME").last() - 1) * 100,
                            dd_pct=dd.resample("ME").max() * 100, roll_sharpe=roll))
    mon.index = mon.index.strftime("%Y-%m"); mon.index.name = "month"
    mon["segment"] = np.where(mon.index >= "2026-01", "2026 untouched", "backtest")
    mon.round(3).reset_index().to_csv(os.path.join(OUT, "monthly.csv"), index=False)

    yr = pd.DataFrame(dict(ret_pct=((1 + P).resample("YE").prod() - 1) * 100, ret_sf_pct=((1 + Psf).resample("YE").prod() - 1) * 100))
    yr.index = [str(i.year) for i in yr.index]; yr.index.name = "year"
    yr["segment"] = np.where(yr.index == "2026", "2026 untouched (Jan-Oct)", "backtest")
    yr.round(2).reset_index().to_csv(os.path.join(OUT, "yearly.csv"), index=False)

    pr = T["profiles"]; zs, sf = pr["Exness Zero + swaps"], pr["Exness Zero swap-free"]
    roles = {"2011-2019": "Learning years: legs and weights fitted", "2020-2022": "Validation years",
             "2023-2025": "Former holdout, seen when the legs were chosen", "2011-2025": "Whole backtest"}
    rec = [dict(period=k, label=k.replace("-", "–"), role=v, ret=zs[k]["cagr"], ret_sf=sf[k]["cagr"], ret_basis="a year",
                sharpe=zs[k]["sharpe"], sharpe_sf=sf[k]["sharpe"], max_dd=zs[k]["max_dd"], months_up=zs[k]["pos_months"],
                years_up=zs[k]["pos_years"]) for k, v in roles.items()]
    b26, b26sf = B["book_2026"]["Exness Zero + swaps"], B["book_2026"]["Exness Zero swap-free"]
    mp = b26["months_positive"].split("/")
    rec.append(dict(period="2026", label="Jan–Oct 2026", role="Untouched: no test or choice has seen it",
                    ret=b26["return_pct_at_1pct"], ret_sf=b26sf["return_pct_at_1pct"], ret_basis="in 10 months",
                    sharpe=b26["sharpe_ann"], sharpe_sf=b26sf["sharpe_ann"], max_dd=b26["max_dd_pct"],
                    months_up=round(100 * int(mp[0]) / int(mp[1]), 1), years_up=""))
    pd.DataFrame(rec).to_csv(os.path.join(OUT, "record.csv"), index=False)

    legs = []
    for k, v in T["legs"].items():
        o = B["legs"][k]
        legs.append(dict(leg=k, name=NAMES[k][0], market=NAMES[k][1], weight=v["weight"], trades_per_year=v["trades_per_year"],
                         mean_R=v["mean_R"], win_pct=round(v["win"] * 100, 1), share_pnl=v["share_of_book_pnl"],
                         trades_2026=o["trades_2026"], R_2026=o["R_sum_exness"],
                         contrib_2026_pct=round(o["weight"] * o["R_sum_exness"], 2)))
    pd.DataFrame(legs).to_csv(os.path.join(OUT, "legs.csv"), index=False)

    tm = T["ten_month_returns"]; v26 = tm["value_2026"] / 100
    r10 = ((1 + p_bt).rolling(210).apply(np.prod, raw=True) - 1).dropna()
    hair = {}
    for h in (0.3, 0.5):
        ph = p_bt - h * p_bt.mean()
        rh = ((1 + ph).rolling(210).apply(np.prod, raw=True) - 1).dropna()
        hair[h] = round(float((rh <= v26).mean()) * 100, 1)
    ten = dict(median=tm["median"], p5=tm["p5"], p10=tm["p10"], value_2026=tm["value_2026"],
               share_at_or_below_2026=tm["share_at_or_below_2026"], share_negative=tm["share_negative"],
               windows=tm["windows"], window_months=10, haircut_lo=30, haircut_hi=50,
               haircut30_share=hair[0.3], haircut50_share=hair[0.5])
    h = T["ten_month_hist"]
    pd.DataFrame([dict(lo=a, hi=b, count=c, has_2026=int(a <= tm["value_2026"] < b))
                  for a, b, c in zip(h["bins"][:-1], h["bins"][1:], h["counts"])]).to_csv(os.path.join(OUT, "ten_month_hist.csv"), index=False)

    st = T["stress_costs1.5_swaps2"]
    m_bt, sd_bt = float(Dbt.r.mean()), float(Dbt.r.std(ddof=1)); m26 = float(D26.r.mean())
    xw_bt = Dbt.r * Dbt.w; xw26 = D26.r * D26.w
    z, pz = z_one_sided(m26, len(D26), m_bt, sd_bt)
    zw, pzw = z_one_sided(float(xw26.mean()), len(D26), float(xw_bt.mean()), float(xw_bt.std(ddof=1)))
    oz = odds["profiles"]["Exness Zero + swaps"] if "profiles" in odds else odds["Exness Zero + swaps"]
    roll_bt = pd.Series(T["rolling_12m_sharpe"])
    facts = dict(legs=len(T["legs"]), markets=len({v[1] for v in NAMES.values()}), trades_total=T["trades_total"],
                 trades_per_year=T["trades_per_year"], avg_corr=T["avg_pairwise_monthly_corr"],
                 trades_2026=int(len(D26)), mean_R_bt=round(m_bt, 3), mean_R_2026=round(m26, 3), z_trade=z, p_trade=pz,
                 z_weighted=zw, p_weighted=pzw, stress_sharpe=st["sharpe"], stress_cagr=st["cagr"], stress_max_dd=st["max_dd"],
                 stress_years_up=st["pos_years"], trades_for_90pct=oz["trades_for_90pct_profit"],
                 fortnights_up_pct=round(oz["book"]["fortnight"] * 100, 1), years_up_pct=round(oz["book"]["year"] * 100, 1),
                 roll12_min=float(roll_bt.min()), roll12_neg_pct=round(float((roll_bt < 0).mean()) * 100, 1),
                 roll12_2026=round(float(mon["roll_sharpe"].iloc[-1]), 2), risk_pct=1)
    facts.update(ten, stress_cost_mult=1.5, stress_swap_mult=2)
    pd.DataFrame([facts]).to_csv(os.path.join(OUT, "summary.csv"), index=False)

    fut = 0.50                                                   # research/multiasset (Carver defaults), 2011-24, see ledger
    live_lo, live_hi = round(zs["2011-2025"]["sharpe"] * 0.5, 2), round(zs["2011-2025"]["sharpe"] * 0.7, 2)
    persp = [dict(id="bt", label="Backtest 2011–25, Exness costs + swaps", group="Champion", lo=zs["2011-2025"]["sharpe"], hi=zs["2011-2025"]["sharpe"]),
             dict(id="sf", label="Backtest 2011–25, swap-free", group="Champion", lo=sf["2011-2025"]["sharpe"], hi=sf["2011-2025"]["sharpe"]),
             dict(id="h23", label="2023–25 only", group="Champion", lo=zs["2023-2025"]["sharpe"], hi=zs["2023-2025"]["sharpe"]),
             dict(id="stress", label="Stress: costs x1.5, swaps x2", group="Champion", lo=st["sharpe"], hi=st["sharpe"]),
             dict(id="live", label="Expected live: 30–50% weaker (P11)", group="Champion", lo=live_lo, hi=live_hi),
             dict(id="y26", label="Jan–Oct 2026, untouched", group="Champion", lo=b26["sharpe_ann"], hi=b26["sharpe_ann"]),
             dict(id="fut", label="Futures trend + carry replica, 2011–24", group="Reference in this project", lo=fut, hi=fut)]
    pd.DataFrame(persp).to_csv(os.path.join(OUT, "perspective.csv"), index=False)
    # Public reference points, RECALLED from general knowledge (not looked up in this study): approximate ranges only.
    pd.DataFrame([dict(id="spx", label="US stocks (S&P 500), about a century", group="Public reference (recalled)", lo=0.3, hi=0.5),
                  dict(id="cta", label="Trend-following funds (SG CTA Index), since 2000", group="Public reference (recalled)", lo=0.2, hi=0.5)]
                 ).to_csv(os.path.join(OUT, "references_recalled.csv"), index=False)
    print(json.dumps(facts, indent=1)); print(hair)


if __name__ == "__main__":
    main()
