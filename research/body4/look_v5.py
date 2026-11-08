"""The owner's 2023-25 look for body4_range_v5 (owner decision 2026-11-08; pre-registered research/body4/PREREGISTRATION_V5.md,
step 3). Logged ONCE: research/results/truth/body4_range_v5/oos_log.json (lab format) + research/results/body4/v5/LOOK_2023_25.json.
The 4 PRIMARY configurations come from study_v5.json (chosen on 2011-22) and are written to the look file before any
2023-25 number is computed. All 768 configurations are reported as description only.
    python3 research/body4/look_v5.py
"""
import os, sys, json, math, time, itertools, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402
import study_v5 as SV  # noqa: E402

S = SV.S
OUT = os.path.join(ROOT, "research", "results", "body4", "v5")
LAB = os.path.join(ROOT, "research", "results", "truth", S.NAME)
Y23 = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp())
Y26 = int(dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc).timestamp())


def worker(sym):
    M = P.market(sym, S)
    cell = {}
    for tf in S.TIMEFRAMES:
        B = M.bars(tf)
        for c in SV.CFGS:
            D = S.detail(M, B, dict(c, tf=tf), cut=2 ** 62)
            m = (D[:, 0] >= Y23) & (D[:, 0] < Y26)
            SV.add(cell.setdefault((sym, SV.ck(tf, c)), SV.zeros()), D[m, 3], D[m, 9], D[m, 7])
    print(sym, flush=True)
    return cell


def main():
    lookp = os.path.join(OUT, "LOOK_2023_25.json")
    if os.path.exists(lookp):
        raise SystemExit("the 2023-25 look for body4_range_v5 was already made: " + lookp)
    st = json.load(open(os.path.join(OUT, "study_v5.json")))
    prim = {k: v["config"] for k, v in st["primary_for_look"].items() if v.get("config")}
    rec = dict(name=S.NAME, fingerprint=S.FINGERPRINT, decided_by="owner, 2026-11-08 ('test the data in 2023-2025')",
               primary_chosen_before_look=prim, started=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    json.dump(rec, open(lookp, "w"), indent=1)                       # the choice is on disk before any 2023-25 number
    from multiprocessing import Pool
    cell = {}
    with Pool(4) as pool:
        for c_ in pool.imap_unordered(worker, S.MARKETS):
            cell.update(c_)
    pooled, mk, per_market = {}, {}, {}
    for (sym, k), a in cell.items():
        b = pooled.setdefault(k, SV.zeros())
        for f in b:
            b[f] += a[f]
        if a["n"] >= 3 and a["s"] > 0:
            mk[k] = mk.get(k, 0) + 1
        per_market.setdefault(k, {})[sym] = SV.stats(a)
    allres = {k: dict(SV.stats(a), markets_positive=mk.get(k, 0)) for k, a in pooled.items()}
    rec["primary"] = {name: dict(config=k, before_2023=st["pooled"][k], look_2023_25=allres[k], per_market=per_market[k])
                      for name, k in prim.items()}
    Es = np.array([v["E"] for v in allres.values() if v.get("n", 0) >= 100])
    rec["all_configurations"] = dict(count=len(allres), with_100_trades=int(len(Es)), positive=int((Es > 0).sum()),
                                     median_E=round(float(np.median(Es)), 4), best=max(((k, v) for k, v in allres.items() if v.get("n", 0) >= 100),
                                                                                       key=lambda z: z[1]["E"]))
    rec["note"] = "SECONDARY results are description only: choosing a setting from them would be hindsight."
    rec["finished"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    json.dump(dict(rec, all=allres), open(lookp, "w"), indent=1, default=float)
    # the lab's own log: one entry per configuration, so a later lab run of this fingerprint reuses it and cannot look again
    logp = os.path.join(LAB, "oos_log.json")
    log = json.load(open(logp)) if os.path.exists(logp) else []
    have = {e["config"] for e in log}
    for k, v in allres.items():
        tf, rest = k.split(" | ")
        cfg = dict(tf=tf, **{kv.split("=")[0]: kv.split("=")[1] for kv in rest.split("|")})
        key = json.dumps(cfg, sort_keys=True)
        if key not in have:
            log.append(dict(fingerprint=S.FINGERPRINT, config=key, time=rec["started"], oos=v, per_market=per_market[k],
                            source="research/body4/look_v5.py (owner-requested look)"))
    os.makedirs(LAB, exist_ok=True)
    json.dump(log, open(logp, "w"), indent=1, default=float)
    return rec


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["primary"], indent=1, default=float)[:4000])
    print(json.dumps(r["all_configurations"], indent=1, default=float))
