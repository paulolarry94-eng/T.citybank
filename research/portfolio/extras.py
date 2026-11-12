"""Account size, payout sizing, leg contributions and rule-chosen trade examples for the portfolio report.
Contract assumptions (standard CFD specifications; to be confirmed with mt5/NorthStarExport.mq5 on the real account): FX 100,000
units a lot; XAUUSD 100 oz a lot; NAS100 1 USD per point a lot; minimum 0.01 lot. Conversion prices: USDJPY 145, GBPUSD 1.27.
Minimum account per leg = the smallest account where the target risk on its 75th-percentile stop is at least two 0.01-lot
steps (so rounding to the 0.01-lot grid moves the risk by at most 25%). Cent account (USC): steps 100x smaller.
Examples: the four legs with the largest 2011-22 contribution (weight x total R); for each, the first winning and the first
losing trade of 2019 (by entry time), drawn on the leg's own timeframe.
    python3 research/portfolio/extras.py -> research/results/portfolio/extras.json, examples/*.png
"""
import os, sys, json, datetime as dt
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
import engine as EN   # noqa: E402

OUT = os.path.join(ROOT, "results", "portfolio")
PF = json.load(open(os.path.join(OUT, "portfolio.json")))
Tr = pd.read_csv(os.path.join(OUT, "trades.csv"))
USDJPY, GBPUSD = 145.0, 1.27
UNIT = {  # USD risk per 1.0 price unit for 0.01 lot
    "EURUSD": 1000.0, "GBPUSD": 1000.0, "EURGBP": 1000.0 * GBPUSD, "USDJPY": 1000.0 / USDJPY, "GBPJPY": 1000.0 / USDJPY,
    "XAUUSD": 1.0, "NAS100": 0.01}
TFMIN = {"EUR_EuroHours_short_TueThu": 15, "tokyo_fix_gotobi_v1": 5, "eurusd_close_beyond_reversal_v1": 240, "XAU_S1_reversion_H1M30M20": 30,
         "XAU_EMA20-50_H4": 240, "XAU_Donchian20_H4_turtle": 240, "JPY_S2_Donchian20_H4_long": 240, "GBP_WeeklySweep_FollowThrough": 60,
         "JPY_RSI2_D1_lo5": 240, "GBPJPY_Donchian20_H4_trail": 240, "v2_EURGBP_H1": 60, "v2_GBPUSD_M15": 15, "v2_NAS100_H1": 60}


def account_sizes():
    out = {}
    for cap, rk in PF["risk"].items():
        rows = {}
        for leg, v in PF["legs"].items():
            u = UNIT[v["market"]] * v["p75_dist"]                  # USD risk of 0.01 lot on a 75th-percentile stop
            frac = rk * v["weight"]
            rows[leg] = dict(market=v["market"], usd_per_001_lot_p75=round(u, 2), risk_pct=round(frac * 100, 3),
                             min_account_usd=round(2 * u / frac, -1), min_account_cent_usd=round(2 * u / frac / 100, 0))
        out[cap] = dict(legs=rows, portfolio_min_usd=max(r["min_account_usd"] for r in rows.values()),
                        portfolio_min_cent_usd=max(r["min_account_cent_usd"] for r in rows.values()),
                        binding_leg=max(rows, key=lambda k: rows[k]["min_account_usd"]))
    return out


def payouts():
    out = {}
    for cap in PF["risk"]:
        f = {pn: PF["profiles"][f"{cap} | base"][pn]["mean_fortnight_pct"] for pn in ("2011-2022 (in-sample)", "2023-2025 (seen)", "Jan-Oct 2026 (out-of-sample)")}
        out[cap] = {"mean_fortnight_pct": f, "account_for_usd_per_fortnight": {str(x): {pn: round(x / (v / 100), -2) if v > 0 else None for pn, v in f.items()} for x in (100, 250, 500, 1000)}}
    return out


def chart(leg, row, path):
    sym = row.sym; tf = TFMIN[leg]
    t0, t1 = int(row.t_in), int(row.t_out)
    span = max(t1 - t0, tf * 60 * 10)
    a, b = t0 - max(span, tf * 60 * 40), t1 + max(span // 3, tf * 60 * 10)
    y0 = dt.datetime.utcfromtimestamp(a).year; y1 = dt.datetime.utcfromtimestamp(b).year
    ts, o, h, l, c = EN.load_m1(sym if sym != "GBPJPY" else "GBPJPY", y0, y1) if sym != "GBPJPY" else (None,) * 5
    m = (ts >= a) & (ts <= b)
    bt, bo, bh, bl, bc, _ = EN.resample(ts[m], o[m], h[m], l[m], c[m], tf)
    i_in = int(np.searchsorted(ts, t0)); i_out = int(np.searchsorted(ts, t1))
    entry = row.entry if np.isfinite(row.entry) else c[max(i_in - 1, 0)]
    stop = entry - row.side * row.dist
    exitp = c[min(i_out, len(c) - 1)]
    fig, ax = plt.subplots(figsize=(11, 5), dpi=110)
    fig.patch.set_facecolor("white")
    x = np.arange(len(bt))
    for i in x:
        col = "#2e7d5b" if bc[i] >= bo[i] else "#b23b3b"
        ax.plot([i, i], [bl[i], bh[i]], color=col, lw=0.8)
        ax.add_patch(Rectangle((i - 0.3, min(bo[i], bc[i])), 0.6, max(abs(bc[i] - bo[i]), 1e-9), color=col))
    xi = np.searchsorted(bt, t0, side="right") - 1; xo = np.searchsorted(bt, t1, side="right") - 1
    ax.axhline(entry, color="#1f4e8c", lw=1, ls="--"); ax.axhline(stop, color="#b23b3b", lw=1, ls=":")
    ax.annotate("", xy=(xo, exitp), xytext=(xi, entry), arrowprops=dict(arrowstyle="->", color="#333", lw=1.2))
    ax.plot([xi], [entry], marker="o", color="#1f4e8c"); ax.plot([xo], [exitp], marker="s", color="#333")
    ax.text(0.01, 0.97, f"entry {entry:.5g}   stop {stop:.5g}   exit {exitp:.5g}   result {row.net:+.2f}R after costs and swaps",
            transform=ax.transAxes, va="top", fontsize=9, bbox=dict(fc="white", ec="#ccc"))
    tk = list(range(0, len(bt), max(1, len(bt) // 8)))
    ax.set_xticks(tk); ax.set_xticklabels([dt.datetime.utcfromtimestamp(int(bt[k])).strftime("%d %b %H:%M") for k in tk], fontsize=8)
    ax.set_title(f"{leg} · {sym} · {'BUY' if row.side > 0 else 'SELL'} · {dt.datetime.utcfromtimestamp(t0):%Y-%m-%d %H:%M} UTC", loc="left", fontsize=10)
    ax.grid(alpha=0.2); fig.tight_layout(); fig.savefig(path); plt.close(fig)


def examples():
    contrib = {leg: v["weight"] * v["expectancy_R"] * v["trades_2011_22"] for leg, v in PF["legs"].items()}
    top = sorted(contrib, key=contrib.get, reverse=True)[:4]
    os.makedirs(os.path.join(OUT, "examples"), exist_ok=True)
    rows = []
    for leg in top:
        g = Tr[(Tr.leg == leg) & (Tr.t_in >= int(dt.datetime(2019, 1, 1, tzinfo=dt.timezone.utc).timestamp()))].sort_values("t_in")
        for kind, sel in (("win", g[g.net > 0]), ("loss", g[g.net <= 0])):
            if not len(sel):
                continue
            r = sel.iloc[0]
            fn = f"{leg}_{kind}.png"
            try:
                chart(leg, r, os.path.join(OUT, "examples", fn))
                rows.append(dict(leg=leg, kind=kind, file=fn, t_in=dt.datetime.utcfromtimestamp(int(r.t_in)).strftime("%Y-%m-%d %H:%M"), R=round(float(r.net), 2)))
            except Exception as e:
                rows.append(dict(leg=leg, kind=kind, error=str(e)))
    return dict(contribution_R={k: round(v, 1) for k, v in sorted(contrib.items(), key=lambda kv: -kv[1])}, top4=top, charts=rows)


if __name__ == "__main__":
    res = dict(assumptions=__doc__, account=account_sizes(), payouts=payouts(), examples=examples())
    json.dump(res, open(os.path.join(OUT, "extras.json"), "w"), indent=1, default=float)
    print(json.dumps(res["account"], indent=1)[:2500]); print(json.dumps(res["payouts"], indent=1)); print(res["examples"])
