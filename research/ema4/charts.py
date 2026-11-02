"""Chart printer for the 4-flip EMA pattern: M5 candles, the 10 EMA, every pattern numbered 1-4, entry (50% of the 4th
candle) and stop (beyond the 4th candle). Times UTC+1 (Lagos), as on the owner's TradingView charts.

    import charts; charts.window(B, E, P, t0, t1, path, title)
"""
import datetime as dt
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

UP, DOWN, EMA_C, INK, MUTED, GRID = "#2a78d6", "#4a4a47", "#eb6834", "#0b0b0b", "#8a8984", "#e4e3df"
GRADE_C = {2: "#1baf7a", 1: "#2a78d6", 0: "#e34948"}
UTC1 = dt.timezone(dt.timedelta(hours=1))


def window(B, E, P, t0, t1, path, title, note=""):
    idx = np.flatnonzero((B["t"] >= t0) & (B["t"] <= t1))
    x = {int(i): n for n, i in enumerate(idx)}
    fig, ax = plt.subplots(figsize=(10, 5.4), dpi=130)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
    for i in idx:
        n = x[int(i)]; o, h, l, c = B["o"][i], B["h"][i], B["l"][i], B["c"][i]
        col = UP if c >= o else DOWN
        ax.plot([n, n], [l, h], color=col, linewidth=0.9, zorder=2)
        ax.add_patch(Rectangle((n - 0.32, min(o, c)), 0.64, max(abs(c - o), 1e-6), color=col, zorder=3, linewidth=0))
    ax.plot([x[int(i)] for i in idx], E[idx], color=EMA_C, linewidth=1.3, label="EMA 10")
    span = B["h"][idx].max() - B["l"][idx].min()
    lines = []
    for k, (i4, s, g) in enumerate(zip(P["i4"], P["side"], P["grade"])):
        if int(i4) not in x or int(i4) - 3 not in x:
            continue
        col = GRADE_C[int(g)]
        for m in range(4):
            j = int(i4) - 3 + m; n = x[j]
            y = B["h"][j] + span * (0.05 + 0.06 * (k % 2)) if s < 0 else B["l"][j] - span * (0.07 + 0.06 * (k % 2))
            ax.text(n, y, str(m + 1), ha="center", va="center", fontsize=8, color=col,
                    bbox=dict(boxstyle="square,pad=0.15", fc="white", ec=col, lw=0.8))
        lab = f"{'SELL' if s < 0 else 'BUY'} {('A+', 'B+')[2 - int(g)] if g else 'rejected'}"
        lines.append(lab)
        if g:
            n4 = x[int(i4)]; ent = P["entry50"][k]; stp = P["hi4"][k] if s < 0 else P["lo4"][k]
            ax.plot([n4, n4 + 6], [ent, ent], color=col, linewidth=1.2); ax.text(n4 + 6.1, ent, f" {lab} entry 50%", fontsize=7, va="center", color=INK)
            ax.plot([n4, n4 + 6], [stp, stp], color="#e34948", linewidth=1.0, linestyle="--"); ax.text(n4 + 6.1, stp, " stop", fontsize=7, va="center", color=INK)
    ticks = [n for n, i in enumerate(idx) if (B["t"][i] // 60) % 15 == 0]
    ax.set_xticks(ticks); ax.set_xticklabels([dt.datetime.fromtimestamp(int(B["t"][idx[n]]), UTC1).strftime("%H:%M") for n in ticks], fontsize=8)
    ax.tick_params(labelsize=8, colors=INK)
    ax.set_title(title + ("  |  scanner: " + ", ".join(lines) if lines else "  |  scanner: no four-flip pattern"), fontsize=9, loc="left", color=INK)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    if note:
        fig.text(0.01, 0.01, note, fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(path, facecolor="white"); plt.close(fig)
