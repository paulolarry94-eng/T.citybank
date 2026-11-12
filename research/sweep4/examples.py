"""Example charts of the pivot-sweep body-engulf range, drawn like the owner's TradingView screenshots: pivot labels
(Pivots HL 10/10), the swept pivot (dotted), candles 1-4, the range box, the 60% entry, stop and target, and the outcome.
Only 2011-19 trades (development data). Also marks WHEN each pivot label could first appear on a live chart.
    python3 research/sweep4/examples.py  ->  research/results/sweep4/examples/*.png + examples.json
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

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "sweep4_pivot_v1.py"))
OUT = os.path.join(ROOT, "research", "results", "sweep4", "examples")
UP, DN = "#5b7bd5", "#4a4a52"                      # the owner's chart colours: blue up candles, dark grey down candles
D0 = int(dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).timestamp())


def chart(M, B, S_, D, row, p, fname, title):
    k = int(S_["k"][int(row[8])]); side = int(row[2]); piv = p["piv"]
    t = B["t"]; o, h, l, c = B["o"], B["h"], B["l"], B["c"]
    j_out = int(np.searchsorted(t, row[1], side="right")) - 1
    ph, pl = S_["ph"], S_["pl"]
    sw = float(S_["swept"][int(row[8])]); sw_i = None
    for x in range(k - 1, max(k - 400, 0), -1):         # the swept pivot (may be far back)
        if (side < 0 and ph[x] and h[x] == sw) or (side > 0 and pl[x] and l[x] == sw):
            sw_i = x; break
    a = max(0, k - 45 if sw_i is None else min(k - 45, max(sw_i - 5, k - 70)))
    b = min(len(t), max(j_out + 8, k + 12)); b = min(b, a + 170)
    fig, ax = plt.subplots(figsize=(13, 6.5), dpi=110)
    fig.patch.set_facecolor("#d6d9e0"); ax.set_facecolor("#d6d9e0")
    for x in range(a, b):
        col = UP if c[x] >= o[x] else DN
        ax.plot([x, x], [l[x], h[x]], color=col, lw=0.9)
        ax.add_patch(Rectangle((x - 0.32, min(o[x], c[x])), 0.64, max(abs(c[x] - o[x]), 1e-9), color=col))
    dig = 5 if M.sym in ("EURUSD", "GBPUSD", "EURGBP") else 3 if M.sym == "USDJPY" else 2
    rng_ = h[a:b].max() - l[a:b].min()
    for x in range(max(a - piv, 0), b):
        if x + piv >= b and x + piv > j_out:
            pass
        if ph[x] and a <= x:
            ax.text(x, h[x] + 0.02 * rng_, f"{h[x]:.{dig}f}", ha="center", va="bottom", fontsize=8, color="#333")
            if x + piv < b:
                ax.plot(x + piv, h[x] + 0.012 * rng_, marker="v", ms=4, color="#999")
        if pl[x] and a <= x:
            ax.text(x, l[x] - 0.02 * rng_, f"{l[x]:.{dig}f}", ha="center", va="top", fontsize=8, color="#333")
            if x + piv < b:
                ax.plot(x + piv, l[x] - 0.012 * rng_, marker="^", ms=4, color="#999")
    if sw_i is not None:
        x0 = max(sw_i, a)
        ax.plot([x0, k - 2], [sw, sw], ls=":", color="#222", lw=1.2)
        when = "" if sw_i >= a else f" (pivot of {dt.datetime.utcfromtimestamp(int(t[sw_i])):%d %b %H:%M}, off the chart)"
        ax.text(x0, sw, f"  swept pivot {sw:.{dig}f}{when}", fontsize=8, va="bottom" if side < 0 else "top")
    for n, x in enumerate(range(k - 3, k + 1), 1):
        y = (h[k - 3:k + 1].max() + 0.07 * rng_) if side < 0 else (l[k - 3:k + 1].min() - 0.07 * rng_)
        ax.text(x, y, str(n), ha="center", va="center", fontsize=7, fontweight="bold", color="#b00",
                )
    entry, stop, tgt = row[10], row[12], row[13]
    j_in = int(np.searchsorted(t, row[0], side="right")) - 1
    hi, lo = float(S_["hi"][int(row[8])]), float(S_["lo"][int(row[8])])
    ax.add_patch(Rectangle((k - 3.5, lo), 4, hi - lo, fc="#7f9cf5", alpha=0.35, ec="none"))
    x1 = max(j_out, j_in) + 1
    ax.add_patch(Rectangle((k + 0.5, min(entry, stop)), x1 - k - 0.5, abs(stop - entry), fc="#b0b0b8", alpha=0.6, ec="none"))
    ax.add_patch(Rectangle((k + 0.5, min(entry, tgt)), x1 - k - 0.5, abs(tgt - entry), fc="#5fb3a3", alpha=0.45, ec="none"))
    ax.axhline(stop, xmin=0, xmax=1, color="#c33", lw=0.8, alpha=0.6)
    for y, lab in ((entry, f"entry 60%  {entry:.{dig}f}"), (stop, f"stop  {stop:.{dig}f}"), (tgt, f"target {p['target']}{'R' if str(p['target']).isdigit() else ''}  {tgt:.{dig}f}")):
        ax.text(b - 0.5, y, lab, fontsize=8, va="center", ha="right", bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
    ax.annotate("", xy=(j_out, row[11]), xytext=(j_in, row[10]), arrowprops=dict(arrowstyle="->", ls="--", color="#333", lw=0.8))
    lo_y = min(l[a:b].min(), tgt, stop); hi_y = max(h[a:b].max(), tgt, stop)
    ax.set_ylim(lo_y - 0.08 * (hi_y - lo_y), hi_y + 0.08 * (hi_y - lo_y)); ax.set_xlim(a - 1, b + 1)
    tk = list(range(a, b, max(1, (b - a) // 8)))
    ax.set_xticks(tk); ax.set_xticklabels([dt.datetime.utcfromtimestamp(int(t[x])).strftime("%d %b %H:%M") for x in tk], fontsize=8)
    ax.yaxis.tick_right()
    ax.set_title(title, fontsize=10, loc="left")
    ax.text(0.01, 0.02, "grey triangles = when that pivot label could first appear live (its 10th candle on the right closed)",
            transform=ax.transAxes, fontsize=7.5, color="#555")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, fname)); plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    picks = []
    for sym, tf, p in (("EURUSD", "M5", dict(piv=10, sweep="c12", stop="range", target=5)),
                       ("XAUUSD", "M5", dict(piv=10, sweep="c12", stop="range", target="p1")),
                       ("GER40", "M5", dict(piv=10, sweep="c12", stop="range", target=5))):
        M = P.market(sym, S); B = M.bars(tf); S_ = S.setups(B, dict(p, tf=tf), M)
        D = S.detail(M, B, dict(p, tf=tf), cut=D0)
        wins = [r for r in D if r[9] == 2 and dt.datetime.utcfromtimestamp(int(r[0])).year == 2019]
        loss = [r for r in D if r[9] in (1, 5) and dt.datetime.utcfromtimestamp(int(r[0])).year == 2019]
        for kind, rows in (("win", wins[:2]), ("loss", loss[:2])):
            for r in rows:
                ts_ = dt.datetime.utcfromtimestamp(int(r[0]))
                fname = f"{sym}_{tf}_{ts_:%Y%m%d_%H%M}_{kind}.png"
                title = (f"{sym} {tf} · {'SELL' if r[2] < 0 else 'BUY'} · pivots HL {p['piv']}/{p['piv']} · sweep by candle 1 or 2 · "
                         f"target {p['target']}{'R' if str(p['target']).isdigit() else ' (nearest pivot >= 3R)'} · result {r[3]:+.2f}R after costs")
                chart(M, B, S_, D, r, p, fname, title)
                picks.append(dict(file=fname, market=sym, tf=tf, side="SELL" if r[2] < 0 else "BUY", entered=f"{ts_:%Y-%m-%d %H:%M} UTC",
                                  entry=float(r[10]), stop=float(r[12]), target=float(r[13]), exit=float(r[11]), R=round(float(r[3]), 2),
                                  result={1: "stop", 2: "target", 5: "stop in the fill minute"}.get(int(r[9]), "other")))
    json.dump(picks, open(os.path.join(OUT, "examples.json"), "w"), indent=1)
    print(json.dumps(picks, indent=1))


if __name__ == "__main__":
    main()
