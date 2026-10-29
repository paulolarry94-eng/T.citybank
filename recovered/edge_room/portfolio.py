"""The Portfolio Architect — orchestration over surviving strategies.

The backend engine is frozen: it investigates ONE hypothesis at a time and
records that Case's evidence and verdict. This module sits above it. A portfolio
is simply the set of Cases that survived their own stress testing; each Case
stays in its own isolated file, so a strategy that later fails never touches one
that already passed.

Truthfulness law. Every figure here is derived from what the engine actually
recorded or from the strategies' own stated risk factors — never invented.
Co-movement and combined-risk are *structural* projections from shared risk
exposure (same instrument, shared currency, direction, timeframe), and are
labelled as such throughout. They are not a claim of a measured joint backtest,
which the frozen engine does not produce; a measured return-correlation would
require a returns-level joint test the engine does not currently run.
"""
from __future__ import annotations
import math
import re

# ---- what "survived stress testing" means, in the engine's own terms ----
SURVIVING_LABELS = {"APPROVED", "PROMISING"}

# ---- the Safety Stack (institutional governance) ----
HEAT_CEILING = 8.0        # Shared Risk Ceiling — soft, blocks new risk beyond this
CORRELATION_CEILING = 0.50   # Correlation Ceiling — warn when co-movement exceeds it
HARD_MAX_HEAT = 10.0      # Hard Floor — unalterable compiled ceiling on total heat
HARD_MAX_RISK = 3.0       # Hard Floor — unalterable compiled ceiling per trade

# ---- vocabulary governance ----
BLACKLIST = ("harvest", "passive income", "withdrawal", "get rich",
             "automated income", "financial freedom")
REQUIRED_VOCAB = ("drawdown containment", "uncorrelated edges", "risk concentration",
                  "capital allocation", "co-movement", "governance")


def audit(text: str) -> list:
    """Return any blacklisted terms present (case-insensitive). Empty == clean."""
    low = (text or "").lower()
    return [w for w in BLACKLIST if w in low]


# ---- reading a strategy's real risk factors ----
_CCY = [
    (("xauusd", "gold", "xau"), "XAUUSD", {"XAU", "USD"}),
    (("xagusd", "silver", "xag"), "XAGUSD", {"XAG", "USD"}),
    (("eurusd", "eur/usd", "euro"), "EURUSD", {"EUR", "USD"}),
    (("gbpusd", "gbp/usd", "cable"), "GBPUSD", {"GBP", "USD"}),
    (("usdjpy", "usd/jpy", "jpy", "yen"), "USDJPY", {"USD", "JPY"}),
]
_TF_WORDS = [("m1", ("m1", "1-minute", "1 minute")), ("m5", ("m5", "5-minute")),
             ("m15", ("m15", "15-minute")), ("m30", ("m30", "30-minute", "30 minute")),
             ("h1", ("h1", "1-hour", "hourly")), ("h4", ("h4", "4-hour")),
             ("d1", ("d1", "daily"))]


def _text(case) -> str:
    h = case.hypothesis
    return " ".join([h.get("claim", ""), str(h.get("instrument") or ""),
                     " ".join(h.get("rules", []))]).lower()


def market_id(case) -> str:
    t = _text(case)
    for keys, mid, _ in _CCY:
        if any(k in t for k in keys):
            return mid
    return ""


def currency_exposure(case) -> set:
    t = _text(case)
    for keys, _, ccy in _CCY:
        if any(k in t for k in keys):
            return set(ccy)
    return set()


def direction(case) -> str:
    t = _text(case)
    lo = any(w in t for w in ("long", "buy", "revert", "reversion", "bounce", "bull"))
    sh = any(w in t for w in ("short", "sell", "fade", "breakdown", "bear"))
    if lo and not sh:
        return "long"
    if sh and not lo:
        return "short"
    return "both"


def timeframe(case) -> str:
    t = _text(case)
    for tf, words in _TF_WORDS:
        if any(w in t for w in words):
            return tf
    return ""


def label(case) -> str:
    """The strategy's short display label — its market, or a trimmed claim."""
    mid = market_id(case)
    if mid:
        return {"XAUUSD": "Gold", "XAGUSD": "Silver", "EURUSD": "EUR/USD",
                "GBPUSD": "GBP/USD", "USDJPY": "USD/JPY"}[mid]
    claim = case.hypothesis.get("claim", "").strip()
    return (claim[:22] + "…") if len(claim) > 23 else (claim or "Strategy")


# ---- portfolio membership (isolation is inherent: each Case is its own file) ----
def survived(case) -> bool:
    return (case.verdict or {}).get("label") in SURVIVING_LABELS


def members(cases) -> list:
    """The surviving strategies, in the order they passed. A rejected or
    unfinished Case is simply absent — it can never taint a passed one."""
    return [c for c in cases if survived(c)]


# ---- structural co-movement (a shared-risk-factor estimate, not a measurement) ----
def co_movement(a, b) -> float:
    """A 0–1 structural co-movement estimate from shared risk factors. High when
    two edges trade the same instrument or currency and lean the same way; lower
    when their exposure is distinct or offsetting. Never a measured correlation."""
    ma, mb = market_id(a), market_id(b)
    if ma and ma == mb:
        score = 0.85                       # the same instrument — highly co-moving
    else:
        shared = currency_exposure(a) & currency_exposure(b)
        score = 0.40 if shared else 0.08   # a shared currency, or largely distinct
    da, db = direction(a), direction(b)
    if ma and ma == mb and da != "both" and db != "both" and da != db:
        score *= 0.5                       # opposite directions partially offset
    if timeframe(a) and timeframe(a) == timeframe(b):
        score = min(1.0, score + 0.05)     # same window — slightly tighter
    return round(min(1.0, max(0.0, score)), 2)


def co_movement_matrix(cases) -> list:
    n = len(cases)
    m = [[1.0 if i == j else co_movement(cases[i], cases[j])
          for j in range(n)] for i in range(n)]
    return m


def orthogonal_pairs(cases):
    """(i, j, rho) pairs whose co-movement breaches the Correlation Ceiling."""
    out = []
    for i in range(len(cases)):
        for j in range(i + 1, len(cases)):
            rho = co_movement(cases[i], cases[j])
            if rho > CORRELATION_CEILING:
                out.append((i, j, rho))
    return out


# ---- risk concentration (fully real: from stated exposure) ----
def concentration(cases) -> dict:
    """Which currencies the portfolio is repeatedly exposed to, and where the
    same instrument or trading window is doubled up — the real overlaps."""
    ccy_count = {}
    for c in cases:
        for ccy in currency_exposure(c):
            ccy_count[ccy] = ccy_count.get(ccy, 0) + 1
    doubled_currencies = sorted([c for c, n in ccy_count.items() if n >= 2])
    mids = [market_id(c) for c in cases if market_id(c)]
    doubled_instruments = sorted({m for m in mids if mids.count(m) >= 2})
    tfs = [timeframe(c) for c in cases if timeframe(c)]
    doubled_windows = sorted({t for t in tfs if tfs.count(t) >= 2})
    return {"currency_counts": ccy_count,
            "doubled_currencies": doubled_currencies,
            "doubled_instruments": doubled_instruments,
            "doubled_windows": doubled_windows}


# ---- capital allocation (real arithmetic on real inputs) ----
def default_weights(cases) -> list:
    """A conservative equal split that sits inside the Shared Risk Ceiling."""
    n = max(1, len(cases))
    per = round(min(2.0, (HEAT_CEILING - 1.0) / n), 2)
    return [per] * len(cases)


def allocation(cases, weights=None) -> dict:
    if weights is None:
        weights = default_weights(cases)
    weights = [max(0.0, float(w)) for w in weights]
    total = round(sum(weights), 2)
    ceiling = min(HEAT_CEILING, HARD_MAX_HEAT)
    return {
        "legs": [{"label": label(c), "weight": round(weights[i], 2),
                  "market": market_id(c) or "—", "direction": direction(c)}
                 for i, c in enumerate(cases)],
        "total": total,
        "ceiling": ceiling,
        "within_ceiling": total <= ceiling + 1e-9,
        "headroom": round(ceiling - total, 2),
        "per_trade_capped": all(w <= HARD_MAX_RISK + 1e-9 for w in weights),
    }


def combined_risk(cases, weights=None) -> dict:
    """Projected simultaneous risk draw, in risk-% terms, under three regimes —
    edges fully independent, edges moving together, and the structural estimate
    from their co-movement. Arithmetic on the allocation and the structural
    co-movement; not a measured joint drawdown."""
    if weights is None:
        weights = default_weights(cases)
    w = [max(0.0, float(x)) for x in weights]
    n = len(cases)
    worst = round(sum(w), 2)                              # fully correlated
    independent = round(math.sqrt(sum(x * x for x in w)), 2)
    ss = sum(x * x for x in w)
    for i in range(n):
        for j in range(i + 1, n):
            ss += 2 * co_movement(cases[i], cases[j]) * w[i] * w[j]
    structural = round(math.sqrt(max(0.0, ss)), 2)
    avg_rho = 0.0
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    if pairs:
        avg_rho = round(sum(co_movement(cases[i], cases[j])
                            for i, j in pairs) / len(pairs), 2)
    return {"independent": independent, "structural": structural, "worst_case": worst,
            "avg_co_movement": avg_rho, "ceiling": min(HEAT_CEILING, HARD_MAX_HEAT)}


def roles(cases) -> list:
    """A simple role per validated strategy — assigned ONLY where the existing
    portfolio signals support it, and left blank otherwise. Never invented:
      Growth        — carries the strongest recorded expectancy.
      Diversification — the most orthogonal edge (lowest co-movement to the rest).
      Protection    — a directional hedge against a same-instrument leg.
    Truthfulness is absolute; if a role isn't earned, it stays empty."""
    n = len(cases)
    out = [""] * n
    if n < 2:
        return out

    def _exp(c):
        vals = [e.get("output", {}).get("expectancy_is") for e in c.evidence
                if isinstance(e.get("output", {}).get("expectancy_is"), (int, float))]
        return max(vals) if vals else None

    exps = [_exp(c) for c in cases]
    if any(x is not None for x in exps):
        gi = max(range(n), key=lambda i: exps[i] if exps[i] is not None else -1e9)
        if exps[gi] is not None and exps[gi] > 0:
            out[gi] = "Growth"

    avg = []
    for i in range(n):
        others = [co_movement(cases[i], cases[j]) for j in range(n) if j != i]
        avg.append(sum(others) / len(others) if others else 1.0)
    di = min(range(n), key=lambda i: avg[i])
    if avg[di] < CORRELATION_CEILING and not out[di]:
        out[di] = "Diversification"

    for i in range(n):
        if out[i]:
            continue
        mi, dir_i = market_id(cases[i]), direction(cases[i])
        for j in range(n):
            if i == j:
                continue
            if mi and mi == market_id(cases[j]) and dir_i in ("long", "short") \
                    and direction(cases[j]) in ("long", "short") \
                    and dir_i != direction(cases[j]):
                out[i] = "Protection"
                break
    return out


def safety_stack(cases, weights=None) -> dict:
    alloc = allocation(cases, weights)
    breaches = orthogonal_pairs(cases)
    return {
        "heat_ceiling": HEAT_CEILING,
        "hard_max_heat": HARD_MAX_HEAT,
        "hard_max_risk": HARD_MAX_RISK,
        "correlation_ceiling": CORRELATION_CEILING,
        "active_heat": alloc["total"],
        "within_ceiling": alloc["within_ceiling"],
        "headroom": alloc["headroom"],
        "correlation_breaches": [
            {"a": label(cases[i]), "b": label(cases[j]), "rho": rho}
            for i, j, rho in breaches],
    }
