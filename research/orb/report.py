"""ORB 50 — dashboard figures (Part 9C). Reads only saved results; makes PNGs in research/orb/figures.
Run after final.py. Colours follow one fixed palette; one axis per chart."""
import os, json, warnings, datetime as dt
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import core, selection as SEL, metrics as MT

warnings.simplefilter("ignore")
FIG = os.path.join(core.HERE, "figures"); os.makedirs(FIG, exist_ok=True)
RES = os.path.join(core.HERE, "..", "results")
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA, YELLOW, RED = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e34948"
DIV = LinearSegmentedColormap.from_list("div", ["#d03b3b", "#f0efec", "#2a78d6"])
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9,
                     "axes.titlesize": 10, "axes.titleweight": "bold", "legend.frameon": False})


def save(fig, name):
    fig.savefig(os.path.join(FIG, name), dpi=140, bbox_inches="tight"); plt.close(fig)


def fig_baseline():
    d = SEL.with_stats(SEL.load(["E0"]))
    d = d[d.tgt == 2.0]
    piv = d.pivot_table(index=["sym", "session"], columns="orb", values="E")
    fig, ax = plt.subplots(figsize=(5.2, 5.4))
    im = ax.imshow(piv.values, cmap=DIV, vmin=-0.25, vmax=0.25, aspect="auto")
    ax.set_xticks(range(len(piv.columns)), [f"{c} min" for c in piv.columns])
    ax.set_yticks(range(len(piv.index)), [f"{a} {b}" for a, b in piv.index])
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            ax.text(j, i, f"{piv.values[i, j]:+.2f}", ha="center", va="center", fontsize=8, color=INK)
    ax.grid(False)
    ax.set_title("Canonical ORB, 2R target: R per trade after costs\n(development years 2011-2019)", loc="left")
    fig.colorbar(im, ax=ax, shrink=0.6, label="expectancy (R)")
    save(fig, "01_baseline_map.png")


def fig_grid_hist():
    fig, ax = plt.subplots(figsize=(7, 3.4))
    for st, lab, col in (("E1", "Model A pure ORB", BLUE), ("E2", "Model B trend ORB", ORANGE), ("E3", "Model C pullback ORB", AQUA)):
        d = SEL.with_stats(SEL.load([st]))
        t = d.loc[d.n >= 150, "t"].dropna()
        ax.hist(t, bins=np.arange(-14, 4, 0.25), histtype="step", lw=2, color=col, label=f"{lab} ({len(t):,} configs)")
    top = ax.get_ylim()[1]
    ax.axvline(2.0, color=INK2, lw=1, ls="--"); ax.text(1.9, top * 0.55, "t = 2", color=INK2, ha="right")
    ax.axvline(5.06, color=RED, lw=1, ls="--"); ax.text(4.95, top * 0.35, "needed after\n118k trials:\nt = 5.1", color=INK2, ha="right")
    ax.set_xlabel("t-statistic of expectancy, development years"); ax.set_ylabel("configurations")
    ax.set_title("Every configuration tested: almost all lose after costs; none clears the multiple-testing bar", loc="left")
    ax.legend(loc="upper left")
    save(fig, "02_grid_tstats.png")


def fig_is_oos():
    d = SEL.load(["E1", "E2", "E3"])
    a = SEL.period_stats(d, SEL.DEV); b = SEL.period_stats(d, SEL.VAL, "v_")
    k = (a.n >= 150) & (b.v_n >= 50)
    x, y = a.E[k], b.v_E[k]
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    hb = ax.hexbin(x, y, gridsize=60, cmap=LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#104281"]), mincnt=1, bins="log")
    ax.axhline(0, color=INK2, lw=0.8); ax.axvline(0, color=INK2, lw=0.8)
    c = np.corrcoef(x, y)[0, 1]
    top = x >= x.quantile(0.99)
    ax.set_xlabel("development 2011-2019 (R per trade)"); ax.set_ylabel("validation 2020-2022 (R per trade)")
    ax.set_title(f"In-sample vs out-of-sample, {k.sum():,} configs\ncorrelation {c:+.2f}; best 1% in-sample average {y[top].mean():+.3f}R later", loc="left")
    fig.colorbar(hb, ax=ax, label="configs (log)")
    save(fig, "03_is_vs_oos.png")
    return float(c), float(y[top].mean()), int(top.sum())


def fig_walkforward():
    W = json.load(open(os.path.join(RES, "orb_walkforward.json")))
    fig, ax = plt.subplots(figsize=(7, 3.2))
    yrs = list(range(2014, 2023)); w = 0.26
    for i, (nm, col) in enumerate((("A pure ORB", BLUE), ("B trend ORB", ORANGE), ("C pullback ORB", AQUA))):
        v = [W[nm]["by_year"][str(y)]["E"] for y in yrs]
        ax.bar(np.arange(len(yrs)) + (i - 1) * w, v, w * 0.9, color=col, label=nm)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xticks(range(len(yrs)), yrs); ax.set_ylabel("R per trade, next year")
    ax.set_title("Walk-forward: best settings of the previous 3 years, traded blind the next year", loc="left")
    ax.legend(ncol=3, loc="lower left")
    save(fig, "04_walkforward.png")


def fig_ablation():
    dv = json.load(open(os.path.join(RES, "orb_ablation.json")))["all 56 combos"]
    oo = json.load(open(os.path.join(RES, "orb_ablation_oos.json")))["all 56 combos"]
    lad = [r for r in dv if r["kind"] == "ladder" or r["variant"] == "ORB alone"]
    names = [r["variant"] for r in lad]
    om = {r["variant"]: r for r in oo}
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    y = np.arange(len(names)); h = 0.26
    ax.barh(y - h, [r["dev_E"] for r in lad], h * 0.9, color=BLUE, label="development 2011-19")
    ax.barh(y, [r["val_E"] for r in lad], h * 0.9, color=ORANGE, label="validation 2020-22")
    ax.barh(y + h, [om[n]["oos_E"] for n in names], h * 0.9, color=AQUA, label="final OOS 2023-25")
    ax.set_yticks(y, [n.replace(" ladder", "") for n in names]); ax.invert_yaxis()
    ax.axvline(0, color=INK2, lw=0.8); ax.set_xlabel("R per trade after costs (pooled over 56 market/session/ORB combos)")
    ax.set_title("Ablation: components added one at a time", loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=3)
    save(fig, "05_ablation.png")


def load_final():
    R = json.load(open(os.path.join(RES, "orb_final.json")))
    out = []
    for c in R["configs"]:
        tr = np.load(os.path.join(RES, "orb_final", f"{c['key']}_trades.npy"))
        out.append((c, tr))
    return out


def fig_equity(F):
    fig, axes = plt.subplots(len(F), 1, figsize=(7.4, 2.2 * len(F)), sharex=True)
    for ax, (c, tr) in zip(axes, F):
        ct, ce, _, _ = MT.account({c["sym"]: tr}, risk=0.005, start=100_000)
        t = [dt.datetime.fromtimestamp(int(x), dt.timezone.utc) for x in ct]
        dd = MT.drawdown(ce, 100_000)
        ax.plot(t, ce / 1000, color=BLUE, lw=1.6)
        ax.fill_between(t, (ce / 1000) * (1 + 0 * dd), (ce / 1000) / (1 + dd + 1e-12) * (1 + dd), color=BLUE, alpha=0)
        for a, b, col in (("2020-01-01", "2023-01-01", "#fdebd9"), ("2023-01-01", "2026-01-01", "#d7f1e7")):
            ax.axvspan(dt.datetime.fromisoformat(a), dt.datetime.fromisoformat(b), color=col, zorder=0, lw=0)
        ax.set_ylabel("$k")
        ax.set_title(f"{c['key']}  {c['name']}  -  {c['sym']} {c['session']} ORB{c['orb']}", loc="left", fontsize=9)
    axes[0].text(dt.datetime(2020, 3, 1), axes[0].get_ylim()[1], "validation", va="top", color=INK2, fontsize=8)
    axes[0].text(dt.datetime(2023, 3, 1), axes[0].get_ylim()[1], "final OOS", va="top", color=INK2, fontsize=8)
    fig.suptitle("Equity, $100k account risking 0.5% per trade (lot-rounded, after costs)", x=0.01, ha="left", fontweight="bold")
    save(fig, "06_equity.png")
    fig, axes = plt.subplots(len(F), 1, figsize=(7.4, 1.7 * len(F)), sharex=True)
    for ax, (c, tr) in zip(axes, F):
        ct, ce, _, _ = MT.account({c["sym"]: tr}, risk=0.005, start=100_000)
        t = [dt.datetime.fromtimestamp(int(x), dt.timezone.utc) for x in ct]
        dd = MT.drawdown(ce, 100_000) * 100
        ax.fill_between(t, dd, 0, color=RED, alpha=0.35, lw=0); ax.plot(t, dd, color=RED, lw=1)
        ax.set_ylabel("%"); ax.set_title(f"{c['key']}  drawdown (max {-dd.min():.1f}%)", loc="left", fontsize=9)
    save(fig, "07_drawdown.png")


def fig_annual_monthly(F):
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    yrs = list(range(2011, 2026)); w = 0.2
    for i, ((c, tr), col) in enumerate(zip(F, (BLUE, ORANGE, AQUA, YELLOW))):
        f = MT.full({c["sym"]: tr}, risk=0.005)
        v = [f["annual"].get(y, 0.0) * 100 for y in yrs]
        ax.bar(np.arange(len(yrs)) + (i - 1.5) * w, v, w * 0.9, color=col, label=f"{c['key']} {c['sym']} {c['session']} ORB{c['orb']}")
    ax.axhline(0, color=INK2, lw=0.8); ax.set_xticks(range(len(yrs)), yrs, rotation=0, fontsize=8)
    ax.axvspan(8.5, 11.5, color="#fdebd9", zorder=0); ax.axvspan(11.5, 14.6, color="#d7f1e7", zorder=0)
    ax.set_ylabel("annual return %"); ax.set_title("Annual returns at 0.5% risk per trade (shaded: validation, final OOS)", loc="left")
    ax.legend(ncol=2, fontsize=8, loc="upper right")
    save(fig, "08_annual.png")
    c, tr = F[3]
    f = MT.full({c["sym"]: tr}, risk=0.005)
    M = np.full((15, 12), np.nan)
    for k, v in f["monthly"].items():
        y, m = map(int, k.split("-")); M[y - 2011, m - 1] = v * 100
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    im = ax.imshow(M, cmap=DIV, vmin=-4, vmax=4, aspect="auto")
    ax.set_xticks(range(12), ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]); ax.set_yticks(range(15), range(2011, 2026))
    ax.grid(False); fig.colorbar(im, ax=ax, label="monthly return %", shrink=0.7)
    ax.set_title(f"Monthly returns - {c['key']} {c['sym']} {c['session']} ORB{c['orb']} (0.5% risk)", loc="left")
    save(fig, "09_monthly_X.png")


def fig_dist(F):
    fig, axes = plt.subplots(1, len(F), figsize=(9, 2.6), sharey=True)
    for ax, (c, tr) in zip(axes, F):
        ax.hist(tr["r"], bins=np.arange(-1.6, 6.0, 0.2), color=BLUE, edgecolor=SURF, lw=1)
        ax.axvline(tr["r"].mean(), color=RED, lw=1.2)
        ax.set_title(f"{c['key']} mean {tr['r'].mean():+.3f}R", loc="left", fontsize=9); ax.set_xlabel("R per trade")
    axes[0].set_ylabel("trades")
    fig.suptitle("Trade outcome distributions, 2011-2025 (red line = mean)", x=0.01, ha="left", fontweight="bold", y=1.05)
    save(fig, "10_trade_dist.png")


def fig_sensitivity():
    d = SEL.with_stats(SEL.load(["E2"]))
    d = d[(d.sym == "XAUUSD") & (d.session == "LDN") & (d.entry == 0) & (d.stop == 0) & (d.buf == 0.0) & (d.tgt == 0.0)]
    d["filter"] = d.bias_kind + np.where(d.bias_kind == "neutral", " z" + d.bias_z.astype(str), "")
    piv = d.pivot_table(index=["filter", "bias_ema"], columns="orb", values="E")
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw=dict(wspace=0.55))
    ax = axes[0]
    im = ax.imshow(piv.values, cmap=DIV, vmin=-0.2, vmax=0.2, aspect="auto")
    ax.set_xticks(range(len(piv.columns)), [f"ORB{c}" for c in piv.columns])
    ax.set_yticks(range(len(piv.index)), [f"{a} EMA{b}" for a, b in piv.index], fontsize=7)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            ax.text(j, i, f"{piv.values[i, j]:+.2f}", ha="center", va="center", fontsize=6.5)
    ax.grid(False); ax.set_title("Model B, gold London: dev R per trade\nby trend filter and ORB length", loc="left")
    d3 = SEL.with_stats(SEL.load(["E3"]))
    d3 = d3[(d3.sym == "XAUUSD") & (d3.session == "LDN") & (d3.orb == 5) & (d3.stop == 0) & (d3.tgt == 0.0) & (d3.bias == 1)]
    d3["pb"] = np.where(d3.entry == 3, "candles " + d3.pb_k.astype(int).astype(str) + np.where(d3.pb_hi == 1, " max", " last"),
                        "ATR " + d3.pb_atr.astype(str))
    p3 = d3.pivot_table(index="pb", columns="disp", values="E")
    ax = axes[1]
    ax.imshow(p3.values, cmap=DIV, vmin=-0.3, vmax=0.3, aspect="auto")
    ax.set_xticks(range(len(p3.columns)), [f"disp {c}" for c in p3.columns]); ax.set_yticks(range(len(p3.index)), p3.index, fontsize=8)
    for i in range(p3.shape[0]):
        for j in range(p3.shape[1]):
            ax.text(j, i, f"{p3.values[i, j]:+.2f}", ha="center", va="center", fontsize=7)
    ax.grid(False); ax.set_title("Model C, gold London ORB5: dev R per trade\nby pullback rule and displacement", loc="left")
    fig.colorbar(im, ax=axes, shrink=0.6, label="expectancy (R)")
    save(fig, "11_sensitivity.png")


def fig_periods(F):
    fig, ax = plt.subplots(figsize=(7, 3.0))
    per = ["dev 2011-19", "val 2020-22", "oos 2023-25"]; w = 0.26
    for i, (p, col) in enumerate(zip(per, (BLUE, ORANGE, AQUA))):
        v = [c["post"]["periods"][p]["E"] for c, _ in F]
        ax.bar(np.arange(len(F)) + (i - 1) * w, v, w * 0.9, color=col, label=p)
    ax.set_xticks(range(len(F)), [f"{c['key']} {c['sym']} {c['session']} ORB{c['orb']}" for c, _ in F], fontsize=8)
    ax.axhline(0, color=INK2, lw=0.8); ax.set_ylabel("R per trade after costs")
    ax.set_title("The four 'best' configurations: in-sample vs validation vs final out-of-sample", loc="left")
    ax.legend(ncol=3, loc="lower left")
    save(fig, "12_is_vs_oos_final.png")


if __name__ == "__main__":
    fig_baseline(); fig_grid_hist()
    c, top, ntop = fig_is_oos()
    fig_walkforward(); fig_ablation()
    F = load_final()
    fig_equity(F); fig_annual_monthly(F); fig_dist(F); fig_sensitivity(); fig_periods(F)
    json.dump(dict(is_oos_corr=c, top1pct_val_E=top, top1pct_n=ntop), open(os.path.join(RES, "orb_is_oos.json"), "w"))
    print("is/oos corr", c, "top1% later", top, ntop)
