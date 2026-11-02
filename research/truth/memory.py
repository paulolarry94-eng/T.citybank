"""The project's memory: what has been tested, what survived, what was learned.

Files (research/truth/memory/):
  ledger.jsonl       one line per tested idea (every Truth Lab run appends automatically; earlier studies seeded)
  PRINCIPLES.md      curated lessons, each with evidence and confidence; changed only when new evidence arrives
  OPEN_QUESTIONS.md  the queue of untested ideas / blockers, highest value first
  JOURNAL.md         one entry per session: what was asked, done, learned, decided
  LESSONS.md         generated overview (verdict counts, survivors, family priors, full ledger)

    python3 research/truth/memory.py --digest          # compact summary (printed at session start by the hook)
    python3 research/truth/memory.py --render          # rebuild LESSONS.md
    python3 research/truth/memory.py --priors liquidity,intraday   # what happened to earlier ideas with these tags
"""
import os, sys, json, time, argparse, re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
MEM = os.path.join(HERE, "memory")
LEDGER = os.path.join(MEM, "ledger.jsonl")
SURVIVE = ("survivor", "tier a", "tier b", "forward-test", "deployment")


def load():
    if not os.path.exists(LEDGER):
        return []
    return [json.loads(l) for l in open(LEDGER) if l.strip()]


def survived(e):
    v = e.get("verdict", "").lower()
    return any(s in v for s in SURVIVE) and not v.startswith("rejected")


def record(entry):
    """Add or replace (same name + fingerprint) an entry, then rebuild LESSONS.md."""
    os.makedirs(MEM, exist_ok=True)
    rows, prev = [], {}
    for e in load():
        if e.get("name") == entry.get("name") and e.get("fingerprint") == entry.get("fingerprint"):
            prev = e                                         # same idea, same rules: update, keep curated fields
        else:
            rows.append(e)
    new = {k: v for k, v in entry.items() if v not in (None, [], "", {})}
    if prev.get("date") and new.get("date") and new["date"] != prev["date"]:    # a re-run keeps the first test date
        new["last_run"] = new.pop("date")
    rows.append({**prev, **new})
    with open(LEDGER, "w") as f:
        for e in rows:
            f.write(json.dumps(e, default=float) + "\n")
    render()


def from_truth(S, rec):
    """Ledger entry from a Truth Lab run record."""
    sel = rec.get("selection") or {}; st = sel.get("stats") or {}
    fl = (rec.get("final_look") or {}).get("oos") or {}
    g = rec.get("grid_summary") or {}
    conf = rec.get("confirmation") or {}
    return dict(date=time.strftime("%Y-%m-%d", time.gmtime()), name=S.NAME, source="truth-lab", fingerprint=rec.get("fingerprint"),
                family=list(getattr(S, "FAMILY", [])), hypothesis=S.HYPOTHESIS, markets=rec.get("markets"), timeframes=rec.get("timeframes"),
                configs=g.get("configs"), verdict=rec.get("verdict"),
                numbers=dict(dev_E=st.get("dev_E"), val_E=st.get("val_E"), final_E=fl.get("E"), final_n=fl.get("n"), final_PF=fl.get("PF"),
                             dsr=(conf.get("dsr") or {}).get("dsr"), share_dev_positive=g.get("share_dev_positive")),
                candidate=sel.get("candidate"), evidence=f"research/results/truth/{S.NAME}/REPORT.md")


def priors(tags):
    """Earlier ideas sharing any tag: how many were tested and how many survived."""
    tags = {t.strip().lower() for t in tags if t.strip()}
    if not tags:
        return []
    hits = [e for e in load() if tags & {f.lower() for f in e.get("family", [])}]
    return hits


def family_table(rows):
    T = defaultdict(lambda: [0, 0, 0])
    for e in rows:
        for f in e.get("family", []):
            T[f][0] += 1; T[f][1] += int(survived(e)); T[f][2] += int(e.get("configs") or 0)
    return sorted(T.items(), key=lambda kv: (-kv[1][0], kv[0]))


def _num(x, nd=3):
    return "—" if x is None else (f"{x:+.{nd}f}" if isinstance(x, (int, float)) else str(x))


def render():
    rows = load()
    n_cfg = sum(int(e.get("configs") or 0) for e in rows)
    L = ["# LESSONS — generated from ledger.jsonl (do not edit; run `python3 research/truth/memory.py --render`)", "",
         f"{len(rows)} ideas tested, about {n_cfg:,} configurations; {sum(survived(e) for e in rows)} survivors. "
         "Principles: `PRINCIPLES.md` · queue: `OPEN_QUESTIONS.md` · sessions: `JOURNAL.md`.", "",
         "## Survivors", "| Idea | Family | Verdict | Key numbers | Evidence |", "|---|---|---|---|---|"]
    for e in rows:
        if survived(e):
            L.append(f"| {e['name']} | {', '.join(e.get('family', []))} | {e['verdict']} | {e.get('summary', '')} | {e.get('evidence', '')} |")
    L += ["", "## Family priors (how earlier ideas with this tag ended)", "| Tag | Ideas | Survived | Configurations |", "|---|---|---|---|"]
    for f, (n, s, c) in family_table(rows):
        L.append(f"| {f} | {n} | {s} | {c:,} |")
    L += ["", "## Every idea tested (newest first)", "| Date | Idea | Family | Configs | Verdict | Key numbers |", "|---|---|---|---|---|---|"]
    for e in sorted(rows, key=lambda e: e.get("date", ""), reverse=True):
        nums = e.get("summary") or ", ".join(f"{k} {_num(v)}" for k, v in (e.get("numbers") or {}).items() if v is not None)
        L.append(f"| {e.get('date', '')} | {e['name']} | {', '.join(e.get('family', []))} | {e.get('configs') or '—'} | {e['verdict']} | {nums} |")
    open(os.path.join(MEM, "LESSONS.md"), "w").write("\n".join(L) + "\n")


def _section_titles(path, pattern):
    if not os.path.exists(path):
        return []
    return [m.group(1).strip() for m in re.finditer(pattern, open(path).read(), re.M)]


def digest(max_recent=6):
    rows = load()
    P = _section_titles(os.path.join(MEM, "PRINCIPLES.md"), r"^### (P\d+.*)$")
    Q = _section_titles(os.path.join(MEM, "OPEN_QUESTIONS.md"), r"^### (Q\d+.*)$")
    J = os.path.join(MEM, "JOURNAL.md")
    last = ""
    if os.path.exists(J):
        parts = re.split(r"^## ", open(J).read(), flags=re.M)
        last = ("## " + parts[-1]).strip() if len(parts) > 1 else ""
        last = "\n".join(last.splitlines()[:14])
    out = ["=== T.citybank RESEARCH MEMORY (loaded at session start) ===",
           f"{len(rows)} ideas tested (~{sum(int(e.get('configs') or 0) for e in rows):,} configurations), {sum(survived(e) for e in rows)} survivors.",
           "Survivors: " + "; ".join(f"{e['name']} ({e.get('summary') or e['verdict']})" for e in rows if survived(e)),
           "Principles (evidence in research/truth/memory/PRINCIPLES.md):"] + [f"  - {p}" for p in P] + \
          ["Open questions (research/truth/memory/OPEN_QUESTIONS.md):"] + [f"  - {q}" for q in Q] + \
          ["Most recent ideas:"] + [f"  - {e.get('date')} {e['name']}: {e['verdict']}" for e in sorted(rows, key=lambda e: e.get('date', ''))[-max_recent:]] + \
          ["Last session:", last,
           "Rules: test new ideas only through the Truth Lab (research/truth/run.py); check priors first "
           "(python3 research/truth/memory.py --priors <tags>); end every session by appending to research/truth/memory/JOURNAL.md "
           "and updating PRINCIPLES / OPEN_QUESTIONS only with evidence."]
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--digest", action="store_true"); ap.add_argument("--render", action="store_true"); ap.add_argument("--priors")
    a = ap.parse_args()
    if a.render:
        render(); print("LESSONS.md rebuilt")
    if a.priors:
        hits = priors(a.priors.split(","))
        if not hits:
            print("no earlier idea shares these tags")
        for e in hits:
            print(f"{e.get('date')} {e['name']} [{', '.join(e.get('family', []))}] -> {e['verdict']}  {e.get('summary', '')}")
    if a.digest or not (a.render or a.priors):
        print(digest())
