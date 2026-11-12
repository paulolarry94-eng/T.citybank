"""The one logged look for the owner's EURUSD M5 pivot-sweep setting (research/sweep4/PREREGISTRATION_LOOK.md).
Step 1 (2011-22 only): choose the stop style, store it. Step 2: open 2023-25 and Jan-Oct 2026 once.
    python3 research/sweep4/look.py   ->   research/results/sweep4/LOOK.json
"""
import os, sys, json, math, time, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p_ in ("research", "research/truth", "research/body4"):
    sys.path.insert(0, os.path.join(ROOT, p_))
sys.path.insert(0, HERE)
import engine as E          # noqa: E402
import gold_traits as GT    # noqa: E402,F401  (its import adds data/holdout/<SYM>_M1_bid_2026.npz to the loader)
import protocol as P        # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "sweep4_pivot_v1.py"))
OUT = os.path.join(ROOT, "research", "results", "sweep4")
UTC = dt.timezone.utc
T = lambda y, m=1: int(dt.datetime(y, m, 1, tzinfo=UTC).timestamp())
PER = {"2011-19": (T(2011), T(2020)), "2020-22": (T(2020), T(2023)), "2023-25": (T(2023), T(2026)), "2026": (T(2026), T(2027))}
PIP = 0.0001
PROFILES = {"RoboForex Prime": (0.1, 0.25, 0.2), "Exness Zero": (0.05, 0.7, 0.2), "Tickmill Raw (owner's figures)": (0.11, 0.6, 0.2),
            "Pepperstone Razor (owner's figures)": (0.1, 0.7, 0.2), "zero cost": (0.0, 0.0, 0.0)}
BASE = dict(piv=10, sweep="c12", target="pv2")
OTHERS = ["GBPUSD", "USDJPY", "EURGBP", "XAUUSD", "GER40"]


def stats(R):
    n = len(R)
    if n == 0:
        return dict(n=0)
    d = dict(n=n, E=round(float(R.mean()), 3), win=round(float((R > 0).mean()), 3), total_R=round(float(R.sum()), 1))
    if n >= 3 and R.std() > 0:
        d["t"] = round(float(R.mean() / R.std() * math.sqrt(n)), 2); d["s"] = round(float(R.mean() / R.std()), 3)
    m = n // 10
    if m:
        C = R[:m * 10].reshape(m, 10).sum(axis=1)
        d["rounds_of_10"] = m; d["rounds_positive"] = round(float((C > 0).mean()), 2); d["rounds_mean_R"] = round(float(C.mean()), 2)
    return d


def run(M, tf, p, cut=2 ** 62, split=None):
    keep = dict(S.SPLIT[M.sym])
    if split:
        S.SPLIT[M.sym] = split
    try:
        D = S.detail(M, M.bars(tf), dict(p, tf=tf), cut=cut)
    finally:
        S.SPLIT[M.sym] = keep
    return D[np.argsort(D[:, 0], kind="stable")]


def by_period(D, pers):
    return {k: stats(D[(D[:, 0] >= PER[k][0]) & (D[:, 0] < PER[k][1]), 3]) for k in pers}


def main():
    path = os.path.join(OUT, "LOOK.json")
    if os.path.exists(path):
        raise SystemExit("the look was already made: " + path)
    M = P.market("EURUSD", S)
    # step 1: the stop, on 2011-22 only
    dev = {}
    for st in ("range", "buf20", "trail"):
        D = run(M, "M5", dict(BASE, stop=st), cut=T(2023))
        R = D[:, 3]
        dev[st] = dict(s=round(float(R.mean() / R.std()), 4), **by_period(D, ("2011-19", "2020-22")))
    stop = max(dev, key=lambda k: dev[k]["s"])
    prim = dict(BASE, stop=stop)
    rec = dict(prereg="research/sweep4/PREREGISTRATION_LOOK.md", decided_by="owner, 2026-11-12 ('test 2026 too ... if M5 EU works let's test it proper')",
               primary=dict(market="EURUSD", tf="M5", **prim), stop_choice_2011_22=dev,
               started=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    json.dump(rec, open(path, "w"), indent=1)            # on record before any later number is computed
    print("stop chosen on 2011-22:", stop, json.dumps(dev, indent=1), flush=True)
    # step 2: the look
    D = run(M, "M5", prim)
    rec["primary_result"] = by_period(D, PER)
    later = D[D[:, 0] >= T(2023)]
    rec["costs"] = {}
    for name, (sp, cm, sl) in PROFILES.items():
        Dc = run(M, "M5", prim, split=dict(spread=sp * PIP, commission=cm * PIP, slippage=sl * PIP))
        rec["costs"][name] = by_period(Dc, ("2011-19", "2020-22", "2023-25", "2026"))
    rec["trades_2023_2026"] = [dict(fill=dt.datetime.fromtimestamp(int(r[0]), UTC).strftime("%Y-%m-%d %H:%M"),
                                    exit=dt.datetime.fromtimestamp(int(r[1]), UTC).strftime("%Y-%m-%d %H:%M"),
                                    side="buy" if r[2] > 0 else "sell", R=round(float(r[3]), 2), target_R=round(float((r[13] - r[10]) / r[4] * r[2]), 1),
                                    reason={1: "stop", 2: "target", 3: "trailed stop", 4: "Friday close", 5: "stop in fill minute"}[int(r[9])])
                               for r in later]
    passed = all(rec["primary_result"][k].get("E", -1) > 0 for k in ("2023-25", "2026"))
    rec["verdict"] = ("PASSES the pre-registered look (positive in 2023-25 and 2026): forward demo candidate, Tier B at most "
                      "(chosen with hindsight)") if passed else "FAILS the pre-registered look"
    # described, not decisive
    desc = {}
    for tf in ("M1", "M15", "M30", "H1"):
        desc[f"EURUSD {tf}"] = by_period(run(M, tf, prim), PER)
    for sym in OTHERS:
        Mo = P.market(sym, S)
        desc[f"{sym} M5"] = by_period(run(Mo, "M5", prim), PER)
    rec["described"] = desc
    rec["finished"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    json.dump(rec, open(path, "w"), indent=1)
    return rec


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("primary", "primary_result", "verdict")}, indent=1))
    print(json.dumps(r["costs"], indent=1))
    for k, v in r["described"].items():
        print(k, {p: (v[p].get("n"), v[p].get("E")) for p in v})
