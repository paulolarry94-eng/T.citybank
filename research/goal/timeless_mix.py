"""The most timeless mix of the survivors (pre-registered: research/goal/PREREGISTRATION_TIMELESS.md, committed first).
A leg is timeless if its R per trade after Exness Zero costs + swaps is above 0 in each of 2011-14, 2015-18 and 2019-22
(10+ trades each). Mixes (leg weights as fixed before): timeless, all 13 survivors, the 11-leg book. Two-week cycles from
Monday 2011-01-03 (exit time); risk per trade for 3.6% / 8% lifecycle caps (36 fortnights, 95% of bootstrapped
lifecycles) set on 2011-22 only, then applied to 2023-25 and Jan-Oct 2026. The Tokyo fix and the EURUSD reversal are run
on 2026 data here with their lab settings unchanged (their 2011-25 trades must match the lab's parity trades).
    python3 research/goal/timeless_mix.py  ->  research/results/goal/timeless_mix.json + TIMELESS_MIX.md
"""
import os, sys, json, math, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "research", "seesare"), os.path.join(ROOT, "research", "truth")):
    sys.path.insert(0, p)
import daily_queue_study as DQ        # noqa: E402
import universe_cap_study as U        # noqa: E402

OUT = os.path.join(ROOT, "research", "results", "goal")
UTC = dt.timezone.utc
ts_ = lambda y, m=1, d=1: int(dt.datetime(y, m, d, tzinfo=UTC).timestamp())
T0, F = ts_(2011, 1, 3), 14 * 86400
Y23, Y26, END26 = ts_(2023), ts_(2026), ts_(2026, 11, 1)
ERAS = (("2011-14", ts_(2011), ts_(2015)), ("2015-18", ts_(2015), ts_(2019)), ("2019-22", ts_(2019), ts_(2023)))
N_LIFE, DRAWS, CAPS, MIN_ERA = 36, 5000, (0.036, 0.08), 10
LAB = {"tokyo_fix_gotobi_v1": "USDJPY", "eurusd_close_beyond_reversal_v1": "EURUSD"}


def lab_2026(profile):
    """2026 trades of the two lab survivors, lab settings unchanged; the 2011-25 part is checked against parity_trades.csv."""
    import pandas as pd
    sys.path.insert(0, os.path.join(ROOT, "research", "body4"))
    import gold_traits                                     # noqa: F401  (adds Jan-Oct 2026 to the price loader)
    import protocol as P
    out, checks = [], {}
    for name, sym in LAB.items():
        S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", f"{name}.py"))
        cand = json.load(open(os.path.join(ROOT, "research", "results", "truth", name, "summary.json")))["selection"]["candidate"]
        p = {k: v for k, v in cand.items() if k not in ("tgt", "trail", "bias")}
        M = P.market(sym, S)
        X = np.asarray(P.run_config(S, M, p, cand["tgt"], cand["trail"], cand["bias"], cut=2 ** 62))
        par = pd.read_csv(os.path.join(ROOT, "research", "results", "truth", name, "parity_trades.csv"))
        old = X[X[:, 0] < Y26]
        checks[name] = dict(lab_trades_2011_25=len(par), rerun_trades_2011_25=int(len(old)),
                            sum_r_lab=round(float(par.r.sum()), 3), sum_r_rerun=round(float(old[:, 3].sum()), 3))
        x = X[X[:, 0] >= Y26]
        zc = U.RB.zero_costs(1.0)[sym]
        r = x[:, 3] + x[:, 5] - zc / x[:, 4]                   # as universe_cap_study.lab_leg: lab cost -> Exness Zero cost
        if profile == "zero_swapfree":
            r = r + x[:, 7]
        w = next(g["w"] for g in DQ.legs(profile) if g["name"] == name)
        out.append(dict(name=name, w=w, t_in=x[:, 0].astype(np.int64), t_out=x[:, 1].astype(np.int64), r=r))
    return out, checks


def blocks(legs, lo, hi):
    """Weighted R of every trade, grouped by the fortnight it closes (empty fortnights kept)."""
    k0, k1 = (lo - T0) // F, (hi - T0 + F - 1) // F
    B = [[] for _ in range(int(k1 - k0))]
    rows = sorted((int(o), float(r) * g["w"]) for g in legs for o, r in zip(g["t_out"], g["r"]) if lo <= o < hi)
    for o, r in rows:
        k = int((o - T0) // F - k0)
        if 0 <= k < len(B):
            B[k].append(r)
    return [np.array(b) for b in B]


def max_dd(path):
    eq = np.r_[0.0, np.cumsum(path)]
    return float(np.max(np.maximum.accumulate(eq) - eq))


def risk_for_caps(B, seed=3):
    rng = np.random.default_rng(seed)
    dd = np.array([max_dd(np.concatenate([B[i] for i in rng.integers(0, len(B), N_LIFE)])) for _ in range(DRAWS)])
    q95 = float(np.quantile(dd, 0.95))
    return {cap: cap / q95 for cap in CAPS}


def period_stats(B, risk, years):
    s = np.array([b.sum() for b in B]); n = np.array([len(b) for b in B])
    d = dict(fortnights=len(B), trades_per_fortnight=round(float(n.mean()), 2), mean_R=round(float(s.mean()), 3),
             sharpe=round(float(s.mean() / s.std(ddof=1)), 3) if s.std(ddof=1) > 0 else None, positive=round(float((s > 0).mean()), 3),
             pct_a_year_at_1pct=round(float(s.sum()) / years, 1))
    path = np.concatenate(B) if B else np.zeros(0)
    for cap, r in risk.items():
        f = s * r * 100
        d[f"cap_{cap:g}"] = dict(risk_per_trade_pct=round(r * 100, 3), pct_per_fortnight=round(float(f.mean()), 3),
                                 pct_a_year=round(float(f.sum()) / years, 1), worst_fortnight_pct=round(float(f.min()), 2),
                                 max_drawdown_pct=round(max_dd(path * r * 100), 2))
    return d


def main():
    res = dict(prereg="research/goal/PREREGISTRATION_TIMELESS.md", eras={}, timeless={}, sets={}, yearly={})
    legs = {pr: DQ.legs(pr) for pr in ("zero_swaps", "zero_swapfree")}
    legs26 = {pr: DQ.legs(pr, y2026=True) for pr in ("zero_swaps", "zero_swapfree")}
    for pr in legs26:
        extra, checks = lab_2026(pr)
        legs26[pr] = legs26[pr] + extra
        res["lab_rerun_checks"] = checks
    # 1. the timeless rule (2011-22 only)
    for g in legs["zero_swaps"]:
        e = {}
        for name, lo, hi in ERAS:
            m = (g["t_in"] >= lo) & (g["t_in"] < hi)
            e[name] = dict(n=int(m.sum()), E=round(float(g["r"][m].mean()), 4) if m.sum() else None)
        res["eras"][g["name"]] = e
        res["timeless"][g["name"]] = all(v["n"] >= MIN_ERA and (v["E"] or -1) > 0 for v in e.values())
    names = {"Timeless mix": [n for n, ok in res["timeless"].items() if ok],
             "All 13 survivors": [g["name"] for g in legs["zero_swaps"]],
             "11-leg book": [g["name"] for g in legs["zero_swaps"] if g["name"] not in LAB]}
    years = {"2011-22": 12.0, "2023-25": 3.0, "Jan-Oct 2026": 10.0 / 12}
    for pr in ("zero_swaps", "zero_swapfree"):
        for setname, ns in names.items():
            L = [g for g in legs[pr] if g["name"] in ns]; L26 = [g for g in legs26[pr] if g["name"] in ns]
            B_dev = blocks(L, T0, Y23)
            risk = risk_for_caps(B_dev)
            rec = {"2011-22": period_stats(B_dev, risk, years["2011-22"]),
                   "2023-25": period_stats(blocks(L, Y23, Y26), risk, years["2023-25"]),
                   "Jan-Oct 2026": period_stats(blocks(L26, Y26, END26), risk, years["Jan-Oct 2026"])}
            later = blocks(L, Y23, Y26) + blocks(L26, Y26, END26)
            s = np.array([b.sum() for b in later])
            rec["2023-Oct 2026 fortnight Sharpe"] = round(float(s.mean() / s.std(ddof=1)), 3)
            rec["legs"] = ns
            res["sets"][f"{setname} | {'swaps' if pr == 'zero_swaps' else 'swap-free'}"] = rec
            if pr == "zero_swaps":
                yr = {}
                for y in range(2011, 2027):
                    lo, hi = ts_(y), (ts_(y + 1) if y < 2026 else END26)
                    LL = L26 if y == 2026 else L
                    v = sum(float((g["r"] * g["w"])[(g["t_out"] >= lo) & (g["t_out"] < hi)].sum()) for g in LL)
                    yr[str(y)] = round(v * risk[0.036] * 100, 2)
                res["yearly"][setname] = yr
    a = res["sets"]["Timeless mix | swaps"]["2023-Oct 2026 fortnight Sharpe"]; b = res["sets"]["All 13 survivors | swaps"]["2023-Oct 2026 fortnight Sharpe"]
    res["recommendation"] = "Timeless mix" if a >= b else "All 13 survivors"
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "timeless_mix.json"), "w"), indent=1, default=float)
    return res


def tables(r):
    """TIMELESS_MIX.md from timeless_mix.json (python3 research/goal/timeless_mix.py --tables rewrites it without re-running)."""
    L = ["# The most timeless mix of the survivors (built by research/goal/timeless_mix.py)", "",
         f"Pre-registered: {r['prereg']}. Exness Zero costs + swaps unless marked; every leg keeps its weight. Risk per trade for "
         "the 3.6% and 8% caps is set on 2011-22 and applied unchanged later. Recommendation by the pre-registered rule: "
         f"**{r['recommendation']}**.", "",
         "Lab legs re-run with unchanged settings (2011-25 must equal the lab's parity trades): " +
         "; ".join(f"{k}: {v['rerun_trades_2011_25']} of {v['lab_trades_2011_25']} trades, sum {v['sum_r_rerun']} vs {v['sum_r_lab']}"
                   for k, v in r["lab_rerun_checks"].items()), "",
         "## Which legs are timeless (R per trade after costs and swaps, trades)", "",
         "| Leg | 2011-14 | 2015-18 | 2019-22 | Timeless |", "|---|---|---|---|---|"]
    for n, e in r["eras"].items():
        L.append(f"| {n} | " + " | ".join(f"{v['E']:+.3f} ({v['n']})" for v in e.values()) + f" | {'yes' if r['timeless'][n] else 'no'} |")
    L += ["", "## The mixes, two-week cycles", "",
          "| Mix | Period | Trades / 2 weeks | Fortnights positive | Fortnight Sharpe | % a year at 1% risk | 3.6% cap: % a year (max drawdown) | 8% cap: % a year (max drawdown) |",
          "|---|---|---|---|---|---|---|---|"]
    for k, v in r["sets"].items():
        for per in ("2011-22", "2023-25", "Jan-Oct 2026"):
            d = v[per]
            L.append(f"| {k} | {per} | {d['trades_per_fortnight']} | {d['positive']:.0%} | {d['sharpe']} | {d['pct_a_year_at_1pct']} | "
                     f"{d['cap_0.036']['pct_a_year']} ({d['cap_0.036']['max_drawdown_pct']}) | {d['cap_0.08']['pct_a_year']} ({d['cap_0.08']['max_drawdown_pct']}) |")
    L += ["", "Fortnight Sharpe over 2023 - October 2026: " + "; ".join(f"{k} {v['2023-Oct 2026 fortnight Sharpe']}" for k, v in r["sets"].items()), "",
          "## Calendar years at the 3.6% cap (%; 2026 = January-October)", "", "| Mix | " + " | ".join(r["yearly"]["Timeless mix"]) + " |",
          "|---|" + "---|" * len(r["yearly"]["Timeless mix"])]
    for k, v in r["yearly"].items():
        L.append(f"| {k} | " + " | ".join(f"{x:+.1f}" for x in v.values()) + " |")
    open(os.path.join(OUT, "TIMELESS_MIX.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__" and "--tables" in sys.argv:
    tables(json.load(open(os.path.join(OUT, "timeless_mix.json"))))
elif __name__ == "__main__":
    r = main()
    tables(r)
    print(json.dumps(dict(checks=r["lab_rerun_checks"], timeless=r["timeless"], recommendation=r["recommendation"]), indent=1))
    for k, v in r["sets"].items():
        print(k, {p: (v[p]["sharpe"], v[p]["mean_R"], v[p]["cap_0.036"]["pct_a_year"], v[p]["cap_0.08"]["pct_a_year"]) for p in ("2011-22", "2023-25", "Jan-Oct 2026")},
              "later Sharpe", v["2023-Oct 2026 fortnight Sharpe"])
