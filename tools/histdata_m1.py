"""Download HistData.com free 1-minute bars (ASCII, bid) and save them in the repo format
data/{SYM}_M1_bid_{YEAR}.npz (ts in ms UTC, o, h, l, c, v).

    python3 tools/histdata_m1.py US500,GER40,WTI,XAGUSD 2011 2025

HistData's ASCII timestamps are EST WITHOUT daylight saving (UTC-5 all year), so UTC = stamp + 5 h.
Instruments: US500 = SPXUSD, GER40 = GRXEUR, WTI = WTIUSD, XAGUSD = XAGUSD, NAS100 = NSXUSD, BRENT = BCOUSD,
UK100 = UKXGBP, JP225 = JPXJPY; FX pairs use their own names. One request at a time, a short pause between files.
A year that is still in progress is published by HistData month by month; this tool fetches whole years only.
"""
import io, os, re, sys, time, zipfile, http.cookiejar, urllib.parse, urllib.request
import datetime as dt
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data")
NAMES = {"US500": "SPXUSD", "GER40": "GRXEUR", "WTI": "WTIUSD", "XAGUSD": "XAGUSD", "NAS100": "NSXUSD",
         "BRENT": "BCOUSD", "UK100": "UKXGBP", "JP225": "JPXJPY"}
PAGE = "https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{p}/{y}"
UA = {"User-Agent": "Mozilla/5.0"}


def fetch_year(pair, y, tries=4):
    url = PAGE.format(p=pair.lower(), y=y)
    for k in range(tries):
        try:
            op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
            html = op.open(urllib.request.Request(url, headers=UA), timeout=60).read().decode("utf-8", "ignore")
            form = dict(re.findall(r'<input type="hidden" name="(\w+)" id="\w+" value="([^"]*)"', html))
            if not form.get("tk"):
                return None                                      # no file for this year (HistData leaves the token empty)
            req = urllib.request.Request("https://www.histdata.com/get.php", data=urllib.parse.urlencode(form).encode(),
                                         headers={**UA, "Referer": url})
            raw = op.open(req, timeout=300).read()
            if raw[:2] != b"PK":
                raise IOError(f"not a zip ({len(raw)} bytes)")
            return raw
        except Exception as e:
            print(f"  {pair} {y}: retry {k + 1} ({e})", flush=True); time.sleep(5 * 2 ** k)
    raise RuntimeError(f"{pair} {y}: download failed")


def parse(raw):
    z = zipfile.ZipFile(io.BytesIO(raw))
    name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    txt = z.read(name).decode()
    a = np.genfromtxt(io.StringIO(txt), delimiter=";", dtype=None, encoding=None,
                      names=["t", "o", "h", "l", "c", "v"])
    stamps = np.array([dt.datetime.strptime(s, "%Y%m%d %H%M%S").replace(tzinfo=dt.timezone.utc).timestamp() for s in a["t"]])
    ts = ((stamps + 5 * 3600) * 1000).astype(np.int64)        # EST (no DST) -> UTC
    return ts, a["o"].astype(float), a["h"].astype(float), a["l"].astype(float), a["c"].astype(float), a["v"].astype(np.float32)


def main(syms, y0, y1):
    os.makedirs(DATA, exist_ok=True)
    done, missing = [], []
    for sym in syms:
        pair = NAMES.get(sym, sym)
        parts = {}
        for y in range(y0 - 1, y1 + 1):                          # the previous file holds the first UTC hours of y0
            out = os.path.join(DATA, f"{sym}_M1_bid_{y}.npz")
            if y >= y0 and os.path.exists(out):
                continue
            try:
                raw = fetch_year(pair, y)
            except RuntimeError as e:
                print(f"{sym} {y}: ERROR {e}", flush=True); raw = None
            if raw is None:
                if y >= y0:
                    missing.append(f"{sym} {y}"); print(f"{sym} {y}: no HistData file", flush=True)
                continue
            parts[y] = parse(raw); time.sleep(2)
        if not parts:
            continue
        cat = [np.concatenate([p[i] for p in parts.values()]) for i in range(6)]
        o = np.argsort(cat[0], kind="stable"); cat = [x[o] for x in cat]
        keep = np.r_[True, np.diff(cat[0]) > 0]; cat = [x[keep] for x in cat]
        yrs = (cat[0] // 1000).astype("datetime64[s]").astype("datetime64[Y]").astype(int) + 1970
        for y in range(y0, y1 + 1):
            out = os.path.join(DATA, f"{sym}_M1_bid_{y}.npz")
            m = yrs == y
            if os.path.exists(out) or not m.any():
                continue
            ts, op, hi, lo, cl, v = (x[m] for x in cat)
            bad = float(np.mean((lo > np.minimum(op, cl) + 1e-9) | (hi < np.maximum(op, cl) - 1e-9)))
            np.savez_compressed(out, ts=ts, o=op, h=hi, l=lo, c=cl, v=v)
            f = lambda t: dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%m-%d")
            print(f"{sym} {y}: {m.sum()} bars, {f(ts[0])} -> {f(ts[-1])}, range {lo.min():g}-{hi.max():g}, bad bars {bad:.2%}", flush=True)
            done.append(f"{sym} {y}")
    print(f"\nDone: {len(done)} year files. Missing: {', '.join(missing) if missing else 'none'}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) != 3:
        sys.exit(__doc__)
    main([s.strip().upper() for s in a[0].split(",")], int(a[1]), int(a[2]))
