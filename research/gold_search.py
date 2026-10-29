"""Run every gold family on every timeframe and judge it with the timeless funnel.

Gates
  G1 in-sample 2011-2018: E > 0 and annualised Sharpe > 0.37 (awesome-repo median)
  G2 out-of-sample 2019-2025: E > 0 and >= half the in-sample E
  G3 whole record: t-stat >= 1.96
  G4 TIMELESS: E > 0 in each regime - 2011-15 bear, 2016-18 range, 2019-25 bull
  G5 neighbours: the same family/timeframe at the neighbouring parameter is also positive
Kept legs: greedy by whole-record Sharpe, monthly-R correlation < 0.30 with legs kept.
"""
import os, json, time, datetime as dt
import numpy as np
import gold_lab as GL

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "trades", "gold"); os.makedirs(OUT, exist_ok=True)
REGIMES = {"bear_2011_15": (2011, 2015), "range_2016_18": (2016, 2018), "bull_2019_25": (2019, 2025)}
TFS = ["M15", "M30", "H1", "H4", "D1"]


def variants():
    for tf in TFS:
        for n in (20, 55):
            yield f"DON_{tf}_n{n}_trail", n, (lambda G, tf=tf, n=n: GL.donchian(G, tf, n, 2.0, 1.5))
            yield f"DON_{tf}_n{n}_turtle", n, (lambda G, tf=tf, n=n: GL.donchian(G, tf, n, 2.0, 0, turtle_exit=True))
        for f, s in ((20, 50), (50, 200)):
            yield f"MAX_{tf}_{f}-{s}", f, (lambda G, tf=tf, f=f, s=s: GL.ma_cross(G, tf, f, s))
        for lo in (5, 10, 20):
            yield f"RSI2_{tf}_lo{lo}", lo, (lambda G, tf=tf, lo=lo: GL.rsi2(G, tf, lo, 100 - lo))
        for k in (1.5, 2.0, 2.5):
            yield f"BB_{tf}_k{k:g}", k, (lambda G, tf=tf, k=k: GL.bollinger(G, tf, 20, k))
        for lo in (0.1, 0.2, 0.3):
            yield f"IBS_{tf}_lo{lo:g}", lo, (lambda G, tf=tf, lo=lo: GL.ibs(G, tf, lo, 1 - lo))
        if tf in ("M30", "H1", "H4"):
            for n in (20, 55):
                yield f"MTF_{tf}_n{n}", n, (lambda G, tf=tf, n=n: GL.mtf_trend(G, tf, n))
        if tf in ("H1", "H4", "D1"):
            for k in (0.3, 0.5, 0.7):
                yield f"VBO_{tf}_k{k:g}", k, (lambda G, tf=tf, k=k: GL.vol_breakout(G, tf, k))
    for sh in (7, 13):
        for mins in (30, 60):
            yield f"ORB_{sh:02d}h_{mins}m", mins, (lambda G, sh=sh, mins=mins: GL.opening_range(G, sh, mins))


def year(ts):
    return np.array([dt.datetime.utcfromtimestamp(int(t)).year for t in ts])


def judge(tr, gap_years=0.53):
    if len(tr) < 30:
        return None
    r = tr["r"]; y = year(tr["t_in"])
    span = (tr["t_in"].max() - tr["t_in"].min()) / (365.25 * 86400) - gap_years   # gold 2018 H2 hole
    def sh(x, yrs):
        return float(x.mean() / x.std(ddof=1) * np.sqrt(len(x) / yrs)) if len(x) > 2 and x.std() > 0 else np.nan
    ins, oos = r[y < 2019], r[y >= 2019]
    reg = {k: float(r[(y >= a) & (y <= b)].mean()) if ((y >= a) & (y <= b)).any() else np.nan
           for k, (a, b) in REGIMES.items()}
    t = float(r.mean() / r.std(ddof=1) * np.sqrt(len(r))) if r.std() > 0 else np.nan
    return {"n": len(r), "per_yr": len(r) / span, "win": float((r > 0).mean()), "E": float(r.mean()),
            "E_is": float(ins.mean()) if len(ins) else np.nan, "E_oos": float(oos.mean()) if len(oos) else np.nan,
            "sh_is": sh(ins, 7.1), "sh_all": sh(r, span), "t": t, "regimes": reg,
            "avg_w": float(r[r > 0].mean()) if (r > 0).any() else 0.0,
            "avg_l": float(r[r <= 0].mean()) if (r <= 0).any() else 0.0,
            "pf": float(r[r > 0].sum() / -r[r <= 0].sum()) if (r <= 0).any() and r[r <= 0].sum() < 0 else np.inf}


def main():
    G = GL.Gold(); res = {}; t0 = time.time()
    for name, param, fn in variants():
        tr = fn(G); np.save(os.path.join(OUT, name + ".npy"), tr)
        j = judge(tr)
        if j: res[name] = {"param": param, **j}
    print(f"{len(res)} variants in {time.time()-t0:.0f}s", flush=True)
    # gates
    fam = {}
    for k in res:
        fam.setdefault(k.rsplit("_", 1)[0], []).append(k)
    for k, v in res.items():
        v["G1"] = v["E_is"] > 0 and v["sh_is"] > 0.37
        v["G2"] = v["E_oos"] > 0 and v["E_oos"] >= 0.5 * v["E_is"]
        v["G3"] = v["t"] >= 1.96
        v["G4"] = all(x > 0 for x in v["regimes"].values())
        sib = [s for s in fam[k.rsplit("_", 1)[0]] if s != k]
        v["G5"] = (not sib) or any(res[s]["E"] > 0 for s in sib)
        v["pass"] = all(v[g] for g in ("G1", "G2", "G3", "G4", "G5"))
    passed = sorted([k for k, v in res.items() if v["pass"]], key=lambda k: -res[k]["sh_all"])
    monthly = {}
    for k in passed:
        tr = np.load(os.path.join(OUT, k + ".npy"))
        mk = np.array([(dt.datetime.utcfromtimestamp(int(t)).year - 2011) * 12 + dt.datetime.utcfromtimestamp(int(t)).month - 1 for t in tr["t_out"]])
        s = np.zeros(180); ok = (mk >= 0) & (mk < 180); np.add.at(s, mk[ok], tr["r"][ok]); monthly[k] = s
    kept = []
    for k in passed:
        if all(abs(np.corrcoef(monthly[k], monthly[q])[0, 1]) < 0.30 for q in kept):
            kept.append(k)
    json.dump({"results": res, "passed": passed, "kept": kept}, open(os.path.join(HERE, "results", "gold_lab.json"), "w"),
              indent=1, default=float)
    return res, passed, kept


if __name__ == "__main__":
    res, passed, kept = main()
    print(f"{len(passed)} pass all five gates; {len(kept)} kept after correlation")
    for k in passed:
        v = res[k]; R = v["regimes"]
        print(f"  {'KEEP' if k in kept else 'corr'} {k:24s} {v['per_yr']:6.1f}/yr win {v['win']:.0%} E {v['E']:+.3f} "
              f"IS {v['E_is']:+.3f} OOS {v['E_oos']:+.3f} Sh {v['sh_all']:.2f} t {v['t']:.2f} | bear {R['bear_2011_15']:+.3f} "
              f"range {R['range_2016_18']:+.3f} bull {R['bull_2019_25']:+.3f}")
