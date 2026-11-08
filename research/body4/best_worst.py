"""The 10 biggest winners and the 10 biggest losers of the owner's body-engulf range, v3 main settings (entry 50%, stop at
the range end, breakeven at 75% of the way, lookback on with dojis bullish, target 10R), 12 markets x M1-H4, 2011-22
(fills before 2023; the 2023-25 holdout stays closed). Chosen by R after costs and swaps alone, at most one per market and
day. Each chart: left, the setup on its own timeframe (lookback, candles 1-4, range, midpoint); right, the whole trade.

    python3 research/body4/best_worst.py  ->  research/results/body4/v3/best_worst/*.png + best_worst.json
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

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v3.py"))
OUT = os.path.join(ROOT, "research", "results", "body4", "v3", "best_worst")
MAIN = dict(entry=0.5, be=1, buffer=0.0, lookback=1, target=10)
UTC = dt.timezone.utc
REASON = {1: "stop (-1R)", 2: "target (+10R)", 3: "breakeven stop", 4: "Friday close", 5: "stop in the fill minute"}
DISPLAY = ["M1", "M5", "M15", "M30", "H1", "H4"]
MIN = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240}


def candles(ax, B, idx, hl=None):
    o, h, l, c = B["o"], B["h"], B["l"], B["c"]
    w = 0.64 if len(idx) < 120 else 0.8
    for x, i in enumerate(idx):
        col = "#2a78d6" if c[i] > o[i] else ("#4a4a47" if c[i] < o[i] else "#b4b2a9")
        ax.plot([x, x], [l[i], h[i]], color=col, linewidth=0.7, zorder=2)
        if c[i] == o[i]:
            ax.plot([x - w / 2, x + w / 2], [o[i], o[i]], color=col, linewidth=1.4, zorder=3)
        else:
            ax.add_patch(Rectangle((x - w / 2, min(o[i], c[i])), w, abs(c[i] - o[i]), color=col, zorder=3, lw=0))


def ticks(ax, B, idx, n=7):
    step = max(1, len(idx) // n)
    ax.set_xticks(range(0, len(idx), step))
    ax.set_xticklabels([dt.datetime.fromtimestamp(int(B["t"][i]), UTC).strftime("%a %d %H:%M") for i in idx[::step]], fontsize=6.5)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, color="#e4e3df", linewidth=0.5); ax.set_axisbelow(True)


def draw(M, tf, row, Sx, rank, kind, path):
    B = M.bars(tf); t = B["t"]
    j = int(row[8]); k = int(Sx["k"][j]); s = int(row[2])
    hi, lo = float(Sx["hi"][j]), float(Sx["lo"][j]); mid = (hi + lo) / 2
    entry, exitp, stop, tp, R0 = row[10], row[11], row[12], row[13], row[4]
    level = tp - s * 10 * R0; be = level + s * 0.75 * 10 * R0
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.6), dpi=120, gridspec_kw=dict(width_ratios=[1, 1.5]))
    # left: the setup
    idx = np.arange(max(0, k - 11), min(len(t), k + 16))
    candles(a1, B, idx); ticks(a1, B, idx, 6)
    a = idx[0]
    a1.add_patch(Rectangle((k - 3 - a - 0.45, lo), 3.9, hi - lo, fill=False, ec="#7a5af5", lw=1.1, ls="--", zorder=4))
    a1.add_patch(Rectangle((k - 8 - a - 0.45, B["l"][k - 8:k - 3].min()), 4.9, B["h"][k - 8:k - 3].max() - B["l"][k - 8:k - 3].min(),
                           fc="#7a5af5", alpha=0.08, lw=0))
    span = B["h"][idx].max() - B["l"][idx].min()
    for m in range(4):
        i = k - 3 + m
        y = B["h"][i] + 0.05 * span if s < 0 else B["l"][i] - 0.05 * span
        a1.text(i - a, y, str(m + 1), ha="center", va="center", fontsize=7, bbox=dict(boxstyle="square,pad=0.12", fc="white", ec="#0b0b0b", lw=0.7))
    a1.text(k - 6 - a, B["h"][k - 8:k - 3].max() + 0.03 * span, f"lookback {int(Sx['lookback'][j])}/5", fontsize=6.5, color="#7a5af5", ha="center")
    a1.axhline(mid, color="#0b0b0b", lw=0.8, ls=":")
    a1.set_title(f"Setup ({tf}): {'SELL' if s < 0 else 'BUY'}, candle 4 closes {dt.datetime.fromtimestamp(int(t[k]) + MIN[tf] * 60, UTC):%Y-%m-%d %H:%M} UTC",
                 fontsize=8, loc="left")
    # right: the whole trade on a timeframe where it fits in about 160 bars
    t0, t1 = int(t[k - 3]), int(row[1])
    dtf = next((d for d in DISPLAY[DISPLAY.index(tf):] if (t1 - t0) / (MIN[d] * 60) <= 160), "H4")
    D = M.bars(dtf); tt = D["t"]
    i0 = max(0, int(np.searchsorted(tt, t0, side="right")) - 1 - 4)
    i1 = min(len(tt), int(np.searchsorted(tt, t1, side="right")) + 6)
    idx2 = np.arange(i0, i1)
    candles(a2, D, idx2); ticks(a2, D, idx2, 8)
    xi = int(np.searchsorted(tt, int(row[0]), side="right")) - 1 - i0
    xo = int(np.searchsorted(tt, int(row[1]), side="right")) - 1 - i0
    for y, lab, col, ls in ((tp, "target 10R", "#1baa55", "-"), (be, "breakeven trigger (75% of the way)", "#eb6834", ":"),
                            (entry, "entry (50% of the range)", "#0b0b0b", "-"), (stop, "stop", "#e34948", "-")):
        a2.plot([xi, len(idx2) - 1], [y, y], color=col, lw=1.0, ls=ls)
        a2.text(len(idx2) - 0.5, y, " " + lab, fontsize=6.5, color=col, va="center")
    a2.plot(xi, entry, "o", color="#0b0b0b", ms=5, zorder=6); a2.plot(xo, exitp, "x", color="#0b0b0b", ms=8, zorder=6)
    ys = [tp, stop, D["h"][idx2].max(), D["l"][idx2].min()]
    a2.set_ylim(min(ys) - 0.04 * (max(ys) - min(ys)), max(ys) + 0.04 * (max(ys) - min(ys)))
    a2.set_xlim(-1, len(idx2) + 14)
    a2.set_title(f"Whole trade ({dtf} candles): {REASON[int(row[9])]}, {row[3]:+.2f}R after costs and swaps "
                 f"(costs {row[5]:.2f}R, swaps {row[7]:.2f}R over {int(row[6])} nights)", fontsize=8, loc="left")
    fig.suptitle(f"{kind} #{rank}: {M.sym} {tf}  {'SELL' if s < 0 else 'BUY'}  fill {dt.datetime.fromtimestamp(int(row[0]), UTC):%Y-%m-%d %H:%M} UTC  "
                 f"-> exit {dt.datetime.fromtimestamp(int(row[1]), UTC):%Y-%m-%d %H:%M}   1R = {R0:.5g}", fontsize=9.5, x=0.01, ha="left")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for sym in S.MARKETS:
        M = P.market(sym, S)
        for tf in S.TIMEFRAMES:
            D = S.detail(M, M.bars(tf), dict(MAIN, tf=tf), cut=P.core.CUT)
            for r in D:
                rows.append((float(r[3]), sym, tf, r.copy()))
        print(sym, len(rows), flush=True)
    R = np.array([x[0] for x in rows])
    summary = dict(trades=len(rows), mean_R=round(float(R.mean()), 4), share_target=round(float(np.mean([x[3][9] == 2 for x in rows])), 4),
                   share_stop=round(float(np.mean([x[3][9] in (1, 5) for x in rows])), 4),
                   share_breakeven=round(float(np.mean([x[3][9] == 3 for x in rows])), 4),
                   share_friday=round(float(np.mean([x[3][9] == 4 for x in rows])), 4))
    picks = {}
    for kind, order in (("Biggest winner", sorted(rows, key=lambda x: -x[0])), ("Biggest loser", sorted(rows, key=lambda x: x[0]))):
        seen, out = set(), []
        for x in order:
            day = (x[1], dt.datetime.fromtimestamp(int(x[3][0]), UTC).date())
            if day in seen:
                continue
            seen.add(day); out.append(x)
            if len(out) == 10:
                break
        picks[kind] = out
    meta = dict(settings=MAIN, summary=summary, picks={})
    cache = {}
    for kind, xs in picks.items():
        for n, (r_, sym, tf, row) in enumerate(xs, 1):
            M = cache.setdefault(sym, P.market(sym, S))
            Sx = S.setups(M.bars(tf), dict(sample="flow"), M)
            path = os.path.join(OUT, f"{'win' if 'winner' in kind else 'loss'}_{n:02d}_{sym}_{tf}.png")
            draw(M, tf, row, Sx, n, kind, path)
            meta["picks"].setdefault(kind, []).append(dict(market=sym, tf=tf, R=round(r_, 3), fill=dt.datetime.fromtimestamp(int(row[0]), UTC).isoformat(),
                                                            side="buy" if row[2] > 0 else "sell", reason=REASON[int(row[9])],
                                                            cost_R=round(float(row[5]), 3), swap_R=round(float(row[7]), 3), nights=int(row[6]), risk=float(row[4])))
            print(kind, n, sym, tf, round(r_, 2), REASON[int(row[9])], flush=True)
    json.dump(meta, open(os.path.join(OUT, "best_worst.json"), "w"), indent=1, default=float)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
