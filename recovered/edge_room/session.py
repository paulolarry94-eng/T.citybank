"""Anonymous browser sessions — the zero-friction front door.

No account, no password, no email. A visitor is known only by a random token
carried in a cookie (mirrored into the browser's local storage for the tray).
Each session may open an Initial Assessment on up to three strategies; the
strategies it has looked at are its own, scoped by this token, and nobody else's
appear. Persistence is the browser's: clear the browser and the session is gone.

This module is pure orchestration. It never touches the engine or a Case's
contents — it only records which Case ids belong to which anonymous token, and
enforces the gentle three-strategy ceiling on the Initial Assessment.
"""
from __future__ import annotations
import json
import os
import re
import secrets

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
os.makedirs(_DIR, exist_ok=True)

LIMIT = 3                       # strategies per anonymous Initial Assessment
_TOKEN_RE = re.compile(r"^[0-9a-f]{24,64}$")


def new_sid() -> str:
    return secrets.token_hex(16)


def valid(sid) -> bool:
    return bool(sid and _TOKEN_RE.match(sid))


def _path(sid: str) -> str:
    return os.path.join(_DIR, f"{sid}.json")


def load(sid: str) -> dict:
    if not valid(sid):
        return {"cases": []}
    try:
        with open(_path(sid)) as f:
            d = json.load(f)
            d.setdefault("cases", [])
            return d
    except (OSError, ValueError):
        return {"cases": []}


def _save(sid: str, d: dict) -> None:
    p = _path(sid)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f)
    os.replace(tmp, p)


def cases(sid: str) -> list:
    return load(sid).get("cases", [])


def count(sid: str) -> int:
    return len(cases(sid))


def remaining(sid: str) -> int:
    return max(0, LIMIT - count(sid))


def at_limit(sid: str) -> bool:
    # the three-strategy ceiling applies only to the Initial Assessment; once the
    # engagement is commissioned the ceiling is lifted
    return not commissioned(sid) and count(sid) >= LIMIT


def commissioned(sid: str) -> bool:
    return bool(load(sid).get("commissioned"))


def commission(sid: str) -> None:
    if not valid(sid):
        return
    d = load(sid)
    d["commissioned"] = True
    _save(sid, d)


def owns(sid: str, cid: str) -> bool:
    return cid in cases(sid)


def add_case(sid: str, cid: str) -> bool:
    """Attach a Case to this session. Returns False if the ceiling is reached."""
    if not valid(sid):
        return False
    d = load(sid)
    if cid in d["cases"]:
        return True
    if len(d["cases"]) >= LIMIT:
        return False
    d["cases"].append(cid)
    _save(sid, d)
    return True
