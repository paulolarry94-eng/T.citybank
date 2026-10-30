"""Import the folder written by mt5/NorthStarExport.mq5 into the research format.

    python3 tools/ingest_mt5.py PATH/TO/NorthStarExport [--broker exness]

For every <SYM>_M1_<YEAR>.csv: data/broker/<SYM>_M1_bid_<YEAR>.npz with ts (ms UTC), o, h, l, c, v and spr (the
broker's spread in price units, minute by minute). The account-type suffix is stripped from the name
(EURUSDz -> EURUSD). specs.csv and calendar.csv are copied to data/broker/ unchanged. Prints coverage per file.
"""
import os, re, sys, glob, shutil, datetime as dt
import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def clean(sym):
    m = re.match(r"^([A-Z0-9]+?)([a-z._#+-]+)?$", sym)
    return m.group(1) if m else sym.upper()


def ingest(folder, out=None):
    out = out or os.path.join(ROOT, "data", "broker"); os.makedirs(out, exist_ok=True)
    specs = os.path.join(folder, "specs.csv")
    point = {}
    if os.path.exists(specs):
        S = pd.read_csv(specs)
        point = {clean(s): float(p) for s, p in zip(S.symbol, S.point)}
        shutil.copy(specs, os.path.join(out, "specs.csv"))
    if os.path.exists(os.path.join(folder, "calendar.csv")):
        shutil.copy(os.path.join(folder, "calendar.csv"), os.path.join(out, "calendar.csv"))
    files = sorted(glob.glob(os.path.join(folder, "*_M1_*.csv")))
    for f in files:
        m = re.match(r"(.+)_M1_(\d{4})\.csv$", os.path.basename(f))
        if not m:
            continue
        raw, y = m.group(1), int(m.group(2)); sym = clean(raw)
        d = pd.read_csv(f)
        if d.empty:
            continue
        d = d.sort_values("time_utc_ms").drop_duplicates("time_utc_ms")
        ts = d.time_utc_ms.values.astype(np.int64)
        pt = point.get(sym, np.nan)
        spr = d.spread_points.values.astype(np.float64) * pt if np.isfinite(pt) else np.full(len(d), np.nan)
        np.savez_compressed(os.path.join(out, f"{sym}_M1_bid_{y}.npz"), ts=ts, o=d.open.values, h=d.high.values, l=d.low.values,
                            c=d.close.values, v=d.tick_volume.values.astype(np.float32), spr=spr)
        print(f"{sym} {y}: {len(d)} bars {dt.datetime.utcfromtimestamp(ts[0] / 1000):%Y-%m-%d} -> "
              f"{dt.datetime.utcfromtimestamp(ts[-1] / 1000):%Y-%m-%d}, median spread {np.nanmedian(spr):.5g}")
    return out


if __name__ == "__main__":
    ingest(sys.argv[1])
