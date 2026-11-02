"""Replay of the owner's six EURUSD 5-minute charts (20-27 Oct 2026) through the scanner, on our data.

    python3 research/ema4/replay.py      # writes research/results/ema4/REPLAY.md, replay.json, charts/*.png

Days found by matching the closes read off the owner's screenshots against every EURUSD day 2011-2026 (best match 0.1-0.2 pip,
the next best day 3-17 pips off). Data: Exness ticks 2026 (data/holdout), 2025 before it for the EMA warm-up. The owner's
charts are TradingView (clock UTC+1 = Lagos); prices differ by a fraction of a pip, and every difference is shown.
"""
import os, sys, json, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import scanner                     # noqa: E402

UTC1 = dt.timezone(dt.timedelta(hours=1))
OUT = os.path.join(ROOT, "research", "results", "ema4")
EXAMPLES = [
    dict(chart=1, day="2026-10-27", first="16:40", side=-1, owner="B+ sell (only the 4th closed below the 3rd open); won"),
    dict(chart="2/3", day="2026-10-27", first="06:35", side=-1, owner="rejected sell: the 4th did not close below the 3rd open"),
    dict(chart=4, day="2026-10-26", first="15:35", side=1, owner="rejected buy: the 4th did not close above the 3rd open"),
    dict(chart=5, day="2026-10-22", first=None, side=0, owner="rejected buy AND sell - 'How? Why!' (07:45-08:45)", window=("07:40", "08:45")),
    dict(chart="6a", day="2026-10-20", first="12:35", side=-1, owner="B+ sell (only the 4th engulfed); failed"),
    dict(chart="6b", day="2026-10-20", first="12:40", side=1, owner="A+ buy (2nd and 4th engulfed); won"),
]


def load():
    parts = [np.load(os.path.join(ROOT, "data", "EURUSD_M1_bid_2025.npz")), np.load(os.path.join(ROOT, "data", "holdout", "EURUSD_M1_bid_2026.npz"))]
    ts = np.concatenate([p["ts"] // 1000 for p in parts]); k = np.argsort(ts, kind="stable")
    o, h, l, c = (np.concatenate([p[x] for p in parts]).astype(float)[k] for x in ("o", "h", "l", "c")); ts = ts[k]
    g = ts // 300; st = np.flatnonzero(np.r_[True, g[1:] != g[:-1]]); en = np.r_[st[1:], len(ts)]
    return dict(t=g[st] * 300, o=o[st], h=np.maximum.reduceat(h, st), l=np.minimum.reduceat(l, st), c=c[en - 1])


def t_of(day, hhmm):
    return int(dt.datetime.fromisoformat(f"{day}T{hhmm}").replace(tzinfo=UTC1).timestamp())


def hm(t):
    return dt.datetime.fromtimestamp(int(t), UTC1).strftime("%H:%M")


def main():
    B = load(); E = scanner.ema(B["c"]); P = scanner.detect(B["o"], B["h"], B["l"], B["c"], E)
    pos = {int(t): i for i, t in enumerate(B["t"])}
    rows = []
    for ex in EXAMPLES:
        if ex["first"]:
            i1 = pos[t_of(ex["day"], ex["first"])]; i4 = i1 + 3
            m = (P["i4"] == i4) & (P["side"] == ex["side"])
            found = [scanner.GRADE[int(g)] for g in P["grade"][m]] or ["no four-flip pattern"]
            a, b = i1 - 1, i4 + 1
        else:
            a, b = pos[t_of(ex["day"], ex["window"][0])], pos[t_of(ex["day"], ex["window"][1])]
            m = (P["i4"] >= a) & (P["i4"] <= b)
            found = [f"{'SELL' if s < 0 else 'BUY'} {hm(B['t'][k - 3])}-{hm(B['t'][k])} {scanner.GRADE[int(g)]}" for k, s, g in
                     zip(P["i4"][m], P["side"][m], P["grade"][m])] or ["no four-flip pattern"]
        candles = [dict(time=hm(B["t"][j]), o=round(B["o"][j], 5), h=round(B["h"][j], 5), l=round(B["l"][j], 5), c=round(B["c"][j], 5),
                        ema=round(E[j], 5)) for j in range(a, b + 1)]
        rows.append(dict(**{k: v for k, v in ex.items() if k != "window"}, scanner=found, candles=candles))
        print(ex["chart"], ex["day"], ex["owner"], "->", found)
    os.makedirs(OUT, exist_ok=True)
    json.dump(rows, open(os.path.join(OUT, "replay.json"), "w"), indent=1)
    return rows


if __name__ == "__main__":
    main()


def trade(B, i4, side, entry, stop, cost, max_wait=6, until=None):
    """Owner's entry: limit at 50% of the 4th candle, live for max_wait candles; stop as given. M5 bars only (a replay
    illustration; the backtest uses minute bars). Returns fill time and which of 1R-4R were reached before the stop."""
    d = abs(entry - stop) + cost
    n = len(B["c"]); kf = -1
    for k in range(i4 + 1, min(i4 + 1 + max_wait, n)):
        if (side < 0 and B["h"][k] >= entry) or (side > 0 and B["l"][k] + cost <= entry):
            kf = k; break
    if kf < 0:
        return dict(filled=False, risk_pips=round(d * 1e4, 1))
    hit = {}
    for r in (1, 2, 3, 4):
        tp = entry - r * d if side < 0 else entry + r * d
        res = None
        for k in range(kf, min(kf + 200, n)):
            stop_hit = (B["h"][k] + cost >= stop) if side < 0 else (B["l"][k] <= stop)
            tgt_hit = (B["l"][k] + cost <= tp) if side < 0 else (B["h"][k] >= tp)
            if stop_hit and (k == kf or not tgt_hit):
                res = "stop"; break
            if tgt_hit and k > kf:
                res = "target"; break
        hit[f"{r}R"] = res
    return dict(filled=True, fill=hm(B["t"][kf]), risk_pips=round(d * 1e4, 1), cost_R=round(cost / d, 2), **hit)


if __name__ != "__main__" or True:
    pass
