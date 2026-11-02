"""Builds research/goal/CYCLE_GOAL_MATH.pdf: the owner's +2-7% per cycle goal as a maths problem (2026-11-02).

Inputs (all in the repo): research/results/seesare/cycle_math_study.json (the 80-shape win/loss map), research/results/truth/
cycle_goal_survivors.json (our strategies, `python3 research/truth/cyclegoal.py --survivors`), research/results/truth/
tokyo_fix_gotobi_v1/summary.json (cost ladder). The trades-per-cycle table is simulated here (research/truth/cyclegoal.py,
needed_s_sim) and cached in research/results/goal/breadth.json.
Run: python3 research/goal/build_cycle_goal_pdf.py
"""
import os
import sys
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import cyclegoal as G   # noqa: E402

OUT_PDF = os.path.join(HERE, "CYCLE_GOAL_MATH.pdf")
RES = os.path.join(ROOT, "research", "results", "goal")
os.makedirs(RES, exist_ok=True)

# palette (dataviz reference instance, light mode)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"
TINT_IN, TINT_NEAR = "#d7e6f8", "#eef4fc"

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
pdfmetrics.registerFont(TTFont("DV", FONT)); pdfmetrics.registerFont(TTFont("DVB", FONTB))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DVB", italic="DV", boldItalic="DVB")

ST = dict(
    title=ParagraphStyle("t", fontName="DVB", fontSize=20, leading=25, textColor=INK, spaceAfter=4),
    sub=ParagraphStyle("s", fontName="DV", fontSize=10, leading=14, textColor=INK2, spaceAfter=10),
    h1=ParagraphStyle("h1", fontName="DVB", fontSize=14, leading=18, textColor=INK, spaceBefore=6, spaceAfter=6),
    h2=ParagraphStyle("h2", fontName="DVB", fontSize=11, leading=14, textColor=INK, spaceBefore=6, spaceAfter=4),
    body=ParagraphStyle("b", fontName="DV", fontSize=9.5, leading=13.5, textColor=INK, spaceAfter=5),
    small=ParagraphStyle("sm", fontName="DV", fontSize=8, leading=11, textColor=INK2, spaceAfter=4),
    box=ParagraphStyle("bx", fontName="DV", fontSize=10, leading=14.5, textColor=INK),
    cell=ParagraphStyle("c", fontName="DV", fontSize=8.5, leading=11, textColor=INK),
    cellb=ParagraphStyle("cb", fontName="DVB", fontSize=8.5, leading=11, textColor=INK),
)


def P(t, s="body"):
    return Paragraph(t, ST[s])


def table(rows, widths, header=True, shade=None, align="CENTER", first_left=True):
    data = [[c if not isinstance(c, str) else Paragraph(c, ST["cellb" if (header and i == 0) else "cell"]) for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, hAlign="LEFT")
    style = [("FONTNAME", (0, 0), (-1, -1), "DV"), ("FONTSIZE", (0, 0), (-1, -1), 8.5),
             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor(INK2)),
             ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.HexColor(GRID)),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    for (c, r), col in (shade or {}).items():
        style.append(("BACKGROUND", (c, r), (c, r), colors.HexColor(col)))
    t.setStyle(TableStyle(style))
    return t


def boxed(flowables, bg="#f3f2ee"):
    t = Table([[flowables]], colWidths=[170 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return t


# ----------------------------------------------------------------------------- data
MAP = json.load(open(os.path.join(ROOT, "research", "results", "seesare", "cycle_math_study.json")))
OURS = json.load(open(os.path.join(ROOT, "research", "results", "truth", "cycle_goal_survivors.json")))["sets"]
TOKYO = json.load(open(os.path.join(ROOT, "research", "results", "truth", "tokyo_fix_gotobi_v1", "summary.json")))
FIT = G.map_fit()
BPATH = os.path.join(RES, "breadth.json")
NS = (10, 20, 40, 80, 160)
PAIRS = ((0.02, 0.036), (0.02, 0.05), (0.07, 0.036), (0.07, 0.05))
if os.path.exists(BPATH):
    BREADTH = {int(k): v for k, v in json.load(open(BPATH)).items()}
else:
    BREADTH = {n: {f"{C * 100:g}/{D * 100:g}": round(G.needed_s_sim(C, D, n=n, sims=3000), 3) for C, D in PAIRS} for n in NS}
    json.dump(BREADTH, open(BPATH, "w"), indent=1)

LABEL = {"book_11_legs_2011_25": "11-leg book (2011-25)", "tokyo_fix_2011_25": "Tokyo fix (2011-25)",
         "eurusd_reversal_2011_25": "EURUSD reversal (2011-25)", "all_13_2011_25": "All 13 together (2011-25)",
         "book_11_legs_2026_forward": "Book, Jan-Oct 2026 (forward)"}


# ----------------------------------------------------------------------------- charts
def style_axes(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(MUTED); ax.spines[sp].set_linewidth(0.8)
    ax.tick_params(colors=INK2, labelsize=8.5, length=3, width=0.6)
    ax.grid(True, which="major", color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    ax.set_facecolor(SURF)


def chart_dd_vs_s(path):
    cells = [c for c in MAP["cells"] if c.get("feasible")]
    fig, ax = plt.subplots(figsize=(7.0, 3.9), dpi=200)
    fig.patch.set_facecolor("white"); style_axes(ax)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.scatter([c["s"] for c in cells], [c["dd_p95"] for c in cells], s=16, color=BLUE, alpha=0.75, linewidths=0,
               label="Win/loss model: 80 win-rate × payoff shapes", zorder=3)
    xs = np.geomspace(0.015, 1.7, 100)
    ax.plot(xs, FIT["a"] * xs ** (-FIT["k"]), color=BLUE, linewidth=2, zorder=2)
    pts = [(k, OURS[k]["s"], OURS[k]["for_target"]["2"]["dd95_pct"]) for k in
           ("book_11_legs_2026_forward", "book_11_legs_2011_25", "tokyo_fix_2011_25", "eurusd_reversal_2011_25")]
    ax.scatter([p[1] for p in pts], [p[2] for p in pts], s=56, color=ORANGE, edgecolors="white", linewidths=1.5,
               label="Our strategies (own trades, Exness costs + swaps)", zorder=4)
    short = {"book_11_legs_2026_forward": "Book 2026", "book_11_legs_2011_25": "Book",
             "tokyo_fix_2011_25": "Tokyo fix", "eurusd_reversal_2011_25": "EURUSD rev."}
    for k, x, y in pts:
        right = k == "book_11_legs_2026_forward"
        ax.annotate(short[k], (x, y), xytext=(7, -3) if right else (-6, -4), textcoords="offset points", fontsize=8, color=INK,
                    ha="left" if right else "right", va="top")
    for D, lab, va, f in ((3.6, "3.6% cap", "top", 0.94), (5.0, "5% cap", "bottom", 1.06)):
        ax.axhline(D, color=INK2, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
        ax.text(0.017, D * f, lab, fontsize=8, color=INK2, ha="left", va=va)
    ax.axvline(G.needed_s(0.02, 0.036), color=MUTED, linewidth=0.8, linestyle=":", zorder=1)
    ax.text(G.needed_s(0.02, 0.036) * 1.04, 300, "needed: 0.42", fontsize=8, color=INK2)
    ax.set_xlim(0.015, 1.7); ax.set_ylim(0.2, 700)
    ax.set_xticks([0.02, 0.05, 0.1, 0.2, 0.42, 1.0]); ax.set_xticklabels(["0.02", "0.05", "0.1", "0.2", "0.42", "1.0"])
    ax.set_yticks([0.5, 1, 3.6, 10, 30, 100, 400]); ax.set_yticklabels(["0.5", "1", "3.6", "10", "30", "100", "400"])
    ax.minorticks_off()
    ax.set_xlabel("Edge quality s per trade (average R ÷ spread of R, after costs)", fontsize=9, color=INK)
    ax.set_ylabel("Drawdown that 95% of lifecycles\nstay inside, % (at +2% per cycle)", fontsize=9, color=INK)
    ax.set_title("Sized for +2% per 10-trade cycle: the drawdown depends on edge quality alone", fontsize=10, color=INK, loc="left")
    ax.legend(fontsize=8, frameon=False, loc="lower left")
    fig.tight_layout(); fig.savefig(path, facecolor="white"); plt.close(fig)


def chart_needed(path):
    Cs = np.linspace(0.02, 0.07, 26)
    fig, ax = plt.subplots(figsize=(7.0, 3.4), dpi=200)
    fig.patch.set_facecolor("white"); style_axes(ax)
    ax.axhspan(0.06, 0.13, color=ORANGE, alpha=0.18, linewidth=0, label="Our verified strategies, backtest (0.06-0.13)")
    ax.axhline(0.02, color=ORANGE, linewidth=2, linestyle=(0, (4, 3)), label="Book on Jan-Oct 2026 forward data (0.02)")
    ax.plot(Cs * 100, [G.needed_s(c, 0.036) for c in Cs], color=BLUE, linewidth=2, label="Needed, 3.6% cap")
    ax.plot(Cs * 100, [G.needed_s(c, 0.05) for c in Cs], color=AQUA, linewidth=2, label="Needed, 5% cap")
    ax.text(7.05, G.needed_s(0.07, 0.036), "3.6% cap", fontsize=8, color=INK, va="center")
    ax.text(7.05, G.needed_s(0.07, 0.05), "5% cap", fontsize=8, color=INK, va="center")
    ax.set_xlim(1.9, 7.7); ax.set_ylim(0, 0.9)
    ax.set_xlabel("Target return per 10-trade cycle, %", fontsize=9, color=INK)
    ax.set_ylabel("Edge quality s needed", fontsize=9, color=INK)
    ax.set_title("What each target needs vs what we have", fontsize=10, color=INK, loc="left")
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(path, facecolor="white"); plt.close(fig)


# ----------------------------------------------------------------------------- document
def needed_rows():
    rows = [["Target per cycle", "Drawdown cap 3.6%", "5%", "6%", "8%"]]
    for C in G.TARGETS:
        rows.append([f"+{C * 100:g}%  ({C * 36 * 100:g}% per lifecycle)"] + [f"{G.needed_s(C, D):.2f}" for D in G.CAPS])
    return rows


def map_rows(C):
    tab = G.map_table(C)
    bs = (0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0)
    rows = [["Win rate"] + [f"{b:g}:1" for b in bs]]
    shade = {}
    for i, w in enumerate((0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80)):
        r = [f"{w:.0%}"]
        for j, b in enumerate(bs):
            v = tab.get((w, b))
            r.append("–" if v is None else (f"{v:.1f}" if v < 100 else f"{v:.0f}"))
            if v is not None and v <= 3.6:
                shade[(j + 1, i + 1)] = TINT_IN
            elif v is not None and v <= 5.0:
                shade[(j + 1, i + 1)] = TINT_NEAR
        rows.append(r)
    return rows, shade


def qualifying(C, D):
    tab = G.map_table(C)
    best = {}
    for (w, b), v in tab.items():
        if v is not None and v <= D * 100 and (w not in best or b < best[w][0]):
            best[w] = (b, v)
    return ", ".join(f"{w:.0%} at {b:g}:1" for w, (b, v) in sorted(best.items()) if w >= 0.35)


def tokyo_s():
    cl = TOKYO["cost_ladder"]; g = TOKYO["cycle_goal"]
    out = {}
    for prof in ("exness_zero", "roboforex_prime"):
        v = cl[prof]["2011-19"]
        out[prof] = v["t"] / math.sqrt(v["n"])
    return out, g


def build():
    c1 = os.path.join(RES, "chart_dd_vs_s.png"); c2 = os.path.join(RES, "chart_needed.png")
    chart_dd_vs_s(c1); chart_needed(c2)
    s2_36, s2_5, s7_36, s7_5 = (G.needed_s(*p) for p in PAIRS)
    book, tok, eur, all13, f26 = (OURS[k] for k in ("book_11_legs_2011_25", "tokyo_fix_2011_25", "eurusd_reversal_2011_25",
                                                    "all_13_2011_25", "book_11_legs_2026_forward"))
    sc = {n: BREADTH[n]["2/3.6"] * math.sqrt(n) for n in NS}
    rule2 = float(np.mean([sc[n] for n in NS]))
    rule7 = float(np.mean([BREADTH[n]["7/3.6"] * math.sqrt(n) for n in NS]))
    story = []

    # ---- page 1: the answer
    story += [P("The 2–7% per cycle goal as a maths problem", "title"),
              P("T.citybank · 2 November 2026 · what it takes, what we have, and what to search for", "sub"),
              boxed([P("<b>The goal, written as maths.</b> Make C = +2% to +7% per cycle (1 cycle = 10 trades), and keep the "
                       "drawdown D inside 3.6% of the starting balance (5% is acceptable) in 19 of every 20 lifecycles "
                       "(1 lifecycle = 36 cycles = 360 trades). Risk per trade is a fixed share of the start.", "box")]),
              Spacer(1, 8),
              P("<b>The answer.</b> Only one property of a strategy decides whether this is possible: its <b>edge quality</b> "
                "s = average result per trade ÷ how much single trades swing (both in R, after all costs). Sizing and ladders change "
                "how deep the dips are, not whether the target fits under the cap; mixing strategies helps only by adding "
                "independent trades to a cycle (section 6)."),
              table([["", "Needed edge quality s", "We have (best backtest)", "We have (2026 forward)"],
                     ["+2% per cycle inside 3.6%", f"{s2_36:.2f}", f"{eur['s']:.2f}", f"{f26['s']:.2f}"],
                     ["+2% per cycle inside 5%", f"{s2_5:.2f}", f"{eur['s']:.2f}", f"{f26['s']:.2f}"],
                     ["+7% per cycle inside 3.6%", f"{s7_36:.2f}", f"{eur['s']:.2f}", f"{f26['s']:.2f}"],
                     ["+7% per cycle inside 5%", f"{s7_5:.2f}", f"{eur['s']:.2f}", f"{f26['s']:.2f}"]],
                    [62 * mm, 38 * mm, 38 * mm, 34 * mm]),
              Spacer(1, 8),
              P(f"<b>The gap.</b> Our best verified strategy (EURUSD reversal, s {eur['s']:.2f}) is {s2_36 / eur['s']:.1f} times short "
                f"of the easiest target; the 11-leg book (s {book['s']:.3f}) is {s2_36 / book['s']:.1f} times short; on untouched "
                f"2026 data the book ran at s {f26['s']:.2f}, about {s2_36 / f26['s']:.0f} times short."),
              P(f"<b>The one rule to remember.</b> Edge quality × √(independent trades per cycle) ≥ {rule2:.1f} for +2% inside "
                f"3.6%, and ≥ {rule7:.1f} for +7%. With 10 trades per cycle that means s ≥ {s2_36:.2f}. A cycle with more "
                "independent trades (for example a fortnight across many unrelated strategies) lowers the bar per trade."),
              boxed([P("<b>What to search for.</b> A trade rule that, after all costs, makes about 70% winners at 1:1, or 55% at 2:1, "
                       "or 45% at 3:1, or 40% at 4:1 (each is s ≈ 0.4), with a named payer who must trade in a known direction; "
                       "or a set of independent rules that together reach the rule above. Because live results run 30-50% "
                       "weaker than backtests (P11), aim for s ≈ 0.6 or more in the backtest.", "box")], bg="#e9f1fb"),
              PageBreak()]

    # ---- page 2: words
    story += [P("1. The words, defined once", "h1"),
              table([["Word", "Meaning", "Example"],
                     ["R", "The amount a trade risks (entry to stop). Results are counted in R.", "Risk $10: +$20 is +2R"],
                     ["Win rate w", "Share of trades that end in profit.", "55%"],
                     ["Payoff b", "Average win ÷ average loss.", "2:1"],
                     ["Average R (μ)", "Mean result per trade after costs: μ = w × b − (1 − w) for a win/loss rule.", "0.55×2 − 0.45 = +0.65R"],
                     ["Spread of R (σ)", "How much single results swing around the average (standard deviation).", "(b+1)×√(w(1−w)) = 1.49R"],
                     ["Edge quality s", "μ ÷ σ: profit per unit of swing. The per-trade Sharpe ratio.", "0.65 ÷ 1.49 = 0.44"],
                     ["Risk r", "Share of the starting balance risked on each trade.", "0.31%"],
                     ["Cycle", "10 trades (owner's unit).", ""],
                     ["Lifecycle", "36 cycles = 360 trades; drawdown is measured inside it.", ""],
                     ["Drawdown D", "Largest fall from a running high, % of the starting balance.", "3.6%"],
                     ["95% drawdown", "The drawdown that 19 of 20 lifecycles stay inside.", ""]],
                    [30 * mm, 95 * mm, 45 * mm]),
              PageBreak(),
              P("2. The maths in four steps", "h1"),
              P("<b>Step 1, the return.</b> A cycle of n trades returns C = n × r × μ. So a target fixes the risk: r = C ÷ (n × μ). "
                "Example: +2% with n = 10 and μ = 0.65R needs r = 0.31% per trade."),
              P("<b>Step 2, the dips.</b> A run of trades wanders around its average. The depth of the dips, in R, grows with "
                "the swing squared and shrinks with the drift: about σ² ÷ μ. In % of the balance it is r × σ² ÷ μ."),
              P("<b>Step 3, put them together.</b> Replace r from step 1: drawdown ≈ (C ÷ n) × σ² ÷ μ² = (C ÷ n) ÷ s². "
                "The return target and the edge quality alone set the drawdown; risk size has already been used up by the target."),
              P("<b>Step 4, exact numbers.</b> A random walk with drift falls D below a peak with probability about "
                "exp(−2 × n × s² × D ÷ C). A lifecycle has many peaks, so the exact figure comes from simulation: 20,000 "
                f"lifecycles for each of 80 win-rate × payoff shapes. At +2% per cycle the 95% drawdown is about "
                f"{FIT['a']:.2f}% × s^−{FIT['k']:.2f}, and it grows in proportion to the target (twice the target, twice the drawdown)."),
              Image(c1, width=170 * mm, height=170 * mm * 3.9 / 7.0),
              P("Read it like this: pick a cap on the vertical axis, go across to the blue line, and read down the edge quality "
                "you need. Every model shape, whatever its win rate or payoff, falls on the same line. Our strategies fall on it "
                "too, far to the left.", "small"),
              PageBreak()]

    # ---- page 3: needed table + chart
    story += [P("3. Edge quality needed for each target", "h1"),
              P("95% of lifecycles inside the cap; 10 trades per cycle; after costs. The lifecycle return is 36 × the cycle return."),
              table(needed_rows(), [52 * mm, 32 * mm, 28 * mm, 28 * mm, 28 * mm]),
              Spacer(1, 8),
              Image(c2, width=170 * mm, height=170 * mm * 3.4 / 7.0),
              P("The orange band is everything we have verified, in backtest. The dashed orange line is the book on untouched "
                "2026 data. Both lines that matter sit well above it.", "small"),
              PageBreak()]

    # ---- page 4: map
    rows, shade = map_rows(0.02)
    story += [P("4. What a qualifying strategy looks like", "h1"),
              P("Each cell is a trade rule with that win rate and payoff (after costs), sized for +2% per cycle. The number is "
                "the drawdown that 95% of lifecycles stay inside. Dark cells fit 3.6%; light cells fit 5%; – means no profit."),
              table(rows, [24 * mm] + [20.8 * mm] * 7, shade=shade),
              Spacer(1, 8),
              P("<b>Cheapest shapes per win rate</b> (smallest payoff that fits):", "h2"),
              table([["Target, cap", "Win rate at payoff (after costs)"],
                     ["+2%, 3.6%", qualifying(0.02, 0.036)], ["+2%, 5%", qualifying(0.02, 0.05)],
                     ["+3%, 3.6%", qualifying(0.03, 0.036)], ["+5%, 5%", qualifying(0.05, 0.05)],
                     ["+7%, 3.6%", qualifying(0.07, 0.036)], ["+7%, 5%", qualifying(0.07, 0.05)]],
                    [26 * mm, 144 * mm]),
              Spacer(1, 6),
              P("Payoff 5:1 is the largest shape in the map, so higher targets can only show shapes up to 5:1. A shape "
                "like 40% at 4:1 means: 4 of 10 trades win four times what the losers lose, every cycle, after costs."),
              P("<b>With the drawdown-keyed ladder</b> (built in Phase 5): the cap can never be broken, but losing streaks walk "
                "a lifecycle into the 3.6% wall and stop it. At the ladder's maximum weight, high win rates finish and low-win, "
                "big-payoff rules stop: 75% at 0.75:1 had a median +1.99% per cycle with 5% of lifecycles stopped; 40% at 4:1 "
                "stopped 95% of lifecycles. Lower weights were not tested.", "small"),
              PageBreak()]

    # ---- page 5: where we are
    ts, _ = tokyo_s()
    rows = [["Strategy", "Trades", "Win rate", "Edge quality s", "Cycle at 3.6% cap", "at 5%", "at 8%", "Short by"]]
    for k in ("book_11_legs_2011_25", "tokyo_fix_2011_25", "eurusd_reversal_2011_25", "all_13_2011_25", "book_11_legs_2026_forward"):
        v = OURS[k]; cm = v["cycle_mean_pct_at_cap"]
        rows.append([LABEL[k], f"{v['trades']:,}", f"{v['win_rate']:.0%}", f"{v['s']:.3f}", f"{cm['3.6']:+.2f}%",
                     f"{cm['5']:+.2f}%", f"{cm['8']:+.2f}%", f"× {v['gap_2pct_at_3.6']}"])
    story += [P("5. Where we are", "h1"),
              P("Our own trades, every signal at 1R, Exness Zero costs and swaps. 2011-25 has been seen before; Jan-Oct 2026 is "
                "the only clean forward data. \"Cycle at 3.6% cap\" is the average cycle when risk is set so that 95% of "
                "lifecycles stay inside 3.6% (block bootstrap of the strategy's own trades)."),
              table(rows, [44 * mm, 15 * mm, 14 * mm, 20 * mm, 22 * mm, 17 * mm, 17 * mm, 17 * mm]),
              Spacer(1, 8),
              P(f"<b>Forcing it.</b> Making the book earn +2% per cycle anyway needs {book['for_target']['2']['risk_pct']:.1f}% risk "
                f"per trade, and then 95% of lifecycles stay inside a {book['for_target']['2']['dd95_pct']:.0f}% drawdown, not 3.6%."),
              P(f"<b>Mixing does not help per trade.</b> All 13 strategies together score s {all13['s']:.3f}, the same as the "
                f"book alone ({book['s']:.3f}). Mixing gives more trades per week, not better trades."),
              P(f"<b>Cheaper prices help a real edge a little.</b> The Tokyo fix in 2011-19 goes from s {ts['exness_zero']:.2f} at "
                f"Exness Zero prices to s {ts['roboforex_prime']:.2f} at RoboForex Prime's published prices (0.65 pip instead of 1.35). "
                "That is still about 4 times short. Cheaper prices do nothing for a rule with no gross edge (the ECB fix: gross ≈ 0)."),
              Spacer(1, 8)]

    # ---- page 6: two dials
    rows = [["Independent trades per cycle", "+2% inside 3.6%", "+2% inside 5%", "+7% inside 3.6%", "+7% inside 5%"]]
    for n in NS:
        b = BREADTH[n]
        rows.append([f"{n}"] + [f"{b[k]:.2f}" for k in ("2/3.6", "2/5", "7/3.6", "7/5")])
    nbook = (rule2 / book["s"]) ** 2
    story += [KeepTogether([P("6. The two dials: quality and breadth", "h1"),
              P("If a cycle is a period of time (say a fortnight) instead of 10 trades, more independent trades fit in it, and "
                "each one can be weaker. Simulation with 36 cycles per lifecycle and trades of normal shape:"),
              table(rows, [50 * mm, 30 * mm, 30 * mm, 30 * mm, 30 * mm])]),
              Spacer(1, 6),
              P(f"Edge quality × √n stays about {rule2:.1f} (+2% inside 3.6%) and {rule7:.1f} (+7% inside 3.6%) whatever n is. "
                f"So the book (s {book['s']:.3f}) would need about {nbook:,.0f} truly independent trades per cycle. The book makes "
                "about 400 trades a year, many of them related (same market, same trend), so a fortnight holds about 16."),
              P("<b>Independent</b> means a trade's result tells you nothing about the others: different payers, different "
                "markets or different timing. Five copies of one trend bet on five correlated markets count as about one trade."),
              PageBreak(),
              P("7. What moves edge quality, and what does not (evidence from the lab)", "h1"),
              table([["Does NOT raise s", "Evidence"],
                     ["Mixing the strategies we have", "All 13: s 0.063 vs book 0.062 (cycle_goal_survivors.json)"],
                     ["Sizing ladders, streak rules, drawdown keys", "Change dips and speed, not s (P8, P26, P27, P28)"],
                     ["Breakeven and scratch stops", "Backtest mirage (P4); costs eat micro-stops (Q21)"],
                     ["A bigger target on the same entries", "Tokyo fix: a 7:1 target is reached on 0.1-3.3% of mornings"],
                     ["Chart shapes on any timeframe or session", "About 300,000 configurations rejected after costs (P21)"],
                     ["A cheaper broker without a gross edge", "ECB fix: gross ≈ 0 pip; costs only decide the size of the loss"]],
                    [70 * mm, 100 * mm]),
              Spacer(1, 6),
              table([["CAN raise s", "How"],
                     ["A payer with a known direction", "Who must trade, when, and which way (P22): the Tokyo fix is our only one so far"],
                     ["Lower costs on a real edge", f"RoboForex Prime vs Exness on the Tokyo fix: s {ts['exness_zero']:.2f} to {ts['roboforex_prime']:.2f}"],
                     ["Selectivity decided in advance", "Take only the best setups by a rule fixed before testing; fewer trades, higher s"],
                     ["Higher timeframes", "Costs are a smaller share of R (P3)"],
                     ["More independent trades per cycle", "Dial 2 above, if the cycle becomes a period of time"]],
                    [70 * mm, 100 * mm]),
              Spacer(1, 10)]

    # ---- page 7: search spec + proof
    story += [KeepTogether([P("8. The search sheet: lock onto this", "h1")]),
              boxed([P("<b>For any new idea, answer these before testing:</b><br/>"
                       "1. Who loses money to me, and why must they trade? Which direction?<br/>"
                       "2. After all costs and swaps, what are the win rate and the payoff? What is s?<br/>"
                       "3. Is s at least 0.45 (target 0.6 in backtest, because live runs 30-50% weaker)?<br/>"
                       "4. If not, how many independent trades per cycle does it add, and is s × √n at least 1.4?<br/>"
                       "5. Is it independent of the book and the Tokyo fix (different payer, market or time)?<br/>"
                       "6. Can it be written as fixed rules and passed through the Truth Lab with one look at 2023-25?", "box")],
                    bg="#e9f1fb"),
              Spacer(1, 8),
              P("How many trades prove it?", "h2"),
              table([["True edge quality s", "Trades for t = 3 on average", "Lab gate (development 2011-19)"],
                     ["0.10", f"{G.trades_to_prove(0.10)}", "200 trades minimum"],
                     ["0.25", f"{G.trades_to_prove(0.25)}", "200 trades minimum"],
                     ["0.45", f"{G.trades_to_prove(0.45)}", "200 trades minimum"],
                     ["0.80", f"{G.trades_to_prove(0.80)}", "200 trades minimum"]],
                    [50 * mm, 55 * mm, 65 * mm]),
              Spacer(1, 4),
              P("A strong edge is quick to see: s = 0.45 shows itself in about 45 trades, while the book's 0.06 needs about 2,300. "
                "That is also why a big claimed edge that needs thousands of trades to show is a warning sign."),
              P("What the lab now reports for every candidate", "h2"),
              P("Every Truth Lab report now ends with a <b>cycle goal</b> table (edge quality per period, the cycle at a 3.6%, 5% "
                "and 8% cap, and how many times short of +2% it is) and a <b>cost ladder</b> (the same trades at gross, RoboForex "
                "Prime, Exness Zero and lab prices). Any trade list can be scored with "
                "<font face='DV'>python3 research/truth/cyclegoal.py --trades file.csv</font>."),
              PageBreak()]

    # ---- page 8: EA build and verify
    story += [P("9. Building and verifying the EA here: what it would take", "h1"),
              P("Today every MQL5 file except TimelessCity is uncompiled source. Checked in this cloud session on 2 November 2026:"),
              table([["Step", "Status here", "What it needs"],
                     ["Wine (runs Windows programs on Linux)", "Installed: Wine 9.0 from Ubuntu's archive", "Nothing more"],
                     ["MetaTrader 5 installer", "Downloaded from MetaQuotes (mt5setup.exe, 23.8 MB, 64-bit)", "Nothing more"],
                     ["Run the installer", "Blocked by this session's safety check: it runs third-party software", "Your OK to run it"],
                     ["Compile every .mq5 with MetaEditor", "Not tried yet (needs the step above)", "MetaEditor's command-line compile under Wine; "
                      "compiler errors come back as a log I can read and fix"],
                     ["Run the self-test scripts and the Strategy Tester", "Not tried", "A demo account login (saved as an environment "
                      "secret) and a network path from MT5 to the broker's servers; unknown whether this environment's proxy allows MT5's "
                      "connection"],
                     ["Parity check vs the lab", "Tool exists (tools/parity_check.py)", "Tester trade logs from the step above"]],
                    [45 * mm, 55 * mm, 70 * mm]),
              Spacer(1, 8),
              P("Three ways to do it", "h2"),
              table([["Option", "Compile", "Tester and parity", "Effort"],
                     ["This cloud environment (Wine)", "Likely, once allowed", "Uncertain: needs a broker login and network access",
                      "Setup script reinstalls Wine and MT5 each new session (a few minutes)"],
                     ["GitHub Actions Windows runner", "Yes (MetaEditor runs on Windows)", "Yes with a demo login stored as a secret",
                      "One workflow file; runs on each push; free minutes are limited"],
                     ["Your PC or a Windows VPS", "Yes", "Yes, the normal way", "You run it and send logs back, or a Linux VPS with "
                      "Wine can be connected to sessions by Remote Control (Mac and Linux only)"]],
                    [38 * mm, 32 * mm, 52 * mm, 48 * mm]),
              Spacer(1, 6),
              P("Suggested order: allow the installer here and compile everything (turns \"uncompiled source\" into compiler-checked "
                "code); then put the Strategy Tester and parity runs on a GitHub Actions Windows runner or a VPS with a RoboForex "
                "Prime demo account."),
              Spacer(1, 10),
              P("Appendix: sources in the repo", "h2"),
              P("Model and map: research/seesare/cycle_math_study.py → research/results/seesare/cycle_math_study.json (80 shapes × "
                "20,000 lifecycles). Calculator: research/truth/cyclegoal.py (tests: research/truth/tests/test_cyclegoal.py). "
                "Our strategies: research/results/truth/cycle_goal_survivors.json. Trades-per-cycle table: research/results/goal/"
                "breadth.json. Principles P4, P8, P11, P21, P22, P26-P28: research/truth/memory/PRINCIPLES.md. This document: "
                "research/goal/build_cycle_goal_pdf.py. All figures are after costs; the model assumes independent trades with a "
                "known, steady edge, so real drawdowns run larger.", "small")]

    def footer(canvas, doc):
        canvas.saveState(); canvas.setFont("DV", 7.5); canvas.setFillColor(colors.HexColor(MUTED))
        canvas.drawString(20 * mm, 10 * mm, "T.citybank · the 2–7% per cycle goal · 2 Nov 2026")
        canvas.drawRightString(190 * mm, 10 * mm, f"page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(OUT_PDF, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                            title="The 2-7% per cycle goal as a maths problem", author="T.citybank research")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("wrote", OUT_PDF)


if __name__ == "__main__":
    build()
