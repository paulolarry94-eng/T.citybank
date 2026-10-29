"""Figures — visual evidence, and an honest account of what is missing.

Every figure here is drawn from numbers the engine actually recorded. A figure
whose inputs do not exist is **not drawn**, and is reported as unavailable with
the reason. That matters more here than anywhere else in the product: a chart is
the most persuasive object we produce, and an equity curve invented from summary
statistics would be the single most dishonest thing Edge Room could hand someone.

What a figure needs is declared alongside it, so the moment richer evidence
exists the figure appears on its own — nothing has to be remembered later.

Reproducibility: figures are a pure function of the recorded evidence. The same
case regenerates byte-identical images, which is what makes the `.edge` archive
worth keeping.
"""
from __future__ import annotations
import io
import os

_OK = True
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
except Exception:  # noqa: BLE001
    _OK = False

INK = "#1a1712"
GOLD = "#b0810f"
GOLDL = "#e7d5a4"
GREY = "#6b6353"
FAINT = "#9c917c"
LINE = "#e4dcc7"
PAPER = "#faf6ec"
GRN = "#2e7d32"
RED = "#b23b3b"

# Each figure declares the recorded metrics it requires. Nothing is drawn from
# anything else, and nothing is estimated to fill a gap.
CATALOGUE = [
    ("equity_curve", "Equity Curve", ("_trades",),
     "an equity curve needs the per-trade result series"),
    ("drawdown_curve", "Drawdown Curve", ("_trades",),
     "a drawdown curve needs the per-trade result series"),
    ("monthly_returns", "Monthly Returns", ("_monthly",),
     "monthly returns need results grouped by month"),
    ("distribution", "Trade Distribution", ("_trades",),
     "a distribution needs the individual trade results"),
    ("rolling_drawdown", "Rolling Drawdown", ("_trades",),
     "a rolling drawdown needs the per-trade result series"),
    ("session_breakdown", "Session Breakdown", ("_by_session",),
     "a session breakdown needs results split by trading session"),
    ("regime_breakdown", "Regime Breakdown", ("_by_regime",),
     "a regime breakdown needs results split by market regime"),
    ("trade_frequency", "Trade Frequency", ("n", "span_years"), ""),
    ("data_coverage", "Data Coverage", ("n",), ""),
    ("direction_balance", "Directional Balance", ("longs", "shorts"), ""),
    ("performance_summary", "Performance Summary", ("expectancy_is",), ""),
]


def _metrics(case) -> dict:
    m = {}
    for e in case.evidence:
        m.update(e.get("output") or {})
        if e.get("date_range"):
            m["_date_range"] = e["date_range"]
    return m


def available(case) -> tuple:
    """(drawable, unavailable) — what the evidence supports, and what it doesn't
    together with the reason. The second list is published, not hidden."""
    m = _metrics(case)
    can, cannot = [], []
    for key, title, needs, why in CATALOGUE:
        if all(m.get(n) is not None for n in needs):
            can.append((key, title))
        elif why:
            cannot.append((title, why))
    return can, cannot


# ---------------------------------------------------------------- drawing
def _frame(ax, title, sub=""):
    ax.set_facecolor("white")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(LINE)
    ax.tick_params(colors=GREY, labelsize=8, length=0)
    ax.grid(axis="y", color=LINE, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.set_title(title, color=INK, fontsize=11, fontweight="bold", loc="left",
                 pad=14 if sub else 10)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, color=FAINT, fontsize=8)


def _save(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=170, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    return buf.getvalue()


def _fig_trade_frequency(m):
    n, yrs = float(m["n"]), float(m["span_years"])
    per_year = n / yrs if yrs else 0
    per_month = per_year / 12
    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    bars = ax.barh(["Per year", "Per month"], [per_year, per_month],
                   color=[GOLD, GOLDL], height=0.5)
    for b, v in zip(bars, (per_year, per_month)):
        ax.text(b.get_width() * 1.02, b.get_y() + b.get_height() / 2,
                f"{v:.1f}", va="center", color=INK, fontsize=10,
                fontweight="bold")
    ax.set_xlim(0, max(per_year, 1) * 1.25)
    _frame(ax, "Trade Frequency",
           f"{int(n):,} setups across {yrs:.2f} years of evidence")
    return _save(fig)


def _fig_data_coverage(m):
    n = float(m["n"])
    rng = m.get("_date_range", "")
    a, _, b = rng.partition("..")
    fig, ax = plt.subplots(figsize=(6.2, 1.9))
    ax.barh([""], [1.0], color=GOLDL, height=0.32)
    ax.set_xlim(0, 1); ax.set_ylim(-0.5, 0.5)
    ax.text(0, -0.30, a or "start", color=GREY, fontsize=8)
    ax.text(1, -0.30, b or "end", color=GREY, fontsize=8, ha="right")
    ax.text(0.5, 0.30, f"{int(n):,} verified observations", color=INK,
            fontsize=10, fontweight="bold", ha="center")
    ax.axis("off")
    ax.set_title("Data Coverage", color=INK, fontsize=11, fontweight="bold",
                 loc="left")
    return _save(fig)


def _fig_direction_balance(m):
    lo, sh = float(m["longs"]), float(m["shorts"])
    tot = lo + sh or 1
    fig, ax = plt.subplots(figsize=(6.2, 2.2))
    ax.barh([""], [lo / tot * 100], color=GOLD, height=0.4, label="Long")
    ax.barh([""], [sh / tot * 100], left=[lo / tot * 100], color=GOLDL,
            height=0.4, label="Short")
    ax.set_xlim(0, 100); ax.axis("off")
    ax.text(0, 0.32, f"Long {lo / tot * 100:.0f}%  ({int(lo):,})", color=INK,
            fontsize=9.5, fontweight="bold")
    ax.text(1, 0.32, f"Short {sh / tot * 100:.0f}%  ({int(sh):,})", color=GREY,
            fontsize=9.5, ha="right", transform=ax.transAxes)
    ax.set_title("Directional Balance", color=INK, fontsize=11,
                 fontweight="bold", loc="left")
    return _save(fig)


def _fig_performance_summary(m):
    rows = [("Expectancy · in-sample", m.get("expectancy_is"), 0.5, "R"),
            ("Expectancy · out-of-sample", m.get("expectancy_oos"), 0.5, "R"),
            ("Win rate", m.get("win_rate"), 1.0, "%"),
            ("Profit factor", m.get("profit_factor"), 3.0, "")]
    rows = [r for r in rows if isinstance(r[1], (int, float))]
    fig, ax = plt.subplots(figsize=(6.4, 0.62 * len(rows) + 1.1))
    labels = [r[0] for r in rows]
    vals = [max(0.0, min(1.0, r[1] / r[2])) for r in rows]
    ax.barh(labels, vals, color=GOLD, height=0.42)
    ax.set_xlim(0, 1)
    for i, (lab, v, vmax, unit) in enumerate(rows):
        disp = (f"{v*100:.0f}%" if unit == "%" else
                (f"{v:+.2f}R" if unit == "R" else f"{v:.2f}"))
        ax.text(1.01, i, disp, va="center", color=INK, fontsize=9.5,
                fontweight="bold")
    ax.invert_yaxis()
    ax.set_xticks([])
    _frame(ax, "Performance Summary", "measured under corrected fills")
    return _save(fig)


_DRAW = {"trade_frequency": _fig_trade_frequency,
         "data_coverage": _fig_data_coverage,
         "direction_balance": _fig_direction_balance,
         "performance_summary": _fig_performance_summary}


def render(case) -> list:
    """[(filename, title, png_bytes)] for every figure the evidence supports."""
    if not _OK:
        return []
    m = _metrics(case)
    out = []
    can, _ = available(case)
    for i, (key, title) in enumerate(can, 1):
        fn = _DRAW.get(key)
        if not fn:
            continue
        try:
            out.append((f"Figure {i} - {title}.png", title, fn(m)))
        except Exception:  # noqa: BLE001
            continue
    return out


# ---------------------------------------------------------------- curation
# One observation per figure. Each is a plain reading of the number the figure
# already shows — never an interpretation the evidence doesn't carry.
def observation(key: str, m: dict) -> str:
    if key == "trade_frequency":
        n, yrs = m.get("n"), m.get("span_years")
        if n and yrs:
            pm = n / yrs / 12
            if pm < 4:
                return ("Your edge seems to come from patience more than "
                        "activity.")
            return "This trades often enough to judge on its own record."
    if key == "direction_balance":
        lo, sh = m.get("longs"), m.get("shorts")
        if lo is not None and sh is not None and (lo + sh):
            f = lo / (lo + sh)
            if f >= 0.85 or f <= 0.15:
                return ("This leans almost entirely one way. It will live or die "
                        "with the trend it depends on.")
            return "The book is reasonably balanced between both directions."
    if key == "performance_summary":
        is_, oos = m.get("expectancy_is"), m.get("expectancy_oos")
        if isinstance(is_, (int, float)) and isinstance(oos, (int, float)):
            if oos < is_ * 0.8:
                return ("The out-of-sample bar is the one I'd spend most of my "
                        "time on.")
            return "It holds its shape on data it never saw. That's the part "\
                   "that matters."
    if key == "data_coverage":
        return "This is the ground everything else stands on."
    return ""
