"""Bug audit of the body-engulf range scan (owner, 2026-11-08: "what in your scan could give negative results, check for
bugs"). Main settings of body4_range_v3 (entry 50%, stop at the range end, breakeven at 75% of the way, lookback on with
dojis bullish), targets 10R and 2R, 12 markets x M1-H4, fills before 2023.

    python3 research/body4/audit.py  ->  research/results/body4/v3/audit.json + AUDIT.md

1. Patterns: every detected setup re-checked from the raw candles with separate scalar code (colours, body engulfing,
   range, lookback with dojis bullish); and a scalar re-scan of the first 100,000 bars of every market x timeframe for
   setups the scanner MISSED.
2. Entries: for every trade, its limit level was not reachable (outside the rollover block) and its target was not touched
   between the order's placement and the fill; the fill price is at or better than the level.
3. Exits: every trade re-scored by an independent first-touch checker (numpy slices, datetime for Fridays and nights):
   exit minute, exit price and R must match the engine.
4. Buys vs sells, before and after costs; outcome mix (target / stop / breakeven / Friday); the most extreme R values.
"""
import os, sys, json, math, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v3.py"))
OUT = os.path.join(ROOT, "research", "results", "body4", "v3")
UTC = dt.timezone.utc
MAIN = dict(entry=0.5, be=1, buffer=0.0, lookback=1)
REASON = {1: "stop", 2: "target", 3: "breakeven stop", 4: "Friday close", 5: "stop in the fill minute"}


def friday_cut(t):
    d = dt.datetime.fromtimestamp(int(t), UTC)
    days = (4 - d.weekday()) % 7
    f = (d + dt.timedelta(days=days)).replace(hour=20, minute=30, second=0, microsecond=0)
    if f <= d:
        f += dt.timedelta(days=7)
    return int(f.timestamp())


def nights(t_in, t_out):
    n = 0
    d = dt.datetime.fromtimestamp(int(t_in), UTC).replace(hour=22, minute=0, second=0, microsecond=0)
    if d.timestamp() <= t_in:
        d += dt.timedelta(days=1)
    while d.timestamp() <= t_out:
        if d.weekday() < 5:
            n += 3 if d.weekday() == 2 else 1
        d += dt.timedelta(days=1)
    return n


def check_pattern(o, h, l, c, k, side, hi, lo, lb):
    """Scalar re-check of one setup. Returns the list of broken conditions."""
    bad = []
    up = lambda i: c[i] > o[i]
    dn = lambda i: c[i] < o[i]
    if side < 0:
        if not (up(k - 3) and dn(k - 2) and up(k - 1) and dn(k)): bad.append("colours")
        if not (o[k - 2] >= c[k - 3] and c[k - 2] < o[k - 3]): bad.append("engulf 2 over 1")
        if not (o[k] >= c[k - 1] and c[k] < o[k - 1]): bad.append("engulf 4 over 3")
    else:
        if not (dn(k - 3) and up(k - 2) and dn(k - 1) and up(k)): bad.append("colours")
        if not (o[k - 2] <= c[k - 3] and c[k - 2] > o[k - 3]): bad.append("engulf 2 over 1")
        if not (o[k] <= c[k - 1] and c[k] > o[k - 1]): bad.append("engulf 4 over 3")
    if abs(hi - max(h[k - 3:k + 1])) > 1e-12 or abs(lo - min(l[k - 3:k + 1])) > 1e-12: bad.append("range")
    cnt = 0
    for i in range(k - 8, k - 3):
        if i < 0:
            continue
        cnt += (c[i] >= o[i]) if side > 0 else (c[i] < o[i])
    if cnt != lb: bad.append("lookback")
    return bad


def scalar_scan(o, c, n):
    """Every setup in bars 3..n-1 by plain scalar rules (independent of body4_scan)."""
    found = set()
    for k in range(3, n):
        a, b, d, e = k - 3, k - 2, k - 1, k
        if c[a] > o[a] and c[b] < o[b] and o[b] >= c[a] and c[b] < o[a] and c[d] > o[d] and c[e] < o[e] and o[e] >= c[d] and c[e] < o[d]:
            found.add((k, -1))
        if c[a] < o[a] and c[b] > o[b] and o[b] <= c[a] and c[b] > o[a] and c[d] < o[d] and c[e] > o[e] and o[e] <= c[d] and c[e] > o[d]:
            found.add((k, 1))
    return found


def check_exit(M1, row, cost, target, be_frac, use_be):
    """Independent first-touch exit check of one engine trade. Returns (exit time, exit price, R)."""
    ts, o, h, l, c = M1
    sp, cm, sl, sw = cost["spread"], cost["commission"], cost["slippage"], cost["swap"]
    t_in, s, entry, stop, tp, R0 = int(row[0]), int(row[2]), row[10], row[12], row[13], row[4]
    level = tp - s * target * R0
    be_lvl = level + s * be_frac * target * R0
    i0 = int(np.searchsorted(ts, t_in))
    F = friday_cut(t_in)
    iF = int(np.searchsorted(ts, F))
    H, L, O = h[i0:iF], l[i0:iF], o[i0:iF]
    if s > 0:
        st_hit, tp_hit, be_hit = L <= stop, H >= tp, H >= be_lvl
    else:
        st_hit, tp_hit, be_hit = H + sp >= stop, L + sp <= tp, L + sp <= be_lvl
    tp_hit = tp_hit.copy(); tp_hit[0] = False; be_hit = be_hit.copy(); be_hit[0] = False
    first = lambda m: int(np.argmax(m)) if m.any() else 10 ** 9
    ks, kt, kb = first(st_hit), first(tp_hit), first(be_hit)
    cur_stop, why = stop, None
    if use_be and kb < min(ks, kt):
        cur_stop = entry
        rest = slice(kb + 1, None)
        st2 = (L[rest] <= entry) if s > 0 else (H[rest] + sp >= entry)
        ks2, kt2 = first(st2), first(tp_hit[rest])
        ks = kb + 1 + ks2 if ks2 < 10 ** 9 else 10 ** 9
        kt = kb + 1 + kt2 if kt2 < 10 ** 9 else 10 ** 9
        moved = True
    else:
        moved = False
    if ks < 10 ** 9 and ks <= kt:
        k = ks
        px = (min(cur_stop, O[k]) - sl) if s > 0 else (max(cur_stop, O[k] + sp) + sl)
        t_out = int(ts[i0 + k]); why = 3 if moved else (5 if k == 0 else 1)
    elif kt < 10 ** 9:
        k = kt
        px = max(tp, O[k]) if s > 0 else min(tp, O[k] + sp)
        t_out = int(ts[i0 + k]); why = 2
    else:
        px = c[iF - 1] - sl if s > 0 else c[iF - 1] + sp + sl
        t_out = F; why = 4
    R = (px - entry) * s / R0 - cm / R0 - nights(t_in, t_out) * sw / R0
    return t_out, px, R, why


def check_entry(M1, row, start_i, level, s, tp, spread):
    """Between the order's placement minute and the fill minute: the level was never reachable outside the rollover
    block and the target was never touched; the fill is at or better than the level."""
    ts, o, h, l, c = M1
    i0 = int(np.searchsorted(ts, int(row[0])))
    seg, seg_t = slice(start_i, i0), slice(start_i, i0 + 1)      # the target may not be touched in the fill minute either
    sod = ts[seg] % 86400
    open_ = ~((sod >= 20 * 3600 + 1800) & (sod < 23 * 3600))
    if s > 0:
        reach = (l[seg] + spread <= level) & open_
        tgt = h[seg_t] >= tp
        ok_px = row[10] <= level + 1e-12
    else:
        reach = (h[seg] >= level) & open_
        tgt = l[seg_t] + spread <= tp
        ok_px = row[10] >= level - 1e-12
    return (not reach.any()) and (not tgt.any()) and ok_px


def main():
    res = dict(settings="body4_range_v3 main settings: entry 50%, buffer 0, breakeven at 75% of the way, lookback on (dojis bullish)",
               patterns={}, missed={}, entries={}, exits={}, sides={}, outcomes={}, extremes={})
    worst, best = [], []
    for sym in S.MARKETS:
        M = P.market(sym, S)
        M1 = (np.asarray(M.ts, np.int64), np.asarray(M.o, float), np.asarray(M.h, float), np.asarray(M.l, float), np.asarray(M.G.c, float))
        cost = dict(S.SPLIT[sym], swap=M.swap)
        for tf in S.TIMEFRAMES:
            B = M.bars(tf)
            o, h, l, c = (np.asarray(B[x], float) for x in "ohlc")
            Sx = S.setups(B, dict(sample="flow"), M)
            # 1. patterns
            nbad = 0
            for j in range(len(Sx["k"])):
                if check_pattern(o, h, l, c, int(Sx["k"][j]), int(Sx["side"][j]), Sx["hi"][j], Sx["lo"][j], int(Sx["lookback"][j])):
                    nbad += 1
            res["patterns"][f"{sym} {tf}"] = dict(setups=int(len(Sx["k"])), broken=nbad)
            n = min(len(c), 100_000)
            mine = {(int(k), int(sd)) for k, sd in zip(Sx["k"], Sx["side"]) if k < n}
            ref = scalar_scan(o, c, n)
            res["missed"][f"{sym} {tf}"] = dict(scalar=len(ref), scanner=len(mine), missed=len(ref - mine), extra=len(mine - ref))
            start = np.searchsorted(M1[0], Sx["t_conf"])
            for T in (10, 2):
                p = dict(MAIN, tf=tf, target=T)
                D = S.detail(M, B, p, cut=P.core.CUT)
                key = f"{T}R"
                e = res["exits"].setdefault(key, dict(trades=0, exit_time_mismatch=0, R_mismatch=0, max_R_diff=0.0))
                en = res["entries"].setdefault(key, dict(trades=0, violations=0))
                for row in D:
                    t_out, px, R, why = check_exit(M1, row, cost, T, S.BE_FRAC, True)
                    e["trades"] += 1
                    if t_out != int(row[1]):
                        e["exit_time_mismatch"] += 1
                    d = abs(R - row[3])
                    if d > 1e-9:
                        e["R_mismatch"] += 1
                    e["max_R_diff"] = max(e["max_R_diff"], float(d))
                    j = int(row[8]); s = int(row[2])
                    w = Sx["hi"][j] - Sx["lo"][j]
                    level = Sx["hi"][j] - 0.5 * w if s > 0 else Sx["lo"][j] + 0.5 * w
                    en["trades"] += 1
                    if not check_entry(M1, row, int(start[j]), level, s, row[13], cost["spread"]):
                        en["violations"] += 1
                # 4. sides, outcomes, extremes (gross = after adding back commission and swaps; spread/slippage stay in)
                for sd, nm in ((1, "buys"), (-1, "sells")):
                    m = D[:, 2] == sd
                    a = res["sides"].setdefault(f"{key} {tf}", {}).setdefault(nm, [0, 0.0, 0.0])
                    a[0] += int(m.sum()); a[1] += float(D[m, 3].sum()); a[2] += float((D[m, 3] + D[m, 7] + D[m, 5]).sum())
                oc = res["outcomes"].setdefault(f"{key} {tf}", {})
                for code, nm in REASON.items():
                    oc[nm] = oc.get(nm, 0) + int((D[:, 9] == code).sum())
                for row in D:
                    rec = (float(row[3]), sym, tf, key, int(row[0]), int(row[2]), float(row[5]), float(row[7]), int(row[6]), REASON[int(row[9])], float(row[4]))
                    worst.append(rec); best.append(rec)
                worst.sort(); worst[:] = worst[:30]
                best.sort(reverse=True); best[:] = best[:30]
            print(sym, tf, res["patterns"][f"{sym} {tf}"], res["missed"][f"{sym} {tf}"], flush=True)
    fmt = lambda r: dict(R=round(r[0], 3), market=r[1], tf=r[2], target=r[3], time=dt.datetime.fromtimestamp(r[4], UTC).strftime("%Y-%m-%d %H:%M"),
                         side="buy" if r[5] > 0 else "sell", cost_R=round(r[6], 3), swap_R=round(r[7], 3), nights=r[8], reason=r[9], risk=r[10])
    res["extremes"] = dict(worst=[fmt(r) for r in worst[:15]], best=[fmt(r) for r in best[:15]])
    res["sides"] = {k: {s: dict(n=v[0], E=round(v[1] / v[0], 4) if v[0] else None, E_before_costs_and_swaps=round(v[2] / v[0], 4) if v[0] else None)
                        for s, v in d.items()} for k, d in res["sides"].items()}
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "audit.json"), "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("exits", "entries")}, indent=1))
    print("broken patterns:", sum(v["broken"] for v in r["patterns"].values()), "missed:", sum(v["missed"] for v in r["missed"].values()),
          "extra:", sum(v["extra"] for v in r["missed"].values()))
    print(json.dumps(r["extremes"]["worst"][:5], indent=0)); print(json.dumps(r["extremes"]["best"][:5], indent=0))
