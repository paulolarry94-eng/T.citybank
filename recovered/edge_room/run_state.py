"""Live investigation progress — a presentation-only sidecar.

While the Execution Bridge does real work, the interface needs to show *what is
happening right now* so the customer watches the investigation unfold rather
than waiting on a spinner. This module records that live progress in a small
sidecar file, separate from the Case, updated as each genuine step is performed.

It holds no research results and makes no research decision. Every label it
carries corresponds to real work the engine is doing; when the run completes the
Case file (written by the engine) is the source of truth and this sidecar is
retired. Nothing here is ever faked — a step is only marked done once it has
actually been performed.
"""
from __future__ import annotations
import json
import os
import time

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")
os.makedirs(_DIR, exist_ok=True)


def _path(cid: str) -> str:
    return os.path.join(_DIR, f"{cid}.run.json")


def _write(cid: str, data: dict) -> None:
    p = _path(cid)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.replace(tmp, p)          # atomic — a concurrent poll never sees a half-write


def load(cid: str):
    try:
        with open(_path(cid)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def clear(cid: str) -> None:
    for p in (_path(cid), _path(cid) + ".tmp"):
        try:
            os.remove(p)
        except OSError:
            pass


# ---------------------------------------------------------------- worker API
def begin(cid: str, stage: str, labels: list) -> None:
    """Open a run: the journey stage under way, and the sequence of real steps
    the customer will watch, all initially waiting."""
    _write(cid, {
        "active": True, "done": False, "error": "",
        "stage": stage,
        "steps": [{"label": lab, "state": "upcoming"} for lab in labels],
        "checkin": "",
        "started": time.time(),
    })


def advance(cid: str, i: int, checkin: str = "") -> None:
    """Mark step i as the one now in progress; everything before it is done.
    A step never turns 'done' until the work it names has actually happened."""
    d = load(cid)
    if not d:
        return
    for j, s in enumerate(d["steps"]):
        s["state"] = "done" if j < i else ("active" if j == i else "upcoming")
    d["checkin"] = checkin or ""
    _write(cid, d)


def complete(cid: str) -> None:
    d = load(cid) or {}
    for s in d.get("steps", []):
        s["state"] = "done"
    d.update({"active": False, "done": True, "checkin": ""})
    _write(cid, d)


def error(cid: str, message: str) -> None:
    d = load(cid) or {"steps": []}
    d.update({"active": False, "done": False, "error": message})
    _write(cid, d)
