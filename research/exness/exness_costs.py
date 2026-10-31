"""Measure real Exness Zero-account spreads from Exness's public tick archive (ticks.ex2archive.com).

Sample fixed BEFORE measuring (2026-10-31):
  symbols : XAUUSD, EURUSD, GBPUSD, USDJPY, XAGUSD, US500, DE30, USOIL   (the *_Zero_Spread feeds)
  months  : 2021-03, 2022-06, 2023-09, 2024-01, 2024-07, 2025-04         (different regimes; 2022 volatile)
Method: for every minute, the spread (ask - bid) of the last tick in that minute = the spread a market order meets
at a random moment. Summaries exclude weekends and the 20:30-23:00 UTC rollover block that the Truth Lab never
trades. Commission is NOT in tick data; it is added from public sources in costs_exness.json (labelled estimate).

    python3 research/exness/exness_costs.py            # downloads ~48 zip files one at a time, keeps only summaries
Output: research/results/exness/zero_spreads.json
"""
import io, os, sys, json, zipfile, urllib.request
import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "research", "results", "exness"); os.makedirs(OUT, exist_ok=True)
SYMS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "XAGUSD", "US500", "DE30", "USOIL"]
MONTHS = [(2021, 3), (2022, 6), (2023, 9), (2024, 1), (2024, 7), (2025, 4)]
URL = "https://ticks.ex2archive.com/ticks/{s}_Zero_Spread/{y}/{m:02d}/Exness_{s}_Zero_Spread_{y}_{m:02d}.zip"


def minute_spreads(sym, y, m):
    raw = urllib.request.urlopen(URL.format(s=sym, y=y, m=m), timeout=300).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    with z.open(z.namelist()[0]) as f:
        d = pd.read_csv(f, usecols=["Timestamp", "Bid", "Ask"])
    t = pd.to_datetime(d["Timestamp"], format="%Y-%m-%d %H:%M:%S.%fZ", utc=True)
    s = pd.Series((d["Ask"] - d["Bid"]).to_numpy(), index=t)
    last = s.groupby(s.index.floor("min")).last()
    mid = ((d["Ask"] + d["Bid"]) / 2).median()
    return last, float(mid), len(d)


def summarise(last):
    idx = last.index
    mins = idx.hour * 60 + idx.minute
    keep = (idx.day_of_week < 5) & ~((mins >= 20 * 60 + 30) & (mins < 23 * 60))
    v = last[keep].to_numpy()
    by_hour = last[keep].groupby(idx[keep].hour).mean()
    return {"minutes": int(len(v)), "mean": float(v.mean()), "median": float(np.median(v)),
            "p90": float(np.quantile(v, 0.9)), "share_zero": float((v <= 1e-12).mean()),
            "mean_by_hour_utc": {int(h): float(x) for h, x in by_hour.items()}}


if __name__ == "__main__":
    syms = sys.argv[1:] or SYMS
    path = os.path.join(OUT, "zero_spreads.json")
    res = json.load(open(path)) if os.path.exists(path) else {}
    for s in syms:
        for y, m in MONTHS:
            key = f"{s} {y}-{m:02d}"
            if key in res:
                continue
            try:
                last, mid, n = minute_spreads(s, y, m)
                r = summarise(last); r.update(ticks=n, mid_price=mid); res[key] = r
                print(f"{key}: mean {r['mean']:.5g} median {r['median']:.5g} p90 {r['p90']:.5g} zero {r['share_zero']:.0%} "
                      f"(price {mid:.5g})", flush=True)
            except Exception as e:
                print(f"{key}: ERROR {e}", flush=True); continue
            json.dump(res, open(path, "w"), indent=1)
