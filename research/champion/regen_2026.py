"""The champion (11-leg book) on 2026 prices that no selection, test or calibration has ever seen.

The book's legs were chosen in October 2026 on data through 2025 (Hunt 2; its "out-of-sample" was 2019-2025), so no
2011-2025 number is a clean test of the book. January-October 2026 is. Method (fixed before running):
  1. extend the shared price loader (engine.load_m1) with 2026 minute bars built from Exness Zero ticks (data/holdout/);
  2. regenerate every leg with its ORIGINAL code and settings (no change);
  3. parity: the regenerated trades entered before 2025-11-01 must match the stored trade files (entry times);
  4. score the 2026 trades with the frozen leg weights, at research costs and at Exness Zero realistic costs
     (with swaps, and swap-free shown separately).
Output: research/results/champion/book_2026.json and the 2026 trade lists in research/trades/champion_2026/.
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
for p in (R, os.path.join(R, "northstar"), os.path.join(R, "hunt"), os.path.join(R, "exness")):
    sys.path.insert(0, p)
os.chdir(R)
import engine as E
_ORIG = E.load_m1
HOLD = os.path.join(R, "..", "data", "holdout")


def load_m1_2026(sym, y0=2011, y1=2025):
    ts, o, h, l, c = _ORIG(sym, y0, min(y1, 2025))
    f = os.path.join(HOLD, f"{sym}_M1_bid_2026.npz")
    if not os.path.exists(f):
        return ts, o, h, l, c
    d = np.load(f)
    t2 = (d["ts"] // 1000).astype(np.int64)
    ts = np.r_[ts, t2]; o = np.r_[o, d["o"]]; h = np.r_[h, d["h"]]; l = np.r_[l, d["l"]]; c = np.r_[c, d["c"]]
    order = np.argsort(ts, kind="stable"); ts, o, h, l, c = ts[order], o[order], h[order], l[order], c[order]
    keep = np.ones(len(ts), bool); keep[1:] = ts[1:] != ts[:-1]
    flat = (o == h) & (h == l) & (l == c); flat[1:] &= o[1:] == c[:-1]; flat[0] = False
    keep &= ~flat
    return ts[keep], o[keep], h[keep], l[keep], c[keep]


E.load_m1 = load_m1_2026
import gold_lab as GL
import liquidity as LQ
import euro_hours as EH
import crosses as CR
import regen_filtered as RF
import core
import ns_portfolio as PF
import rescore_book as RB
from rescore import COST, SWAP

JAN26 = 1767225600; NOV25 = 1761955200


def legs():
    xau = GL.Market("XAUUSD"); jpy = GL.Market("USDJPY")
    out = {}
    out["EUR_EuroHours_short_TueThu"] = EH.build(k=0.5, days=(1, 2, 3))
    out["XAU_S1_reversion_H1M30M20"] = E.run_s1("XAUUSD", E.load_m1("XAUUSD"), tfs=(60, 30, 20), sides=(1,), offset_min=120)
    D_jpy = jpy.tf("D1", offset=0)
    b = GL.vol_breakout(jpy, "D1", 0.7)
    k, H, L = RF.prev_day(D_jpy, b["t_in"]); out["JPY_VolBreakout_D1_k0.7"] = b[(k >= 0) & np.where(b["side"] > 0, b["entry"] > H, b["entry"] < L)]
    out["XAU_Donchian20_H4_turtle"] = GL.donchian(xau, "H4", 20, 2.0, 0, turtle_exit=True)
    b = E.run_trend("USDJPY", E.load_m1("USDJPY"), tf=240, atr_mult=2.0, sides=(1,), offset_min=120)
    k, H = RF.prev_week_high(D_jpy, b["t_in"]); out["JPY_S2_Donchian20_H4_long"] = b[(k >= 0) & (b["entry"] > H)]
    D_xau = xau.tf("D1", offset=0)
    b = GL.ma_cross(xau, "H4", 20, 50)
    k, H, L = RF.prev_day(D_xau, b["t_in"]); out["XAU_EMA20-50_H4"] = b[(k >= 0) & (b["entry"] >= L) & (b["entry"] <= H)]
    out["GBP_WeeklySweep_FollowThrough"] = LQ.Lab("GBPUSD").build(level="weekly", tfm=60, K=6, kind="follow", target="2")
    out["JPY_Donchian55_D1_trail"] = GL.donchian(jpy, "D1", 55, 2.0, 1.5)
    out["JPY_RSI2_D1_lo5"] = GL.rsi2(jpy, "D1", 5, 95)
    out["GBPJPY_Donchian20_H4_trail"] = GL.donchian(CR.Cross("GBPJPY"), "H4", 20, 2.0, 1.5)
    out["EURGBP_Bollinger_D1_k1.5"] = GL.bollinger(CR.Cross("EURGBP"), "D1", 20, 1.5)
    return out


def main():
    book = json.load(open(os.path.join(R, "results", "book_v3.json")))
    _, names = PF.build("BOOK"); W = {n["leg"]: n["weight"] for n in names}; SYM = {n["leg"]: n["sym"] for n in names}
    T = legs()
    os.makedirs(os.path.join(R, "trades", "champion_2026"), exist_ok=True)
    parity = {}; res = {"parity": parity, "legs": {}}
    zc = RB.zero_costs(1.0)
    rows = {"research costs + swaps": [], "Exness Zero + swaps": [], "Exness Zero swap-free": []}
    for leg, tr in T.items():
        st = np.load(os.path.join(R, book["files"][leg]))
        a = set(int(x) for x in tr["t_in"][tr["t_in"] < NOV25]); s = set(int(x) for x in st["t_in"][st["t_in"] < NOV25])
        parity[leg] = dict(regenerated=len(a), stored=len(s), common=len(a & s), match=round(len(a & s) / max(1, len(s)), 3))
        x = tr[tr["t_in"] >= JAN26]
        np.save(os.path.join(R, "trades", "champion_2026", f"{leg}.npy"), x)
        sym = SYM[leg]
        nights = np.array([core.nights_held(int(p), int(q)) for p, q in zip(x["t_in"], x["t_out"])]) if len(x) else np.zeros(0)
        r_res = x["r"] - nights * SWAP[sym] / x["dist"] if len(x) else np.zeros(0)
        r_zero = x["r"] + COST[sym] / x["dist"] - zc[sym] / x["dist"] - nights * SWAP[sym] / x["dist"] if len(x) else np.zeros(0)
        r_sf = x["r"] + COST[sym] / x["dist"] - zc[sym] / x["dist"] if len(x) else np.zeros(0)
        res["legs"][leg] = dict(weight=round(W[leg], 3), trades_2026=int(len(x)),
                                R_sum_exness=round(float(r_zero.sum()), 2), R_mean_exness=round(float(r_zero.mean()), 3) if len(x) else None)
        for lab, r in (("research costs + swaps", r_res), ("Exness Zero + swaps", r_zero), ("Exness Zero swap-free", r_sf)):
            rows[lab] += [(int(t), float(rr), W[leg]) for t, rr in zip(x["t_out"], r)]
        print(f"{leg:32s} parity {parity[leg]['common']}/{parity[leg]['stored']}  2026 trades {len(x)}  R(Exness) {res['legs'][leg]['R_sum_exness']}", flush=True)
    import pandas as pd
    out = {}
    for lab, rr in rows.items():
        D = pd.DataFrame(rr, columns=["t_out", "r", "w"])
        D = D[D.t_out >= JAN26]
        d = pd.DatetimeIndex(pd.to_datetime(D.t_out.to_numpy(), unit="s")).normalize()
        p = pd.Series(0.01 * D.w.to_numpy() * D.r.to_numpy(), index=d).groupby(level=0).sum()
        idx = pd.date_range("2026-01-01", "2026-10-30", freq="B"); p = p.reindex(idx, fill_value=0.0)
        eq = (1 + p).cumprod(); dd = float((1 - eq / eq.cummax()).max())
        mon = p.resample("ME").sum()
        out[lab] = dict(trades=int(len(D)), mean_R=round(float(D.r.mean()), 3), win=round(float((D.r > 0).mean()), 3),
                        return_pct_at_1pct=round(float(eq.iloc[-1] - 1) * 100, 2), max_dd_pct=round(dd * 100, 2),
                        sharpe_ann=round(float(p.mean() / p.std() * np.sqrt(252)), 2) if p.std() > 0 else None,
                        months_positive=f"{int((mon > 0).sum())}/{len(mon)}",
                        monthly_pct={k.strftime("%Y-%m"): round(float(v) * 100, 2) for k, v in mon.items()})
        print(lab, {k: v for k, v in out[lab].items() if k != "monthly_pct"}, flush=True)
    res["book_2026"] = out
    os.makedirs(os.path.join(R, "results", "champion"), exist_ok=True)
    json.dump(res, open(os.path.join(R, "results", "champion", "book_2026.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
