"""Build 1-minute bid bars from Exness's public tick archive (ticks.ex2archive.com) in the repo format
data/{SYM}_M1_bid_{YEAR}.npz (ts in ms UTC, o, h, l, c, v = tick count). History starts in 2020.

    python3 tools/exness_m1.py GER40 2020 2025 [--overwrite]

Feeds are the Zero-account ones (the owner's account type): GER40 = DE30_Zero_Spread, WTI = USOIL_Zero_Spread,
US500 = US500_Zero_Spread, XAGUSD = XAGUSD_Zero_Spread; other symbols use {SYM}_Zero_Spread. Bars use the Bid.
Weekends and the gaps between sessions have no bars (as in MT5). One month at a time.
"""
import io, os, sys, zipfile, urllib.request
import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data")
FEED = {"GER40": "DE30", "WTI": "USOIL"}
URL = "https://ticks.ex2archive.com/ticks/{f}_Zero_Spread/{y}/{m:02d}/Exness_{f}_Zero_Spread_{y}_{m:02d}.zip"


def month(feed, y, m):
    raw = urllib.request.urlopen(URL.format(f=feed, y=y, m=m), timeout=600).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    with z.open(z.namelist()[0]) as f:
        d = pd.read_csv(f, usecols=["Timestamp", "Bid"])
    t = pd.to_datetime(d["Timestamp"], format="%Y-%m-%d %H:%M:%S.%fZ", utc=True)
    s = pd.Series(d["Bid"].to_numpy(), index=t).sort_index()
    g = s.groupby(s.index.floor("min"))
    b = pd.DataFrame({"o": g.first(), "h": g.max(), "l": g.min(), "c": g.last(), "v": g.size()})
    return b


def main(sym, y0, y1, overwrite=False):
    feed = FEED.get(sym, sym)
    for y in range(y0, y1 + 1):
        out = os.path.join(DATA, f"{sym}_M1_bid_{y}.npz")
        if os.path.exists(out) and not overwrite:
            print(f"{sym} {y}: exists (use --overwrite)"); continue
        parts = []
        for m in range(1, 13):
            try:
                parts.append(month(feed, y, m))
            except Exception as e:
                print(f"{sym} {y}-{m:02d}: ERROR {e}", flush=True)
        if not parts:
            continue
        b = pd.concat(parts); b = b[~b.index.duplicated()].sort_index()
        b = b[b.index.year == y]
        ts = b.index.as_unit("ms").asi8.astype(np.int64)
        np.savez_compressed(out, ts=ts, o=b.o.to_numpy(float), h=b.h.to_numpy(float), l=b.l.to_numpy(float),
                            c=b.c.to_numpy(float), v=b.v.to_numpy(np.float32))
        print(f"{sym} {y}: {len(b)} bars from Exness {feed}_Zero_Spread, {b.index[0]:%m-%d} -> {b.index[-1]:%m-%d}, "
              f"range {b.l.min():g}-{b.h.max():g}", flush=True)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) != 3:
        sys.exit(__doc__)
    for s in a[0].split(","):
        main(s.strip().upper(), int(a[1]), int(a[2]), "--overwrite" in sys.argv)
