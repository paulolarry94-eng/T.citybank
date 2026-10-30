"""Hunt 2, step 4: the European-hours euro leg as a tradeable strategy.

Rule (pre-declared from the seasonality scan, window chosen on 2011-2018 only): every weekday,
sell EURUSD at the open of the 09:00 London minute, buy back at the open of the 13:00 London
minute. Protective stop k x ATR14 of the last closed UTC day (k = 0.5; also 0.35 / 0.75 shown).
Same fill law and all-in cost (1.5 pips) as everything else; R = stop distance.
Variants: plain; skip Mondays and Fridays (weekly flows); only when the euro is above its
20-day average (fading strength)."""
import os, sys, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import engine as E, liquidity as LQ, gold_search as GS

LDN = ZoneInfo("Europe/London")
OUT = os.path.join(HERE, "..", "trades", "hunt"); os.makedirs(OUT, exist_ok=True)


def build(k=0.5, a=9, b=13, sym="EURUSD", side=-1, days=(0, 1, 2, 3, 4), above_ma=None):
    ts, o, h, l, c = E.load_m1(sym)
    cost = E.COST[sym]
    gaps = E.data_gaps(ts)
    dt_, do, dh, dl, dc, _ = E.resample(ts, o, h, l, c, 1440, 0)
    atr = E.atr_sma(dh, dl, dc, 14)
    ma = np.convolve(dc, np.ones(20) / 20, mode="full")[:len(dc)]; ma[:19] = np.nan
    ent, sd, sl, tpa, tpr, ex, md = [], [], [], [], [], [], []
    for d in np.unique(ts // 86400):
        D = dt.datetime.utcfromtimestamp(int(d) * 86400).date()
        if D.weekday() not in days:
            continue
        t0 = int(dt.datetime(D.year, D.month, D.day, a, 0, tzinfo=LDN).timestamp())
        t1 = int(dt.datetime(D.year, D.month, D.day, b, 0, tzinfo=LDN).timestamp())
        i0 = np.searchsorted(ts, t0); i1 = np.searchsorted(ts, t1)
        if i1 >= len(ts) or ts[i0] - t0 > 300 or ts[i1] - t1 > 300:
            continue
        kd = np.searchsorted(dt_ + 86400, t0, side="right") - 1
        if kd < 20 or not np.isfinite(atr[kd]):
            continue
        if above_ma is not None and not ((dc[kd] > ma[kd]) == above_ma):
            continue
        px = o[i0] + cost if side > 0 else o[i0]
        dist = k * atr[kd]
        ent.append(i0); sd.append(side); sl.append(px - dist if side > 0 else px + dist)
        tpa.append(0.0); tpr.append(0.0); ex.append(i1); md.append(3 * cost)
    A = lambda x, t=np.float64: np.asarray(x, t)
    res = LQ.run_abs(o, h, l, ts, A(ent, np.int64), A(sd, np.int64), A(sl), A(tpa), A(tpr), A(ex, np.int64), cost, A(md), gaps)
    return LQ.pack(res)


if __name__ == "__main__":
    for label, kw in (("k0.50 plain", dict(k=0.5)), ("k0.35 plain", dict(k=0.35)), ("k0.75 plain", dict(k=0.75)),
                      ("k0.50 Tue-Thu", dict(k=0.5, days=(1, 2, 3))), ("k0.50 euro above 20d MA", dict(k=0.5, above_ma=True)),
                      ("k0.50 euro below 20d MA", dict(k=0.5, above_ma=False))):
        tr = build(**kw)
        j = GS.judge(tr, 0.0); R = j["regimes"]
        print(f"{label:24s} {j['per_yr']:5.0f}/yr E {j['E']:+.3f}R IS {j['E_is']:+.3f} OOS {j['E_oos']:+.3f} t {j['t']:.2f} "
              f"Sh {j['sh_all']:.2f} win {j['win']:.0%} | eras {R['bear_2011_15']:+.3f} {R['range_2016_18']:+.3f} {R['bull_2019_25']:+.3f}")
        if label == "k0.50 plain":
            np.save(os.path.join(OUT, "EUR_EuroHours_short_0913.npy"), tr)
