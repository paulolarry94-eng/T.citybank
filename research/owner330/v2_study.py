"""v2 (owner's corrected 3:30 rules, 1:1): win rate against the win rate needed, by period, market, season and data feed.

    python3 research/owner330/v2_study.py      # writes research/results/owner330/v2_study.json and V2_STUDY.md

For each of the 16 configurations (anchor x stop placement x ATR buffer), trades of all markets in time order:
- 2011-19 and 2020-22 (lab data, fills before 2023; the 2023-25 holdout is not opened), Jan-Oct 2026 on the five markets with
  2026 data, on our files (Exness ticks; EURGBP HistData) and on the second feed (data/holdout/histdata).
- win rate; the break-even win rate at 1:1 after costs = (1 + mean cost in R) / 2; net and gross R per trade; t.
- "wicked out": of the trades stopped out, the share where price later reached the 1R target before the time exit.
- US summer vs winter (15:30 WAT = 10:30 vs 9:30 New York).
"""
import os, sys, json, itertools, datetime as dt
import numpy as np
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "research", "truth"))
import replay                      # noqa: E402  (Market2026)
import protocol as P               # noqa: E402
import cyclegoal as G              # noqa: E402
from grid import year_index        # noqa: E402

S = P.load_strategy(os.path.join(ROOT, "research", "truth", "strategies", "owner330_ema_retest_v2.py"))
NY = ZoneInfo("America/New_York")
FIVE = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP"]
T2026 = int(dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc).timestamp())
OUT = os.path.join(ROOT, "research", "results", "owner330")


def configs():
    names = list(S.GRID)
    for vals in itertools.product(*[S.GRID[k] for k in names]):
        yield dict(tf="M5", **dict(zip(names, vals)))


def wicked(M, T):
    """For stopped trades: did price reach the 1R target after the stop, before the time exit (16:00 New York)?"""
    flag = np.zeros(len(T), bool)
    for i, r in enumerate(T):
        if int(r[12]) != 1:
            continue
        side, tp, t_out = r[2], r[10], r[1]
        D = dt.datetime.fromtimestamp(int(r[0]), NY).date()
        tx = int(dt.datetime(D.year, D.month, D.day, 16, 0, tzinfo=NY).timestamp())
        a, b = np.searchsorted(M.ts, t_out, side="right"), np.searchsorted(M.ts, tx)
        if b > a:
            flag[i] = (M.h[a:b].max() >= tp) if side > 0 else (M.l[a:b].min() + M.cost <= tp)
    return flag


def summer(t):
    return np.array([1 if dt.datetime.fromtimestamp(int(x), NY).dst() else 0 for x in t], int)


def stats(T, wk=None):
    if len(T) < 3:
        return dict(n=int(len(T)))
    R, c = T[:, 3], T[:, 5]
    sd = R.std(ddof=1); stopped = T[:, 12] == 1
    out = dict(n=int(len(R)), win_rate=round(float((R > 0).mean()), 3), needed_win_rate=round(float((1 + c.mean()) / 2), 3),
               net_R=round(float(R.mean()), 4), gross_R=round(float((R + c).mean()), 4), cost_R=round(float(c.mean()), 3),
               t=round(float(R.mean() / sd * np.sqrt(len(R))), 2) if sd > 0 else None, s=round(float(R.mean() / sd), 4) if sd > 0 else None,
               time_exits=round(float((T[:, 12] == 3).mean()), 3))
    if wk is not None and stopped.any():
        out["stopped_then_target"] = round(float(wk[stopped].mean()), 3)
    return out


def main():
    lab = {s: P.market(s, S) for s in S.MARKETS}
    feeds = {"our 2026 files": {s: replay.Market2026(s, S.COSTS.get(s, P.COSTS.get(s, {}).get("realistic"))) for s in FIVE}}
    hd = os.path.join(ROOT, "data", "holdout", "histdata")
    feeds["HistData 2026"] = {s: replay.Market2026(s, S.COSTS.get(s), os.path.join(hd, f"{s}_M1_bid_2026.npz")
                                                   if os.path.exists(os.path.join(hd, f"{s}_M1_bid_2026.npz")) else None) for s in FIVE}
    rows = []
    for p in configs():
        cfg = {k: p[k] for k in S.GRID}
        parts, wks = [], []
        for i, s in enumerate(S.MARKETS):
            S._CACHE.clear()
            D = S.detail(lab[s], lab[s].bars("M5"), p, cut=P.core.CUT)
            parts.append(np.c_[D, np.full(len(D), i)]); wks.append(wicked(lab[s], D))
        T = np.vstack(parts); W = np.concatenate(wks); o = np.argsort(T[:, 0], kind="stable"); T, W = T[o], W[o]
        y = year_index(T[:, 0]); sm = summer(T[:, 0])
        row = dict(config=cfg)
        for per, m in (("2011-19", y <= 2019), ("2020-22", (y >= 2020) & (y <= 2022))):
            row[per] = stats(T[m], W[m])
            row[per]["cycle"] = {k: v for k, v in G.score(T[m, 3], T[m, 0]).items() if k in ("s", "cycle_mean_pct_at_cap")}
            row[per]["by_market"] = {s: stats(T[m & (T[:, 15] == i)]) for i, s in enumerate(S.MARKETS)}
            row[per]["summer"] = stats(T[m & (sm == 1)]); row[per]["winter"] = stats(T[m & (sm == 0)])
        for fname, mk in feeds.items():
            parts = []
            for i, s in enumerate(FIVE):
                S._CACHE.clear()
                D = S.detail(mk[s], mk[s].bars("M5"), p); D = D[D[:, 0] >= T2026]
                parts.append(np.c_[D, np.full(len(D), i)])
            X = np.vstack(parts); X = X[np.argsort(X[:, 0], kind="stable")]; sx = summer(X[:, 0])
            row[fname] = dict(all=stats(X), summer=stats(X[sx == 1]), winter=stats(X[sx == 0]),
                              by_market={s: stats(X[X[:, 15] == i]) for i, s in enumerate(FIVE)})
        row["2011-22 five markets"] = stats(T[(y <= 2022) & np.isin(T[:, 15], [S.MARKETS.index(s) for s in FIVE])])
        rows.append(row)
        a, b = row["2011-19"], row["our 2026 files"]["all"]
        print(cfg, "2011-19 win", a.get("win_rate"), "need", a.get("needed_win_rate"), "net", a.get("net_R"),
              "wicked", a.get("stopped_then_target"), "| 2026 win", b.get("win_rate"), "net", b.get("net_R"), flush=True)
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(note=__doc__, rows=rows), open(os.path.join(OUT, "v2_study.json"), "w"), indent=1, default=float)
    open(os.path.join(OUT, "V2_STUDY.md"), "w").write(markdown(rows))


def markdown(rows):
    f = lambda v, fm="{:+.3f}": fm.format(v) if v is not None else "-"
    L = ["# 3:30 v2 (owner's corrected rules, 1:1): win rate vs the win rate needed", "",
         "Needed win rate at 1:1 = (1 + cost in R) / 2. Net R after RoboForex Prime published costs. 'Stopped, then target' = "
         "share of stopped trades where price later reached the 1R target before 16:00 New York. 2026 = the five markets with "
         "2026 data (not a clean test: the owner's period).", "",
         "| Anchor | Stop | Buffer (ATR) | 2011-19 trades | Win rate | Needed | Net R | Stopped, then target | 2020-22 win / needed / net R | "
         "2026 win / needed / net R (our files) | 2026 net R (HistData) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: -(r["2011-19"].get("net_R") or -9)):
        c, a, v, b, h = r["config"], r["2011-19"], r["2020-22"], r["our 2026 files"]["all"], r["HistData 2026"]["all"]
        L.append(f"| {c['anchor']} | {c['stop']} | {c['buffer']} | {a.get('n')} | {f(a.get('win_rate'), '{:.1%}')} | "
                 f"{f(a.get('needed_win_rate'), '{:.1%}')} | {f(a.get('net_R'))} | {f(a.get('stopped_then_target'), '{:.0%}')} | "
                 f"{f(v.get('win_rate'), '{:.1%}')} / {f(v.get('needed_win_rate'), '{:.1%}')} / {f(v.get('net_R'))} | "
                 f"{f(b.get('win_rate'), '{:.1%}')} / {f(b.get('needed_win_rate'), '{:.1%}')} / {f(b.get('net_R'))} ({b.get('n')}) | "
                 f"{f(h.get('net_R'))} ({h.get('n')}) |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
