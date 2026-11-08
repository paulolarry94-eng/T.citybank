"""Third set of examples (owner's corrections of 2026-11-08): each chart shows one rule, taken as the FIRST time that
event happens on XAUUSD M5 in 2019 (chosen by event type, never by outcome), plus the two charts the owner disputed.
    python3 research/body4/examples3.py  ->  research/results/body4/examples3/*.png + events_2019.txt
Main rules: skip if candle 4 closes beyond the midpoint; entry 50%; stop at the range end; breakeven at +2R; lookback on.
Costs: RoboForex Prime gold, spread 0.05 (decides whether a price is reached), commission 0.06, slippage 0.05.
Dojis (open = close) are drawn grey: they count for neither side in the lookback.
"""
import os, sys, datetime as dt
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research")); sys.path.insert(0, HERE)
import body4_orders as BE   # noqa: E402
import engine as EN   # noqa: E402  (research/engine.py: M1 loader and resampler)

OUT = os.path.join(ROOT, "research", "results", "body4", "examples3")
SYM, TF = "XAUUSD", 5
SPREAD, COMM, SLIP = 0.05, 0.06, 0.05      # RoboForex Prime published, gold
WANT = [("no intent", "Candle 4 closes beyond the midpoint: setup skipped (no intent)"),
        ("removed pending", "Two buy orders wait; the first to fill removes the other"),
        ("WIDER than every pending order", "An opposite setup with a WIDER range replaces the waiting order(s)"),
        ("not wider than pending", "An opposite setup with a NARROWER range is ignored"),
        ("closed: Friday close", "Open trade closed at the Friday cutoff (20:30 UTC)"),
        ("closed: breakeven stop", "+2R reached, stop moved to entry, then stopped at breakeven"),
        ("fewer than 3 of the 5 lookback", "Setup rejected by the lookback (grey candles are dojis and count for neither side)"),
        ("price reached its target first", "Price reaches the target level before the order fills: order cancelled"),
        ("#10 closed: target", "Your image 6: the sell reaches its 4R target (ask = bid + 0.05 spread reaches it)")]


def main():
    os.makedirs(OUT, exist_ok=True)
    ts, o, h, l, c = EN.load_m1(SYM, 2019, 2019)
    M = dict(ts=ts, o=o, h=h, l=l, c=c)
    bt, bo, bh, bl, bc, _ = EN.resample(ts, o, h, l, c, TF)
    B = dict(t=bt, o=bo, h=bh, l=bl, c=bc)
    pats = BE.patterns(B, TF)
    for n, p in enumerate(pats, 1):
        p["id"] = n
    byid = {p["id"]: p for p in pats}
    runs = {}
    for lb in (True, False):
        trades, log, _ = BE.run(M, [dict(p) for p in pats], SPREAD, COMM, SLIP, use_lookback=lb)
        runs[lb] = ({t_["id"]: t_ for t_ in trades}, log)
        open(os.path.join(OUT, f"events_2019_lookback_{'on' if lb else 'off'}.txt"), "w").write("\n".join(x[1] for x in log))
        print("lookback", lb, "patterns", len(pats), "trades", len(trades))
    made = 0
    for key, title in WANT:
        for lb in (True, False):
            tr_by, log = runs[lb]
            hit = next((x for x in log if key in x[1]), None)
            if hit is not None:
                break
        if hit is None:
            print("no event:", key); continue
        made += 1
        ids = sorted({int(w[1:]) for w in hit[1].replace(":", " ").replace(",", " ").replace(")", " ").split() if w.startswith("#") and w[1:].isdigit()})
        draw(B, byid, tr_by, log, ids, hit, made, title + ("" if lb else "  [run with the lookback filter OFF]"))
    print("charts", made)


def draw(B, byid, tr_by, log, ids, hit, n, title):
    t, o, h, l, c = B["t"], B["o"], B["h"], B["l"], B["c"]
    ks = [byid[i]["k"] for i in ids]
    a = max(0, min(ks) - 3 - 9)
    end_t = hit[0]
    for i in ids:
        if i in tr_by:
            end_t = max(end_t, tr_by[i]["t_out"])
    b = min(len(t) - 1, int(np.searchsorted(t, end_t, side="right")) + 5)
    b = min(b, a + 110)
    idx = np.arange(a, b + 1)
    fig = plt.figure(figsize=(12, 7.6), dpi=130)
    ax = fig.add_axes([0.06, 0.33, 0.78, 0.6]); tx = fig.add_axes([0.06, 0.02, 0.9, 0.25]); tx.axis("off")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, color="#e4e3df", linewidth=0.5); ax.set_axisbelow(True)
    for x, i in enumerate(idx):
        col = "#2a78d6" if c[i] > o[i] else ("#4a4a47" if c[i] < o[i] else "#b4b2a9")    # doji: grey, counts for neither
        ax.plot([x, x], [l[i], h[i]], color=col, linewidth=0.8, zorder=2)
        if c[i] == o[i]:
            ax.plot([x - 0.32, x + 0.32], [o[i], o[i]], color=col, linewidth=1.6, zorder=3)
        else:
            ax.add_patch(Rectangle((x - 0.32, min(o[i], c[i])), 0.64, abs(c[i] - o[i]), color=col, zorder=3, lw=0))
    span = h[idx].max() - l[idx].min()
    pal = ["#7a5af5", "#eb6834", "#1baa55", "#e34948"]
    ys = [h[idx].max(), l[idx].min()]
    for z, pid in enumerate(ids):
        p = byid[pid]; k = p["k"]; col = pal[z % 4]
        x0 = k - 3 - a - 0.45
        ax.add_patch(Rectangle((x0, p["lo"]), k - a + 0.45 - x0, p["width"], fill=False, ec=col, lw=1.1, ls="--", zorder=4))
        for m in range(4):
            i = k - 3 + m
            y = h[i] + 0.04 * span if p["side"] < 0 else l[i] - 0.04 * span
            ax.text(i - a, y, str(m + 1), ha="center", va="center", fontsize=7, color=col,
                    bbox=dict(boxstyle="square,pad=0.12", fc="white", ec=col, lw=0.8))
        lb0 = k - 8
        ax.add_patch(Rectangle((lb0 - a - 0.45, l[lb0:k - 3].min()), 5 - 0.1, h[lb0:k - 3].max() - l[lb0:k - 3].min(),
                               fill=True, fc=col, alpha=0.07, lw=0))
        ax.text(lb0 - a + 2, h[lb0:k - 3].max() + 0.02 * span, f"lookback {p['lookback']}/5", fontsize=6.5, color=col, ha="center")
        ax.plot([k - a + 0.5, len(idx) - 1], [p["mid"]] * 2, color=col, lw=0.9, ls=":")
        ax.text(len(idx) - 0.5, p["mid"], f" #{pid} {'SELL' if p['side'] < 0 else 'BUY'} midpoint", fontsize=6.5, color=col, va="center")
        if pid in tr_by:
            T = tr_by[pid]
            xi = int(np.searchsorted(t, T["t_in"], side="right")) - 1 - a
            xo = int(np.searchsorted(t, T["t_out"], side="right")) - 1 - a
            for y, lab, lc in ((T["stop0"], "stop", "#e34948"), (T["tp"], "target 4R", "#1baa55"), (T["be"], "+2R breakeven", "#eb6834")):
                ax.plot([xi, max(xo, xi + 3)], [y, y], color=lc, lw=1.0)
                ax.text(max(xo, xi + 3) + 0.2, y, " " + lab, fontsize=6.5, color=lc, va="center")
                ys.append(y)
            ax.plot(xi, T["entry"], "o", color="#0b0b0b", ms=5, zorder=6)
            ax.plot(xo, T["exit"], "x", color="#0b0b0b", ms=7, zorder=6)
    lo_, hi_ = min(ys), max(ys)
    ax.set_ylim(lo_ - 0.05 * (hi_ - lo_), hi_ + 0.08 * (hi_ - lo_))
    step = max(2, len(idx) // 10)
    ax.set_xticks(range(0, len(idx), step))
    ax.set_xticklabels([dt.datetime.fromtimestamp(int(t[i]), dt.timezone.utc).strftime("%a %H:%M") for i in idx[::step]], fontsize=7)
    ax.set_xlim(-1, len(idx) + 9)
    ax.set_title(f"Example {n}: {title}\n{SYM} M5, {dt.datetime.fromtimestamp(int(t[a]), dt.timezone.utc):%Y-%m-%d} (UTC). "
                 "Dashed box = range of candles 1-4, shaded = 5-candle lookback, dot = fill, x = exit", fontsize=8.5, loc="left")
    t0, t1 = t[a], max(hit[0], t[b])
    lines = [x[1] for x in log if t0 <= x[0] <= t1 and any(f"#{i} " in x[1] + " " or f"#{i}:" in x[1] or f"#{i})" in x[1] for i in ids)]
    tx.text(0, 1, "Event log (engine output):\n" + "\n".join(lines[:14]), fontsize=7, va="top", family="monospace")
    fig.savefig(os.path.join(OUT, f"example_{n}.png")); plt.close(fig)
    print(n, title, ids)


if __name__ == "__main__":
    main()
