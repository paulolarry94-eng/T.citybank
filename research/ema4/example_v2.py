"""Examples of the v2 rule (full engulfing) for the owner: the owner's EURUSD 2014-08-20 chart plus random v2 patterns
(fixed seed, 2011-2022), drawn with the engulfing levels (1st and 3rd candles' low/high), both entries (50% of the 4th,
close of the 4th) and the three stop choices (4th candle, 3rd+4th candles, all four candles).

    python3 research/ema4/example_v2.py      # writes research/results/ema4/v2_examples/*.png
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
import protocol as P   # noqa: E402
import scanner         # noqa: E402

OUT = os.path.join(ROOT, "research", "results", "ema4", "v2_examples")
UTC1 = dt.timezone(dt.timedelta(hours=1))
VER = sys.argv[1] if len(sys.argv) > 1 else "v2"
S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", f"ema4_flip_{VER}.py"))
FRESH = VER != "v2"
CLEAR = 0.1 if VER == "v4" else 0.0
if VER != "v2":
    OUT = os.path.join(ROOT, "research", "results", "ema4", f"{VER}_examples")


def draw(B, E, Pt, j, path, note):
    i4 = int(Pt["i4"][j]); s = int(Pt["side"][j]); g = int(Pt["grade"][j]); t = B["t"]
    idx = np.arange(i4 - 12, min(i4 + 14, len(t)))
    fig, ax = plt.subplots(figsize=(10, 5.4), dpi=130)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, color="#e4e3df", linewidth=0.5); ax.set_axisbelow(True)
    for n, i in enumerate(idx):
        o, h, l, c = B["o"][i], B["h"][i], B["l"][i], B["c"][i]; col = "#2a78d6" if c >= o else "#4a4a47"
        ax.plot([n, n], [l, h], color=col, linewidth=0.9, zorder=2)
        ax.add_patch(Rectangle((n - 0.32, min(o, c)), 0.64, max(abs(c - o), 1e-9), color=col, zorder=3, linewidth=0))
    ax.plot(range(len(idx)), E[idx], color="#eb6834", linewidth=1.3, label="EMA 10")
    a = idx[0]; span = B["h"][idx].max() - B["l"][idx].min()
    for m in range(4):
        k = i4 - 3 + m; y = B["h"][k] + 0.06 * span if s < 0 else B["l"][k] - 0.06 * span
        ax.text(k - a, y, str(m + 1), ha="center", va="center", fontsize=8, bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="#0b0b0b", lw=0.8))
    ref = (lambda k: B["l"][k]) if s < 0 else (lambda k: B["h"][k])
    word = "low" if s < 0 else "high"
    for k, lab in ((i4 - 3, f"1st candle {word} (A+: 2nd closes beyond)"), (i4 - 1, f"3rd candle {word} (4th must close beyond)")):
        ax.plot([k - a - 0.4, i4 - a + 0.4], [ref(k)] * 2, color="#7a5af5", linewidth=1.2)
        ax.text(i4 - a + 0.5, ref(k), " " + lab, fontsize=7, va="center", color="#7a5af5")
    stops = {"stop: 4th candle": (Pt["hi4"][j] if s < 0 else Pt["lo4"][j]),
             "stop: 3rd+4th candles": (max(Pt["hi3"][j], Pt["hi4"][j]) if s < 0 else min(Pt["lo3"][j], Pt["lo4"][j])),
             "stop: all four candles": (Pt["hi_all"][j] if s < 0 else Pt["lo_all"][j])}
    x0, x1 = i4 - a + 1, len(idx) - 1
    for (lab, y), ls in zip(stops.items(), ("--", "-.", ":")):
        ax.plot([x0, x1], [y, y], color="#e34948", linewidth=1.0, linestyle=ls); ax.text(x1, y, " " + lab, fontsize=7, va="center")
    ax.plot([x0, x1], [Pt["entry50"][j]] * 2, color="#1baf7a", linewidth=1.2); ax.text(x1, Pt["entry50"][j], " entry: 50% of 4th", fontsize=7, va="center")
    ax.plot([x0, x1], [B["c"][i4]] * 2, color="#1baf7a", linewidth=1.0, linestyle="--"); ax.text(x1, B["c"][i4], " entry: 4th close", fontsize=7, va="center")
    ticks = [n for n, i in enumerate(idx) if (t[i] // 60) % 15 == 0]
    ax.set_xticks(ticks); ax.set_xticklabels([dt.datetime.fromtimestamp(int(t[idx[n]]), UTC1).strftime("%H:%M") for n in ticks], fontsize=8)
    ax.ticklabel_format(axis="y", useOffset=False, style="plain"); ax.tick_params(labelsize=8)
    day = dt.datetime.fromtimestamp(int(t[i4]), UTC1)
    ax.set_title(f"{note}  {day:%Y-%m-%d} (UTC+1)  {'SELL' if s < 0 else 'BUY'} {scanner.GRADE[g]} (full engulfing)  4th candle {day:%H:%M}",
                 fontsize=9, loc="left"); ax.legend(fontsize=7, frameon=False, loc="upper left")
    fig.subplots_adjust(right=0.80); fig.savefig(path, facecolor="white"); plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    M = P.market("EURUSD", S); B = M.bars("M5"); E = scanner.ema(B["c"])
    Pt = scanner.detect(B["o"], B["h"], B["l"], B["c"], engulf="extreme", fresh=FRESH, clear=CLEAR)
    t4 = int(dt.datetime(2014, 8, 20, 6, 35, tzinfo=dt.timezone.utc).timestamp())
    j = int(np.flatnonzero((B["t"][Pt["i4"]] == t4) & (Pt["side"] == 1))[0])
    draw(B, E, Pt, j, os.path.join(OUT, "ex1_EURUSD_2014-08-20_owner.png"), "EURUSD M5 (owner's chart)")
    rng = np.random.default_rng(11)
    for n, (sym, want) in enumerate((("XAUUSD", -1), ("GBPUSD", 1)) if VER == "v2" else (("XAUUSD", -1), ("GBPUSD", 1), ("EURUSD", -1), ("USDJPY", 1)) + ((("US500", -1), ("GBPUSD", -1)) if VER == "v4" else ()), 2):
        M = P.market(sym, S); B = M.bars("M5"); E = scanner.ema(B["c"])
        Pt = scanner.detect(B["o"], B["h"], B["l"], B["c"], engulf="extreme", fresh=FRESH, clear=CLEAR)
        g_want = (Pt["grade"] == 2) if (VER != "v2" and n % 2 == 0) else (Pt["grade"] > 0)
        ok = np.flatnonzero(g_want & (Pt["side"] == want) & (B["t"][Pt["i4"]] < P.core.CUT))
        j = int(rng.choice(ok)); draw(B, E, Pt, j, os.path.join(OUT, f"ex{n}_{sym}_random.png"), f"{sym} M5 (random)")
        print(sym, dt.datetime.utcfromtimestamp(int(B["t"][Pt["i4"][j]])), scanner.GRADE[int(Pt["grade"][j])])


if __name__ == "__main__":
    main()
