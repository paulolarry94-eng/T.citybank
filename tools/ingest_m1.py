"""Import Dukascopy 1-minute bid CSVs (dukascopy-node export) into data/{SYM}_M1_bid_{YEAR}.npz.

Usage: python3 tools/ingest_m1.py FILE.csv [FILE.csv ...]
Symbol and year come from the file name (e.g. xauusd-m1-bid-2019-01-01-2020-01-01.csv).
Handles exports with or without a volume column. Bars are kept exactly as exported;
flat weekend/holiday bars (if present) are removed later, at test time, not here.
Prints a coverage line per file so gaps are visible before anything is tested."""
import sys, re, os, datetime as dt
import numpy as np

def ingest(path, outdir="data"):
    m = re.search(r"([a-z]{6})-m1-bid-(\d{4})-01-01", os.path.basename(path))
    if not m:
        raise SystemExit(f"cannot read symbol/year from {path}")
    sym, year = m.group(1).upper(), int(m.group(2))
    a = np.loadtxt(path, delimiter=",", skiprows=1)
    a = a[np.argsort(a[:, 0])]
    ts = a[:, 0].astype(np.int64)
    keep = np.array([dt.datetime.utcfromtimestamp(t / 1000).year == year for t in ts])
    a, ts = a[keep], ts[keep]
    v = a[:, 5].astype(np.float32) if a.shape[1] > 5 else np.zeros(len(a), np.float32)
    out = os.path.join(outdir, f"{sym}_M1_bid_{year}.npz")
    np.savez_compressed(out, ts=ts, o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4], v=v)
    gaps = int((np.diff(ts) / 60000 > 4 * 24 * 60).sum())
    flat = int(((a[:, 1] == a[:, 2]) & (a[:, 2] == a[:, 3]) & (a[:, 3] == a[:, 4])).mean() * 100)
    print(f"{sym} {year}: {len(a)} bars  {dt.datetime.utcfromtimestamp(ts[0]/1000):%Y-%m-%d %H:%M} -> "
          f"{dt.datetime.utcfromtimestamp(ts[-1]/1000):%Y-%m-%d %H:%M}  gaps>4d={gaps}  flat bars={flat}%  "
          f"range {a[:,3].min():g}-{a[:,2].max():g}")
    return out

if __name__ == "__main__":
    for p in sys.argv[1:]:
        ingest(p)
