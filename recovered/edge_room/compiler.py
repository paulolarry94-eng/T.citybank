"""The Strategy Compiler — understand before you measure.

Constitutional principle:

    Python never guesses. Seesare never invents. The trader always approves the
    reconstructed strategy before investigation begins.

Reconstruction here is **deterministic**. It is pattern recognition over a closed
vocabulary of things the institution can genuinely measure — not a model's
impression of what someone meant. That matters for two reasons: the same words
always produce the same specification, and the compiler physically cannot
recognise a concept it has no way to test. What it cannot reconstruct, it says
so about, rather than quietly approximating.

The model's role is only to *narrate* what this module produced. It never fills a
facet, never raises a confidence, and never approves a specification.

Nothing enters the Institution until the trader has accepted the reconstruction.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from datetime import datetime

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "compiler")
os.makedirs(_DIR, exist_ok=True)
_SPECS = os.path.join(_DIR, "specs")
os.makedirs(_SPECS, exist_ok=True)
_PRECEDENT = os.path.join(_DIR, "reconstructions.jsonl")

COMPILER_VERSION = "1.0"

# ---------------------------------------------------------------- vocabulary
# Only concepts with a measurable definition appear here. Each carries the
# definition the institution will actually test, so nothing is ambiguous.
ENTRIES = {
    "liquidity_sweep": ("Liquidity sweep",
                        "price trades beyond a prior swing extreme, then closes "
                        "back inside it",
                        ("sweep", "sweeps", "swept", "liquidity", "stop hunt",
                         "stophunt", "raid", "took liquidity", "takes liquidity",
                         "taking liquidity", "grab", "runs the highs",
                         "runs the lows")),
    "breakout": ("Breakout",
                 "a close beyond a prior range extreme",
                 ("breakout", "breaks out", "break out", "breaks above",
                  "breaks below", "break of")),
    "donchian_breakout": ("Donchian breakout",
                          "a close beyond the highest high or lowest low of the "
                          "last N bars",
                          ("donchian", "n-bar high", "20-period high",
                           "channel breakout")),
    "retest": ("Retest of a broken level",
               "price returns to a level it has already broken and holds it",
               ("retest", "re-test", "pullback to", "comes back to",
                "second time", "revisit")),
    "mean_reversion": ("Reversion from an extreme",
                       "price extends a measured distance from its mean and turns",
                       ("revert", "reversion", "mean revert", "comes back",
                        "fade", "overextended", "exhaustion")),
    "structure_shift": ("Market structure shift",
                        "the first close beyond the last opposing swing point",
                        ("structure shift", "market structure", "bos",
                         "break of structure", "choch", "change of character")),
    "ma_cross": ("Moving-average cross",
                 "a faster moving average crossing a slower one",
                 ("ema cross", "ma cross", "moving average cross", "golden cross",
                  "crossover")),
    "range_sweep": ("Session-range sweep",
                    "price trades beyond a session's range, then closes back inside",
                    ("asian range", "asian sweep", "session range",
                     "london sweep")),
}

CONFIRMATIONS = {
    "close_back_inside": ("Close back inside",
                          ("close back", "closes back", "back inside",
                           "closes above", "closes below", "confirmed by a close")),
    "structure_shift": ("Market structure shift",
                        ("structure shift", "bos", "choch", "break of structure")),
    "fair_value_gap": ("Fair-value gap",
                       ("fair value gap", "fvg", "imbalance", "inefficiency")),
    "engulfing": ("Engulfing candle", ("engulf", "engulfing")),
}

STOPS = {
    "prior_extreme": ("Beyond the swept extreme",
                      ("under the base", "below the base", "above the high",
                       "beyond the high", "under the low", "below the low",
                       "under the swing", "beyond the swept", "above the swept",
                       "below the swept", "above the sweep", "below the sweep",
                       "above the swing", "under the wick", "beyond the wick")),
    "atr": ("A multiple of ATR", ("atr", "average true range")),
    "fixed_distance": ("A fixed distance", ("pips", "points", "fixed stop")),
    "structure": ("Beyond the last structure point",
                  ("under structure", "below structure", "swing low", "swing high")),
}

TARGETS = {
    "r_multiple": ("A fixed reward-to-risk multiple",
                   ("1:1", "1:2", "1:3", "2r", "3r", "1r", "rr", "reward to risk",
                    "risk reward")),
    "opposing_liquidity": ("The opposing liquidity pool",
                           ("opposing", "opposite high", "opposite low",
                            "previous high", "previous low", "liquidity above",
                            "liquidity below")),
    "mean": ("A return to the mean", ("mean", "midpoint", "equilibrium", "vwap")),
    "trail": ("A trailing stop", ("trail", "trailing")),
}

SESSIONS = {
    "london": ("London", ("london",)),
    "new_york": ("New York", ("new york", "ny session", "us session")),
    "asia": ("Asia", ("asia", "asian", "tokyo")),
    "any": ("Any session", ("any session", "all sessions", "24 hours", "anytime")),
}

TIMEFRAMES = {"M1": ("1 minute", ("m1", "1 minute", "1-minute", "one minute")),
              "M5": ("5 minute", ("m5", "5 minute", "5-minute")),
              "M15": ("15 minute", ("m15", "15 minute", "15-minute")),
              "M30": ("30 minute", ("m30", "30 minute", "30-minute", "half hour")),
              "H1": ("1 hour", ("h1", "1 hour", "hourly", "60 minute")),
              "H4": ("4 hour", ("h4", "4 hour", "4-hour")),
              "D1": ("Daily", ("d1", "daily", "day chart"))}

INSTRUMENTS = {"XAUUSD": ("Gold (XAU/USD)", ("xauusd", "gold", "xau")),
               "EURUSD": ("EUR/USD", ("eurusd", "eur/usd", "euro", "fiber")),
               "GBPUSD": ("GBP/USD", ("gbpusd", "gbp/usd", "cable", "pound")),
               "USDJPY": ("USD/JPY", ("usdjpy", "usd/jpy", "yen", "jpy"))}

BIAS = {"mean_reversion": ("Mean reversion",
                           ("revert", "reversion", "fade", "comes back", "bounce")),
        "trend": ("Trend continuation",
                  ("trend", "continuation", "momentum", "with the trend")),
        "breakout": ("Breakout", ("breakout", "break out", "expansion"))}

# language that names a judgement rather than a rule. These cannot be compiled.
DISCRETIONARY = ("looks like", "feels", "feel", "gut", "instinct", "discretion",
                 "i can tell", "experience tells", "when it's clean", "obvious",
                 "quality setup", "a-plus", "a+ setup", "if it looks",
                 "context", "narrative", "premium and discount", "draw a trendline",
                 "elliott", "harmonic", "gartley", "wolfe wave")

# named methodologies that are really bundles of measurable parts
NAMED_BUNDLES = {
    "unicorn": ("ICT Unicorn", ["liquidity_sweep", "structure_shift",
                                "fair_value_gap"]),
    "silver bullet": ("ICT Silver Bullet", ["liquidity_sweep", "fair_value_gap"]),
    "smart money": ("Smart Money Concepts", ["liquidity_sweep", "structure_shift"]),
    "turtle": ("Turtle breakout", ["donchian_breakout"]),
    "judas": ("Judas swing", ["range_sweep", "structure_shift"]),
}

# what Python needs before it can test anything at all
REQUIRED = ("instrument", "timeframe", "entry", "stop", "target")
OPTIONAL = ("confirmation", "session", "bias")


# A level named while describing the entry is not a target. These facets are
# only read when the trader actually signals a target, so nothing is inferred.
_TARGET_CUES = ("target", "tp", "take profit", "aim", "exit at", "exits at",
                "profit at", "runs to", "run to", "closes at")


def _has_target_cue(text) -> bool:
    return any(c in text for c in _TARGET_CUES)


def _find(text, table):
    """First vocabulary entry whose phrasing appears in the text. Longest phrase
    wins, so 'break of structure' beats 'breakout'."""
    best, best_len = "", 0
    for key, spec in table.items():
        for phrase in spec[-1]:
            if phrase in text and len(phrase) > best_len:
                best, best_len = key, len(phrase)
    return best


def _label(table, key):
    return table[key][0] if key in table else ""


# ---------------------------------------------------------------- reconstruction
def reconstruct(text: str, market_hint: str = "") -> dict:
    """Deterministically read a strategy description into a specification.
    Facets that are not stated are left empty — never inferred."""
    t = " " + (text or "").lower() + " "
    spec = {
        "instrument": _find(t, INSTRUMENTS) or (market_hint or ""),
        "timeframe": _find(t, TIMEFRAMES),
        "bias": _find(t, BIAS),
        "entry": _find(t, ENTRIES),
        "confirmation": _find(t, CONFIRMATIONS),
        "stop": _find(t, STOPS),
        "target": _target_of(t),
        "session": _find(t, SESSIONS),
    }
    # a named methodology is recognised as its measurable parts, never as itself
    bundle = ""
    for needle, (title, parts) in NAMED_BUNDLES.items():
        if needle in t:
            bundle = title
            if not spec["entry"] and parts:
                pass          # the bundle is *offered*, not silently applied
            break
    discretion = [w for w in DISCRETIONARY if w in t]
    return {"spec": spec, "bundle": bundle, "discretionary": discretion,
            "source_len": len((text or "").split())}


def _target_of(t):
    """Self-evident targets (an R-multiple, a trail) are read directly. A level
    or a mean is only a target when the trader says it is."""
    if _find(t, {"r_multiple": TARGETS["r_multiple"]}):
        return "r_multiple"          # an explicit reward multiple is never ambiguous
    key = _find(t, TARGETS)
    if key == "trail":
        return key
    if key and _has_target_cue(t):
        return key
    return ""


def missing(recon: dict) -> list:
    return [f for f in REQUIRED if not recon["spec"].get(f)]


def confidence(recon: dict) -> int:
    """Compiler confidence — how completely the description maps onto things the
    institution can measure. Not a judgement about the strategy, and not the
    model's opinion: it is the share of testable facets actually pinned down."""
    spec = recon["spec"]
    have_req = sum(1 for f in REQUIRED if spec.get(f))
    have_opt = sum(1 for f in OPTIONAL if spec.get(f))
    score = (have_req / len(REQUIRED)) * 85 + (have_opt / len(OPTIONAL)) * 15
    if recon["discretionary"]:
        score -= 25 * min(2, len(recon["discretionary"]))
    return max(0, min(100, round(score)))


def status(recon: dict) -> str:
    if recon["discretionary"] and not compilable(recon):
        return "Cannot compile"
    return "Ready" if not missing(recon) else "Needs clarification"


def compilable(recon: dict) -> bool:
    """A strategy is compilable when every facet Python needs is pinned to a
    measurable definition. Discretion alone does not block it — an otherwise
    complete rule set with a stray 'looks like' is still testable."""
    return not missing(recon)


# ---------------------------------------------------------------- questions
_QUESTIONS = {
    "instrument": "Which market are you trading this on?",
    "timeframe": "Which timeframe does the setup form on?",
    "entry": "What exactly has to happen before you're in? The trigger, as you'd "
             "describe it to yourself.",
    "stop": "Where does the stop sit — the point where the trade admits it was "
            "wrong?",
    "target": "What defines the target?",
}


def next_question(recon: dict) -> str:
    m = missing(recon)
    return _QUESTIONS.get(m[0], "") if m else ""


def outstanding(recon: dict) -> list:
    return [_QUESTIONS[f] for f in missing(recon) if f in _QUESTIONS]


# ---------------------------------------------------------------- refusal
def refusal(recon: dict) -> str:
    d = recon["discretionary"]
    if not d:
        return ""
    return ("I can't test this faithfully as written. The rules still depend on "
            f"judgement — \"{d[0]}\" is something you decide in the moment, not "
            "something I can measure the same way twice. I can investigate the "
            "closest measurable version if you'd like.")


def nearest(recon: dict) -> dict | None:
    """The closest architecture the institution already investigates. Offered,
    never substituted silently."""
    if recon.get("bundle"):
        for needle, (title, parts) in NAMED_BUNDLES.items():
            if title == recon["bundle"]:
                return {"title": title,
                        "parts": [_label(ENTRIES, p) or _label(CONFIRMATIONS, p)
                                  for p in parts]}
    if recon["discretionary"]:
        ent = recon["spec"].get("entry")
        if ent:
            return {"title": _label(ENTRIES, ent),
                    "parts": [ENTRIES[ent][1]]}
    return None


# ---------------------------------------------------------------- the artefact
def fingerprint(spec: dict) -> str:
    """A derived, stable identifier for this architecture. The same architecture
    always fingerprints the same way, so the institution can recognise it."""
    ent = (spec.get("entry") or "xx")
    code = "".join(w[0] for w in ent.split("_"))[:2].upper() or "XX"
    bias = (spec.get("bias") or "")
    bcode = {"mean_reversion": "MR", "trend": "TR", "breakout": "BO"}.get(bias, "GN")
    basis = json.dumps({k: spec.get(k, "") for k in
                        ("instrument", "timeframe", "entry", "confirmation",
                         "stop", "target")}, sort_keys=True)
    digits = int(hashlib.sha256(basis.encode()).hexdigest()[:8], 16) % 10000
    return f"{code}-{bcode}-{digits:04d}"


def specification(recon: dict) -> dict:
    """The deterministic payload Python receives. Never shown to the trader."""
    s = recon["spec"]
    return {
        "compiler_version": COMPILER_VERSION,
        "pair": s.get("instrument", ""),
        "timeframe": s.get("timeframe", ""),
        "bias": s.get("bias", ""),
        "entry": s.get("entry", ""),
        "confirmation": s.get("confirmation", ""),
        "stop": s.get("stop", ""),
        "target": s.get("target", ""),
        "session": s.get("session", "any"),
        "fingerprint": fingerprint(s),
    }


def human_rows(recon: dict) -> list:
    """The reconstruction as the trader reads it — every facet, including the
    ones still unknown, because an honest blank is the point."""
    s = recon["spec"]
    return [
        ("Instrument", _label(INSTRUMENTS, s.get("instrument")) or s.get("instrument", "")),
        ("Timeframe", _label(TIMEFRAMES, s.get("timeframe"))),
        ("Bias", _label(BIAS, s.get("bias"))),
        ("Entry", _label(ENTRIES, s.get("entry"))),
        ("Confirmation", _label(CONFIRMATIONS, s.get("confirmation"))),
        ("Stop", _label(STOPS, s.get("stop"))),
        ("Target", _label(TARGETS, s.get("target"))),
        ("Session", _label(SESSIONS, s.get("session"))),
    ]


def definition_of(recon: dict) -> str:
    ent = recon["spec"].get("entry")
    return ENTRIES[ent][1] if ent in ENTRIES else ""


# ---------------------------------------------------------------- persistence
def _path(cid):
    return os.path.join(_SPECS, f"{cid}.json")


def save(cid: str, recon: dict, approved: bool = False) -> dict:
    """Store the reconstruction. Once approved the specification is immutable —
    a later description opens a new reconstruction rather than editing this one."""
    existing = load(cid)
    if existing and existing.get("approved"):
        return existing
    rec = {"reconstruction": recon, "spec": specification(recon),
           "confidence": confidence(recon), "status": status(recon),
           "approved": approved,
           "approved_at": datetime.now().strftime("%Y-%m-%d %H:%M") if approved else "",
           "description": recon.get("description", "")}
    tmp = _path(cid) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(rec, f)
    os.replace(tmp, _path(cid))
    if approved:
        _remember(rec)
    return rec


def load(cid: str) -> dict | None:
    try:
        with open(_path(cid)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def is_approved(cid: str) -> bool:
    r = load(cid)
    return bool(r and r.get("approved"))


# ---- reconstruction precedent: the institution remembers how ideas compile ----
# Kept separate from the Institution's verdict archive, which stays frozen. Only
# the architecture is recorded — never the trader's words.
def _remember(rec: dict) -> None:
    row = {"fingerprint": rec["spec"]["fingerprint"],
           "entry": rec["spec"]["entry"], "bias": rec["spec"]["bias"],
           "instrument": rec["spec"]["pair"], "timeframe": rec["spec"]["timeframe"],
           "on": datetime.now().strftime("%Y-%m-%d")}
    with open(_PRECEDENT, "a") as f:
        f.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------- the contract
# THE SINGLE SOURCE OF TRUTH.
#
# Whatever eventually runs the backtest must import these definitions rather than
# restate them. The trader was shown `definition` and approved it; if the engine
# implements something else, the approval is void and every downstream result is
# a different strategy from the one that was agreed. `contract()` is the whole
# agreement in one structure, and `validate()` is how an engine proves it honours
# it — so drift becomes a test failure instead of a silent lie.
def contract() -> dict:
    """Every concept the compiler can emit, with the definition the trader was
    shown. An engine claiming to test Edge Room strategies must satisfy this."""
    return {
        "compiler_version": COMPILER_VERSION,
        "entries": {k: {"label": v[0], "definition": v[1]}
                    for k, v in ENTRIES.items()},
        "confirmations": {k: {"label": v[0]} for k, v in CONFIRMATIONS.items()},
        "stops": {k: {"label": v[0]} for k, v in STOPS.items()},
        "targets": {k: {"label": v[0]} for k, v in TARGETS.items()},
        "sessions": {k: {"label": v[0]} for k, v in SESSIONS.items()},
        "timeframes": {k: {"label": v[0]} for k, v in TIMEFRAMES.items()},
        "instruments": {k: {"label": v[0]} for k, v in INSTRUMENTS.items()},
        "required": list(REQUIRED),
    }


def validate(spec: dict) -> list:
    """Return the reasons this specification is not executable. Empty means an
    engine may run it. Anything an engine receives must pass this first."""
    c = contract()
    problems = []
    checks = (("pair", "instruments"), ("timeframe", "timeframes"),
              ("entry", "entries"), ("stop", "stops"), ("target", "targets"))
    for field, table in checks:
        val = spec.get(field)
        if not val:
            problems.append(f"{field} is not specified")
        elif val not in c[table]:
            problems.append(f"{field} '{val}' is not in the compiler vocabulary")
    for field, table in (("confirmation", "confirmations"), ("session", "sessions")):
        val = spec.get(field)
        if val and val not in c[table]:
            problems.append(f"{field} '{val}' is not in the compiler vocabulary")
    if spec.get("compiler_version") != COMPILER_VERSION:
        problems.append("specification was compiled by a different compiler version")
    return problems


def executable(spec: dict) -> bool:
    return not validate(spec)


def precedent(spec: dict) -> dict | None:
    """How often this architecture has been reconstructed before. None when too
    few to be worth stating."""
    try:
        with open(_PRECEDENT) as f:
            rows = [json.loads(ln) for ln in f if ln.strip()]
    except (OSError, ValueError):
        return None
    fp = spec.get("fingerprint")
    same = [r for r in rows if r.get("fingerprint") == fp]
    family = [r for r in rows if r.get("entry") and r["entry"] == spec.get("entry")]
    if len(family) < 12:
        return None
    return {"identical": len(same), "family": len(family),
            "entry": spec.get("entry", "")}
