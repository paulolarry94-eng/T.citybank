"""The 3:30 scanner on Jan-Oct 2026, the period the owner trades now (NOT a clean test: the owner built the idea on it).

    python3 research/owner330/check_2026.py     # writes research/results/owner330/check_2026.json and CHECK_2026.md
    python3 research/owner330/check_2026.py --feed data/holdout/histdata   # 2026 from a second feed (HistData monthly files,
        # downloaded 2026-11-02, clock-corrected by tools/histdata_m1.py) -> check_2026_histdata.json (2026 only, with a
        # week-by-week clock check of that feed against our 2026 files)

Markets with 2026 minute data here: XAUUSD, EURUSD, GBPUSD, USDJPY (Exness ticks) and EURGBP (HistData, clock fixed).
2025 is loaded only to warm up the EMAs: trades before 2026-01-01 are dropped unseen. Same rules, costs (RoboForex Prime
published) and news-day skips as the lab run. For comparison the same five markets in 2011-19 and 2020-22 (lab data).
Scored in the owner's units with research/truth/cyclegoal.py (cycles of 10 trades, lifecycles of 360).
"""
import os, sys, json, itertools, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import replay                      # noqa: E402  (Market2026, the strategy module S)
import protocol as P               # noqa: E402
import cyclegoal as G              # noqa: E402
from grid import year_index        # noqa: E402

S = replay.S
MKTS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP"]
T2026 = int(dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc).timestamp())
OUT = os.path.join(ROOT, "research", "results", "owner330")


def configs():
    names = list(S.GRID)
    for vals in itertools.product(*[S.GRID[k] for k in names]):
        yield dict(tf="M5", **dict(zip(names, vals)))


def pooled(parts):
    T = np.vstack(parts) if parts else np.zeros((0, 16))
    return T[np.argsort(T[:, 0], kind="stable")]


def summary(T):
    if len(T) == 0:
        return dict(trades=0)
    R, c = T[:, 3], T[:, 5]
    sc = G.score(R, T[:, 0])
    return dict(trades=int(len(R)), net_R=round(float(R.mean()), 4), gross_R=round(float((R + c).mean()), 4),
                cost_R=round(float(c.mean()), 4), win_rate=round(float((R > 0).mean()), 3), s=sc.get("s"),
                cycle_at_3_6=(sc.get("cycle_mean_pct_at_cap") or {}).get("3.6"), sequence=sc.get("sequence"),
                by_market={m: (round(float(T[T[:, 15] == i, 3].mean()), 3) if (T[:, 15] == i).any() else None) for i, m in enumerate(MKTS)})


def feed_clock(feed):
    """Week by week, the shift (-60/0/+60 min) that best aligns the other feed's 1-minute returns with our 2026 files."""
    import datetime as _dt
    out = {}
    for s in MKTS:
        p = os.path.join(feed, f"{s}_M1_bid_2026.npz")
        if not os.path.exists(p):
            continue
        a, b = np.load(os.path.join(ROOT, "data", "holdout", f"{s}_M1_bid_2026.npz")), np.load(p)
        ta, ca, tb, cb = a["ts"] // 1000, a["c"].astype(float), b["ts"] // 1000, b["c"].astype(float)
        on = lambda ts, c, g: np.where((np.searchsorted(ts, g, side="right") > 0) & (np.abs(ts[np.clip(np.searchsorted(ts, g, side="right") - 1, 0, None)] - g) < 120),
                                       c[np.clip(np.searchsorted(ts, g, side="right") - 1, 0, None)], np.nan)
        best = []
        monday = _dt.date(2026, 1, 5)
        while monday <= _dt.date(2026, 10, 26):
            t0 = int(_dt.datetime(monday.year, monday.month, monday.day, tzinfo=_dt.timezone.utc).timestamp())
            g = np.arange(t0, t0 + 5 * 86400, 60)
            ra = np.diff(np.log(on(ta, ca, g))); cs = {}
            for sh in (-60, 0, 60):
                rb = np.diff(np.log(on(tb + sh * 60, cb, g)))
                m = np.isfinite(ra) & np.isfinite(rb) & (ra != 0) & (rb != 0)
                if m.sum() > 500:
                    cs[sh] = float(np.corrcoef(ra[m], rb[m])[0, 1])
            if cs:
                best.append(max(cs, key=cs.get))
            monday += _dt.timedelta(days=7)
        out[s] = dict(weeks=len(best), best_shift_0=int(sum(x == 0 for x in best)))
    return out


def main(feed=None):
    alt = lambda s: os.path.join(feed, f"{s}_M1_bid_2026.npz") if feed and os.path.exists(os.path.join(feed, f"{s}_M1_bid_2026.npz")) else None
    m26 = {s: replay.Market2026(s, S.COSTS.get(s, P.COSTS.get(s, {}).get("realistic")), alt(s)) for s in MKTS}
    lab = {} if feed else {s: P.market(s, S) for s in MKTS}
    rows = []
    for p in configs():
        a, b, c = [], [], []
        for i, s in enumerate(MKTS):
            S._CACHE.clear()
            D = S.detail(m26[s], m26[s].bars("M5"), p)
            D = D[D[:, 0] >= T2026]
            a.append(np.c_[D, np.full(len(D), i)])
            if feed:
                continue
            S._CACHE.clear()
            L = S.detail(lab[s], lab[s].bars("M5"), p, cut=P.core.CUT)
            y = year_index(L[:, 0]) if len(L) else np.zeros(0)
            b.append(np.c_[L[y <= 2019], np.full(int((y <= 2019).sum()), i)])
            c.append(np.c_[L[(y >= 2020) & (y <= 2022)], np.full(int(((y >= 2020) & (y <= 2022)).sum()), i)])
        rows.append(dict(config={k: p[k] for k in S.GRID}, y2026=summary(pooled(a)), y2011_19=summary(pooled(b)),
                         y2020_22=summary(pooled(c))))
        print(rows[-1]["config"], "2026", rows[-1]["y2026"].get("net_R"), rows[-1]["y2026"].get("trades"),
              "| 2011-19", rows[-1]["y2011_19"].get("net_R"), flush=True)
    os.makedirs(OUT, exist_ok=True)
    if feed:
        feeds = {s: ("alternative feed" if alt(s) else "default feed") for s in MKTS}
        clock = feed_clock(feed); print("clock check (weeks aligned at 0 shift):", clock, flush=True)
        json.dump(dict(note=__doc__, feed=os.path.basename(os.path.normpath(feed)), feeds=feeds, clock_check=clock, markets=MKTS, rows=rows),
                  open(os.path.join(OUT, f"check_2026_{os.path.basename(os.path.normpath(feed))}.json"), "w"), indent=1, default=float)
        return
    json.dump(dict(note=__doc__, markets=MKTS, rows=rows), open(os.path.join(OUT, "check_2026.json"), "w"), indent=1, default=float)
    open(os.path.join(OUT, "CHECK_2026.md"), "w").write(markdown(rows))


def markdown(rows):
    L = ["# The 3:30 scanner on Jan-Oct 2026 (not a clean test: the owner built the idea on this period)", "",
         f"Markets: {', '.join(MKTS)} (the ones with 2026 minute data here). Net R after RoboForex Prime published costs. "
         "Same five markets in 2011-19 and 2020-22 for comparison. Cycle at 3.6% = mean return per 10-trade cycle at the risk "
         "where 95% of bootstrapped 360-trade lifecycles stay inside a 3.6% drawdown (negative edge: the loss per cycle).", "",
         "| Configuration | 2026 trades | 2026 net R | 2026 gross R | 2026 win rate | 2026 cycle at 3.6% | 2011-19 net R | 2020-22 net R |",
         "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: -(r["y2026"].get("net_R") or -9)):
        a, b, c = r["y2026"], r["y2011_19"], r["y2020_22"]
        cfg = ", ".join(f"{k} {v}" for k, v in r["config"].items())
        f = lambda v, fm="{:+.3f}": fm.format(v) if v is not None else "-"
        L.append(f"| {cfg} | {a.get('trades', 0)} | {f(a.get('net_R'))} | {f(a.get('gross_R'))} | {f(a.get('win_rate'), '{:.0%}')} | "
                 f"{f(a.get('cycle_at_3_6'), '{:+.2f}%')} | {f(b.get('net_R'))} | {f(c.get('net_R'))} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--feed") + 1] if "--feed" in sys.argv else None)
