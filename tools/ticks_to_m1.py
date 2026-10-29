"""Convert a Dukascopy tick-CSV year (FX-Data-*-DS repo layout) into the same M1 format as
tools/ingest_m1.py, plus the real spread of every minute.

Tick line: 'YYYY.MM.DD HH:MM:SS.mmm,p1,p2,v1,v2' (UTC). The lower of p1/p2 is the bid,
the higher the ask (checked per file, not assumed). Gold in these repos is stored /100,
so prices are multiplied back to dollars to match the 2019-2025 files.
Output: data/{SYM}_M1_bid_{YEAR}.npz with ts(ms), o,h,l,c (bid), spr_med, spr_max, n_ticks."""
import sys, os, glob
import numpy as np, pandas as pd

SCALE = {"XAUUSD": 100.0, "XAGUSD": 100.0}

def convert(root, sym, year, outdir="data"):
    files = sorted(glob.glob(os.path.join(root, sym, str(year), "*", "*_ticks.csv")))
    if not files:
        raise SystemExit(f"no tick files under {root}")
    frames = []
    for f in files:
        if os.path.getsize(f) == 0:
            continue
        d = pd.read_csv(f, header=None, usecols=[0, 1, 2], names=["t", "p1", "p2"],
                        engine="pyarrow")
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    t = pd.to_datetime(d["t"], format="%Y.%m.%d %H:%M:%S.%f", utc=True)
    s = SCALE.get(sym, 1.0)
    bid = np.minimum(d["p1"].values, d["p2"].values) * s
    ask = np.maximum(d["p1"].values, d["p2"].values) * s
    m = pd.DataFrame({"min": t.dt.floor("min"), "bid": bid, "spr": ask - bid})
    m = m.sort_values("min", kind="stable")
    g = m.groupby("min", sort=True)
    out = pd.DataFrame({"o": g["bid"].first(), "h": g["bid"].max(), "l": g["bid"].min(),
                        "c": g["bid"].last(), "spr_med": g["spr"].median(),
                        "spr_max": g["spr"].max(), "n": g["bid"].size()})
    ts = out.index.as_unit("ms").asi8.astype(np.int64)   # always milliseconds, whatever pandas' native unit
    path = os.path.join(outdir, f"{sym}_M1_bid_{year}.npz")
    np.savez_compressed(path, ts=ts, o=out.o.values, h=out.h.values, l=out.l.values,
                        c=out.c.values, spr_med=out.spr_med.values.astype(np.float32),
                        spr_max=out.spr_max.values.astype(np.float32),
                        n_ticks=out.n.values.astype(np.int32), v=np.zeros(len(out), np.float32))
    print(f"{sym} {year}: {len(d):,} ticks -> {len(out):,} M1 bars  "
          f"{out.index[0]:%Y-%m-%d %H:%M} -> {out.index[-1]:%Y-%m-%d %H:%M}  "
          f"range {out.l.min():g}-{out.h.max():g}  median spread {np.median(out.spr_med):.5g}",
          flush=True)
    return path

if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2], int(sys.argv[3]))
