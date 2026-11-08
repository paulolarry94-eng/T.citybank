"""10 examples of the v5 rules (owner, 2026-11-08: "our last test, show me 10 examples, let me be sure you understood").
Drawn from the 4 settings chosen on 2011-22 for the 2023-25 look (research/results/body4/v5/LOOK_2023_25.json), using the
lab's own code (research/truth/strategies/body4_range_v5.py): the same setups, the same safe-window and layering masks, the
same M1 order engine. Picked at random with a fixed seed among each setting's filled trades 2011-2025, one market at most
once per group; fixed before drawing:
  A  strict engulf, no layering      (M15, 10R, breakeven 75% on, stop 20% beyond the range, lookback on)   2 examples
  B  loose engulf, no layering       (H1, 10R, breakeven off, stop at the range end, lookback off)          3 examples,
                                      only setups that pass "loose" but FAIL "strict" (to show the difference)
  C  strict engulf + layering        (M1 entry, M15 big, 10R, breakeven on, stop 20% beyond, lookback on)   2 examples
  D  loose engulf + layering         (M5 entry, H1 big, 5R, breakeven off, stop 20% beyond, lookback on)    3 examples
    python3 research/body4/examples_v5.py  ->  research/results/body4/v5/examples/*.png + examples.json
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
import body4_scan as SC   # noqa: E402
from best_worst import candles   # noqa: E402


def ticks(ax, B, idx, n=6):
    step = max(1, len(idx) // n)
    ax.set_xticks(range(0, len(idx), step))
    ax.set_xticklabels([dt.datetime.fromtimestamp(int(B["t"][i]), UTC).strftime("%a %H:%M") for i in idx[::step]], fontsize=6.5)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, color="#e4e3df", linewidth=0.5); ax.set_axisbelow(True)

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "body4_range_v5.py"))
OUT = os.path.join(ROOT, "research", "results", "body4", "v5", "examples")
UTC = dt.timezone.utc
SEED = 20261108
GROUPS = [
    ("A", "strict engulf, no layering", dict(tf="M15", engulf="body", layer="none", target=10, be=1, buffer=0.2, lookback=1), 2, False),
    ("B", "loose engulf (loose only), no layering", dict(tf="H1", engulf="loose", layer="none", target=10, be=0, buffer=0.0, lookback=0), 3, True),
    ("C", "strict engulf + layering (M15 big, M1 entry)", dict(tf="M1", engulf="body", layer="on", target=10, be=1, buffer=0.2, lookback=1), 2, False),
    ("D", "loose engulf + layering (H1 big, M5 entry)", dict(tf="M5", engulf="loose", layer="on", target=5, be=0, buffer=0.2, lookback=1), 3, False),
]
MIN = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
DISPLAY = ["M1", "M5", "M15", "M30", "H1", "H4"]
DEC = {"XAUUSD": 2, "XAGUSD": 3, "EURUSD": 5, "GBPUSD": 5, "USDJPY": 3, "EURGBP": 5, "WTI": 3, "US500": 1, "NAS100": 1,
       "GER40": 1, "UK100": 1, "JP225": 0}
REASON = {1: "stop", 2: "target", 3: "breakeven stop", 4: "time close at 20:30 UTC", 5: "stop in the fill minute"}


def fmt(sym, x):
    return f"{x:,.{DEC.get(sym, 5)}f}"


def engulf_checks(B, k, s):
    """For candles 2 and 4: does it open at/beyond the previous close (strict), and close beyond the previous open (both)?"""
    o, c = B["o"], B["c"]
    out = []
    for m in (2, 4):
        i = k - 4 + m; pv = i - 1
        strict_open = (o[i] >= c[pv]) if s < 0 else (o[i] <= c[pv])
        beyond = (c[i] < o[pv]) if s < 0 else (c[i] > o[pv])
        out.append(dict(m=m, open=o[i], prev_close=c[pv], close=c[i], prev_open=o[pv], strict_open=bool(strict_open), beyond=bool(beyond)))
    return out


def setup_panel(ax, M, B, k, s, hi, lo, lb, title, mark_t=None, mark_label=None):
    t = B["t"]
    idx = np.arange(max(0, k - 11), min(len(t), k + 6))
    candles(ax, B, idx); ticks(ax, B, idx, 6)
    a = idx[0]; mid = (hi + lo) / 2
    ax.add_patch(Rectangle((k - 3 - a - 0.45, lo), 3.9, hi - lo, fill=False, ec="#7a5af5", lw=1.1, ls="--", zorder=4))
    lh, ll = B["h"][k - 8:k - 3].max(), B["l"][k - 8:k - 3].min()
    ax.add_patch(Rectangle((k - 8 - a - 0.45, ll), 4.9, lh - ll, fc="#7a5af5", alpha=0.08, lw=0))
    span = B["h"][idx].max() - B["l"][idx].min()
    ys = []
    for m in range(4):
        i = k - 3 + m
        y = B["h"][i] + 0.06 * span if s < 0 else B["l"][i] - 0.06 * span
        ys.append(y)
        ax.text(i - a, y, str(m + 1), ha="center", va="center", fontsize=7,
                bbox=dict(boxstyle="square,pad=0.12", fc="white", ec="#0b0b0b", lw=0.7))
    ax.text(k - 6 - a, lh + 0.03 * span, f"lookback {lb}/5", fontsize=6.5, color="#7a5af5", ha="center")
    ax.set_ylim(min(B["l"][idx].min(), min(ys)) - 0.05 * span, max(B["h"][idx].max(), max(ys), lh + 0.06 * span) + 0.05 * span)
    ax.axhline(mid, color="#0b0b0b", lw=0.8, ls=":")
    ax.text(len(idx) - 0.6, mid, " midpoint", fontsize=6.5, va="center")
    if mark_t is not None:
        bi = int(np.searchsorted(t, mark_t - 1, side="right")) - 1          # the big candle the small setup happened in
        x = bi - a - 0.5 + (mark_t - int(t[bi])) / (60.0 * B["minutes"])     # placed inside it, at the right time
        ax.axvline(x, color="#eb6834", lw=1.0, ls="--")
        ax.text(x + 0.1, B["h"][idx].max(), mark_label, fontsize=6.5, color="#eb6834", va="top")
    ax.set_title(title, fontsize=8, loc="left")


def trade_panel(ax, M, tf, row, p):
    s = int(row[2]); R0 = row[4]; T = p["target"]
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
    lines = [(tp, f"target {T}R", "#1baa55", "-"), (level, "entry: limit at 50% of the range", "#0b0b0b", "-"),
             (stop, "stop" + (" (range end + 20% of the range)" if p["buffer"] > 0 else " (range end)"), "#e34948", "-")]
    if p["be"]:
        lines.append((level + s * 0.75 * T * R0, "breakeven trigger (75% of the way)", "#eb6834", ":"))
    lo_ = min(D["l"][idx].min(), stop, level); hi_ = max(D["h"][idx].max(), stop, level)
    pad = 0.08 * (hi_ - lo_)
    ylo, yhi = lo_ - pad, hi_ + pad
    stack = {"up": 0, "down": 0}
    for y, lab, col, ls in lines:
        if ylo <= y <= yhi:
            ax.plot([max(xi - 12, 0), len(idx) - 1], [y, y], color=col, lw=1.0, ls=ls)
            ax.text(len(idx) - 0.5, y, " " + lab, fontsize=6.5, color=col, va="center")
        else:                                            # far away: say where it is instead of squashing the candles
            up = y > yhi; key = "up" if up else "down"
            edge = (yhi - stack[key] * 0.05 * (yhi - ylo)) if up else (ylo + stack[key] * 0.05 * (yhi - ylo))
            stack[key] += 1
            ax.text(len(idx) - 0.5, edge, f" {lab} at {fmt(M.sym, y)} ({'above' if up else 'below'}, off the chart)",
                    fontsize=6.5, color=col, va="top" if up else "bottom")
    ax.plot(xi, row[10], "o", color="#0b0b0b", ms=5, zorder=6); ax.plot(xo, row[11], "x", color="#0b0b0b", ms=8, zorder=6)
    ax.set_ylim(ylo, yhi); ax.set_xlim(-1, len(idx) + 0.45 * len(idx) + 6)
    ax.set_title(f"The trade ({dtf} candles; dot = fill, cross = exit): {REASON[int(row[9])]}, {row[3]:+.2f}R after costs "
                 f"(costs {row[5]:.2f}R; no swaps: flat at 20:30 UTC)", fontsize=8, loc="left")


def big_setup_for(M, p, t_small, s):
    """The bigger timeframe's setup that let the small one trade: same direction, same engulf type, passing intent and
    lookback, candle 4 closed at or before the small setup, less than 2 big candles earlier (the latest such)."""
    htf = S.HTF[p["tf"]]
    H = S._htf_bars(M, htf)
    SH = SC.setups(H, S.HTF_MIN[htf], sample="flow", doji_bullish=S.DOJI_BULLISH, engulf=p["engulf"])
    mid = (SH["hi"] + SH["lo"]) / 2
    ok = np.where(SH["side"] > 0, SH["c4"] > mid, SH["c4"] < mid) & (SH["side"] == s) & (SH["t_conf"] <= t_small)
    if p["lookback"]:
        ok &= SH["lookback"] >= 3
    ok &= (t_small - SH["t_conf"]) < S.LAYER_BARS * S.HTF_MIN[htf] * 60
    js = np.flatnonzero(ok)
    return (htf, H, SH, int(js[-1])) if len(js) else (htf, H, SH, None)


def checks_text(M, B, k, s, hi, lo, lb, tconf, p, row, layer_note):
    sym = M.sym; side = "SELL" if s < 0 else "BUY"; mid = (hi + lo) / 2
    lines = []
    for e in engulf_checks(B, k, s):
        word_o = "at or above" if s < 0 else "at or below"; word_c = "below" if s < 0 else "above"
        kind = "strict (body covers the previous body)" if e["strict_open"] else "LOOSE ONLY (opens inside the previous body)"
        lines.append(f"Candle {e['m']}: opens {fmt(sym, e['open'])}, {word_o} candle {e['m'] - 1}'s close {fmt(sym, e['prev_close'])}? "
                     f"{'yes' if e['strict_open'] else 'NO'}.  Closes {fmt(sym, e['close'])}, {word_c} candle {e['m'] - 1}'s open "
                     f"{fmt(sym, e['prev_open'])}? {'yes' if e['beyond'] else 'NO'}.  -> {kind}")
    c4 = B["c"][k]
    lines.append(f"Intent: candle 4 closes {fmt(sym, c4)}, {'below' if s < 0 else 'above'} the midpoint {fmt(sym, mid)} -> "
                 f"{'take it' if (c4 < mid if s < 0 else c4 > mid) else 'skip'}.   Lookback (5 candles before candle 1, dojis bullish): "
                 f"{lb} of 5 {'bearish' if s < 0 else 'bullish'}" + (" (needs 3) -> pass" if p["lookback"] else " (lookback off in this setting)"))
    tc = dt.datetime.fromtimestamp(tconf, UTC)
    lines.append(f"Safe window: candle 4 closed {tc:%a %Y-%m-%d %H:%M} UTC (07:00-19:00 allowed), not a US news day (NFP/CPI/FOMC); "
                 f"everything closes at 20:30 UTC.")
    if layer_note:
        lines.append(layer_note)
    R0 = row[4]
    lines.append(f"Orders: {side} limit at 50% {fmt(sym, row[13] - s * p['target'] * R0)}, stop {fmt(sym, row[12])}, 1R = {fmt(sym, R0)}, "
                 f"target {p['target']}R {fmt(sym, row[13])}" + (", breakeven at 75% of the way" if p["be"] else ", no breakeven")
                 + f".  Filled {dt.datetime.fromtimestamp(int(row[0]), UTC):%H:%M} at {fmt(sym, row[10])}; exit "
                 f"{dt.datetime.fromtimestamp(int(row[1]), UTC):%H:%M} at {fmt(sym, row[11])} ({REASON[int(row[9])]}): {row[3]:+.2f}R after costs.")
    return "\n".join(lines)


def draw(n, gid, gname, p, M, row, path):
    tf = p["tf"]; B = M.bars(tf)
    Sx = S.setups(B, p, M)
    j = int(row[8]); k = int(Sx["k"][j]); s = int(row[2])
    hi, lo, lb, tconf = float(Sx["hi"][j]), float(Sx["lo"][j]), int(Sx["lookback"][j]), int(Sx["t_conf"][j])
    side = "SELL" if s < 0 else "BUY"
    layer_note = None
    if p["layer"] == "on":
        htf, H, SH, jb = big_setup_for(M, p, tconf, s)
        fig = plt.figure(figsize=(15, 9.6), dpi=120)
        gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.34])
        a0, a1, a2 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])
        ax_txt = fig.add_subplot(gs[2, :]); ax_txt.axis("off")
        kb = int(SH["k"][jb]); tb = int(SH["t_conf"][jb])
        setup_panel(a0, M, H, kb, s, float(SH["hi"][jb]), float(SH["lo"][jb]), int(SH["lookback"][jb]),
                    f"1. BIG timeframe ({htf}): {side} setup, candle 4 closes {dt.datetime.fromtimestamp(tb, UTC):%H:%M} UTC",
                    mark_t=tconf, mark_label=f" {tf} setup confirmed")
        setup_panel(a1, M, B, k, s, hi, lo, lb, f"2. SMALL timeframe ({tf}): {side} setup, candle 4 closes "
                    f"{dt.datetime.fromtimestamp(tconf, UTC):%H:%M} UTC -> orders from THIS range")
        gap_min = (tconf - tb) // 60
        layer_note = (f"Layering: the {htf} {side} setup (same engulf rule, intent and lookback passed) confirmed at "
                      f"{dt.datetime.fromtimestamp(tb, UTC):%H:%M} UTC; the {tf} {side} setup {gap_min} minutes later (allowed: less than "
                      f"2 {htf} candles = {2 * S.HTF_MIN[htf]} minutes) -> both agree, entry on the {tf} range.")
    else:
        fig = plt.figure(figsize=(15, 6.6), dpi=120)
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.3], width_ratios=[1, 1.5])
        a1, a2 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
        ax_txt = fig.add_subplot(gs[1, :]); ax_txt.axis("off")
        setup_panel(a1, M, B, k, s, hi, lo, lb, f"Setup ({tf}): {side}, candle 4 closes {dt.datetime.fromtimestamp(tconf, UTC):%Y-%m-%d %H:%M} UTC")
    trade_panel(a2, M, tf, row, p)
    ax_txt.text(0.0, 1.0, checks_text(M, B, k, s, hi, lo, lb, tconf, p, row, layer_note), fontsize=7.3, va="top", ha="left",
                family="DejaVu Sans Mono", transform=ax_txt.transAxes)
    sett = (f"{'strict' if p['engulf'] == 'body' else 'loose'} engulf, layering {p['layer']}, {tf}, target {p['target']}R, "
            f"breakeven {'on' if p['be'] else 'off'}, stop {'20% beyond' if p['buffer'] else 'at'} the range, lookback {'on' if p['lookback'] else 'off'}")
    fig.suptitle(f"Example {n} ({gid}: {gname}): {M.sym} {tf} {side}, {dt.datetime.fromtimestamp(tconf, UTC):%Y-%m-%d}   |   setting: {sett}",
                 fontsize=9.5, x=0.01, ha="left")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(SEED)
    cache, meta, n = {}, [], 0
    for gid, gname, p, count, loose_only in GROUPS:
        pool = []
        for sym in S.MARKETS:
            M = cache.setdefault(sym, P.market(sym, S))
            B = M.bars(p["tf"]); Sx = S.setups(B, p, M)
            D = S.detail(M, B, p)
            for r in D:
                if loose_only:
                    j = int(r[8]); k = int(Sx["k"][j])
                    if all(e["strict_open"] for e in engulf_checks(B, k, int(r[2]))):
                        continue
                pool.append((sym, r.copy()))
        print(gid, "pool", len(pool), flush=True)
        order = rng.permutation(len(pool)); used = set(); picked = []
        for i in order:
            sym, r = pool[i]
            if sym in used:
                continue
            used.add(sym); picked.append((sym, r))
            if len(picked) == count:
                break
        for sym, r in picked:
            n += 1
            path = os.path.join(OUT, f"example_{n:02d}_{gid}_{sym}_{p['tf']}.png")
            draw(n, gid, gname, p, cache[sym], r, path)
            meta.append(dict(n=n, group=gid, what=gname, market=sym, tf=p["tf"], side="buy" if r[2] > 0 else "sell",
                             fill=dt.datetime.fromtimestamp(int(r[0]), UTC).isoformat(), exit=dt.datetime.fromtimestamp(int(r[1]), UTC).isoformat(),
                             reason=REASON[int(r[9])], R=round(float(r[3]), 3), cost_R=round(float(r[5]), 3), file=os.path.basename(path)))
            print(n, gid, sym, p["tf"], meta[-1]["side"], meta[-1]["fill"], meta[-1]["reason"], meta[-1]["R"], flush=True)
    json.dump(dict(seed=SEED, groups=[dict(id=g[0], what=g[1], setting=g[2], examples=g[3]) for g in GROUPS], examples=meta),
              open(os.path.join(OUT, "examples.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
