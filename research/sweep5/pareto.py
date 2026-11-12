"""Portfolio Pareto for the owner (2026-11-12; pre-registered research/sweep5/PREREGISTRATION.md, last section).
A = max timelessness (highest integrity, then lowest envelope), B = balanced (best two-week Sharpe with integrity >= 90%),
C = max return inside a 3.6% envelope (integrity >= 90%), also shown at 8%, 15%, 25% caps (outside the walls).
Universe: the 13 survivors (Exness Zero costs + swaps, timeless_mix.py loaders) + v2 legs that pass their rule and look
(research/results/sweep5/v2_legs.pkl, if present). Risk for each cap set on 2011-22 only (36-fortnight lifecycles, 95%).
    python3 research/sweep5/pareto.py -> research/results/sweep5/pareto.json + PARETO.md
"""
import os, sys, json, pickle, math, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "goal"))
import timeless_mix as TM   # noqa: E402

OUT = os.path.join(ROOT, "research", "results", "sweep5")
META = {  # magic: market, timeframe, what
    "EUR_EuroHours_short_TueThu": ("EURUSD", "clock 09-13 London", "Tue-Thu short"),
    "XAU_S1_reversion_H1M30M20": ("XAUUSD", "H1/M30/M20", "dip reversion long"),
    "JPY_VolBreakout_D1_k0.7": ("USDJPY", "D1", "volatility breakout"),
    "XAU_Donchian20_H4_turtle": ("XAUUSD", "H4", "20-bar breakout"),
    "JPY_S2_Donchian20_H4_long": ("USDJPY", "H4", "20-bar breakout long"),
    "XAU_EMA20-50_H4": ("XAUUSD", "H4", "EMA 20/50 cross"),
    "GBP_WeeklySweep_FollowThrough": ("GBPUSD", "H1", "weekly sweep follow-through"),
    "JPY_Donchian55_D1_trail": ("USDJPY", "D1", "55-day breakout"),
    "JPY_RSI2_D1_lo5": ("USDJPY", "D1", "RSI(2) dip"),
    "GBPJPY_Donchian20_H4_trail": ("GBPJPY", "H4", "20-bar breakout"),
    "EURGBP_Bollinger_D1_k1.5": ("EURGBP", "D1", "Bollinger reversion"),
    "tokyo_fix_gotobi_v1": ("USDJPY", "M5 clock 23:00-00:55 UTC", "Tokyo fix flow"),
    "eurusd_close_beyond_reversal_v1": ("EURUSD", "D1", "close-beyond reversal"),
}
CAPS = (0.036, 0.08, 0.15, 0.25)
YEARS = {"2011-22": 12.0, "2023-25": 3.0, "Jan-Oct 2026": 10.0 / 12}


def leg_stats(g, lo, hi):
    m = (g["t_out"] >= lo) & (g["t_out"] < hi); R = g["r"][m]
    if not len(R):
        return dict(n=0)
    w, l = R[R > 0], R[R <= 0]
    months = (hi - lo) / (86400 * 30.44)
    return dict(n=int(len(R)), per_month=round(len(R) / months, 2), win=round(float((R > 0).mean()), 3),
                avg_win_R=round(float(w.mean()), 2) if len(w) else None, avg_loss_R=round(float(l.mean()), 2) if len(l) else None,
                expectancy_R=round(float(R.mean()), 3), PF=round(float(w.sum() / -l.sum()), 2) if l.sum() < 0 else None)


def heat(L, risk, lo, hi):
    """Average open risk (% of equity): sum over trades of weight x risk x time open, divided by the period length."""
    tot = sum(float((np.minimum(g["t_out"], hi) - np.maximum(g["t_in"], lo)).clip(0).sum()) * g["w"] for g in L)
    return round(tot / (hi - lo) * risk * 100, 2)


def integrity(L, risk):
    yr = {}
    for y in range(2011, 2026):
        lo, hi = TM.ts_(y), TM.ts_(y + 1)
        yr[y] = sum(float((g["r"] * g["w"])[(g["t_out"] >= lo) & (g["t_out"] < hi)].sum()) for g in L) * risk * 100
    return round(sum(v > 0 for v in yr.values()) / len(yr), 3), {str(k): round(v, 2) for k, v in yr.items()}


def evaluate(name, L, L26):
    B_dev = TM.blocks(L, TM.T0, TM.Y23)
    rng = np.random.default_rng(3)
    dd = np.array([TM.max_dd(np.concatenate([B_dev[i] for i in rng.integers(0, len(B_dev), TM.N_LIFE)])) for _ in range(TM.DRAWS)])
    q95 = float(np.quantile(dd, 0.95))
    risk = {c: c / q95 for c in CAPS}
    per = {"2011-22": TM.blocks(L, TM.T0, TM.Y23), "2023-25": TM.blocks(L, TM.Y23, TM.Y26), "Jan-Oct 2026": TM.blocks(L26, TM.Y26, TM.END26)}
    rec = dict(legs=[g["name"] for g in L], risk_per_trade_pct={f"{c:g}": round(r * 100, 3) for c, r in risk.items()})
    for p, B in per.items():
        s = np.array([b.sum() for b in B])
        d = dict(fortnight_sharpe=round(float(s.mean() / s.std(ddof=1)), 3), positive_fortnights=round(float((s > 0).mean()), 3),
                 trades_per_fortnight=round(float(np.mean([len(b) for b in B])), 1))
        path = np.concatenate(B) if B else np.zeros(0)
        for c, r in risk.items():
            f = s * r * 100
            d[f"cap {c:g}"] = dict(pct_per_fortnight=round(float(f.mean()), 3), pct_a_year=round(float(f.sum()) / YEARS[p], 1),
                                   max_dd_pct=round(TM.max_dd(path * r * 100), 2), worst_fortnight_pct=round(float(f.min()), 2))
        rec[p] = d
    rec["integrity"], rec["yearly_at_3.6"] = integrity(L, risk[0.036])
    rec["heat_avg_pct_at_3.6"] = heat(L, risk[0.036], TM.T0, TM.Y23)
    later = TM.blocks(L, TM.Y23, TM.Y26) + TM.blocks(L26, TM.Y26, TM.END26)
    s = np.array([b.sum() for b in later]); rec["later_sharpe"] = round(float(s.mean() / s.std(ddof=1)), 3)
    rec["envelope_95_pct_at_3.6"] = 3.6
    rec["legs_detail"] = [dict(magic=i + 1, name=g["name"], market=META.get(g["name"], ("?", "?", "?"))[0],
                               timeframe=META.get(g["name"], ("?", "?", "?"))[1], weight=round(float(g["w"]), 2),
                               avg_risk_pct_at_3p6=round(float(g["w"]) * risk[0.036] * 100, 3),
                               **{k: leg_stats(g, *v) for k, v in (("2011-22", (TM.T0, TM.Y23)), ("2023-25", (TM.Y23, TM.Y26)))})
                          for i, g in enumerate(L)]
    return rec


def main():
    L = TM.DQ.legs("zero_swaps")
    L26 = TM.DQ.legs("zero_swaps", y2026=True) + TM.lab_2026("zero_swaps")[0]
    extra = []
    pk = os.path.join(OUT, "v2_legs.pkl")
    if os.path.exists(pk):
        extra = pickle.load(open(pk, "rb"))                  # list of dicts like the survivors' legs (+ 2026 part)
        for g in extra:
            META[g["name"]] = (g["market"], g["tf"], "pivot-sweep v2")
    timeless = [n for n, ok in json.load(open(os.path.join(ROOT, "research", "results", "goal", "timeless_mix.json")))["timeless"].items() if ok]
    sets = {"Timeless 10": timeless, "All 13": [g["name"] for g in L],
            "Book 11": [g["name"] for g in L if g["name"] not in TM.LAB]}
    if extra:
        for k in list(sets):
            sets[k + " + v2"] = sets[k] + [g["name"] for g in extra]
    allL = L + [dict(g, t_in=g["t_in"], t_out=g["t_out"], r=g["r"]) for g in extra]
    allL26 = L26 + [dict(name=g["name"], w=g["w"], t_in=g["t_in26"], t_out=g["t_out26"], r=g["r26"]) for g in extra]
    res = {}
    for name, ns in sets.items():
        res[name] = evaluate(name, [g for g in allL if g["name"] in ns], [g for g in allL26 if g["name"] in ns])
        print(name, res[name]["integrity"], res[name]["2011-22"]["fortnight_sharpe"], res[name]["2011-22"]["cap 0.036"]["pct_a_year"], flush=True)
    A = max(res, key=lambda k: (res[k]["integrity"], -res[k]["2011-22"]["cap 0.036"]["max_dd_pct"]))
    ok = [k for k in res if res[k]["integrity"] >= 0.9]
    B = max(ok, key=lambda k: res[k]["later_sharpe"]) if ok else None
    C = max(ok, key=lambda k: res[k]["2011-22"]["cap 0.036"]["pct_a_year"]) if ok else None
    out = dict(prereg="research/sweep5/PREREGISTRATION.md", mixes=res, A=A, B=B, C=C)
    # what cap would 80% / 120% a year need, at each mix's 2011-22 return per unit of cap (linear in risk)
    for k, v in res.items():
        per_cap = v["2011-22"]["cap 0.036"]["pct_a_year"] / 3.6
        v["cap_needed_for_80pct_a_year"] = round(80 / per_cap, 0) if per_cap > 0 else None
        v["cap_needed_for_120pct_a_year"] = round(120 / per_cap, 0) if per_cap > 0 else None
    json.dump(out, open(os.path.join(OUT, "pareto.json"), "w"), indent=1, default=float)
    return out


if __name__ == "__main__":
    o = main()
    print("A", o["A"], "B", o["B"], "C", o["C"])
