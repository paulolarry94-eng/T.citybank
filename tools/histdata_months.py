"""HistData 1-minute bars for a year still in progress (published month by month) -> data/holdout/{SYM}_M1_bid_{YEAR}.npz.
Same parsing and clock correction as tools/histdata_m1.py.
    python3 tools/histdata_months.py GER40 2026 1 11
"""
import os, sys, time, re, http.cookiejar, urllib.parse, urllib.request
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import histdata_m1 as H   # noqa: E402

PAGE = "https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{p}/{y}/{m}"


def fetch_month(pair, y, m, tries=4):
    url = PAGE.format(p=pair.lower(), y=y, m=m)
    for k in range(tries):
        try:
            op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
            html = op.open(urllib.request.Request(url, headers=H.UA), timeout=60).read().decode("utf-8", "ignore")
            form = dict(re.findall(r'<input type="hidden" name="(\w+)" id="\w+" value="([^"]*)"', html))
            if not form.get("tk"):
                return None
            req = urllib.request.Request("https://www.histdata.com/get.php", data=urllib.parse.urlencode(form).encode(),
                                         headers={**H.UA, "Referer": url})
            raw = op.open(req, timeout=300).read()
            if raw[:2] != b"PK":
                raise IOError(f"not a zip ({len(raw)} bytes)")
            return raw
        except Exception as e:
            print(f"  {pair} {y}-{m}: retry {k + 1} ({e})", flush=True); time.sleep(5 * 2 ** k)
    return None


def main(sym, y, m0, m1):
    pair = H.NAMES.get(sym, sym)
    parts = []
    for m in range(m0, m1 + 1):
        raw = fetch_month(pair, y, m)
        print(f"{sym} {y}-{m:02d}: {'ok' if raw else 'no file'}", flush=True)
        if raw:
            parts.append(H.parse(raw)); time.sleep(2)
    if not parts:
        return
    cat = [np.concatenate([p[i] for p in parts]) for i in range(6)]
    o = np.argsort(cat[0], kind="stable"); cat = [x[o] for x in cat]
    keep = np.r_[True, np.diff(cat[0]) > 0]; cat = [x[keep] for x in cat]
    yrs = (cat[0] // 1000).astype("datetime64[s]").astype("datetime64[Y]").astype(int) + 1970
    cat = [x[yrs == y] for x in cat]
    out = os.path.join(H.ROOT, "data", "holdout", f"{sym}_M1_bid_{y}.npz")
    np.savez_compressed(out, ts=cat[0], o=cat[1], h=cat[2], l=cat[3], c=cat[4], v=cat[5])
    print(f"saved {out}: {len(cat[0])} bars")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0].upper(), int(a[1]), int(a[2]), int(a[3]))
