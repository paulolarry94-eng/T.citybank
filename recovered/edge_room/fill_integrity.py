"""Fill integrity — what a one-minute record can and cannot honestly resolve.

The archive is one-minute OHLC, not tick. We cannot see the path inside a minute.
The corrected scanner therefore assumes the worst on every ambiguous bar: if a
single minute could have hit both the stop and the target, the trade is scored a
LOSS (backtest.py:16, true_outcomes.py). Results are a **lower bound** — the real
outcome should be no worse than what we report.

That protection has a limit. If a stop is small relative to how far price moves
inside a minute, almost every exit bar becomes ambiguous, every one is scored a
loss, and the test stops being informative. This module holds the *measured*
boundary at which that happens, so Seesare can decline honestly instead of
publishing mush.

MEASURED, 2026-07-23, over the full archive (5.5M–6.6M one-minute bars per
market: XAUUSD, EURUSD, GBPUSD, USDJPY). Share of bars whose range is large
enough to span a 1:1 trade's stop and target (an upper bound on ambiguity):

    stop = 0.5x median M1 range   ~44%     unusable
    stop = 1.0x                   ~17%     unusable
    stop = 2.0x                 3.1-5.0%   testable, disclose
    stop = 3.0x                 0.7-1.9%   testable, disclose
    stop = 5.0x                 0.1-0.5%   clean
    stop = 8.0x                <0.1%       clean

The four markets agreed to within a factor of two, so the boundary is expressed
scale-free — in multiples of the median one-minute range — and holds across all
of them. Nothing here calculates a research result; it decides only whether a
result can be trusted enough to report.
"""
from __future__ import annotations

# multiples of the median one-minute range
DECLINE_BELOW = 1.0      # ~17% of bars ambiguous — the test would be mush
DISCLOSE_BELOW = 3.0     # ~1-5% ambiguous — testable, but say so
CLEAN_AT = 5.0           # <0.5% ambiguous

# the measured table, kept alongside the boundary it justifies
MEASURED = [(0.5, 44.4), (1.0, 18.6), (2.0, 5.0), (3.0, 1.9),
            (5.0, 0.5), (8.0, 0.1), (12.0, 0.02)]
MEASURED_NOTE = ("Measured over the full one-minute archive of all four markets "
                 "(5.5–6.6 million bars each).")


def ambiguity_bound(stop_multiple: float) -> float:
    """Upper bound on the share of exit bars that could be ambiguous, from the
    measured table. Interpolated between measured points; never extrapolated
    optimistically below the smallest measured stop."""
    if stop_multiple is None or stop_multiple <= 0:
        return 100.0
    pts = MEASURED
    if stop_multiple <= pts[0][0]:
        return pts[0][1]
    if stop_multiple >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= stop_multiple <= x1:
            t = (stop_multiple - x0) / (x1 - x0)
            return round(y0 + t * (y1 - y0), 2)
    return pts[-1][1]


def verdict(stop_multiple: float) -> str:
    """'decline' | 'disclose' | 'clean' — what we may honestly do with this stop."""
    if stop_multiple is None or stop_multiple <= 0:
        return "unknown"
    if stop_multiple < DECLINE_BELOW:
        return "decline"
    if stop_multiple < DISCLOSE_BELOW:
        return "disclose"
    return "clean"


def refusal(stop_multiple: float) -> str:
    """Seesare's honest refusal — the reason, in plain language, no jargon."""
    pct = ambiguity_bound(stop_multiple)
    return ("Your stop sits inside the noise of a single minute. I only have "
            "minute-by-minute prices, so on roughly "
            f"{pct:.0f}% of exits I couldn't tell whether your stop or your "
            "target came first — and I score every one of those as a loss. I'd "
            "be handing you a number shaped by my own blind spot rather than by "
            "your idea. I won't do that. Widen the stop, or bring me a slower "
            "version of this, and I can test it properly.")


def disclosure(stop_multiple: float) -> str:
    """Stated plainly when the stop is testable but close to the boundary."""
    pct = ambiguity_bound(stop_multiple)
    return ("One thing to hold in mind: I read minute bars, not every tick. On "
            f"about {pct:.1f}% of exits a single minute could have contained both "
            "your stop and your target, and I scored every one of those as a "
            "loss. Your real result should be no worse than this.")


ASSURANCE = ("I can't see inside a minute. So when a minute could have hit both "
             "your stop and your target, I count it as a loss. What I show you "
             "is a floor, not a hope.")


# ---- evidence grade — derived from recorded numbers only (Sprint 9, Part 7) ----
def grade(observations, span_years, stop_multiple=None, has_oos=False) -> str:
    """Weak | Moderate | Strong | Institutional. Python decides, never the model.
    Graded on how much evidence there is and how cleanly it could be read."""
    if not observations or not span_years:
        return "Weak"
    n, yrs = float(observations), float(span_years)
    if stop_multiple is not None and verdict(stop_multiple) == "decline":
        return "Weak"
    per_year = n / yrs if yrs else 0
    if n >= 400 and yrs >= 10 and has_oos and per_year >= 30:
        return "Institutional"
    if n >= 200 and yrs >= 5:
        return "Strong"
    if n >= 60 and yrs >= 1.5:
        return "Moderate"
    return "Weak"
