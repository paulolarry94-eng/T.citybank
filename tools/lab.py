#!/usr/bin/env python3
"""Front door of the Truth Lab: start, check and run a strategy test with the project's discipline built in.

    python3 tools/lab.py new my_idea_v1 --family reversal,intraday --markets XAUUSD,EURUSD --timeframes H1,H4 \
            --hypothesis "Who pays, and why?"          # scaffold from TEMPLATE.py + show how earlier ideas like it ended
    python3 tools/lab.py priors reversal,intraday      # the same priors on their own
    python3 tools/lab.py check my_idea_v1              # the file loads, markets have data and costs, grid size
    python3 tools/lab.py run my_idea_v1                # everything except the final look (always safe to repeat)
    python3 tools/lab.py run my_idea_v1 --look         # + the ONE logged look at 2023-25 (the file must be committed)
    python3 tools/lab.py list [--tag T] [--survivors]  # every idea ever tested, and strategy files not yet run
    python3 tools/lab.py catalogue                     # rebuild docs/STRATEGY_CATALOGUE.md from the ledger

It wraps research/truth/run.py and research/truth/memory.py and changes neither. The guide for a new idea is
docs/TEST_A_STRATEGY.md.
"""
import os, re, sys, json, time, argparse, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TRUTH = os.path.join(ROOT, "research", "truth")
STRAT_DIR = os.path.join(TRUTH, "strategies")
TEMPLATE = os.path.join(STRAT_DIR, "TEMPLATE.py")
DATA = os.path.join(ROOT, "data")
NAME_RE = re.compile(r"^[a-z][a-z0-9_]{2,59}$")
RESERVED = {"template", "init"}
PLACEHOLDER_NAME = "my_idea_v1"
PLACEHOLDER_HYPOTHESIS = "Why should this make money? Who is on the other side?"
MANY_SETTINGS = 100            # a grid bigger than this per market is a lottery the deflated Sharpe will charge for


class LabError(Exception):
    pass


def _memory():
    if TRUTH not in sys.path:
        sys.path.insert(0, TRUTH)
    import memory
    return memory


def _csv(s):
    return [x.strip() for x in (s or "").split(",") if x.strip()]


def load_costs(path=None):
    c = json.load(open(path or os.path.join(TRUTH, "costs.json")))
    return {k: v for k, v in c.items() if not k.startswith("_")}


def known_names(strat_dir=STRAT_DIR, ledger_names=None):
    """Every NAME already taken: strategy files plus ledger entries (a name is never reused: changed rules = new NAME)."""
    names = set(RESERVED)
    if os.path.isdir(strat_dir):
        names |= {f[:-3] for f in os.listdir(strat_dir) if f.endswith(".py") and f != "TEMPLATE.py"}
    if ledger_names is None:
        ledger_names = {e.get("name", "") for e in _memory().load()}
    return names | set(ledger_names)


def bump(name):
    m = re.match(r"^(.*)_v(\d+)$", name)
    return f"{m.group(1)}_v{int(m.group(2)) + 1}" if m else f"{name}_v2"


def market_problems(markets, costs=None, data_dir=DATA, extra_costs=()):
    costs = load_costs() if costs is None else costs
    out = []
    for m in markets:
        if m not in costs and m not in extra_costs:
            out.append(f"{m}: no cost line in research/truth/costs.json (add one, marked as an estimate or from your broker)")
        if not os.path.exists(os.path.join(data_dir, f"{m}_M1_bid_2011.npz")):
            out.append(f"{m}: no data file data/{m}_M1_bid_2011.npz (see tools/DATA_HOWTO.md)")
    return out


def render_template(text, name, family, markets, timeframes, hypothesis, today):
    """Fill the five identity fields of TEMPLATE.py and add the pre-registration block. Refuses if the template changed shape."""
    subs = [
        (r'^(NAME\s*=\s*)"[^"]*"', lambda m: m.group(1) + json.dumps(name)),
        (r'^(HYPOTHESIS\s*=\s*)"[^"]*"', lambda m: m.group(1) + json.dumps(hypothesis or PLACEHOLDER_HYPOTHESIS)),
        (r'^(FAMILY\s*=\s*)\[[^\]]*\]', lambda m: m.group(1) + json.dumps(family)),
        (r'^(MARKETS\s*=\s*)\[[^\]]*\]', lambda m: m.group(1) + json.dumps(markets)),
        (r'^(TIMEFRAMES\s*=\s*)\[[^\]]*\]', lambda m: m.group(1) + json.dumps(timeframes)),
    ]
    for pat, fn in subs:
        text, n = re.subn(pat, fn, text, count=1, flags=re.M)
        if n != 1:
            raise LabError(f"TEMPLATE.py changed shape (no match for {pat[:14]}...): update render_template in tools/lab.py")
    block = (
        "# PRE-REGISTRATION: fill in BEFORE the first run, then commit and push this file (that commit is the record).\n"
        f"#   Created (UTC): {today}\n"
        "#   Who is on the other side of this trade, and why do they pay?   <answer>\n"
        "#   What result would make me drop this idea?                       <answer, e.g. negative after costs in 2011-19 or 2020-22>\n"
        "#   Costs: research/truth/costs.json (Exness Zero measured) unless COSTS says otherwise; RoboForex Prime is in costs_roboforex_prime.json\n"
        "#   Editing the rules after seeing a result is tuning: make a new file with a new NAME instead (_v2).\n")
    if "import numpy as np\n" not in text:
        raise LabError("TEMPLATE.py changed shape (no 'import numpy as np'): update render_template in tools/lab.py")
    return text.replace("import numpy as np\n", block + "import numpy as np\n", 1)


def scaffold(name, family, markets, timeframes, hypothesis="", strat_dir=STRAT_DIR, ledger_names=None, costs=None, data_dir=DATA, today=None):
    """Create strategy_dir/<name>.py from TEMPLATE.py. Returns its path."""
    if not NAME_RE.match(name):
        raise LabError("NAME must be lowercase letters, digits and underscores, start with a letter, 3-60 characters (example: tokyo_fix_v2)")
    if not family:
        raise LabError("give at least one --family tag (tags already used: python3 tools/lab.py list)")
    if not markets or not timeframes:
        raise LabError("give --markets and --timeframes (fixed before any result)")
    if name in known_names(strat_dir, ledger_names):
        raise LabError(f"the name {name!r} is already used (a strategy file or a ledger entry); changed rules need a new NAME, for example {bump(name)!r}")
    bad = market_problems(markets, costs, data_dir)
    if bad:
        raise LabError("; ".join(bad))
    today = today or time.strftime("%Y-%m-%d", time.gmtime())
    text = render_template(open(TEMPLATE).read(), name, [f.lower() for f in family], markets, timeframes, hypothesis, today)
    os.makedirs(strat_dir, exist_ok=True)
    path = os.path.join(strat_dir, name + ".py")
    try:
        with open(path, "x") as f:
            f.write(text)
    except FileExistsError:
        raise LabError(f"{path} already exists")
    return path


def n_settings(S):
    """Settings per market the lab will try: timeframes x grid x management (the deflated Sharpe charges for each)."""
    n = len(S.TIMEFRAMES)
    for v in S.GRID.values():
        n *= len(v)
    mg = getattr(S, "MANAGEMENT", None) or {}
    for v in mg.values():
        n *= max(1, len(v))
    return n


def check_strategy(path, costs=None, data_dir=DATA):
    """Load the file the way the lab does and report what is wrong before a long run. Returns dict(errors, warnings, info)."""
    if TRUTH not in sys.path:
        sys.path.insert(0, TRUTH)
    import protocol
    errors, warnings = [], []
    try:
        S = protocol.load_strategy(os.path.abspath(path))
    except SystemExit as e:
        raise LabError(str(e.code))
    except Exception as e:                                  # syntax error, import error, ...
        raise LabError(f"cannot load {path}: {e!r}")
    stem = os.path.basename(path)[:-3]
    if S.NAME == PLACEHOLDER_NAME:
        errors.append("NAME is still the template default")
    elif S.NAME != stem:
        warnings.append(f"NAME {S.NAME!r} differs from the file name {stem!r}; results go to research/results/truth/{S.NAME}/")
    if not isinstance(S.HYPOTHESIS, str) or S.HYPOTHESIS.strip() in ("", PLACEHOLDER_HYPOTHESIS):
        errors.append("HYPOTHESIS is empty or still the template text: say who is on the other side and why they pay")
    fam = getattr(S, "FAMILY", [])
    if not fam:
        errors.append("FAMILY is empty: tags let the lab show how earlier ideas like this one ended")
    if not isinstance(S.GRID, dict) or not all(isinstance(v, (list, tuple)) and len(v) > 0 for v in S.GRID.values()):
        errors.append("GRID must be a dict of non-empty lists (ordered: neighbours are one step either side)")
    if not S.TIMEFRAMES:
        errors.append("TIMEFRAMES is empty")
    if not callable(S.signals):
        errors.append("signals is not a function")
    bad = market_problems(S.MARKETS, costs, data_dir, extra_costs=tuple(getattr(S, "COSTS", {}) or {}))
    errors += bad
    cfg = 0
    if not errors:
        cfg = n_settings(S)
        if cfg > MANY_SETTINGS:
            warnings.append(f"{cfg} settings per market: a large grid is a lottery; the deflated Sharpe charges for every one. Prefer a small, meaningful grid")
    return dict(errors=errors, warnings=warnings, info=dict(name=S.NAME, markets=S.MARKETS, timeframes=S.TIMEFRAMES, settings_per_market=cfg,
                                                               family=list(fam), fingerprint=getattr(S, "FINGERPRINT", "")))


def is_committed(path, repo=ROOT):
    """True when the file is tracked by git and identical to HEAD (so the rules are on record)."""
    rel = os.path.relpath(os.path.abspath(path), repo)
    git = lambda *a: subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
    if git("ls-files", "--error-unmatch", "--", rel).returncode != 0:
        return False
    return git("status", "--porcelain", "--", rel).stdout.strip() == ""


def priors_text(tags):
    M = _memory()
    hits = M.priors(tags)
    if not hits:
        return "No earlier idea shares these tags: a new area (that is not evidence it works)."
    won = sum(M.survived(e) for e in hits)
    lines = [f"Earlier ideas with these tags: {len(hits)} tested, {won} survived."]
    for e in sorted(hits, key=lambda e: e.get("date", ""), reverse=True)[:6]:
        lines.append(f"  {e.get('date')} {e['name']} -> {(e.get('verdict') or '')[:90]}")
    if len(hits) > 6:
        lines.append(f"  ... and {len(hits) - 6} more: python3 research/truth/memory.py --priors {','.join(tags)}")
    if len(hits) >= 3 and won == 0:
        lines.append("All rejected. Before spending effort, write down why this idea differs (CLAUDE.md learning rule 1).")
    return "\n".join(lines)


NEXT = """
Next:
  1. Edit {rel}: HYPOTHESIS (who pays?), RULES, GRID, signals(), and the PRE-REGISTRATION block.
     Fix MARKETS, TIMEFRAMES and GRID now, before any result.
  2. python3 tools/lab.py check {name}
  3. git add {rel} && git commit && git push      (that commit is the pre-registration)
  4. python3 tools/lab.py run {name}               (everything except the final look; safe to repeat)
  5. Read research/results/truth/{name}/REPORT.md. A rejection is a result: record it, do not rescue it.
     Different rules = a new file and a new NAME ({bumped}).
  6. Only if it passed the development and validation gates and you want the verdict:
     python3 tools/lab.py run {name} --look        (the ONE logged look at 2023-25; the file must be committed)
"""


def cmd_new(a):
    fam = _csv(a.family)
    path = scaffold(a.name, fam, _csv(a.markets), _csv(a.timeframes), a.hypothesis or "")
    rel = os.path.relpath(path, ROOT)
    print(f"Created {rel}\n")
    print(priors_text(fam))
    print(NEXT.format(rel=rel, name=a.name, bumped=bump(a.name)))


def cmd_priors(a):
    print(priors_text(_csv(a.tags)))


def cmd_check(a):
    path = _resolve(a.target)
    r = check_strategy(path)
    i = r["info"]
    print(f"{i['name']}  markets {','.join(i['markets'])}  timeframes {','.join(i['timeframes'])}  settings per market {i['settings_per_market']}  fingerprint {i['fingerprint'][:12]}")
    for w in r["warnings"]:
        print("warning:", w)
    for e in r["errors"]:
        print("ERROR:  ", e)
    print("committed:", "yes" if is_committed(path) else "no (commit and push it before the run: that is the pre-registration)")
    return 1 if r["errors"] else 0


def cmd_run(a):
    path = _resolve(a.target)
    r = check_strategy(path)
    for w in r["warnings"]:
        print("warning:", w)
    if r["errors"]:
        for e in r["errors"]:
            print("ERROR:  ", e)
        raise LabError("fix the errors above first")
    committed = is_committed(path)
    if a.look and not committed:
        raise LabError("the final look needs a committed file: git add/commit/push it first, so the rules are on record before the answer is seen")
    if not committed:
        print("warning: the strategy file is not committed; commit and push it first so the pre-registration is on record")
    cmd = [sys.executable, os.path.join(TRUTH, "run.py"), path] + ([] if a.look else ["--no-look"])
    if a.markets:
        cmd += ["--markets", a.markets]
    print(("FULL protocol including the one logged look at 2023-25" if a.look else "Protocol without the final look") + ": " + " ".join(os.path.relpath(c, ROOT) if os.path.isabs(c) else c for c in cmd[1:]))
    rc = subprocess.call(cmd, cwd=ROOT)
    print(f"\nReport: research/results/truth/{r['info']['name']}/REPORT.md   (the lab appended the run to the research memory ledger)")
    return rc


def cmd_list(a):
    M = _memory()
    rows = M.load()
    tag = (a.tag or "").lower()
    if tag:
        rows = [e for e in rows if tag in {f.lower() for f in e.get("family", [])}]
    if a.survivors:
        rows = [e for e in rows if M.survived(e)]
    for e in sorted(rows, key=lambda e: e.get("date", "")):
        print(f"{e.get('date')}  {e['name'][:56]:56}  {(e.get('verdict') or '')[:58]}")
    print(f"\n{len(rows)} ideas" + (f" with tag {tag!r}" if tag else "") + (", survivors only" if a.survivors else ""))
    if not tag and not a.survivors:
        ran = {e.get("name") for e in M.load()}
        todo = sorted(f[:-3] for f in os.listdir(STRAT_DIR) if f.endswith(".py") and f != "TEMPLATE.py" and f[:-3] not in ran)
        if todo:
            print("strategy files with no ledger entry (not run yet, or run outside the lab): " + ", ".join(todo))


def _cell(x, n):
    x = " ".join(str(x or "").split()).replace("|", "\\|")
    return x if len(x) <= n else x[:n - 1].rstrip() + "…"


def classify(e, M):
    v = (e.get("verdict") or "").lower()
    if M.survived(e):
        return "survivor"
    return "rejected" if re.search(r"reject|fail", v) else "other"


def catalogue_text(rows, M):
    """Markdown catalogue of every idea in the ledger (deterministic: no clock, sorted by date and name)."""
    rows = sorted(rows, key=lambda e: (e.get("date", ""), e.get("name", "")))
    groups = {"survivor": [], "rejected": [], "other": []}
    for e in rows:
        groups[classify(e, M)].append(e)
    cfg = sum(M.n_configs(e) for e in rows)
    last = max((e.get("date", "") for e in rows), default="")
    L = ["# Strategy catalogue: every idea tested", "",
         f"Generated by `python3 tools/lab.py catalogue` from `research/truth/memory/ledger.jsonl` (last entry {last}); do not edit by hand.",
         f"{len(rows)} ideas, about {cfg:,} configurations: {len(groups['survivor'])} survivors or candidates, {len(groups['rejected'])} rejected, "
         f"{len(groups['other'])} other (studies, reports, controls).",
         "A survivor is a verdict that starts with Survivor, Tier A or Tier B. Lessons: `research/truth/memory/PRINCIPLES.md`; family priors: `LESSONS.md`.", ""]
    titles = (("survivor", "Survivors and candidates"), ("rejected", "Rejected"), ("other", "Other: studies, reports, controls"))
    for key, title in titles:
        L += [f"## {title} ({len(groups[key])})", "", "| Date | Idea | Family | Configs | Verdict | Evidence |", "|---|---|---|---|---|---|"]
        for e in groups[key]:
            ev = e.get("evidence") or e.get("source") or ""
            L.append(f"| {e.get('date', '')} | {_cell(e.get('name'), 70)} | {_cell(', '.join(e.get('family', [])), 60)} | "
                     f"{M.n_configs(e):,} | {_cell(e.get('verdict'), 110)} | {_cell(ev, 90)} |")
        L.append("")
    return "\n".join(L)


def cmd_catalogue(a):
    M = _memory()
    out = a.out if os.path.isabs(a.out) else os.path.join(ROOT, a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    rows = M.load()
    open(out, "w").write(catalogue_text(rows, M))
    print(f"wrote {os.path.relpath(out, ROOT)} ({len(rows)} ideas)")


def _resolve(target):
    """A path, or a bare NAME of a file in research/truth/strategies."""
    if os.path.exists(target):
        return os.path.abspath(target)
    p = os.path.join(STRAT_DIR, target if target.endswith(".py") else target + ".py")
    if os.path.exists(p):
        return p
    raise LabError(f"no strategy file {target!r} (looked in {os.path.relpath(STRAT_DIR, ROOT)})")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    n = sp.add_parser("new", help="create a strategy file from TEMPLATE.py and show the priors")
    n.add_argument("name"); n.add_argument("--family", required=True, help="comma-separated tags, e.g. reversal,intraday")
    n.add_argument("--markets", default="XAUUSD,EURUSD,GBPUSD,USDJPY"); n.add_argument("--timeframes", default="H1,H4"); n.add_argument("--hypothesis")
    n.set_defaults(fn=cmd_new)
    p = sp.add_parser("priors", help="how earlier ideas with these tags ended"); p.add_argument("tags"); p.set_defaults(fn=cmd_priors)
    c = sp.add_parser("check", help="load the file, check markets, data, costs and grid size"); c.add_argument("target"); c.set_defaults(fn=cmd_check)
    r = sp.add_parser("run", help="run the Truth Lab (no final look unless --look)"); r.add_argument("target")
    r.add_argument("--look", action="store_true", help="the ONE logged look at 2023-25 (the file must be committed)"); r.add_argument("--markets")
    r.set_defaults(fn=cmd_run)
    l = sp.add_parser("list", help="every idea in the ledger"); l.add_argument("--tag"); l.add_argument("--survivors", action="store_true"); l.set_defaults(fn=cmd_list)
    k = sp.add_parser("catalogue", help="rebuild the strategy catalogue from the ledger"); k.add_argument("--out", default="docs/STRATEGY_CATALOGUE.md")
    k.set_defaults(fn=cmd_catalogue)
    a = ap.parse_args(argv)
    try:
        return a.fn(a) or 0
    except LabError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
