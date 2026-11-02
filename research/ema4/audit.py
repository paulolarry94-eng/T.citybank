"""Audit: 10 random trades of the 4-flip pattern, drawn like the owner's charts, for the owner to check by eye.

    python3 research/ema4/audit.py      # writes research/results/ema4/audit/*.png and AUDIT.md

Owner's original rules: M5, entry limit at 50% of the 4th candle (live 3 candles), stop at the 4th candle's high/low, 2R,
A+ and B+, close daily. Drawn at random (seed 4): 10 of the 12 markets, then one random trade in each, from every trade the
scanner took in 2011-2022 (fills before 2023). Not chosen by result. Times UTC+1 (the owner's clock).
"""
import os, sys, datetime as dt
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import protocol as P       # noqa: E402
import scanner             # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "ema4_flip_v1.py"))
CFG = dict(tf="M5", entry="mid50", stop="c4", buffer=0.0, target=2, grade="AB")
OUT = os.path.join(ROOT, "research", "results", "ema4")
UTC1 = dt.timezone(dt.timedelta(hours=1))
UP, DOWN, EMA_C, INK, MUTED = "#2a78d6", "#4a4a47", "#eb6834", "#0b0b0b", "#8a8984"


def draw(M, B, E, i4, side, grade, tr, path, title):
    t = B["t"]; kx = int(np.searchsorted(t, tr[1], side="right")) - 1
    a, b = i4 - 14, min(max(kx, i4 + 3) + 5, len(t) - 1)
    idx = np.arange(a, b + 1)
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=130)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, color="#e4e3df", linewidth=0.5); ax.set_axisbelow(True)
    for n, i in enumerate(idx):
        o, h, l, c = B["o"][i], B["h"][i], B["l"][i], B["c"][i]; col = UP if c >= o else DOWN
        ax.plot([n, n], [l, h], color=col, linewidth=0.9, zorder=2)
        ax.add_patch(Rectangle((n - 0.32, min(o, c)), 0.64, max(abs(c - o), 1e-9), color=col, zorder=3, linewidth=0))
    ax.plot(range(len(idx)), E[idx], color=EMA_C, linewidth=1.3, label="EMA 10")
    span = B["h"][idx].max() - B["l"][idx].min()
    for m in range(4):
        n = i4 - 3 + m - a
        y = B["h"][i4 - 3 + m] + 0.06 * span if side < 0 else B["l"][i4 - 3 + m] - 0.06 * span
        ax.text(n, y, str(m + 1), ha="center", va="center", fontsize=8, bbox=dict(boxstyle="square,pad=0.15", fc="white", ec=INK, lw=0.8))
    nin = int(np.searchsorted(t, tr[0], side="right")) - 1 - a; nout = kx - a
    for y, col, lab, ls in ((tr[8], "#1baf7a" if side > 0 else "#2a78d6", f"entry {tr[8]:.5g}", "-"), (tr[9], "#e34948", f"stop {tr[9]:.5g}", "--"),
                            (tr[10], "#1baf7a", f"2R target {tr[10]:.5g}", "--")):
        ax.plot([i4 - a + 0.5, max(nout, i4 - a + 3) + 0.5], [y, y], color=col, linewidth=1.1, linestyle=ls)
        ax.text(max(nout, i4 - a + 3) + 0.6, y, " " + lab, fontsize=7, va="center", color=INK)
    ax.plot([nout], [tr[11]], marker="o", color=INK, markersize=5)
    ticks = [n for n, i in enumerate(idx) if (t[i] // 60) % 15 == 0]
    ax.set_xticks(ticks); ax.set_xticklabels([dt.datetime.fromtimestamp(int(t[idx[n]]), UTC1).strftime("%H:%M") for n in ticks], fontsize=8)
    ax.tick_params(labelsize=8, colors=INK); ax.ticklabel_format(axis="y", useOffset=False, style="plain")
    ax.set_title(title, fontsize=9, loc="left", color=INK); ax.legend(fontsize=7, frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(path, facecolor="white"); plt.close(fig)


def main():
    os.makedirs(os.path.join(OUT, "audit"), exist_ok=True)
    rng = np.random.default_rng(4)
    mk = sorted(rng.choice(S.MARKETS, size=10, replace=False))
    lines = ["# 10 random 4-flip trades (owner's original rules), for the owner to check", "", __doc__.split("\n\n")[1], "",
             "| # | Market | Day (UTC+1) | Grade | Side | Entry | Stop | Target | Exit | Result | Chart |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, sym in enumerate(mk, 1):
        M = P.market(sym, S); B = M.bars("M5"); E = scanner.ema(B["c"])
        D = S.detail(M, B, CFG, cut=P.core.CUT)
        Sx = S.select(S.setups(B, CFG, M), CFG)
        r = D[rng.integers(len(D))]; j = int(r[13]); i4 = int(Sx["i4"][j]); side = int(Sx["side"][j]); g = int(Sx["grade"][j])
        day = dt.datetime.fromtimestamp(int(B["t"][i4]), UTC1)
        res = f"{r[3]:+.2f}R ({S.REASON[int(r[12])]})"
        f = f"audit_{n:02d}_{sym}_{day:%Y-%m-%d}.png"
        draw(M, B, E, i4, side, g, r, os.path.join(OUT, "audit", f),
             f"{sym} M5 {day:%Y-%m-%d} (UTC+1)  {('SELL' if side < 0 else 'BUY')} {scanner.GRADE[g]}  4th candle {day:%H:%M}  ->  {res}")
        lines.append(f"| {n} | {sym} | {day:%Y-%m-%d %H:%M} | {scanner.GRADE[g]} | {'SELL' if side < 0 else 'BUY'} | {r[8]:.5g} | {r[9]:.5g} | "
                     f"{r[10]:.5g} | {dt.datetime.fromtimestamp(int(r[1]), UTC1):%H:%M} | {res} | `audit/{f}` |")
        print(lines[-1], flush=True)
    open(os.path.join(OUT, "AUDIT.md"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
