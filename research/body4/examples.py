"""Five examples of the owner's body-engulf 4-candle pattern, picked at RANDOM (fixed seed, not chosen by outcome) from
XAUUSD and EURUSD M5, 2019-2022, to confirm the rule before any backtest.
    python3 research/body4/examples.py   ->  research/results/body4/examples/*.png
"""
import os, sys, datetime as dt
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "research"))
import scanner as SC   # noqa: E402
import engine as EN    # noqa: E402

OUT = os.path.join(ROOT, "research", "results", "body4", "examples")


def bars(sym):
    ts, o, h, l, c = EN.load_m1(sym, 2019, 2022)
    bt, bo, bh, bl, bc, _ = EN.resample(ts, o, h, l, c, 5)
    return bt, bo, bh, bl, bc


def draw(sym, B, r, out, n):
    t, o, h, l, c = B
    k, side, hi, lo, mid, stop, risk = r
    res = SC.follow(o, h, l, c, k, side, mid, stop, risk)
    end = res["exit"] if res["exit"] is not None else k + 20
    idx = np.arange(k - 10, min(len(c), max(end, k + 8) + 6))
    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=130)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, color="#e4e3df", linewidth=0.5); ax.set_axisbelow(True)
    for x, i in enumerate(idx):
        col = "#2a78d6" if c[i] >= o[i] else "#4a4a47"
        ax.plot([x, x], [l[i], h[i]], color=col, linewidth=0.9, zorder=2)
        ax.add_patch(Rectangle((x - 0.32, min(o[i], c[i])), 0.64, max(abs(c[i] - o[i]), 1e-9), color=col, zorder=3, lw=0))
    a = idx[0]; span = h[idx].max() - l[idx].min()
    for m in range(4):
        i = k - 3 + m
        y = h[i] + 0.05 * span if side < 0 else l[i] - 0.05 * span
        ax.text(i - a, y, str(m + 1), ha="center", va="center", fontsize=8, bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="#0b0b0b", lw=0.8))
    x0, x1 = k - 3 - a - 0.45, len(idx) - 1
    ax.add_patch(Rectangle((x0, lo), k - a + 0.45 - x0, hi - lo, fill=False, ec="#7a5af5", lw=1.0, ls="--"))
    for y, lab, col, ls in ((mid, "entry: range midpoint", "#0b0b0b", "-"), (stop, "stop: far end of range (-1R)", "#e34948", "-"),
                            (res["be"], "+2R: stop to breakeven", "#eb6834", ":"), (res["tp"], "target +4R", "#1baa55", "-")):
        ax.plot([k - a + 0.5, x1], [y, y], color=col, lw=1.1, ls=ls); ax.text(x1 + 0.2, y, " " + lab, fontsize=7, va="center", color=col)
    if res["fill"] is not None:
        ax.plot(res["fill"] - a, mid, marker="o", color="#0b0b0b", ms=5, zorder=5)
    if res["exit"] is not None and res["fill"] is not None:
        ax.plot(res["exit"] - a, res["tp"] if "target" in res["result"] else (mid if "breakeven" in res["result"] else stop),
                marker="x", color="#0b0b0b", ms=7, zorder=5)
    lo_y = min(l[idx].min(), res["tp"], stop); hi_y = max(h[idx].max(), res["tp"], stop)
    ax.set_ylim(lo_y - 0.04 * (hi_y - lo_y), hi_y + 0.04 * (hi_y - lo_y))
    step = max(1, len(idx) // 10)
    ax.set_xticks(range(0, len(idx), step))
    ax.set_xticklabels([dt.datetime.fromtimestamp(int(t[i]), dt.timezone.utc).strftime("%H:%M") for i in idx[::step]], fontsize=7)
    ax.set_xlim(-1, len(idx) + 7)
    day = dt.datetime.fromtimestamp(int(t[k]), dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ax.set_title(f"Example {n}: {sym} M5 {'SELL' if side < 0 else 'BUY'} - 4th candle closes {day} - outcome: {res['result']}", fontsize=9, loc="left")
    fig.tight_layout(); fig.savefig(out); plt.close(fig)
    return res


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(20261107)
    picks = [("XAUUSD", 3), ("EURUSD", 2)]
    n = 0
    for sym, m in picks:
        B = bars(sym); rows = SC.detect(*B[1:])
        print(sym, "patterns 2019-22:", len(rows), "buys", sum(r[1] > 0 for r in rows), "sells", sum(r[1] < 0 for r in rows))
        for j in sorted(rng.choice(len(rows), m, replace=False)):
            n += 1
            res = draw(sym, B, rows[j], os.path.join(OUT, f"example_{n}_{sym}.png"), n)
            print(n, sym, rows[j][1], res["result"])
