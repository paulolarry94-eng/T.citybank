"""The one observation worth remembering — derived, never invented.

Every completed investigation *attempts* to leave the client with a single useful
remark. The rule that governs this module is absolute: an observation may only
restate what the recorded evidence actually shows. Each candidate below reads
real numbers off the Case's evidence, and every figure it prints is one the
engine measured. If nothing in the record genuinely warrants a remark, this
module returns nothing — silence is the honest answer, and preferable to a
manufactured insight.

Nothing here computes new research. It reinterprets, in plain language, numbers
the frozen engine already produced.
"""
from __future__ import annotations


def _metrics(case) -> dict:
    """The most complete set of recorded metrics across the case's evidence."""
    m = {}
    for e in case.evidence:
        for k, v in (e.get("output") or {}).items():
            if not str(k).startswith("_"):
                m[k] = v
    return m


def _num(m, key):
    v = m.get(key)
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def candidates(case) -> list:
    """Every observation the recorded evidence genuinely supports, strongest
    first. Each is a plain restatement of a measured number."""
    m = _metrics(case)
    out = []

    # 1. Winners barely larger than losers -> sizing outranks entry accuracy.
    wr, pf = _num(m, "win_rate"), _num(m, "profit_factor")
    if wr is not None and pf is not None and wr > 0.5 and pf < 2.0:
        loss_share = 1 - wr
        # average win / average loss implied by the two recorded figures
        if loss_share > 0 and wr > 0:
            rr = pf * loss_share / wr
            if rr < 1.5:
                out.append(
                    (95, f"You win {wr*100:.0f}% of the time, yet the profit factor "
                         f"is only {pf:.2f} — each winner is worth roughly "
                         f"{rr:.2f} of a loser. On this record, how much you risk "
                         "would move the outcome more than how well you enter."))

    # 2. The edge decays out of sample.
    is_, oos = _num(m, "expectancy_is"), _num(m, "expectancy_oos")
    if is_ is not None and oos is not None and is_ > 0:
        drop = (is_ - oos) / abs(is_) if is_ else 0
        if drop >= 0.10:
            out.append(
                (90, f"The edge is weaker on data it never saw: {is_:+.2f}R "
                     f"in-sample against {oos:+.2f}R out — about {drop*100:.0f}% of "
                     "it does not survive the move. That gap, not the headline "
                     "number, is what deserves your attention."))
        elif oos > 0:
            out.append(
                (70, f"The edge holds its shape out of sample — {is_:+.2f}R "
                     f"in-sample against {oos:+.2f}R out. That consistency matters "
                     "more than the size of either number."))

    # 3. A one-sided book: this is a directional bet, not a two-sided edge.
    lf = _num(m, "long_frac")
    n = _num(m, "n")
    if lf is not None and (lf >= 0.85 or lf <= 0.15):
        side = "long" if lf >= 0.85 else "short"
        pct = lf * 100 if side == "long" else (1 - lf) * 100
        out.append(
            (85, f"{pct:.0f}% of these setups were {side}. That makes this a "
                 f"directional position on the market rather than a two-sided "
                 "edge — it will live or die with the trend it leans on."))

    # 4. A thin record: how often the idea actually trades.
    span = _num(m, "span_years")
    if n is not None and span and span > 0:
        per_year = n / span
        if per_year < 120:
            days = 365.0 / per_year if per_year else 0
            out.append(
                (80, f"{int(n)} setups across {span:.1f} years is roughly one every "
                     f"{days:.0f} days. A record this sparse can be shaped by a "
                     "single unusual stretch, so its span matters as much as its "
                     "size."))

    out.sort(key=lambda x: -x[0])
    return [text for _, text in out]


def observation(case) -> str:
    """The single most useful remark the evidence supports — or "" if none does."""
    c = candidates(case)
    return c[0] if c else ""
