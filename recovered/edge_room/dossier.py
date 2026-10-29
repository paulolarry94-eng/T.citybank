"""Case -> Investigation Report (PDF).

The deliverable a client leaves Edge Room with: a premium research report, the
kind a serious quantitative firm would put its name to. It renders only the
Case's real record — hypothesis, verdict, the evidence with full provenance, the
prior art considered, the peer-review objections, and the investigation as it
unfolded. Every figure and every chart is drawn from what the engine actually
recorded; nothing is invented and no number appears that the evidence does not
carry. The report is beautiful because the work is real — not the other way round.
"""
from __future__ import annotations
import html as _html
import io
import os
import re
import sys
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, PageBreak, KeepTogether,
                                Image as RLImage)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backi"))
from engine import Institution, DecisionEngine  # noqa: E402
import dataset  # noqa: E402
import figures  # noqa: E402
import present  # noqa: E402

# ---------------------------------------------------------------- palette
INK   = colors.HexColor("#1a1712")
GREY  = colors.HexColor("#6b6353")
FAINT = colors.HexColor("#9c917c")
GOLD  = colors.HexColor("#b0810f")
GOLDL = colors.HexColor("#e7d5a4")
PAPER = colors.HexColor("#faf6ec")
LINE  = colors.HexColor("#e4dcc7")
GRN   = colors.HexColor("#2e7d32")
RED   = colors.HexColor("#b23b3b")
_LABEL_COLOR = {"APPROVED": GRN, "PROMISING": GOLD,
                "NEEDS MORE EVIDENCE": GREY, "REJECTED": RED}

PAGE_W, PAGE_H = A4
MARGIN = 22 * mm
CONTENT_W = PAGE_W - 2 * MARGIN


# ---------------------------------------------------------------- fonts
def _register_serif():
    """An editorial serif for display type, if the system has one; else Times."""
    pairs = [("EdgeSerif", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
              "EdgeSerif-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
             ("EdgeSerif", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
              "EdgeSerif-Bold", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf")]
    for reg, rp, bold, bp in pairs:
        if os.path.exists(rp) and os.path.exists(bp):
            try:
                pdfmetrics.registerFont(TTFont(reg, rp))
                pdfmetrics.registerFont(TTFont(bold, bp))
                return reg, bold
            except Exception:  # noqa: BLE001
                continue
    return "Times-Roman", "Times-Bold"


SERIF, SERIF_B = _register_serif()

# ---------------------------------------------------------------- styles
def _s(name, **kw):
    return ParagraphStyle(name, **kw)


DISPLAY  = _s("Display", fontName=SERIF_B, fontSize=27, leading=32, textColor=INK,
              alignment=TA_CENTER)
WORDMARK = _s("Wordmark", fontName="Helvetica-Bold", fontSize=11, textColor=INK,
              alignment=TA_CENTER, tracking=3)
KICKER   = _s("Kicker", fontName="Helvetica-Bold", fontSize=8.5, textColor=GOLD,
              alignment=TA_CENTER, tracking=3)
COVER_VD = _s("CoverVd", fontName=SERIF_B, fontSize=23, leading=27, alignment=TA_CENTER)
LEADC    = _s("LeadC", fontName=SERIF, fontSize=12.5, leading=18, textColor=GREY,
              alignment=TA_CENTER)
FINEC    = _s("FineC", fontName="Helvetica", fontSize=8.5, leading=13, textColor=FAINT,
              alignment=TA_CENTER, tracking=1)

SEC_NUM   = _s("SecNum", fontName=SERIF_B, fontSize=13, leading=15, textColor=GOLD)
SEC_TITLE = _s("SecTitle", fontName="Helvetica-Bold", fontSize=10.5, textColor=INK,
               tracking=2)
LEAD    = _s("Lead", fontName=SERIF, fontSize=12, leading=18, textColor=INK)
BODY    = _s("Body", fontName="Helvetica", fontSize=9.6, leading=14.5, textColor=INK,
             spaceAfter=3)
SMALL   = _s("Small", fontName="Helvetica", fontSize=8.2, leading=12, textColor=GREY)
KV_K    = _s("KvK", fontName="Helvetica-Bold", fontSize=9.4, textColor=INK)
STATNUM = _s("StatNum", fontName=SERIF_B, fontSize=19, textColor=INK, leading=21)
STATTXT = _s("StatTxt", fontName=SERIF_B, fontSize=13.5, textColor=INK, leading=17)
STATLAB = _s("StatLab", fontName="Helvetica-Bold", fontSize=7, textColor=FAINT,
             leading=9, tracking=1)
NOTE_L  = _s("NoteL", fontName="Helvetica-Bold", fontSize=7.5, textColor=GOLD,
             leading=10, tracking=1.5, spaceAfter=1)
NOTE_B  = _s("NoteB", fontName=SERIF, fontSize=10.6, leading=15, textColor=INK,
             spaceAfter=2)
TL_WHO  = _s("TlWho", fontName="Helvetica-Bold", fontSize=8, textColor=GOLD,
             tracking=1)
TL_BODY = _s("TlBody", fontName="Helvetica", fontSize=9.4, leading=14, textColor=INK,
             spaceAfter=7)
TH      = _s("Th", fontName="Helvetica-Bold", fontSize=7.4, textColor=GOLD, tracking=1)
TD      = _s("Td", fontName="Helvetica", fontSize=8.2, leading=11, textColor=INK)


def _esc(s):
    return _html.escape(str(s))


# ---------------------------------------------------------------- charts
def _confidence_gauge(conf, width, ready):
    h = 9
    d = Drawing(width, h); d.hAlign = "CENTER"
    d.add(Rect(0, 0, width, h, rx=4.5, ry=4.5, fillColor=LINE, strokeColor=None))
    if ready:
        w = max(0.0, min(1.0, conf)) * width
        if w > 1:
            d.add(Rect(0, 0, w, h, rx=4.5, ry=4.5, fillColor=GOLD, strokeColor=None))
    return d


def _metric_bars(rows, width):
    """rows: (label, value, vmax, display). A quiet, publication-style bar band."""
    rowh = 21
    d = Drawing(width, rowh * len(rows))
    labw = 52 * mm
    barw = width - labw - 24 * mm
    for i, (lab, val, vmax, disp) in enumerate(rows):
        y = (len(rows) - 1 - i) * rowh + 6
        d.add(String(0, y, lab, fontName="Helvetica", fontSize=9, fillColor=GREY))
        d.add(Rect(labw, y - 1, barw, 6, rx=3, ry=3, fillColor=LINE, strokeColor=None))
        frac = 0 if vmax <= 0 else max(0.0, min(1.0, val / vmax))
        if frac > 0:
            d.add(Rect(labw, y - 1, frac * barw, 6, rx=3, ry=3, fillColor=GOLD,
                       strokeColor=None))
        d.add(String(width, y, disp, fontName="Helvetica-Bold", fontSize=9,
                     fillColor=INK, textAnchor="end"))
    return d


def _coverage(evidence, width):
    dr = evidence.get("date_range", "")
    if ".." not in dr:
        return None
    a, b = (x.strip() for x in dr.split("..", 1))
    h = 30
    d = Drawing(width, h)
    y = 15
    d.add(Rect(0, y, width, 5, rx=2.5, ry=2.5, fillColor=GOLDL, strokeColor=None))
    d.add(Rect(0, y - 3, 2, 11, fillColor=GOLD, strokeColor=None))
    d.add(Rect(width - 2, y - 3, 2, 11, fillColor=GOLD, strokeColor=None))
    d.add(String(0, 3, a[:7], fontName="Helvetica", fontSize=8, fillColor=GREY))
    d.add(String(width, 3, b[:7], fontName="Helvetica", fontSize=8, fillColor=GREY,
                 textAnchor="end"))
    n = evidence.get("output", {}).get("n")
    if n:
        d.add(String(width / 2, y + 9, f"{int(n):,} verified observations",
                     fontName="Helvetica-Bold", fontSize=8.5, fillColor=INK,
                     textAnchor="middle"))
    return d


# ---------------------------------------------------------------- building blocks
def _section(story, num, title):
    story.append(Spacer(1, 12))
    row = Table([[Paragraph(f"{num:02d}", SEC_NUM),
                  Paragraph(_esc(title).upper(), SEC_TITLE)]],
                colWidths=[13 * mm, CONTENT_W - 13 * mm])
    row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                             ("LEFTPADDING", (0, 0), (-1, -1), 0),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story.append(row)
    story.append(HRFlowable(width="100%", thickness=0.8, color=GOLD,
                            spaceBefore=1, spaceAfter=10))


def _stat_band(story, tiles):
    if not tiles:
        return
    n = len(tiles)
    # numeric figures get the large display size; a text value (a source name,
    # "Verified") is set smaller so it never wraps inside its tile
    bigs = [Paragraph(_esc(b), STATNUM if re.match(r"^[+\-]?\d", b) else STATTXT)
            for b, _ in tiles]
    labs = [Paragraph(_esc(s).upper(), STATLAB) for _, s in tiles]
    t = Table([bigs, labs], colWidths=[CONTENT_W / n] * n)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, 0), "BOTTOM"),
        ("VALIGN", (0, 1), (-1, 1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, 0), 0), ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
        ("TOPPADDING", (0, 1), (-1, 1), 0), ("BOTTOMPADDING", (0, 1), (-1, 1), 0),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("LEFTPADDING", (1, 0), (-1, -1), 14),
        ("LINEBEFORE", (1, 0), (-1, -1), 0.5, LINE)]))
    story.append(t)
    story.append(Spacer(1, 4))


def _note_panel(note):
    inner = []
    for lab, key in (("Observation", "observation"), ("Evidence", "evidence"),
                     ("Meaning", "meaning")):
        val = note.get(key)
        if not val:
            continue
        inner.append(Paragraph(lab.upper(), NOTE_L))
        inner.append(Paragraph(_esc(val).replace("\n", "<br/>"), NOTE_B))
        inner.append(Spacer(1, 5))
    if inner:
        inner.pop()   # drop trailing spacer
    t = Table([[inner]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PAPER),
        ("LINEBEFORE", (0, 0), (0, -1), 2.4, GOLD),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 17), ("RIGHTPADDING", (0, 0), (-1, -1), 17),
        ("TOPPADDING", (0, 0), (-1, -1), 15), ("BOTTOMPADDING", (0, 0), (-1, -1), 13)]))
    return t


def _table(story, header, rows, colw):
    data = [[Paragraph(_esc(h).upper(), TH) for h in header]]
    data += [[Paragraph(_esc(c), TD) for c in r] for r in rows]
    t = Table(data, colWidths=colw, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, GOLD),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(t)


# ---------------------------------------------------------------- figures from evidence
_METRIC_NAME = {"n": "observations", "span_years": "span (yrs)",
                "expectancy_is": "expectancy", "expectancy_oos": "OOS expectancy",
                "win_rate": "win rate", "profit_factor": "profit factor",
                "risk_of_ruin": "risk of ruin", "max_drawdown": "max drawdown"}


def _findings_cell(out):
    parts = []
    for k, val in list(out.items())[:3]:
        name = _METRIC_NAME.get(k, k.replace("_", " "))
        if k == "win_rate" and isinstance(val, (int, float)):
            val = f"{val*100:.0f}%"
        elif k in ("expectancy_is", "expectancy_oos") and isinstance(val, (int, float)):
            val = f"{val:+.2f}R"
        elif isinstance(val, float):
            val = f"{val:.2f}"
        parts.append(f"{name} {val}")
    return ", ".join(parts)


def _strongest(case):
    best = None
    for e in case.evidence:
        if "expectancy_is" in e.get("output", {}):
            best = e
    return best or (case.evidence[-1] if case.evidence else None)


def _key_figures(case):
    e = _strongest(case)
    if not e:
        return []
    m = e.get("output", {})
    tiles = []
    if "expectancy_is" in m:
        tiles.append((f"{m['expectancy_is']:+.2f}R", "Expectancy · in-sample"))
        if "expectancy_oos" in m:
            tiles.append((f"{m['expectancy_oos']:+.2f}R", "Out-of-sample"))
        if "win_rate" in m:
            tiles.append((f"{m['win_rate']*100:.0f}%", "Win rate"))
        if "profit_factor" in m:
            tiles.append((f"{m['profit_factor']:.2f}", "Profit factor"))
    elif "n" in m:
        tiles.append((f"{int(m['n']):,}", "Observations"))
        if m.get("span_years"):
            tiles.append((f"{m['span_years']:.1f}", "Years of data"))
        if e.get("source"):
            tiles.append((e["source"], "Data source"))
        tiles.append(("Verified", "Fill integrity" if e.get("passed_fill_timing")
                      else "Record"))
    return tiles[:4]


def _metric_rows(case):
    e = _strongest(case)
    m = (e or {}).get("output", {})
    rows = []
    if "expectancy_is" in m:
        rows.append(("Expectancy — in-sample", m["expectancy_is"], 0.5,
                     f"{m['expectancy_is']:+.2f}R"))
        if "expectancy_oos" in m:
            rows.append(("Expectancy — out-of-sample", m["expectancy_oos"], 0.5,
                         f"{m['expectancy_oos']:+.2f}R"))
        if "win_rate" in m:
            rows.append(("Win rate", m["win_rate"], 1.0, f"{m['win_rate']*100:.0f}%"))
        if "profit_factor" in m:
            rows.append(("Profit factor", m["profit_factor"], 3.0,
                         f"{m['profit_factor']:.2f}"))
    return rows


# ---------------------------------------------------------------- the report
def build_dossier(case, out_path):
    inst = Institution(); de = DecisionEngine()
    v = case.verdict or {}
    label = v.get("label", "IN PROGRESS")
    conf = v.get("confidence", 0)
    ready = present.confidence_ready(case)
    market = present.detect_market(case)
    e0 = _strongest(case)
    period = (e0 or {}).get("date_range", "").replace("..", " – ") if e0 else ""
    # the stage and the dataset actually investigated — the report never implies
    # one depth of evidence while resting on another
    stg = dataset.stage_of(case.id)
    dlabel = (present.dataset_label(e0) if e0 else "") or dataset.label_for(stg)
    story = []

    # ---- cover ----
    story.append(Spacer(1, 46))
    story.append(Paragraph("EDGE ROOM", WORDMARK))
    story.append(Spacer(1, 26))
    story.append(Paragraph("RISK ARCHITECTURE REPORT", KICKER))
    story.append(Spacer(1, 6))
    story.append(Paragraph(dataset.stage_title(stg), _s("stg", parent=FINEC,
                                                        textColor=FAINT)))
    story.append(Spacer(1, 18))
    story.append(Paragraph(_esc(case.hypothesis.get("claim", "")), DISPLAY))
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width=40 * mm, thickness=0.8, color=GOLDL, hAlign="CENTER"))
    story.append(Spacer(1, 22))
    story.append(Paragraph(_esc(label), _s("cvl", parent=COVER_VD,
                                            textColor=_LABEL_COLOR.get(label, INK))))
    story.append(Spacer(1, 8))
    story.append(Paragraph(_esc(present.verdict_sentence(label)), LEADC))
    story.append(Spacer(1, 22))
    story.append(_confidence_gauge(conf, 96 * mm, ready))
    story.append(Spacer(1, 7))
    ctext = (f"CONFIDENCE&nbsp;&nbsp;·&nbsp;&nbsp;{conf:.0%}" if ready
             else "CONFIDENCE&nbsp;&nbsp;·&nbsp;&nbsp;NOT YET ESTABLISHED")
    story.append(Paragraph(ctext, _s("cf", parent=FINEC, fontName="Helvetica-Bold",
                                      textColor=GREY)))
    story.append(Spacer(1, 10))
    story.append(Paragraph("EVIDENCE&nbsp;&nbsp;·&nbsp;&nbsp;" + _esc(dlabel),
                           _s("cev", parent=FINEC, fontName="Helvetica-Bold",
                              textColor=GOLD)))
    story.append(Spacer(1, 50))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE))
    story.append(Spacer(1, 10))
    meta = "&nbsp;&nbsp;·&nbsp;&nbsp;".join(
        x for x in (market if market != "the market" else "",
                    period, datetime.now().strftime("%d %B %Y")) if x)
    story.append(Paragraph(meta, FINEC))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Prepared by Seesare&nbsp;&nbsp;·&nbsp;&nbsp;Edge Room",
                           _s("by", parent=FINEC, textColor=GOLD)))
    story.append(PageBreak())

    # ---- 01 the verdict ----
    _section(story, 1, "Strategy Overview")
    if v.get("summary"):
        story.append(Paragraph(_esc(v["summary"]), LEAD))
        story.append(Spacer(1, 8))
    kv = []
    strongest = present.strongest_finding(case)
    if strongest:
        kv.append(("Strongest evidence", strongest))
    kv.append(("Confidence", present.confidence_words(conf)
               + (f" ({conf:.0%})" if ready else "")))
    if v.get("recommended_next_step"):
        kv.append(("Recommended next step", v["recommended_next_step"]))
    if v.get("remaining_risks"):
        kv.append(("Remaining risks", v["remaining_risks"]))
    rows = [[Paragraph(_esc(k), KV_K), Paragraph(_esc(val), BODY)] for k, val in kv]
    t = Table(rows, colWidths=[46 * mm, CONTENT_W - 46 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                           ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE)]))
    story.append(t)

    # ---- 02 key figures + chart ----
    tiles = _key_figures(case)
    mrows = _metric_rows(case)
    if tiles or mrows or (e0 and ".." in (e0.get("date_range") or "")):
        _section(story, 2, "Key Figures")
        _stat_band(story, tiles)
        if mrows:
            story.append(Spacer(1, 10))
            story.append(_metric_bars(mrows, CONTENT_W))
        elif e0:
            cov = _coverage(e0, CONTENT_W)
            if cov:
                story.append(Spacer(1, 8))
                story.append(Paragraph("DATA COVERAGE", STATLAB))
                story.append(Spacer(1, 4))
                story.append(cov)

    # ---- 03 research notes (the highlights) ----
    notes = [present.research_note(e) for e in case.evidence]
    notes = [n for n in notes if n]
    if notes:
        _section(story, 3, "Research Notes")
        for i, n in enumerate(notes):
            story.append(KeepTogether(_note_panel(n)))
            if i < len(notes) - 1:
                story.append(Spacer(1, 9))

    # ---- 04 evidence & provenance ----
    _section(story, 4, "Evidence")
    if case.evidence:
        rows = []
        for e in case.evidence:
            out = {k: val for k, val in e.get("output", {}).items()
                   if not str(k).startswith("_")}
            rows.append([present.method_label(e.get("capability", "")),
                         e.get("parameters", {}).get("instrument", "—"),
                         e.get("source", ""), (e.get("date_range") or "").replace("..", "–"),
                         _findings_cell(out),
                         "Verified" if e.get("passed_fill_timing") else "—"])
        _table(story, ["Method", "Market", "Source", "Period", "Findings", "Fills"],
               rows, [30 * mm, 20 * mm, 24 * mm, 26 * mm, 46 * mm,
                      CONTENT_W - 146 * mm])
        story.append(Spacer(1, 6))
        story.append(Paragraph("Every result was measured over the stated data and "
                               "period, under realistic execution assumptions — real "
                               "spreads, real slippage, and fills only where they "
                               "could genuinely have happened.", SMALL))
    else:
        story.append(Paragraph("No measured evidence recorded.", SMALL))

    # ---- 05 figures — numbered, referenced, and honest about what is absent ----
    try:
        figs = figures.render(case)
        _can, missing = figures.available(case)
    except Exception:  # noqa: BLE001
        figs, missing = [], []
    if figs or missing:
        _section(story, 5, "Figures")
        mets = {}
        for e in case.evidence:
            mets.update(e.get("output") or {})
        for i, (fname, title, blob) in enumerate(figs, 1):
            try:
                img = RLImage(io.BytesIO(blob))
                scale = min(1.0, (CONTENT_W - 4 * mm) / img.imageWidth)
                img.drawWidth = img.imageWidth * scale
                img.drawHeight = img.imageHeight * scale
                block = [Paragraph(f"Figure {i} &nbsp;·&nbsp; {_esc(title)}",
                                   _s("figc", parent=SMALL, fontName="Helvetica-Bold",
                                      textColor=GOLD)),
                         Spacer(1, 5), img]
                key = next((k for k, t, _n, _w in figures.CATALOGUE if t == title), "")
                note = figures.observation(key, mets)
                if note:
                    block += [Spacer(1, 4),
                              Paragraph(_esc(note), _s("fign", parent=SMALL,
                                                        fontName=SERIF,
                                                        fontSize=9.5, leading=13))]
                story.append(KeepTogether(block))
                story.append(Spacer(1, 14))
            except Exception:  # noqa: BLE001
                continue
        if missing:
            story.append(Paragraph("Figures not included", _s(
                "mh", parent=SMALL, fontName="Helvetica-Bold", textColor=INK)))
            story.append(Spacer(1, 3))
            for title, why in missing:
                story.append(Paragraph(f"{_esc(title)} — {_esc(why)}.", SMALL))
            story.append(Spacer(1, 4))
            story.append(Paragraph(
                "These were not drawn because the evidence to draw them honestly "
                "does not exist in this investigation. A figure estimated from "
                "summary statistics would not be evidence.", SMALL))

    # ---- 06 recommendations — only what the verdict actually recorded ----
    recs = [(k.replace("_", " ").title(), v[k]) for k in
            ("recommended_next_step", "remaining_risks", "weaknesses") if v.get(k)]
    if recs:
        _section(story, 6, "Recommendations")
        rows = [[Paragraph(_esc(k), KV_K), Paragraph(_esc(val), BODY)]
                for k, val in recs]
        t = Table(rows, colWidths=[46 * mm, CONTENT_W - 46 * mm])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 6),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                               ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE)]))
        story.append(t)

    # ---- 06 appendix · prior art ----
    _section(story, 7, "Appendix · Prior Art")
    hits = inst.precedent.search(case.hypothesis, exclude_id=case.id)
    if hits:
        # the institution's accumulated principles, stated plainly — never the
        # internal reference codes they are filed under
        _table(story, ["What the institution already knew"],
               [[h.precedent.title] for h in hits[:6]], [CONTENT_W])
    else:
        story.append(Paragraph("No close precedent — comparatively novel ground.", SMALL))

    # ---- 06 peer review ----
    _section(story, 8, "Appendix · Peer Review")
    ruling = inst.rule(case, proposed_label=de.suggest_verdict_label(case))
    rep = ruling.review
    if rep.objections:
        _table(story, ["Severity", "Objection"],
               [[o.severity.title(), o.message] for o in rep.objections],
               [26 * mm, CONTENT_W - 26 * mm])
    else:
        story.append(Paragraph("The referee cleared the evidence with no objections.",
                               SMALL))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Verdict ceiling supported by the evidence: "
                           f"<b>{_esc(rep.verdict_ceiling)}</b>.", BODY))

    # ---- 07 how it unfolded ----
    story.append(Spacer(1, 4))
    _section(story, 9, "Appendix · How the Investigation Unfolded")
    for o in present.visible_timeline(case):
        if o.get("kind") == "evidence":
            who, text = "Research note", o.get("text", "")
        else:
            who, text = o.get("who", ""), o.get("text", "")
        block = (f"<b><font color='#b0810f'>{_esc(who)}</font></b>&nbsp;&nbsp;{_esc(text)}"
                 if who else _esc(text))
        story.append(Paragraph(block, TL_BODY))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Every hypothesis enters Edge Room innocent and must earn "
                           "the right to trade. Nothing here is funded until a live "
                           "demo on the funding broker passes its gate.",
                           _s("close", parent=SMALL, alignment=TA_CENTER,
                              textColor=FAINT)))

    ref = case.id.replace("CASE-", "")

    def _chrome(canvas, doc):
        canvas.saveState()
        if doc.page > 1:
            canvas.setFont("Helvetica-Bold", 7)
            canvas.setFillColor(FAINT)
            canvas.drawString(MARGIN, 13 * mm, "EDGE ROOM")
            canvas.setFont("Helvetica", 7)
            canvas.drawCentredString(PAGE_W / 2, 13 * mm, f"Ref · {ref}")
            canvas.drawRightString(PAGE_W - MARGIN, 13 * mm, f"{doc.page:02d}")
            canvas.setStrokeColor(LINE); canvas.setLineWidth(0.4)
            canvas.line(MARGIN, 16 * mm, PAGE_W - MARGIN, 16 * mm)
        canvas.restoreState()

    doc = SimpleDocTemplate(out_path, pagesize=A4, topMargin=MARGIN,
                            bottomMargin=20 * mm, leftMargin=MARGIN, rightMargin=MARGIN,
                            title="Edge Room · Risk Architecture Report",
                            author="Seesare · Edge Room")
    doc.build(story, onFirstPage=_chrome, onLaterPages=_chrome)
    return out_path
