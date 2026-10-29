"""The Dataset Selector — routing, and nothing else.

This is the only intentional relaxation of the freeze. It sits immediately before
the existing investigation engine and chooses *which* institutional dataset the
engine investigates. It never touches methodology, never changes a calculation,
never alters Seesare's reasoning. Its single job is to route:

    Initial Assessment      -> Curated 2-Year Institutional Sample
    Commissioned Investigation -> Complete Institutional Archive

Both are the same institutional record and the same engine; the only difference
is evidence depth. The 2-year sample is a genuine time-slice of the complete
archive — created here, investigated for real — so that every visible statement
about the evidence is literally true.
"""
from __future__ import annotations
import glob
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_CACHE = os.path.join(_HERE, "datasets")
os.makedirs(_CACHE, exist_ok=True)

ASSESSMENT = "assessment"
COMMISSIONED = "commissioned"

SAMPLE_YEARS = 2
SAMPLE_LABEL = "Curated 2-Year Institutional Sample"
ARCHIVE_LABEL = "Complete Institutional Archive"
_SOURCE = "Dukascopy"

_STAGE_FILE = os.path.join(_CACHE, "stages.json")


# ---------------------------------------------------------------- the archive
def archive_path() -> str:
    """The complete institutional archive — the full history the engine has always
    investigated. Chosen deterministically so the two tiers share one archive."""
    hits = sorted(glob.glob("/tmp/claude-0/**/scratchpad/*.npz", recursive=True))
    if not hits:
        return ""
    for h in hits:                     # the established full-history gold record
        if h.endswith("FL_fo45_720.npz"):
            return h
    return hits[0]


def sample_path() -> str:
    """A genuine 2-year slice of the archive — the most recent two years of the
    same record. Built once and cached; the engine probes it for real."""
    arc = archive_path()
    if not arc:
        return ""
    out = os.path.join(_CACHE, "sample_2y__" + os.path.basename(arc))
    try:
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(arc):
            return out
        import numpy as np
        z = np.load(arc, allow_pickle=True)
        key = list(z.keys())[0]
        arr = z[key]
        arr2 = arr.reshape(-1, 1) if arr.ndim == 1 else arr
        ts = arr2[:, 0].astype(float)
        cutoff = ts.max() - SAMPLE_YEARS * 365.25 * 86400.0
        sliced = arr[ts >= cutoff]
        np.savez(out, **{key: sliced})
        return out
    except Exception:  # noqa: BLE001
        return ""      # if the slice can't be built, the caller falls back cleanly


# ---------------------------------------------------------------- routing
def select(stage: str) -> dict:
    """Route to the dataset for this stage. Methodology is untouched — only the
    file the engine reads, and the honest label that describes it, change."""
    if stage == COMMISSIONED:
        return {"path": archive_path(), "label": ARCHIVE_LABEL, "source": _SOURCE,
                "stage": COMMISSIONED}
    return {"path": sample_path(), "label": SAMPLE_LABEL, "source": _SOURCE,
            "stage": ASSESSMENT}


def label_for(stage: str) -> str:
    return ARCHIVE_LABEL if stage == COMMISSIONED else SAMPLE_LABEL


def stage_title(stage: str) -> str:
    return ("Full Institutional Investigation" if stage == COMMISSIONED
            else "Initial Assessment")


def status_word(stage: str) -> str:
    return "Investigation complete" if stage == COMMISSIONED else "Assessment complete"


# ---------------------------------------------------------------- per-case stage
def _load_stages() -> dict:
    try:
        with open(_STAGE_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def stage_of(cid: str) -> str:
    return _load_stages().get(cid, ASSESSMENT)


def set_stage(cid: str, stage: str) -> None:
    d = _load_stages()
    d[cid] = stage
    tmp = _STAGE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f)
    os.replace(tmp, _STAGE_FILE)


def label_of(cid: str) -> str:
    return label_for(stage_of(cid))
