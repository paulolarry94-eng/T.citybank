"""Download Dukascopy 1-minute BID candles straight from the public datafeed (one LZMA file per day) and save
them in the repo's format: data/{SYM}_M1_bid_{YEAR}.npz (ts in ms UTC, o, h, l, c, v).

    python3 tools/dukascopy_m1.py AUDUSD 2011 2025           # one symbol, years inclusive
    python3 tools/dukascopy_m1.py --all 2011 2025            # the whole breadth list below

Day file: https://datafeed.dukascopy.com/datafeed/{SYM}/{YYYY}/{MM-1:02d}/{DD:02d}/BID_candles_min_1.bi5
Records: 24 bytes big-endian: seconds-from-midnight u32, open, close, low, high (u32 price x factor), volume f32.
The price factor is found per instrument from a plausible price range (checked, not assumed) and printed.
Stdlib only. Polite: 8 parallel requests, retries with backoff.
"""
import os, sys, lzma, struct, time, datetime as dt, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data")
URL = "https://datafeed.dukascopy.com/datafeed/{s}/{y}/{m:02d}/{d:02d}/BID_candles_min_1.bi5"
# repo symbol -> (Dukascopy feed name, plausible price range used to find the integer price factor)
BREADTH = {
    "AUDUSD": ("AUDUSD", (0.4, 1.2)), "NZDUSD": ("NZDUSD", (0.4, 1.0)), "USDCAD": ("USDCAD", (0.9, 1.6)),
    "USDCHF": ("USDCHF", (0.6, 1.3)), "EURJPY": ("EURJPY", (90, 200)), "GBPJPY": ("GBPJPY", (110, 230)),
    "EURGBP": ("EURGBP", (0.6, 1.0)), "AUDJPY": ("AUDJPY", (55, 115)), "CADJPY": ("CADJPY", (60, 125)),
    "CHFJPY": ("CHFJPY", (60, 190)), "EURAUD": ("EURAUD", (1.0, 2.1)), "EURCHF": ("EURCHF", (0.85, 1.7)),
    "GBPAUD": ("GBPAUD", (1.4, 2.6)), "AUDNZD": ("AUDNZD", (0.95, 1.4)), "XAGUSD": ("XAGUSD", (10, 60)),
    "XPTUSD": ("XPTUSD", (500, 2000)), "WTI": ("LIGHTCMDUSD", (-50, 160)), "BRENT": ("BRENTCMDUSD", (10, 160)),
    "NATGAS": ("GASCMDUSD", (1, 12)), "US500": ("USA500IDXUSD", (1000, 8000)), "NAS100": ("USATECHIDXUSD", (1800, 30000)),
    "US30": ("USA30IDXUSD", (10000, 50000)), "GER40": ("DEUIDXEUR", (5000, 26000)), "UK100": ("GBRIDXGBP", (4500, 10000)),
    "JP225": ("JPNIDXJPY", (8000, 45000)), "BTCUSD": ("BTCUSD", (100, 200000)), "ETHUSD": ("ETHUSD", (5, 10000)),
}
FACTORS = [1, 10, 100, 1000, 10000, 100000, 1000000]


def parse(raw):
    """Decompressed day file -> int array (n, 6): seconds, open, close, low, high, volume-bits."""
    n = len(raw) // 24
    if n == 0:
        return np.zeros((0, 5)), np.zeros(0, np.float32)
    a = np.frombuffer(raw[:n * 24], dtype=">u4").reshape(n, 6)
    vol = np.frombuffer(a[:, 5].astype(">u4").tobytes(), dtype=">f4").astype(np.float32)
    return a[:, :5].astype(np.int64), vol


def fetch_day(feed, day, tries=5):
    u = URL.format(s=feed, y=day.year, m=day.month - 1, d=day.day)
    for k in range(tries):
        try:
            with urllib.request.urlopen(u, timeout=60) as r:
                b = r.read()
            if not b:
                return None
            return lzma.decompress(b, format=lzma.FORMAT_AUTO)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 ** k)
        except Exception:
            time.sleep(2 ** k)
    raise RuntimeError(f"failed {u}")


def factor_for(medians, lo_hi):
    lo, hi = lo_hi
    for f in FACTORS:
        m = np.median(medians) / f
        if lo <= m <= hi:
            return f
    raise ValueError(f"no price factor maps median {np.median(medians)} into {lo_hi}")


def year(sym, y, workers=8):
    feed, rng = BREADTH.get(sym, (sym, None))
    out = os.path.join(DATA, f"{sym}_M1_bid_{y}.npz")
    if os.path.exists(out):
        print(f"{sym} {y}: exists"); return out
    days = [dt.date(y, 1, 1) + dt.timedelta(d) for d in range((dt.date(y + 1, 1, 1) - dt.date(y, 1, 1)).days)]
    days = [d for d in days if d <= dt.date.today()]
    with ThreadPoolExecutor(workers) as ex:
        raws = list(ex.map(lambda d: fetch_day(feed, d), days))
    ts, px, vol = [], [], []
    for d, raw in zip(days, raws):
        if raw is None:
            continue
        a, v = parse(raw)
        if not len(a):
            continue
        t0 = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())
        ts.append((t0 + a[:, 0]) * 1000); px.append(a[:, 1:5]); vol.append(v)
    if not ts:
        print(f"{sym} {y}: no data"); return None
    ts = np.concatenate(ts); P = np.concatenate(px).astype(np.float64); vol = np.concatenate(vol)
    flat = (P[:, 0] == P[:, 1]) & (P[:, 1] == P[:, 2]) & (P[:, 2] == P[:, 3])
    keep = ~((vol == 0) & flat)                             # drop padding minutes (closed market), keep real quiet minutes
    ts, P, vol = ts[keep], P[keep], vol[keep]
    f = factor_for(P[:, 0], rng) if rng else 100000
    o, c, l, h = (P[:, i] / f for i in range(4))
    bad = float(np.mean((l > np.minimum(o, c) + 1e-12) | (h < np.maximum(o, c) - 1e-12)))
    if bad > 0.01:
        raise ValueError(f"{sym} {y}: {bad:.1%} bars violate low <= open/close <= high (column order?)")
    np.savez_compressed(out, ts=ts.astype(np.int64), o=o, h=h, l=l, c=c, v=vol)
    print(f"{sym} {y}: {len(ts)} bars, factor {f}, {dt.datetime.utcfromtimestamp(ts[0] / 1000):%m-%d} -> "
          f"{dt.datetime.utcfromtimestamp(ts[-1] / 1000):%m-%d}, range {l.min():g}-{h.max():g}", flush=True)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    syms = list(BREADTH) if a[0] == "--all" else [a[0].upper()]
    y0, y1 = int(a[1]), int(a[2])
    for s in syms:
        for y in range(y0, y1 + 1):
            try:
                year(s, y)
            except Exception as e:
                print(f"{s} {y}: ERROR {e}", flush=True)
