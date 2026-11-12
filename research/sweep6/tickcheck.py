"""One-minute resolution check (research/sweep6/PREREGISTRATION.md, addendum): the same setups simulated on M1 bars built
from Exness ticks and tick by tick, frictionless, bid prices.
    python3 research/sweep6/tickcheck.py -> research/results/sweep6/tickcheck.json
"""
import io, os, sys, json, zipfile, urllib.request, datetime as dt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "research"))
import engine as EN             # noqa: E402
import sweep6_scan as SC        # noqa: E402
import sweep6_outcomes as OC    # noqa: E402

URL = "https://ticks.ex2archive.com/ticks/{s}_Zero_Spread/{y}/{m:02d}/Exness_{s}_Zero_Spread_{y}_{m:02d}.zip"
SAMPLE = [(s, y, m) for s in ("EURUSD", "GBPUSD", "XAUUSD") for (y, m) in ((2021, 3), (2021, 9), (2022, 6))]
RECENT = sum(1 << d for d in range(2, 10))
OUT = os.path.join(ROOT, "research", "results", "sweep6")
SHOW = ["1R", "2R", "3R", "5R", "10R", "20R", "TP1", "TP2", "TP2-BE75", "5R-BE75", "P60"]


def ticks(sym, y, m):
    raw = urllib.request.urlopen(URL.format(s=sym, y=y, m=m), timeout=600).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    with z.open(z.namelist()[0]) as f:
        d = pd.read_csv(f, usecols=["Timestamp", "Bid"])
    t = pd.to_datetime(d["Timestamp"], format="%Y-%m-%d %H:%M:%S.%fZ", utc=True)
    ms = (t.astype("int64") // 1_000_000).to_numpy()
    o = np.argsort(ms, kind="stable")
    return ms[o], d["Bid"].to_numpy(float)[o]


def one(sym, y, m):
    ms, bid = ticks(sym, y, m)
    sec = ms // 1000
    mins = sec // 60 * 60
    u, first = np.unique(mins, return_index=True)
    last = np.r_[first[1:] - 1, len(bid) - 1]
    o = bid[first]; c = bid[last]
    h = np.maximum.reduceat(bid, first); l = np.minimum.reduceat(bid, first)
    B = dict(t=u.astype(np.int64), o=o, h=h, l=l, c=c, atr=np.nan_to_num(EN.atr_sma(h, l, c, 14)))
    S, L = SC.setups(B, 1, sym)
    base = (S["body_min"] >= 0.5) & ((S["swmask"] & RECENT) > 0)
    S = {k: (v[base] if isinstance(v, np.ndarray) and len(v) == len(base) else v) for k, v in S.items()}
    O = SC.orders(S, L, 60)
    M1 = dict(ts=B["t"], o=o, h=h, l=l, c=c)
    pes = OC.run(M1, O, L); opt = OC.run(M1, O, L, optimistic=True, post_min=0)
    TK = dict(ts=sec.astype(np.int64), o=bid, h=bid, l=bid, c=bid)       # every tick a zero-range bar
    tk = OC.run(TK, O, L, post_min=0)
    both = (pes["status"] == 3) & (tk["status"] == 3)
    res = dict(setups=int(len(O["t_conf"])), filled_m1=int((pes["status"] == 3).sum()), filled_tick=int((tk["status"] == 3).sum()),
               fill_agree=round(float(((pes["status"] == 3) == (tk["status"] == 3)).mean()), 4), structures={})
    for nm in SHOW:
        q = OC.NAMES.index(nm)
        a, b, c2 = pes["R"][both, q], opt["R"][both, q], tk["R"][both, q]
        ok = np.isfinite(a) & np.isfinite(c2)
        res["structures"][nm] = dict(n=int(ok.sum()), m1_pessimistic=round(float(a[ok].mean()), 4), m1_optimistic=round(float(b[ok].mean()), 4),
                                     tick=round(float(c2[ok].mean()), 4), differ=round(float((np.abs(a[ok] - c2[ok]) > 0.05).mean()), 4),
                                     win_m1=round(float((a[ok] > 0).mean()), 4), win_tick=round(float((c2[ok] > 0).mean()), 4))
    return res


def main():
    out = {}
    for s, y, m in SAMPLE:
        try:
            out[f"{s} {y}-{m:02d}"] = r = one(s, y, m)
            print(s, y, m, r["setups"], r["filled_m1"], r["filled_tick"], {k: (v["m1_pessimistic"], v["tick"]) for k, v in r["structures"].items()}, flush=True)
        except Exception as e:
            print(s, y, m, "ERROR", e, flush=True)
    pooled = {}
    for nm in SHOW:
        rows = [v["structures"][nm] for v in out.values()]
        n = sum(r["n"] for r in rows)
        pooled[nm] = {k: round(sum(r[k] * r["n"] for r in rows) / n, 4) for k in ("m1_pessimistic", "m1_optimistic", "tick", "differ", "win_m1", "win_tick")}
        pooled[nm]["n"] = n
    json.dump(dict(prereg="research/sweep6/PREREGISTRATION.md (addendum)", months=out, pooled=pooled),
              open(os.path.join(OUT, "tickcheck.json"), "w"), indent=1)
    return pooled


if __name__ == "__main__":
    for k, v in main().items():
        print(k, v)
