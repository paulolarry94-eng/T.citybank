"""One logged look at 2023-2025 for the FVG watch-list cluster (H4, displacement >= 1.5 ATR, entry at
the gap midpoint, stop beyond candle 1, no target) and the same displacement followed at market."""
import os, sys, json, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "four"))
import fvg_lab as F
from runner import year_index
RES = os.path.join(HERE, "..", "results")
log = json.load(open(os.path.join(RES, "orb_oos_log.json")))
log.append(dict(when=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), label="FVG watch-list cluster + market-entry comparison, 2023-2025"))
json.dump(log, open(os.path.join(RES, "orb_oos_log.json"), "w"), indent=1)
RULES = [("CE retrace, gap>=0.3", ("H4", "ce", 1.5, 0.3, "origin", 0.0, 0.0)), ("CE retrace, gap>=0.1", ("H4", "ce", 1.5, 0.1, "origin", 0.0, 0.0)),
         ("edge retrace, gap>=0.3", ("H4", "edge", 1.5, 0.3, "origin", 0.0, 0.0)),
         ("market entry after candle 3", ("H4", "market", 1.5, 0.3, "origin", 0.0, 0.0)),
         ("market entry, 2R target", ("H4", "market", 1.5, 0.3, "origin", 2.0, 0.0))]
L = {s: F.Lab(s) for s in ("XAUUSD", "EURUSD", "GBPUSD", "USDJPY")}
out = {}
for lab, cfg in RULES:
    pooled = {"dev": [], "val": [], "oos": []}; per = {}
    for s, lb in L.items():
        tr = lb.run(*cfg)
        y = year_index(tr[:, 0].astype(np.int64)) if len(tr) else np.zeros(0)
        per[s] = {}
        for p, (a, b) in (("dev", (2011, 2019)), ("val", (2020, 2022)), ("oos", (2023, 2025))):
            r = tr[(y >= a) & (y <= b), 3] if len(tr) else np.zeros(0)
            pooled[p].append(r); per[s][p] = float(r.mean()) if len(r) else np.nan
    st = {}
    for p, v in pooled.items():
        r = np.concatenate(v); st[p] = (len(r), float(r.mean()), float(r.mean() / r.std(ddof=1) * np.sqrt(len(r))))
    out[lab] = dict(pooled=st, per=per)
    print(f"{lab:30s} " + " | ".join(f"{p} n {v[0]:4d} E {v[1]:+.3f} t {v[2]:+.2f}" for p, v in st.items()))
    print(f"{'':30s} 2023-25 by market: " + " ".join(f"{s} {per[s]['oos']:+.3f}" for s in per))
json.dump(out, open(os.path.join(RES, "fvg", "final_check.json"), "w"), indent=1)
