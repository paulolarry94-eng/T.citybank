"""10 examples of the v6 rules (owner, 2026-11-09: "give me the examples to be sure you understand"), drawn with the lab's
own code (research/truth/strategies/body4_range_v6.py: setups, safe window, the new body and lookback rules, M1 engine).
Fixed before drawing, random with a fixed seed, one market at most once per group:
  A  7 trades of the main configuration: candles 2 and 4 at least 60% body, the 2 candles before candle 1 both in the
     trade's direction, target 5R, stop at the range end, no breakeven, safe window
  B  3 setups rejected ONLY by a new rule (everything else passes): candle 2 body below 60%; candle 4 body below 60%;
     lookback 1 of 2
    python3 research/body4/examples_v6.py  ->  research/results/body4/v6/examples/*.png + examples.json
"""
import os, sys, json, datetime as dt
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P   # noqa: E402
from best_worst import candles   # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v6.py"))
OUT = os.path.join(ROOT, "research", "results", "body4", "v6", "examples")
UTC = dt.timezone.utc
SEED = 20261109
MAIN = dict(body60=1, lb2=1, target=5)
MIN = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240}
DISPLAY = ["M1", "M5", "M15", "M30", "H1", "H4"]
DEC = {"XAUUSD": 2, "XAGUSD": 3, "EURUSD": 5, "GBPUSD": 5, "USDJPY": 3, "EURGBP": 5, "WTI": 3, "US500": 1, "NAS100": 1,
       "GER40": 1, "UK100": 1, "JP225": 0}
REASON = {1: "stop", 2: "target", 3: "breakeven stop", 4: "time close at 20:30 UTC", 5: "stop in the fill minute"}


def fmt(sym, x):
    return f"{x:,.{DEC.get(sym, 5)}f}"


def ticks(ax, B, idx, n=6):
    step = max(1, len(idx) // n)
    ax.set_xticks(range(0, len(idx), step))
    ax.set_xticklabels([dt.datetime.fromtimestamp(int(B["t"][i]), UTC).strftime("%a %H:%M") for i in idx[::step]], fontsize=6.5)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, color="#e4e3df", linewidth=0.5); ax.set_axisbelow(True)


def setup_panel(ax, B, X, j, title):
    k = int(X["k"][j]); s = int(X["side"][j]); hi, lo = float(X["hi"][j]), float(X["lo"][j]); mid = (hi + lo) / 2
    t = B["t"]
    idx = np.arange(max(0, k - 9), min(len(t), k + 6))
    candles(ax, B, idx); ticks(ax, B, idx, 6)
    a = idx[0]
    ax.add_patch(Rectangle((k - 3 - a - 0.45, lo), 3.9, hi - lo, fill=False, ec="#7a5af5", lw=1.1, ls="--", zorder=4))
    lh, ll = B["h"][k - 5:k - 3].max(), B["l"][k - 5:k - 3].min()
    ax.add_patch(Rectangle((k - 5 - a - 0.45, ll), 1.9, lh - ll, fc="#eb6834", alpha=0.12, lw=0))
    span = B["h"][idx].max() - B["l"][idx].min()
    ys = []
    for m in range(4):
        i = k - 3 + m
        y = B["h"][i] + 0.06 * span if s < 0 else B["l"][i] - 0.06 * span
        ys.append(y)
        ax.text(i - a, y, str(m + 1), ha="center", va="center", fontsize=7, bbox=dict(boxstyle="square,pad=0.12", fc="white", ec="#0b0b0b", lw=0.7))
    for m, key in ((2, "body2"), (4, "body4")):                       # body share of the engulfing candles
        i = k - 4 + m; y = ys[m - 1] + (0.06 * span if s < 0 else -0.06 * span)
        ys.append(y)
        ok = X[key][j] >= S.BODY_MIN
        ax.text(i - a, y, f"body {X[key][j]:.0%}", ha="center", va="center", fontsize=6.5, color="#1baa55" if ok else "#e34948")
    word = "bullish" if s > 0 else "bearish"
    ax.text(k - 4.5 - a, lh + 0.04 * span, f"lookback {int(X['lookback2'][j])}/2 {word}", fontsize=6.5, color="#eb6834", ha="center")
    ax.set_ylim(min(B["l"][idx].min(), min(ys)) - 0.05 * span, max(B["h"][idx].max(), max(ys), lh + 0.08 * span) + 0.05 * span)
    ax.axhline(mid, color="#0b0b0b", lw=0.8, ls=":")
    ax.text(len(idx) - 0.6, mid, " midpoint", fontsize=6.5, va="center")
    ax.set_title(title, fontsize=8, loc="left")


def trade_panel(ax, M, tf, row, T):
    s = int(row[2]); R0 = row[4]
    tp, stop = row[13], row[12]; level = tp - s * T * R0
    t0, t1 = int(row[0]), int(row[1])
    dtf = next((d for d in DISPLAY[DISPLAY.index(tf):] if (t1 - t0) / (MIN[d] * 60) <= 120), "H4")
    D = M.bars(dtf); tt = D["t"]
    i0 = max(0, int(np.searchsorted(tt, t0, side="right")) - 1 - 12)
    i1 = min(len(tt), int(np.searchsorted(tt, t1, side="right")) + 6)
    idx = np.arange(i0, i1)
    candles(ax, D, idx); ticks(ax, D, idx, 5)
    xi = int(np.searchsorted(tt, t0, side="right")) - 1 - i0
    xo = int(np.searchsorted(tt, t1, side="right")) - 1 - i0
    lines = [(tp, f"target {T}R", "#1baa55"), (level, "entry: limit at 50% of the range", "#0b0b0b"), (stop, "stop (range end)", "#e34948")]
    lo_ = min(D["l"][idx].min(), stop, level); hi_ = max(D["h"][idx].max(), stop, level)
    pad = 0.08 * (hi_ - lo_); ylo, yhi = lo_ - pad, hi_ + pad
    for y, lab, col in lines:
        if ylo <= y <= yhi:
            ax.plot([max(xi - 12, 0), len(idx) - 1], [y, y], color=col, lw=1.0)
            ax.text(len(idx) - 0.5, y, " " + lab, fontsize=6.5, color=col, va="center")
        else:
            up = y > yhi
            ax.text(len(idx) - 0.5, yhi if up else ylo, f" {lab} at {fmt(M.sym, y)} ({'above' if up else 'below'}, off the chart)",
                    fontsize=6.5, color=col, va="top" if up else "bottom")
    ax.plot(xi, row[10], "o", color="#0b0b0b", ms=5, zorder=6); ax.plot(xo, row[11], "x", color="#0b0b0b", ms=8, zorder=6)
    ax.set_ylim(ylo, yhi); ax.set_xlim(-1, len(idx) + 0.45 * len(idx) + 6)
    ax.set_title(f"The trade ({dtf} candles; dot = fill, cross = exit): {REASON[int(row[9])]}, {row[3]:+.2f}R after costs "
                 f"(costs {row[5]:.2f}R; flat at 20:30 UTC, no swaps)", fontsize=8, loc="left")


def checks_text(M, B, X, j, row=None, T=5, verdict=None):
    sym = M.sym; k = int(X["k"][j]); s = int(X["side"][j]); o, c = B["o"], B["c"]
    hi, lo = float(X["hi"][j]), float(X["lo"][j]); mid = (hi + lo) / 2
    L = []
    for m, key in ((2, "body2"), (4, "body4")):
        i = k - 4 + m; pv = i - 1
        so = (o[i] >= c[pv]) if s < 0 else (o[i] <= c[pv]); be = (c[i] < o[pv]) if s < 0 else (c[i] > o[pv])
        L.append(f"Candle {m}: body engulfs candle {m - 1} (opens {fmt(sym, o[i])} {'at/above' if s < 0 else 'at/below'} its close "
                 f"{fmt(sym, c[pv])}: {'yes' if so else 'NO'}; closes {fmt(sym, c[i])} {'below' if s < 0 else 'above'} its open "
                 f"{fmt(sym, o[pv])}: {'yes' if be else 'NO'}).  Body {X[key][j]:.0%} of its high-low: "
                 f"{'60% or more -> pass' if X[key][j] >= S.BODY_MIN else 'BELOW 60% -> fails the new body rule'}")
    word = "bullish (dojis count as bullish)" if s > 0 else "bearish"
    n2 = int(X["lookback2"][j])
    L.append(f"Lookback: the 2 candles before candle 1 must both be {word}: {n2} of 2 -> {'pass' if n2 >= 2 else 'FAILS the new lookback rule'}.")
    L.append(f"Intent: candle 4 closes {fmt(sym, c[k])}, {'below' if s < 0 else 'above'} the midpoint {fmt(sym, mid)} -> take it.   "
             f"Safe window: candle 4 closed {dt.datetime.fromtimestamp(int(X['t_conf'][j]), UTC):%a %Y-%m-%d %H:%M} UTC (07:00-19:00, "
             f"no US news day) -> pass.")
    if row is not None:
        R0 = row[4]
        L.append(f"Orders: {'SELL' if s < 0 else 'BUY'} limit at 50% {fmt(sym, row[13] - s * T * R0)}, stop at the range end "
                 f"{fmt(sym, row[12])}, 1R = {fmt(sym, R0)}, target {T}R {fmt(sym, row[13])}, no breakeven.  Filled "
                 f"{dt.datetime.fromtimestamp(int(row[0]), UTC):%H:%M} at {fmt(sym, row[10])}; exit {dt.datetime.fromtimestamp(int(row[1]), UTC):%H:%M} "
                 f"at {fmt(sym, row[11])} ({REASON[int(row[9])]}): {row[3]:+.2f}R after costs.")
    if verdict:
        L.append(verdict)
    return "\n".join(L)


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(SEED)
    cache, meta, n = {}, [], 0
    pool, rej = [], {"candle 2 body below 60%": [], "candle 4 body below 60%": [], "lookback 1 of 2": []}
    for sym in S.MARKETS:
        M = cache.setdefault(sym, P.market(sym, S))
        for tf in S.TIMEFRAMES:
            B = M.bars(tf); X = S.setups(B, MAIN, M)
            D = S.detail(M, B, MAIN)
            pool += [(sym, tf, r.copy()) for r in D]
            mid = (X["hi"] + X["lo"]) / 2
            base = (S.safe_mask(X) == 1) & np.where(X["side"] > 0, X["c4"] > mid, X["c4"] < mid)
            b2, b4, l2 = X["body2"] >= S.BODY_MIN, X["body4"] >= S.BODY_MIN, X["lookback2"]
            for name, m in (("candle 2 body below 60%", base & ~b2 & b4 & (l2 == 2)), ("candle 4 body below 60%", base & b2 & ~b4 & (l2 == 2)),
                            ("lookback 1 of 2", base & b2 & b4 & (l2 == 1))):
                rej[name] += [(sym, tf, int(j)) for j in np.flatnonzero(m)]
    print("trades", len(pool), {k: len(v) for k, v in rej.items()}, flush=True)
    used = set(); picks = []
    for i in rng.permutation(len(pool)):
        sym, tf, r = pool[i]
        if sym in used:
            continue
        used.add(sym); picks.append((sym, tf, r))
        if len(picks) == 7:
            break
    for sym, tf, r in picks:
        n += 1
        M = cache[sym]; B = M.bars(tf); X = S.setups(B, MAIN, M); j = int(r[8])
        fig = plt.figure(figsize=(15, 6.6), dpi=120)
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.3], width_ratios=[1, 1.5])
        a1, a2 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]); at = fig.add_subplot(gs[1, :]); at.axis("off")
        side = "SELL" if r[2] < 0 else "BUY"
        setup_panel(a1, B, X, j, f"Setup ({tf}): {side}, candle 4 closes {dt.datetime.fromtimestamp(int(X['t_conf'][j]), UTC):%Y-%m-%d %H:%M} UTC")
        trade_panel(a2, M, tf, r, MAIN["target"])
        at.text(0, 1, checks_text(M, B, X, j, r, MAIN["target"]), fontsize=7.3, va="top", family="DejaVu Sans Mono", transform=at.transAxes)
        fig.suptitle(f"Example {n} (traded): {sym} {tf} {side}   |   setting: candles 2 and 4 at least 60% body, 2-candle lookback, "
                     f"target 5R, stop at the range end, no breakeven, safe window", fontsize=9.5, x=0.01, ha="left")
        path = os.path.join(OUT, f"example_{n:02d}_traded_{sym}_{tf}.png")
        fig.tight_layout(); fig.savefig(path); plt.close(fig)
        meta.append(dict(n=n, kind="traded", market=sym, tf=tf, side=side.lower(), fill=dt.datetime.fromtimestamp(int(r[0]), UTC).isoformat(),
                         reason=REASON[int(r[9])], R=round(float(r[3]), 3), file=os.path.basename(path)))
        print(meta[-1], flush=True)
    for name, lst in rej.items():
        sym, tf, j = lst[int(rng.integers(len(lst)))]
        n += 1
        M = cache[sym]; B = M.bars(tf); X = S.setups(B, MAIN, M)
        side = "SELL" if X["side"][j] < 0 else "BUY"
        fig = plt.figure(figsize=(15, 6.2), dpi=120)
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 0.36])
        a1 = fig.add_subplot(gs[0]); at = fig.add_subplot(gs[1]); at.axis("off")
        setup_panel(a1, B, X, j, f"Setup ({tf}): {side}, candle 4 closes {dt.datetime.fromtimestamp(int(X['t_conf'][j]), UTC):%Y-%m-%d %H:%M} UTC")
        at.text(0, 1, checks_text(M, B, X, j, verdict=f"-> NOT TRADED: {name}. Everything else passes."), fontsize=7.3, va="top",
                family="DejaVu Sans Mono", transform=at.transAxes)
        fig.suptitle(f"Example {n} (rejected by a new rule: {name}): {sym} {tf} {side}", fontsize=9.5, x=0.01, ha="left")
        path = os.path.join(OUT, f"example_{n:02d}_rejected_{sym}_{tf}.png")
        fig.tight_layout(); fig.savefig(path); plt.close(fig)
        meta.append(dict(n=n, kind="rejected", why=name, market=sym, tf=tf, side=side.lower(),
                         candle4_close=dt.datetime.fromtimestamp(int(X["t_conf"][j]), UTC).isoformat(), file=os.path.basename(path)))
        print(meta[-1], flush=True)
    json.dump(dict(seed=SEED, main=MAIN, examples=meta), open(os.path.join(OUT, "examples.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
