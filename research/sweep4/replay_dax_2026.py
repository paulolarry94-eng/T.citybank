"""Replay of the owner's DAX screenshot (FXCM GER30 M5, 2026) in our GER40 data (HistData, 2026-11-06).
    python3 research/sweep4/replay_dax_2026.py -> research/results/sweep4/replay/GER40_20261106.png
"""
import os, sys, datetime as dt
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research")); sys.path.insert(0, HERE)
import engine as EN, pivots as PV   # noqa: E402

d = np.load(os.path.join(ROOT, "data", "holdout", "GER40_M1_bid_2026.npz")); ts = d["ts"] // 1000
t, o, h, l, c, _ = EN.resample(ts, d["o"], d["h"], d["l"], d["c"], 5)
ph, pl = PV.pivots(h, l, 10, 10)
a = int(np.searchsorted(t, int(dt.datetime(2026, 11, 6, 14, 0, tzinfo=dt.timezone.utc).timestamp()))); b = len(t)
fig, ax = plt.subplots(figsize=(13, 6.5), dpi=110); fig.patch.set_facecolor("#d6d9e0"); ax.set_facecolor("#d6d9e0")
for x in range(a, b):
    col = "#5b7bd5" if c[x] >= o[x] else "#4a4a52"
    ax.plot([x, x], [l[x], h[x]], color=col, lw=0.9)
    ax.add_patch(Rectangle((x - 0.32, min(o[x], c[x])), 0.64, max(abs(c[x] - o[x]), 0.3), color=col))
for x in range(a, b):
    if ph[x]: ax.text(x, h[x] + 3, f"{h[x]:.2f}", ha="center", va="bottom", fontsize=8)
    if pl[x]: ax.text(x, l[x] - 3, f"{l[x]:.2f}", ha="center", va="top", fontsize=8)
k1 = int(np.searchsorted(t, int(dt.datetime(2026, 11, 6, 19, 50, tzinfo=dt.timezone.utc).timestamp())))
for n in range(4):
    ax.text(k1 + n, l[k1:k1 + 4].min() - 14, str(n + 1), ha="center", fontsize=8, fontweight="bold", color="#b00")
sw = [x for x in range(a, k1) if pl[x] and abs(l[x] - 25679.1) < 0.6]
if sw: ax.plot([sw[0], k1], [l[sw[0]]] * 2, ls=":", color="#222"); ax.text(sw[0], l[sw[0]] + 1, " swept pivot low", fontsize=8)
hi, lo = h[k1 + 3], l[k1:k1 + 4].min(); entry = hi - 0.6 * (hi - lo)
ax.add_patch(Rectangle((k1 - 0.5, lo), 4, hi - lo, fc="#7f9cf5", alpha=0.35, ec="none"))
ax.axhline(entry, color="#2a6", lw=0.8, ls="--"); ax.text(a + 1, entry + 1, f"60% entry {entry:.1f} (your chart 25684.74)", ha="left", va="bottom", fontsize=8)
ax.axhline(lo, color="#c33", lw=0.8); ax.text(a + 1, lo - 1, f"stop {lo:.1f} (your chart 25668.27)", ha="left", va="top", fontsize=8)
note = ("Our feed (HistData): candle 2 opened 0.5 points above candle 1's close -> not a strict body engulf; candle 4 body 56% "
        "(< 60%).\nData ends Friday 20:58 UTC, before your chart's rally to 25,854. FXCM prices are about 4 points above HistData here.")
ax.text(0.01, 0.02, note, transform=ax.transAxes, fontsize=8, color="#333")
tk = list(range(a, b, 6)); ax.set_xticks(tk); ax.set_xticklabels([dt.datetime.utcfromtimestamp(int(t[x])).strftime("%H:%M") for x in tk], fontsize=8)
ax.yaxis.tick_right(); ax.set_xlim(a - 1, b + 1)
ax.set_title("GER40 M5, Friday 6 Nov 2026 (UTC), Pivots HL 10/10: your DAX screenshot in our data", loc="left", fontsize=10)
out = os.path.join(ROOT, "research", "results", "sweep4", "replay"); os.makedirs(out, exist_ok=True)
fig.tight_layout(); fig.savefig(os.path.join(out, "GER40_20261106.png"))
print("saved")
