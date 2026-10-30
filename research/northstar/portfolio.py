"""NS4: sizing policies compared on identical trades, risk chosen on 2011-2022, 2023-2025 reported.

Portfolios: BOOK (11 frozen legs) and BOOK+FOUR (the 23-leg reference), all R after costs AND financing.

    python3 portfolio.py -> results/northstar/portfolio.json, weekly_bands.json
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import risk
from rescore import ROOT, PFX, finance
from grid import year_index

RES = os.path.join(ROOT, "results", "northstar")
INST = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "GBPJPY", "EURGBP"]
CUT23 = 1672531200
DEMO = ("FF+RED", 0.01)                     # amendment 3
RISKS = [0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015, 0.0175, 0.02]


def legs(which):
    out = []
    book = json.load(open(os.path.join(ROOT, "results", "book_v3.json")))
    for leg in book["kept"]:
        out.append((leg, PFX[leg.split("_")[0]], np.load(os.path.join(ROOT, book["files"][leg]))))
    if which == "BOOK+FOUR":
        for st in ("TC", "FB", "VC", "VE"):
            for s in INST[:4]:
                out.append((f"{st}_{s}", s, np.load(os.path.join(ROOT, "trades", "four", f"{st}_{s}.npy"))))
    return out


def monthly_vol(x, r):
    m = x["t_in"].astype("datetime64[s]").astype("datetime64[M]").astype(np.int64)      # calendar month
    keep = year_index(x["t_in"]) <= 2019
    if keep.sum() < 10:
        return np.nan
    s = {}
    for k, v in zip(m[keep], r[keep]):
        s[k] = s.get(k, 0.0) + v
    return float(np.std(list(s.values()))) if len(s) > 5 else np.nan


def build(which):
    rows = []; names = []
    for i, (name, sym, x) in enumerate(legs(which)):
        r = x["r"] - finance(x, sym)
        names.append(dict(leg=name, sym=sym, vol=monthly_vol(x, r)))
        rows.append(dict(t_in=x["t_in"].astype(np.int64), t_out=x["t_out"].astype(np.int64), side=x["side"].astype(np.int64), r=r,
                         leg=np.full(len(x), i, np.int64), inst=np.full(len(x), INST.index(sym), np.int64),
                         usd=np.full(len(x), risk.USD_SHORT[sym], np.int64)))
    iv = np.array([1 / n["vol"] if np.isfinite(n["vol"]) and n["vol"] > 0 else np.nan for n in names])
    w = iv / np.nanmax(iv); w = np.where(np.isfinite(w), w, np.nanmedian(w))
    for n, ww in zip(names, w):
        n["weight"] = float(ww)
    T = {k: np.concatenate([r[k] for r in rows]) for k in rows[0]}
    T["w"] = w[T["leg"]].astype(np.float64)
    o = np.argsort(T["t_in"], kind="stable")
    return {k: v[o] for k, v in T.items()}, names


def window(T, a, b):
    m = (T["t_in"] >= a) & (T["t_in"] < b)
    return {k: v[m] for k, v in T.items()}


def fortnights(eq, et):
    """Fortnightly returns from the equity path (last value in each 14-day bucket)."""
    b = (et - et[0]) // (14 * 86400)
    last = {}
    for k, v in zip(b, eq):
        last[k] = v
    vals = np.array([last[k] for k in sorted(last)])
    return vals[1:] / vals[:-1] - 1 if len(vals) > 1 else np.zeros(0)


def main():
    out = {}
    for which in ("BOOK", "BOOK+FOUR"):
        T, names = build(which)
        IS = window(T, 0, CUT23); OOS = window(T, CUT23, 2 ** 62)
        res = dict(legs=names, frontier=[])
        for pol in risk.POLICIES:
            for b in RISKS:
                s = risk.simulate(IS, b, pol)
                tail, med = risk.drawdown_tail(IS, b, pol, n=200)
                res["frontier"].append(dict(policy=pol, risk=b, cagr=s["cagr"], max_dd=s["max_dd"], dd_1in20=tail, dd_median=med,
                                            taken=s["taken"], skipped=s["skipped"], red=s["red_episodes"]))
                print(f"{which:9s} {pol:7s} risk {b:.4f}: CAGR {s['cagr']:+.3f} maxDD {s['max_dd']:.3f} 1in20 {tail:.3f} "
                      f"taken {s['taken']} skipped {s['skipped']} red {s['red_episodes']}", flush=True)
        ok = [f for f in res["frontier"] if f["policy"] == "RAG" and f["max_dd"] <= 0.30 and f["dd_1in20"] <= 0.35]
        chosen = max(ok, key=lambda f: f["risk"])["risk"] if ok else None
        res["chosen_risk_RAG"] = chosen
        if chosen:
            res["at_chosen"] = {}
            for pol in risk.POLICIES:
                si, so = risk.simulate(IS, chosen, pol), risk.simulate(OOS, chosen, pol)
                fn = fortnights(so["eq"], so["eq_t"]); fi = fortnights(si["eq"], si["eq_t"])
                res["at_chosen"][pol] = dict(
                    is_cagr=si["cagr"], is_max_dd=si["max_dd"], oos_cagr=so["cagr"], oos_max_dd=so["max_dd"], oos_final=so["final"],
                    oos_taken=so["taken"], oos_skipped=so["skipped"], oos_red=so["red_episodes"],
                    fortnight_pos_share_is=float((fi > 0).mean()), fortnight_median_is=float(np.median(fi)),
                    fortnight_pos_share_oos=float((fn > 0).mean()), fortnight_median_oos=float(np.median(fn)))
                print(f"  @{chosen:.4f} {pol:7s} IS CAGR {si['cagr']:+.3f} DD {si['max_dd']:.3f} | OOS CAGR {so['cagr']:+.3f} DD {so['max_dd']:.3f} "
                      f"| fortnights + {np.mean(fn > 0):.2f}", flush=True)
        pol, b = DEMO
        si, so = risk.simulate(IS, b, pol), risk.simulate(OOS, b, pol)
        tail, med = risk.drawdown_tail(IS, b, pol, n=500)
        fn = fortnights(so["eq"], so["eq_t"]); fi = fortnights(si["eq"], si["eq_t"])
        res["demo"] = dict(policy=pol, risk=b, is_cagr=si["cagr"], is_max_dd=si["max_dd"], is_dd_1in20=tail, is_dd_median=med,
                           is_skipped=si["skipped"], is_red=si["red_episodes"], is_shadow_amber_entries=si["amber_entries"],
                           oos_cagr=so["cagr"], oos_max_dd=so["max_dd"], oos_final=so["final"], oos_skipped=so["skipped"],
                           oos_red=so["red_episodes"], oos_shadow_amber_entries=so["amber_entries"], oos_trades=so["taken"],
                           fortnight_pos_share_is=float((fi > 0).mean()), fortnight_median_is=float(np.median(fi)),
                           fortnight_pos_share_oos=float((fn > 0).mean()), fortnight_median_oos=float(np.median(fn)),
                           oos_equity=[[int(t), float(e)] for t, e in zip(so["eq_t"][::5], so["eq"][::5])],
                           is_equity=[[int(t), float(e)] for t, e in zip(si["eq_t"][::10], si["eq"][::10])])
        print(f"  DEMO {pol} @{b}: IS CAGR {si['cagr']:+.3f} DD {si['max_dd']:.3f} 1in20 {tail:.3f} | OOS CAGR {so['cagr']:+.3f} "
              f"DD {so['max_dd']:.3f} red {so['red_episodes']} | fortnights+ IS {np.mean(fi > 0):.2f} OOS {np.mean(fn > 0):.2f}", flush=True)
        if True:
            chosen = b
            # weekly expectation bands for the demo configuration, from 2011-2022 reshuffled paths
            rng = np.random.default_rng(11); wk = []; nwk = []
            for _ in range(200):
                s = risk.simulate(risk.quarter_shuffle(IS, rng), b, pol)
                wb = (s["eq_t"] - s["eq_t"][0]) // (7 * 86400); last = {}
                for k, v in zip(wb, s["eq"]):
                    last[k] = v
                vals = np.array([last[k] for k in sorted(last)]); wk.extend(vals[1:] / vals[:-1] - 1)
            wk = np.array(wk); tw = IS["t_in"] // (7 * 86400); _, cnt = np.unique(tw, return_counts=True)
            weeks = (IS["t_in"][-1] - IS["t_in"][0]) / (7 * 86400)
            res["weekly_bands"] = dict(return_p05=float(np.quantile(wk, 0.05)), return_p25=float(np.quantile(wk, 0.25)),
                                       return_median=float(np.median(wk)), return_p75=float(np.quantile(wk, 0.75)),
                                       return_p95=float(np.quantile(wk, 0.95)), trades_per_week=float(len(IS["t_in"]) / weeks),
                                       trades_per_active_week_p05=float(np.quantile(cnt, 0.05)), trades_per_active_week_p95=float(np.quantile(cnt, 0.95)),
                                       win_rate=float((IS["r"] > 0).mean()), mean_R=float(IS["r"].mean()),
                                       losing_streak_p95=int(np.quantile(streaks(IS["r"]), 0.95)), max_losing_streak=int(streaks(IS["r"]).max()))
        out[which] = res
    json.dump(out, open(os.path.join(RES, "portfolio.json"), "w"), indent=1, default=float)


def streaks(r):
    s = []; c = 0
    for x in r:
        if x < 0:
            c += 1
        else:
            if c:
                s.append(c)
            c = 0
    if c:
        s.append(c)
    return np.array(s or [0])


if __name__ == "__main__":
    main()
