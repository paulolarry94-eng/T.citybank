"""The Institution's memory — anonymous evidence, never people.

Every completed investigation contributes ONE record. It carries what was
investigated and what happened; it never carries who asked, what they typed, or
anything they uploaded. Seesare does not remember clients. The institution
remembers patterns.

Two rules govern this file:

  1. Nothing personal is ever written. `record()` builds its row from a fixed
     whitelist of fields; anything else is dropped, so a future caller cannot
     accidentally leak a claim, a message or an id into the archive.
  2. Nothing is ever displayed unless enough cases support it. Every query
     returns None below `MIN_SAMPLE`. Silence beats fiction.

Statistics here are counts over real completed cases. No model touches them.
"""
from __future__ import annotations
import json
import os
import threading
from datetime import datetime

INSTITUTION_VERSION = "1.0"

# below this, a percentage is noise dressed as knowledge
MIN_SAMPLE = 30
MIN_SAMPLE_SIMILAR = 12

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "institution")
os.makedirs(_DIR, exist_ok=True)
_PATH = os.path.join(_DIR, "prior_art.jsonl")
_FIRSTS = os.path.join(_DIR, "firsts.json")
_LOCK = threading.Lock()

# the ONLY fields that may ever be written. Anything else is dropped.
_ALLOWED = ("institution_version", "case", "market", "objective", "architecture",
            "verdict", "primary_failure", "secondary_failure", "confidence",
            "observations", "years", "evidence_grade", "stage", "recorded")

# a value must never be free text a client wrote — these are closed vocabularies
_FAILURES = ("Sparse Historical Density", "Negative Out-of-Sample",
             "Unvalidated Fills", "Single Instrument", "Untested Robustness",
             "Costs Not Charged", "Risk Of Ruin Unestablished", "")


def _sanitise(rec: dict) -> dict:
    out = {k: rec.get(k) for k in _ALLOWED if k in rec}
    # numbers stay numbers; everything else is coerced to a short plain string
    for k, v in list(out.items()):
        if k in ("confidence", "observations", "years"):
            out[k] = v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
        elif v is not None:
            out[k] = str(v)[:64]
    return out


def record(*, case_ref, market, objective, architecture, verdict, primary_failure="",
           secondary_failure="", confidence=None, observations=None, years=None,
           evidence_grade="", stage="") -> dict:
    """Write one anonymous row for a completed investigation."""
    row = _sanitise({
        "institution_version": INSTITUTION_VERSION,
        "case": str(case_ref).replace("Case-", ""),
        "market": market, "objective": objective, "architecture": architecture,
        "verdict": verdict,
        "primary_failure": primary_failure if primary_failure in _FAILURES else "",
        "secondary_failure": secondary_failure if secondary_failure in _FAILURES else "",
        "confidence": confidence, "observations": observations, "years": years,
        "evidence_grade": evidence_grade, "stage": stage,
        "recorded": datetime.now().strftime("%Y-%m-%d"),
    })
    with _LOCK:
        with open(_PATH, "a") as f:
            f.write(json.dumps(row) + "\n")
    _update_firsts(row)
    return row


def all_records() -> list:
    try:
        with open(_PATH) as f:
            return [json.loads(ln) for ln in f if ln.strip()]
    except (OSError, ValueError):
        return []


# ---------------------------------------------------------------- queries
def _mode(values):
    vals = [v for v in values if v]
    if not vals:
        return ""
    return max(set(vals), key=vals.count)


def similar(market="", objective="", architecture="") -> dict | None:
    """Prior art for an investigation like this one. None if too few to speak."""
    rows = all_records()
    hits = [r for r in rows
            if (not market or r.get("market") == market)
            and (not objective or r.get("objective") == objective)]
    if len(hits) < MIN_SAMPLE_SIMILAR:
        return None
    n = len(hits)
    verdicts = [r.get("verdict", "") for r in hits]
    needs = sum(1 for v in verdicts if v == "NEEDS MORE EVIDENCE")
    rejected = sum(1 for v in verdicts if v == "REJECTED")
    advanced = sum(1 for v in verdicts if v in ("APPROVED", "PROMISING"))
    return {
        "count": n,
        "most_common_outcome": _mode(verdicts),
        "most_common_weakness": _mode([r.get("primary_failure", "") for r in hits]),
        "needed_more_evidence_pct": round(needs / n * 100),
        "failed_review_pct": round(rejected / n * 100),
        "advanced_pct": round(advanced / n * 100),
    }


def statistics() -> dict | None:
    """The institution's own archive figures. None until meaningful."""
    rows = all_records()
    if len(rows) < MIN_SAMPLE:
        return None
    verdicts = [r.get("verdict", "") for r in rows]
    advanced = sum(1 for v in verdicts if v in ("APPROVED", "PROMISING"))
    return {
        "investigations": len(rows),
        "markets": len({r.get("market") for r in rows if r.get("market")}),
        "advanced_pct": round(advanced / len(rows) * 100),
        "most_common_verdict": _mode(verdicts),
        "most_common_failure": _mode([r.get("primary_failure", "") for r in rows]),
    }


def by_objective() -> dict | None:
    """Which objectives actually reach deployment. None until meaningful."""
    rows = all_records()
    if len(rows) < MIN_SAMPLE:
        return None
    out = {}
    for r in rows:
        obj = r.get("objective") or "Unstated"
        out.setdefault(obj, []).append(r.get("verdict", ""))
    result = {}
    for obj, vs in out.items():
        if len(vs) < MIN_SAMPLE_SIMILAR:
            continue                      # a rate on nine cases is not a rate
        adv = sum(1 for v in vs if v in ("APPROVED", "PROMISING"))
        result[obj] = {"n": len(vs), "advanced_pct": round(adv / len(vs) * 100)}
    return result or None


def is_uncommon(verdict_label) -> bool:
    """True when this outcome is genuinely rare in the archive — the only basis
    on which Seesare may remark that a result is unusual."""
    rows = all_records()
    if len(rows) < MIN_SAMPLE:
        return False
    share = sum(1 for r in rows if r.get("verdict") == verdict_label) / len(rows)
    return share <= 0.10


# ---------------------------------------------------------------- firsts
_FIRST_RULES = [
    ("first_institutional_grade", "Evidence Grade: Institutional",
     lambda r: r.get("evidence_grade") == "Institutional"),
    ("first_archive_approval", "A strategy approved on the complete archive",
     lambda r: r.get("verdict") == "APPROVED"
     and r.get("stage") == "Full Institutional Investigation"),
]


def _load_firsts() -> dict:
    try:
        with open(_FIRSTS) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _update_firsts(row) -> None:
    d = _load_firsts()
    changed = False
    for key, title, test in _FIRST_RULES:
        if key not in d and test(row):
            d[key] = {"title": title, "case": row.get("case", ""),
                      "on": row.get("recorded", "")}
            changed = True
    if changed:
        tmp = _FIRSTS + ".tmp"
        with open(tmp, "w") as f:
            json.dump(d, f)
        os.replace(tmp, _FIRSTS)


def firsts() -> list:
    """Milestones the institution genuinely reached, oldest first."""
    d = _load_firsts()
    return sorted(d.values(), key=lambda x: x.get("on", ""))
