"""The case's own file of record — journal, objective, market.

A real investigation leaves a trail. This module records that trail (timestamped
entries, written only when something genuinely happened) alongside the two facts
the client supplies about intent: what they are ultimately trying to achieve, and
which market they trade.

It is orchestration only. It holds no research result, makes no calculation, and
never touches the engine or the Case's own evidence. Entries are appended when a
real event occurs — never in advance, never to decorate.
"""
from __future__ import annotations
import json
import os
from datetime import datetime

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "casefiles")
os.makedirs(_DIR, exist_ok=True)

# what the client is ultimately trying to achieve -> the architecture it implies
OBJECTIVES = [
    ("income", "Monthly Income", "Income Architecture"),
    ("growth", "Long-term Growth", "Growth Architecture"),
    ("funded", "Funded Challenge", "Drawdown-First Architecture"),
    ("preservation", "Capital Preservation", "Preservation Architecture"),
    ("other", "Other", "Balanced Architecture"),
]
MARKETS = [("XAUUSD", "Gold"), ("EURUSD", "EUR/USD"),
           ("GBPUSD", "GBP/USD"), ("USDJPY", "USD/JPY")]


def _path(cid: str) -> str:
    return os.path.join(_DIR, f"{cid}.json")


def load(cid: str) -> dict:
    try:
        with open(_path(cid)) as f:
            d = json.load(f)
    except (OSError, ValueError):
        d = {}
    d.setdefault("journal", [])
    return d


def _save(cid: str, d: dict) -> None:
    p = _path(cid)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f)
    os.replace(tmp, p)


# ---------------------------------------------------------------- journal
def note(cid: str, text: str) -> None:
    """Record that something actually happened, with the time it happened."""
    d = load(cid)
    if d["journal"] and d["journal"][-1]["text"] == text:
        return                      # never record the same event twice
    d["journal"].append({"at": datetime.now().strftime("%H:%M"), "text": text})
    _save(cid, d)


def journal(cid: str) -> list:
    return load(cid).get("journal", [])


# ---------------------------------------------------------------- intent
def set_objective(cid: str, key: str) -> None:
    if key not in {k for k, _, _ in OBJECTIVES}:
        return
    d = load(cid)
    d["objective"] = key
    _save(cid, d)


def objective(cid: str) -> str:
    return load(cid).get("objective", "")


def objective_label(cid: str) -> str:
    k = objective(cid)
    return next((lab for key, lab, _ in OBJECTIVES if key == k), "")


def architecture(cid: str) -> str:
    """The architecture inferred from the client's objective. The goal belongs to
    the trader; the architecture is our reading of it."""
    k = objective(cid)
    return next((arch for key, _, arch in OBJECTIVES if key == k), "")


def set_market(cid: str, mid: str) -> None:
    if mid not in {m for m, _ in MARKETS}:
        return
    d = load(cid)
    d["market"] = mid
    _save(cid, d)


def market(cid: str) -> str:
    return load(cid).get("market", "")


def market_label(cid: str) -> str:
    m = market(cid)
    return next((lab for mid, lab in MARKETS if mid == m), "")
