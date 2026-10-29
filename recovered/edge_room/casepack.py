"""The case package — what the client keeps.

A completed investigation is handed over as a single archive: the portable
`.edge` case file (the investigation's own record, so it can be brought back),
the Risk Architecture Report, and the Research Notes. Nothing here computes or
alters research; it packages what already exists.

The `.edge` file is plain JSON so it stays readable and portable — a case a
client can keep for years and return with when the strategy changes.
"""
from __future__ import annotations
import io
import json
import os
import zipfile
from datetime import datetime

import casefile
import compiler as SC
import dataset
import figures
import institution_db
import observation
import present

EDGE_FORMAT = 1


def case_ref(case) -> str:
    """A short, human case reference — Case-018 rather than an opaque id."""
    digits = "".join(ch for ch in case.id if ch.isdigit())
    n = int(digits[-3:]) if digits else abs(hash(case.id)) % 1000
    return f"Case-{n:03d}"


def edge_document(case) -> dict:
    """The portable record of the investigation — evidence, verdict, trail."""
    v = case.verdict or {}
    stg = dataset.stage_of(case.id)
    return {
        "format": EDGE_FORMAT,
        "institution_version": institution_db.INSTITUTION_VERSION,
        "reference": case_ref(case),
        "version": 1,          # the original investigation; reviews increment
        "reviews": 0,          # history is immutable — reviews build on top
        "prepared": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prepared_by": "Seesare · Edge Room",
        "strategy": {
            "claim": case.hypothesis.get("claim", ""),
            "rules": case.hypothesis.get("rules", []),
            "market": casefile.market_label(case.id) or present.detect_market(case),
            "objective": casefile.objective_label(case.id),
            "architecture": casefile.architecture(case.id),
        },
        "stage": dataset.stage_title(stg),
        "evidence_base": dataset.label_for(stg),
        "findings": [present.research_note(e) for e in case.evidence],
        "observation": observation.observation(case),
        "verdict": {
            "label": v.get("label", ""),
            "confidence": v.get("confidence", 0),
            "recommended_next_step": v.get("recommended_next_step", ""),
            "remaining_risks": v.get("remaining_risks", ""),
        },
        "specification": (SC.load(case.id) or {}).get("spec", {}),
        "compiler_confidence": (SC.load(case.id) or {}).get("confidence"),
        "journal": casefile.journal(case.id),
    }


def _research_notes_text(case) -> str:
    doc = edge_document(case)
    L = [f"EDGE ROOM — RESEARCH NOTES",
         f"{doc['reference']}  ·  prepared {doc['prepared']}",
         f"Evidence base: {doc['evidence_base']}",
         "", "=" * 66, ""]
    L.append(f"STRATEGY\n{doc['strategy']['claim']}")
    if doc["strategy"]["objective"]:
        L.append(f"\nOBJECTIVE\n{doc['strategy']['objective']} "
                 f"({doc['strategy']['architecture']})")
    L.append("")
    for i, n in enumerate(doc["findings"], 1):
        L.append("-" * 66)
        L.append(f"RESEARCH NOTE {i}")
        for key in ("observation", "evidence", "meaning"):
            if n.get(key):
                L.append(f"\n{key.upper()}\n{n[key]}")
        L.append("")
    if doc["observation"]:
        L += ["-" * 66, "WORTH REMEMBERING", "", doc["observation"], ""]
    if doc["verdict"]["label"]:
        L += ["-" * 66, "VERDICT", "",
              f"{doc['verdict']['label']}",
              doc["verdict"]["recommended_next_step"], ""]
    if doc["journal"]:
        L += ["-" * 66, "INVESTIGATION JOURNAL", ""]
        L += [f"  {e['at']}   {e['text']}" for e in doc["journal"]]
    L += ["", "=" * 66,
          "Every hypothesis enters Edge Room innocent and must earn the right to",
          "trade. Nothing is funded until a live demo passes its gate."]
    return "\n".join(L) + "\n"


def _readme(case, figs, missing) -> str:
    doc = edge_document(case)
    spec = doc.get("specification") or {}
    L = ["EDGE ROOM — CASE ARCHIVE", "=" * 66, "",
         f"Case                 {doc['reference']}",
         f"Investigation date   {doc['prepared']}",
         f"Evidence base        {doc['evidence_base']}",
         f"Stage                {doc['stage']}",
         f"Institution version  {doc.get('institution_version','')}",
         f"Compiler version     {spec.get('compiler_version','—')}",
         f"Strategy fingerprint {spec.get('fingerprint','—')}", "",
         "CONTENTS", "-" * 66,
         f"  {doc['reference']}.edge            the portable case record",
         "  Risk Architecture Report.pdf   the full report",
         "  Research Notes.txt             the findings in plain text"]
    if figs:
        L.append("  Figures/                       the visual evidence")
        for name, _t, _b in figs:
            L.append(f"      {name}")
    L += ["", "FIGURES NOT INCLUDED", "-" * 66] if missing else []
    for title, why in missing:
        L.append(f"  {title}: {why}.")
    if missing:
        L += ["", "  These were not drawn because the evidence to draw them",
              "  honestly does not exist in this investigation. A figure",
              "  estimated from summary statistics would not be evidence."]
    L += ["", "REPRODUCIBILITY", "-" * 66,
          "  This archive is a complete record. The report and every figure are",
          "  a function of the recorded evidence alone, so the same case",
          "  regenerates the same document and the same charts.", "",
          "  Nothing in this case will change. Future investigations build from",
          "  it — they never rewrite it.", "",
          "=" * 66,
          "Prepared by Seesare · Edge Room"]
    return "\n".join(L) + "\n"


def build_zip(case, report_path="") -> tuple:
    """Returns (filename, bytes) — the case package the client downloads."""
    ref = case_ref(case)
    try:
        figs = figures.render(case)
        _can, missing = figures.available(case)
    except Exception:  # noqa: BLE001
        figs, missing = [], []
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", _readme(case, figs, missing))
        z.writestr(f"{ref}.edge",
                   json.dumps(edge_document(case), indent=2, default=str))
        if report_path and os.path.exists(report_path):
            z.write(report_path, "Risk Architecture Report.pdf")
        z.writestr("Research Notes.txt", _research_notes_text(case))
        for name, _title, blob in figs:
            z.writestr(f"Figures/{name}", blob)
    return f"{ref}.zip", buf.getvalue()
