"""Slow literal re-implementation of stop / target / break-even / chandelier trail, compared trade
by trade with the fast engine on random entries."""
import numpy as np
import runner as R, signals as SG


def slow(G, B, i, sd, stop_abs, dk, tgt, be, trail, cost, tstop=100):
    o, h, l, ts = G.o, G.h, G.l, G.ts
    nb = len(B["nxt"]); k0 = int(B["nxt"][i]); kend = int(B["nxt"][min(i + tstop, nb - 1)])
    entry = o[k0] + cost if sd > 0 else o[k0]
    a = B["atr"][i]
    stop = entry - sd * dk * a if dk > 0 else stop_abs
    dist = (entry - stop) * sd
    if dist < 3 * cost or dist <= 0 or dist > 5 * a:
        return None
    tp = entry + sd * tgt * dist; be_on = False; jb = i + 1
    for k in range(k0, kend):
        if sd > 0:
            if l[k] <= stop:
                px = stop if (k == k0 or o[k] > stop) else o[k]; return ts[k], (px - entry) / dist
            if tgt > 0 and h[k] >= tp:
                px = tp if (k == k0 or o[k] < tp) else o[k]; return ts[k], (px - entry) / dist
            fav = (h[k] - entry) / dist
        else:
            if h[k] + cost >= stop:
                px = stop if (k == k0 or o[k] + cost < stop) else o[k] + cost; return ts[k], (entry - px) / dist
            if tgt > 0 and l[k] + cost <= tp:
                px = tp if (k == k0 or o[k] + cost > tp) else o[k] + cost; return ts[k], (entry - px) / dist
            fav = (entry - (l[k] + cost)) / dist
        if be > 0 and not be_on and fav >= be:
            be_on = True; stop = max(stop, entry) if sd > 0 else min(stop, entry)
        if k + 1 >= B["nxt"][jb]:
            if trail > 0 and B["atr"][jb] > 0:
                j0 = max(jb - 21, 0)
                new = B["h"][j0:jb + 1].max() - trail * B["atr"][jb] if sd > 0 else B["l"][j0:jb + 1].min() + trail * B["atr"][jb]
                stop = max(stop, new) if sd > 0 else min(stop, new)
            jb += 1
    px = o[kend] if sd > 0 else o[kend] + cost
    return ts[kend], ((px - entry) if sd > 0 else (entry - px)) / dist


if __name__ == "__main__":
    rng = np.random.default_rng(3)
    for sym, tf in (("XAUUSD", "H4"), ("USDJPY", "H1"), ("EURUSD", "D1")):
        M = R.Mkt(sym); B = M.bars(tf)
        sig, side, stp = SG.tc(B, "don20")
        pick = np.sort(rng.choice(len(sig), 60, replace=False))
        bad = tot = 0
        for mg in (("atr2.5", 0.0, 0.0, 3.0), ("struct", 2.0, 1.0, 0.0), ("atr1.5", 3.0, 0.5, 2.0), ("struct", 0.0, 1.5, 4.0)):
            for p in pick:
                fast = M.run(B, sig[p:p + 1], side[p:p + 1], stp[p:p + 1], mg, cut=None)
                ref = slow(M.G, B, sig[p], side[p], stp[p], 0.0 if mg[0] == "struct" else float(mg[0][3:]), mg[1], mg[2], mg[3], M.cost)
                if ref is None and len(fast) == 0:
                    continue
                tot += 1
                if ref is None or len(fast) == 0 or int(fast[0, 1]) != int(ref[0]) or abs(fast[0, 3] - ref[1]) > 1e-9:
                    bad += 1
        print(f"{sym} {tf}: {tot} trades compared, {bad} mismatches")
