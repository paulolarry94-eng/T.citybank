"""Which reward:risk is reached 50% of the time? (owner, 2026-11-08). Pre-registered: research/body4/PREREGISTRATION_V4.md
section 3a. v4 rules, breakeven off, NO target (so every trade runs to its stop or its time exit), entry 50%, stop at the
range end, lookback on (dojis bullish); windows "safe" (London/New York hours, no US news days, flat at 20:30 UTC) and
"all"; 12 markets pooled, per timeframe, 2011-19 and 2020-22.
For each trade: the furthest favourable move in R before the stop or the time exit (buys: bid high; sells: ask low = bid
low + spread; the fill minute and the exit minute are left out, the cautious reading). Hit rate at RR x = share of trades
whose favourable move reaches x. The RR where the curve crosses 50% is what "hits half the time".
    python3 research/body4/rr_curve.py  ->  research/results/body4/v4/rr_curve.json + RR_CURVE.md
"""
import os, sys, json, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v4.py"))
OUT = os.path.join(ROOT, "research", "results", "body4", "v4")
RR = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
Y20 = int(dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).timestamp())


def mfe(ts, h, l, row, spread):
    i0 = int(np.searchsorted(ts, int(row[0])))
    i1 = int(np.searchsorted(ts, int(row[1])))        # exit minute (or the first minute at/after a time exit)
    if i1 <= i0 + 1:
        return 0.0
    s, e, R0 = int(row[2]), row[10], row[4]
    if s > 0:
        return max(0.0, (h[i0 + 1:i1].max() - e) / R0)
    return max(0.0, (e - (l[i0 + 1:i1].min() + spread)) / R0)


def main():
    acc = {}
    cost = {}
    for sym in S.MARKETS:
        M = P.market(sym, S)
        ts, h, l = np.asarray(M.ts, np.int64), np.asarray(M.h, float), np.asarray(M.l, float)
        sp = S.SPLIT[sym]["spread"]
        for tf in S.TIMEFRAMES:
            for w in ("safe", "all"):
                p = dict(tf=tf, target=1000, window=w, entry=0.5, be=0, buffer=0.0, lookback=1)
                D = S.detail(M, M.bars(tf), p, cut=P.core.CUT)
                for r in D:
                    per = "2011-19" if r[0] < Y20 else "2020-22"
                    acc.setdefault((tf, w, per), []).append(mfe(ts, h, l, r, sp))
                    cost.setdefault((tf, w, per), []).append(r[5])
        print(sym, flush=True)
    res = {}
    for (tf, w, per), xs in sorted(acc.items()):
        x = np.asarray(xs)
        curve = {str(t): round(float((x >= t).mean()), 4) for t in RR}
        c = float(np.mean(cost[(tf, w, per)]))
        half = float(np.median(x))                     # the RR reached by half the trades
        res[f"{tf} | {w} | {per}"] = dict(trades=len(x), hit_rate=curve, rr_reached_by_half=round(half, 3),
                                          cost_R=round(c, 3), needed={str(t): round((1 + c) / (t + 1), 3) for t in RR})
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "rr_curve.json"), "w"), indent=1)
    L = ["# How far do the trades go before the stop? (body-engulf range, v4 rules, breakeven off, no target)", "",
         "Share of trades whose favourable move reaches each RR before the stop or the time exit (12 markets pooled). "
         "'Half' = the RR that half the trades reach. 'Needed' = the hit rate a target at that RR needs to break even after "
         "costs, about (1 + cost) / (RR + 1).", ""]
    for w in ("safe", "all"):
        L += [f"## Window: {w}", "", "| Timeframe | Period | Trades | 0.5R | 1R | 2R | 3R | 5R | 10R | Half reach | Needed at 2R / 5R / 10R |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for tf in S.TIMEFRAMES:
            for per in ("2011-19", "2020-22"):
                v = res.get(f"{tf} | {w} | {per}")
                if not v:
                    continue
                hr = v["hit_rate"]; nd = v["needed"]
                L.append(f"| {tf} | {per} | {v['trades']:,} | {hr['0.5']:.0%} | {hr['1.0']:.0%} | {hr['2.0']:.0%} | {hr['3.0']:.0%} | "
                         f"{hr['5.0']:.0%} | {hr['10.0']:.1%} | {v['rr_reached_by_half']:.2f}R | {nd['2.0']:.0%} / {nd['5.0']:.0%} / {nd['10.0']:.0%} |")
        L.append("")
    open(os.path.join(OUT, "RR_CURVE.md"), "w").write("\n".join(L) + "\n")
    return res


if __name__ == "__main__":
    main()
    print(open(os.path.join(OUT, "RR_CURVE.md")).read())
