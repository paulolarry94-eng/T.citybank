"""Does the Leg 34 gold detector (truth/strategies/leg34_gold_v1.py) see the owner's dated gold trades of 29-30 Oct 2026?
Lists every sell setup the detector finds that evening/night (k = 3, 4, 5), its fill within 8 hours, and the 5-minute
candles, for comparison with the owner's screenshot (dated by its 30 Oct 01:20 UTC candle). Structure only, no results."""
import sys, os, numpy as np, pandas as pd
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path[:0] = [R, os.path.join(R, "northstar"), os.path.join(R, "truth"), os.path.join(R, "truth", "strategies")]
import engine as E, leg34_gold_v1 as S
d = np.load(os.path.join(R, "..", "data", "holdout", "XAUUSD_M1_bid_2026.npz"))
ts = (d["ts"] // 1000).astype(np.int64)
t0 = int(pd.Timestamp("2026-10-27", tz="UTC").timestamp()); t1 = int(pd.Timestamp("2026-10-31", tz="UTC").timestamp())
m = (ts >= t0) & (ts < t1)
bt, bo, bh, bl, bc, nxt = E.resample(ts[m], d["o"][m], d["h"][m], d["l"][m], d["c"][m], 5)
B = dict(t=bt, o=bo, h=bh, l=bl, c=bc, minutes=5)
u = lambda x: pd.Timestamp(int(x), unit="s").strftime("%m-%d %H:%M")
lo = int(pd.Timestamp("2026-10-29 18:00", tz="UTC").timestamp()); hi = int(pd.Timestamp("2026-10-30 08:00", tz="UTC").timestamp())
for k in (3, 4, 5):
    S._CACHE.clear()
    for s in S._setups(B, {"k": k, "engulf": "any"}):
        dec = int(bt[s["d"]] + 300)
        if lo <= dec <= hi and s["side"] < 0:
            # first fill of the sell limit within 96 candles
            fill = None
            for j in range(s["d"] + 1, min(len(bt), s["d"] + 1 + S.VALID)):
                if bh[j] >= s["entry"]:
                    fill = j; break
            legs = [u(bt[x]) + f" {bh[x] if i % 2 == 0 else bl[x]:.2f}" for i, x in enumerate(s["legs"])]
            print(f"k={k} decision {u(dec)} legs(4,3,2,1) {legs} entry {s['entry']:.2f} p4 {s['p4']:.2f} "
                  f"stop fixed {S.stop_of(s,'fixed'):.2f} scaled {S.stop_of(s,'scaled'):.2f} pct {s['pct']} "
                  f"fill {u(bt[fill]) if fill is not None else None}")

e = S.ema(bc)
print("\n time   open    high     low    close   ema10")
a = int(pd.Timestamp("2026-10-29 20:00", tz="UTC").timestamp()); b = int(pd.Timestamp("2026-10-30 06:30", tz="UTC").timestamp())
for i in np.flatnonzero((bt >= a) & (bt <= b)):
    print(u(bt[i]), f"{bo[i]:.2f} {bh[i]:.2f} {bl[i]:.2f} {bc[i]:.2f} {e[i]:.2f}", "bull" if bc[i] > bo[i] else "bear")
