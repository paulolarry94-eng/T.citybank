"""The commission boundary — where an investigation honestly ends, and when it
may expand.

Constitutional law:

    An investigation ends when the available evidence has been honestly
    exhausted. It expands only when additional evidence can materially improve
    the conclusion.

Two ideas are kept strictly apart here, because conflating them is how research
products turn into funnels:

  * the **verdict** is about the strategy — did it support what the client is
    trying to achieve?
  * the **evidence boundary** is about the archive — what this record simply
    cannot speak to, regardless of how good the strategy is.

A strategy can support its objective on evidence that remains narrow. Saying so
plainly is the whole point. The boundary is never phrased as a weakness of the
idea, and a continuation is never offered unless it would genuinely change what
we could conclude.

Nothing here calculates research. The engine's verdict is frozen; this module
reads it, reads the client's stated objective, and decides what may honestly be
said and offered next.
"""
from __future__ import annotations

import casefile
import dataset
import fill_integrity

# ---- the three outcomes a client actually cares about -----------------------
SUPPORTS = "Supports Objective"
NEEDS_EVIDENCE = "Needs More Evidence"
DOES_NOT_SUPPORT = "Does Not Support Objective"

# how often a strategy must trade to be capable of a monthly income objective.
# Not a performance claim — an arithmetic feasibility floor.
INCOME_MIN_TRADES_PER_MONTH = 4.0


def _metrics(case) -> dict:
    m = {}
    for e in case.evidence:
        m.update(e.get("output") or {})
    return m


def trades_per_month(case):
    m = _metrics(case)
    n, yrs = m.get("n"), m.get("span_years")
    if isinstance(n, (int, float)) and isinstance(yrs, (int, float)) and yrs > 0:
        return round(n / (yrs * 12.0), 2)
    return None


# ---------------------------------------------------------------- the verdict
def objective_verdict(case) -> dict:
    """Map the engine's frozen label, plus the client's objective, onto one of
    three plain outcomes. The mapping is deterministic and stated; the engine's
    own verdict is never overridden, only translated into the client's terms."""
    label = (case.verdict or {}).get("label", "")
    obj = casefile.objective(case.id)
    tpm = trades_per_month(case)

    if label == "REJECTED":
        return {"verdict": DOES_NOT_SUPPORT,
                "because": "The evidence does not support this idea as it stands."}

    if label in ("APPROVED", "PROMISING"):
        # a positive result can still fail the client's actual objective, and
        # saying so is more useful than a compliment
        if obj == "income" and tpm is not None and tpm < INCOME_MIN_TRADES_PER_MONTH:
            return {"verdict": NEEDS_EVIDENCE,
                    "because": (f"The idea holds up, but at about {tpm:.1f} trades a "
                                "month it is unlikely on its own to produce income "
                                "you could rely on.")}
        return {"verdict": SUPPORTS,
                "because": "On the evidence examined, the idea does what you asked "
                           "of it."}

    return {"verdict": NEEDS_EVIDENCE,
            "because": "The evidence examined is not sufficient to settle this "
                       "either way."}


# ---------------------------------------------------------------- the boundary
def evidence_boundary(case) -> dict:
    """What this record cannot speak to. Always present, always about the
    evidence — never about the strategy."""
    stg = dataset.stage_of(case.id)
    m = _metrics(case)
    yrs = m.get("span_years")
    n = m.get("n")
    limits = []

    if stg == dataset.ASSESSMENT:
        headline = ("This conclusion rests on approximately two years of historical "
                    "evidence. It does not represent a complete market cycle.")
        limits.append("A rate-hiking cycle and its reversal are outside this window.")
        limits.append("A volatility shock on the scale of 2020 is outside this window.")
    else:
        headline = (f"This conclusion rests on the complete institutional archive"
                    + (f" — about {yrs:.1f} years of evidence." if isinstance(yrs, (int, float))
                       else "."))
    if isinstance(n, (int, float)) and isinstance(yrs, (int, float)) and yrs > 0:
        if n / yrs < 120:
            limits.append(f"The record is sparse — about {n / yrs:.0f} setups a year — "
                          "so a single unusual stretch carries real weight.")
    if "expectancy_oos" not in m:
        limits.append("The idea has not yet been scored on data it never saw.")
    if len({e.get("parameters", {}).get("instrument") for e in case.evidence
            if e.get("parameters", {}).get("instrument")}) <= 1:
        limits.append("Only one market has been examined, so nothing here shows "
                      "whether the behaviour travels.")
    limits.append(fill_integrity.ASSURANCE)
    return {"headline": headline, "limits": limits}


# ---------------------------------------------------------------- continuation
# Each continuation states the evidence gap it closes AND the objective it
# serves. If it cannot state both, it is not offered.
def continuations(case) -> list:
    obj = casefile.objective(case.id)
    m = _metrics(case)
    stg = dataset.stage_of(case.id)
    v = objective_verdict(case)["verdict"]
    tpm = trades_per_month(case)
    out = []

    # a settled negative is not a sales opportunity
    if v == DOES_NOT_SUPPORT:
        return []

    if obj == "income" and tpm is not None and tpm < INCOME_MIN_TRADES_PER_MONTH:
        out.append({
            "title": "Investigate whether a second strategy complements this one",
            "why": (f"You're aiming for monthly income, and this trades about "
                    f"{tpm:.1f} times a month. One strategy may not be enough to "
                    "produce that reliably."),
            "kind": "strategy"})

    if len({e.get("parameters", {}).get("instrument") for e in case.evidence
            if e.get("parameters", {}).get("instrument")}) <= 1:
        why = ("Nothing here shows whether this behaviour travels. If it holds on "
               "another market, that is real evidence; if it doesn't, that is too.")
        if obj == "preservation":
            why = ("You're aiming to preserve capital. A single market is a single "
                   "point of failure, so I'd want to see this on another before "
                   "anything is deployed.")
        out.append({"title": "Investigate another market", "why": why, "kind": "market"})

    if stg == dataset.ASSESSMENT:
        out.append({
            "title": "Extend the evidence to the complete archive",
            "why": ("Two years cannot contain a full market cycle. The complete "
                    "archive would show how this behaves through conditions this "
                    "window never saw."),
            "kind": "archive"})

    if obj == "growth" or "expectancy_is" in m:
        out.append({
            "title": "Parameter Stability Investigation",
            "why": ("A result that exists at exactly one setting is usually luck. "
                    "This examines whether the behaviour survives across the "
                    "neighbouring settings."),
            "kind": "stability"})

    return out


def should_close(case) -> dict:
    """Whether the Institution should simply end the case. Trust is worth more
    than another commission."""
    v = objective_verdict(case)["verdict"]
    if v == DOES_NOT_SUPPORT:
        return {"close": True,
                "reason": ("Additional investigation is unlikely to materially "
                           "change today's conclusion. I'd set this one aside "
                           "rather than spend more on it.")}
    if not continuations(case):
        return {"close": True,
                "reason": ("I've documented everything the available evidence "
                           "supports. There's nothing further I could test that "
                           "would change what we know.")}
    return {"close": False, "reason": ""}


def closure_line(case) -> str:
    return ("Our investigation is complete. I've documented everything the "
            "available evidence supports. Your case is ready to archive.")


# ---------------------------------------------------------------- review mode
_DRIFT_FIELDS = (("stop logic", ("stop", "sl", "atr")),
                 ("entry logic", ("entry", "breakout", "cross", "trigger", "enter")),
                 ("trade window", ("session", "window", "hour", "time", "london",
                                   "new york", "asia")),
                 ("targets", ("target", "tp", "1:1", "1:2", "reward")),
                 ("risk", ("risk", "%", "sizing", "lot")))


def _facet_text(rules, claim=""):
    return " ".join([claim] + list(rules or [])).lower()


def drift(previous_doc: dict, current_rules, current_claim="") -> dict:
    """Deterministic comparison between an archived case and the strategy as it
    stands now. Same inputs always give the same answer — no model involved."""
    prev = previous_doc.get("strategy", {}) if previous_doc else {}
    a = _facet_text(prev.get("rules", []), prev.get("claim", ""))
    b = _facet_text(current_rules, current_claim)
    changes, checked = [], 0
    for name, keys in _DRIFT_FIELDS:
        pa = {k for k in keys if k in a}
        pb = {k for k in keys if k in b}
        if not pa and not pb:
            continue                       # the facet was never specified either side
        checked += 1
        if pa != pb:
            changes.append(f"{name} changed")
        else:
            changes.append(f"{name} unchanged")
    changed = sum(1 for c in changes if c.endswith("changed")
                  and not c.endswith("unchanged"))
    pct = round(changed / checked * 100) if checked else 0
    return {"changes": changes, "drift_pct": pct,
            "material": pct >= 40,
            "verdict": ("The idea has moved enough that the earlier evidence no "
                        "longer describes it. I'd investigate it afresh."
                        if pct >= 40 else
                        "The idea is close enough to the one we investigated that "
                        "the earlier evidence still applies.")}
