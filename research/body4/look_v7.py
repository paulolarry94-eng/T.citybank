"""The one logged look at unseen January-October 2026 for body4_range_v7 (pre-registered research/body4/PREREGISTRATION_V7.md,
step 4; the owner said "run the final check", 2026-11-09). The PRIMARY only (lbbody=1, target 5R, M5 + M15, 13:00-17:00 UTC),
on the markets that have 2026 data here: EURUSD, GBPUSD, USDJPY, EURGBP, XAUUSD (Exness ticks; EURGBP HistData). US500,
NAS100, GER40, WTI and JP225 have no 2026 data in this repo. Logged once: research/results/body4/v7/LOOK_2026.json.
    python3 research/body4/look_v7.py
"""
import os, sys, json, math, time, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research")); sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import engine as E   # noqa: E402
import gold_traits as GT   # noqa: E402  (its import adds the 2026 data to the price loader)
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v7.py"))
OUT = os.path.join(ROOT, "research", "results", "body4", "v7")
WITH_2026 = ["EURUSD", "GBPUSD", "USDJPY", "EURGBP", "XAUUSD"]
Y26 = int(dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc).timestamp())


def main():
    path = os.path.join(OUT, "LOOK_2026.json")
    if os.path.exists(path):
        raise SystemExit("the 2026 look for body4_range_v7 was already made: " + path)
    st = json.load(open(os.path.join(OUT, "study_v7.json")))
    k = st["primary"]["config"]
    cfg = {kv.split("=")[0]: int(kv.split("=")[1]) for kv in k.split("|")}
    rec = dict(name=S.NAME, primary=k, markets=WITH_2026, missing=[m for m in S.MARKETS if m not in WITH_2026],
               decided_by="owner, 2026-11-09 ('run the final check')", started=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    json.dump(rec, open(path, "w"), indent=1)                 # the look is on record before any 2026 number is computed
    rows = []
    for sym in WITH_2026:
        M = P.market(sym, S)
        sp, cm, sl = S.SPLIT[sym]["spread"], S.SPLIT[sym]["commission"], S.SPLIT[sym]["slippage"]
        for tf in S.TIMEFRAMES:
            D = S.detail(M, M.bars(tf), dict(cfg, tf=tf))
            D = D[D[:, 0] >= Y26]
            for r in D:
                why = int(r[9]); slip = sl / r[4] if why in (1, 3, 4, 5) else 0.0
                rows.append(dict(market=sym, tf=tf, fill=dt.datetime.fromtimestamp(int(r[0]), dt.timezone.utc).isoformat(),
                                 side="buy" if r[2] > 0 else "sell", reason=int(why), R_prime=round(float(r[3]), 4),
                                 R_low=round(float(r[3] + slip), 4), R_zero=round(float(r[3] + slip + (sp + cm) / r[4]), 4)))
    R = np.array([x["R_prime"] for x in rows])
    rec["trades"] = rows
    rec["result"] = dict(n=len(R), E_prime=round(float(R.mean()), 4) if len(R) else None,
                         E_low=round(float(np.mean([x["R_low"] for x in rows])), 4) if rows else None,
                         E_zero=round(float(np.mean([x["R_zero"] for x in rows])), 4) if rows else None,
                         targets_hit=int(sum(x["reason"] == 2 for x in rows)), total_R_prime=round(float(R.sum()), 3))
    rec["verdict"] = ("v7 was already rejected on 2011-25 (pre-registered pass not met); this look is the last unseen data "
                      "for the body-engulf family and cannot change that")
    rec["finished"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    json.dump(rec, open(path, "w"), indent=1)
    return rec


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["result"], indent=1))
    for t in r["trades"]:
        print(t)
