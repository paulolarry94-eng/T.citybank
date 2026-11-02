"""Chart printer for the owner's 3:30 setups: the M30 anchor and the M5 entry, drawn like the owner's TradingView charts.

    import charts; charts.day_chart(M, date, p, S, "out.png")

Top panel: M30 candles with the 10 EMA and the anchor candle's range (box). Bottom panel: M5 candles with the 10 EMA, the
range, the reference candle, and the trade (entry, stop, target, exit) if there is one. Times in Nigerian time (WAT).
"""
import datetime as dt
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

UP, DOWN, EMA_C, RANGE_C, ENTRY_C, STOP_C, TGT_C, INK, MUTED, GRID = (
    "#2a78d6", "#4a4a47", "#eb6834", "#e34948", "#1baf7a", "#e34948", "#1baf7a", "#0b0b0b", "#8a8984", "#e4e3df")


def _candles(ax, t, o, h, l, c, width):
    for ti, oi, hi, li, ci in zip(t, o, h, l, c):
        col = UP if ci >= oi else DOWN
        ax.plot([ti, ti], [li, hi], color=col, linewidth=0.8, zorder=2)
        ax.add_patch(Rectangle((ti - width / 2, min(oi, ci)), width, max(abs(ci - oi), 1e-12), color=col, zorder=3, linewidth=0))


def _style(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=7.5)
    ax.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)


def day_chart(M, D, p, S, path, note=""):
    B = M.bars("M5")
    t5 = np.asarray(B["t"], np.int64)
    ta, tx = S.anchor_times(D, p["anchor"], p.get("sample", "flow"))
    g = t5 // 1800
    st = np.flatnonzero(np.r_[True, g[1:] != g[:-1]]); en = np.r_[st[1:], len(t5)]
    m30_t = g[st] * 1800
    m30 = dict(o=B["o"][st], h=np.maximum.reduceat(B["h"], st), l=np.minimum.reduceat(B["l"], st), c=B["c"][en - 1])
    e30 = S.ema(m30["c"]); e5 = S.ema(B["c"])
    tz = S.WAT
    to_x = lambda t: (np.asarray(t, np.int64) - ta) / 3600.0                # hours from the anchor
    lbl = lambda x: dt.datetime.fromtimestamp(int(ta + x * 3600), tz).strftime("%H:%M")
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 7.2), dpi=130, gridspec_kw=dict(height_ratios=[1, 1.25]))
    for ax in (a1, a2):
        _style(ax)
    # M30 panel: 6 hours before the anchor to the time exit
    m = (m30_t >= ta - 6 * 3600) & (m30_t <= tx)
    x30 = to_x(m30_t[m])
    _candles(a1, x30 + 0.25, m30["o"][m], m30["h"][m], m30["l"][m], m30["c"][m], 0.35)
    a1.plot(x30 + 0.5, e30[m], color=EMA_C, linewidth=1.4, label="EMA 10 (M30)")
    ia = np.flatnonzero(m30_t == ta)
    S._CACHE.clear()
    st_ = S.setups(B, p, M)
    k = [i for i, dd in enumerate(st_["date"]) if dd == D.toordinal()]
    if len(ia):
        i = ia[0]
        H, L = m30["h"][i], m30["l"][i]
        a1.add_patch(Rectangle((0, L), to_x(tx), H - L, fill=False, edgecolor=RANGE_C, linewidth=1))
        a1.set_title(f"{M.sym} {D} - M30, anchor {lbl(0)} WAT (box = the anchor candle's range)", fontsize=9, loc="left", color=INK)
    a1.legend(fontsize=7, frameon=False, loc="upper left")
    # M5 panel: from the anchor to the time exit
    m5 = (t5 >= ta - 3600) & (t5 <= tx)
    x5 = to_x(t5[m5])
    _candles(a2, x5 + 5 / 120, B["o"][m5], B["h"][m5], B["l"][m5], B["c"][m5], 5 / 60 * 0.7)
    a2.plot(x5 + 5 / 60, e5[m5], color=EMA_C, linewidth=1.2, label="EMA 10 (M5)")
    if len(ia):
        a2.add_patch(Rectangle((0.5, L), to_x(tx) - 0.5, H - L, fill=False, edgecolor=RANGE_C, linewidth=1))
    a2.axvline(0, color=MUTED, linewidth=0.7, linestyle=":"); a2.axvline(0.5, color=MUTED, linewidth=0.7, linestyle=":")
    title = "M5 - "
    if k:
        j = k[0]; jr = int(st_["j"][j]); xr = float(to_x(t5[jr]))
        a2.add_patch(Rectangle((xr, st_["rlo"][j]), 5 / 60, st_["rhi"][j] - st_["rlo"][j], fill=False, edgecolor=INK, linewidth=1.2))
        side = "SELL" if st_["side"][j] < 0 else "BUY"
        title += f"{side} day, reference {lbl(xr)}{' (displaced: 50% entry)' if st_['disp'][j] else ''}"
        tr = [r for r in S.detail(M, B, p) if int(r[14]) == j]
        if tr:
            r = tr[0]; xi, xo = float(to_x(r[0])), float(to_x(r[1]))
            for y, col, name in ((r[8], ENTRY_C, "entry"), (r[9], STOP_C, "stop"), (r[10], TGT_C, f"{p['target']}R target")):
                a2.plot([xi, xo], [y, y], color=col, linewidth=1.2, linestyle="--" if name != "entry" else "-")
                a2.text(xo, y, f" {name}", fontsize=7, color=INK, va="center")
            a2.plot([xo], [r[11]], marker="o", color=INK, markersize=4)
            title += f"; entry {lbl(xi)}, exit {lbl(xo)} ({S.REASON[int(r[12])]}, {r[3]:+.2f}R)"
        else:
            title += "; no fill"
    else:
        title += "no setup"
    a2.set_title(title, fontsize=9, loc="left", color=INK)
    a2.legend(fontsize=7, frameon=False, loc="upper left")
    for ax in (a1, a2):
        ticks = ax.get_xticks()
        ax.set_xticks(ticks); ax.set_xticklabels([lbl(x) for x in ticks])
    if note:
        fig.text(0.01, 0.005, "Owner: " + note, fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(path, facecolor="white"); plt.close(fig)
