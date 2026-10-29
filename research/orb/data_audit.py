"""PART 1 — inspect every data file before any strategy work."""
import glob, os, json, datetime as dt
import numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data")
rows, summary = [], {}
for f in sorted(glob.glob(os.path.join(DATA, "*_M1_bid_*.npz"))):
    sym, _, _, y = os.path.basename(f)[:-4].split("_"); y = int(y)
    d = np.load(f); ts = d["ts"] // 1000
    o, h, l, c = d["o"], d["h"], d["l"], d["c"]
    dup = int((np.diff(ts) == 0).sum())
    nonmono = int((np.diff(ts) < 0).sum())
    flat_fill = (o == h) & (h == l) & (l == c); flat_fill[1:] &= o[1:] == c[:-1]; flat_fill[0] = False
    real = ts[~flat_fill]
    wd = ((real // 86400) + 3) % 7                      # 0 = Monday
    # expected FX/metal minutes: Sun 22:00 -> Fri 22:00 UTC approx (5 x 1440 minus holidays)
    trading_days = len(np.unique(real[wd < 5] // 86400))
    cov = len(real) / max(trading_days * 1440, 1)
    gaps = np.diff(real) / 60
    big = int((gaps > 4 * 1440).sum())
    bad_ohlc = int(((h < np.maximum(o, c)) | (l > np.minimum(o, c)) | (h < l)).sum())
    src = "tick->M1 (bid+ask)" if "spr_med" in d.files else "M1 bid upload"
    spr = float(np.median(d["spr_med"])) if "spr_med" in d.files else None
    vol = ("tick count" if "n_ticks" in d.files else ("volume" if float(np.abs(d["v"]).sum()) > 0 else "none"))
    rows.append(dict(sym=sym, year=y, source=src, bars=int(len(ts)), real_bars=int(len(real)),
                     first=str(dt.datetime.utcfromtimestamp(int(ts[0]))), last=str(dt.datetime.utcfromtimestamp(int(ts[-1]))),
                     duplicates=dup, out_of_order=nonmono, flat_filler_pct=round(100 * flat_fill.mean(), 1),
                     coverage_pct=round(100 * cov, 1), gaps_over_4d=big, bad_ohlc=bad_ohlc,
                     median_spread=spr, volume=vol))
json.dump(rows, open(os.path.join(os.path.dirname(__file__), "..", "results", "orb_data_audit.json"), "w"), indent=1)
print(f"{'sym':7s} {'yr':4s} {'source':20s} {'bars':>7s} {'filler%':>7s} {'cover%':>6s} {'dup':>3s} {'gap>4d':>6s} {'badOHLC':>7s} {'spread':>8s} volume")
for r in rows:
    print(f"{r['sym']:7s} {r['year']:4d} {r['source']:20s} {r['real_bars']:7d} {r['flat_filler_pct']:7.1f} {r['coverage_pct']:6.1f} {r['duplicates']:3d} {r['gaps_over_4d']:6d} {r['bad_ohlc']:7d} {str(r['median_spread'] and round(r['median_spread'],5)):>8s} {r['volume']}")
