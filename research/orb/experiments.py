"""ORB 50 — controlled experiments (Part 5). Every configuration that is run is logged.

Protocol
* Grid runs only ever see 2011-2022 (development + validation). The final out-of-sample years
  2023-2025 are masked out here, so no grid can be tuned on them.
* Each logged row keeps per-year aggregates (trades, sum R, sum R^2, sum of wins, sum of losses,
  cost in R). Selection (selection.py) reads only the development years 2011-2019; validation
  2020-2022 is read for a short list only; walk-forward rolls through 2011-2022.
* Stages: E0 canonical baseline map, E1 Model A mechanics, E2 Model B (H4 EMA bias), E3 Model C
  (pullback continuation), E6 failed-breakout reversal. E4 (management) and E5 (filters) run on
  the short list (see refine.py).
"""
import os, sys, csv, gzip, time, itertools
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import core, strategy as S                              # noqa: E402

RES = os.path.join(HERE, "..", "results")
YEARS = list(range(2011, 2023))                         # what grids are allowed to see
LAST_GRID_YEAR = 2022
NO_DATA = {("XAUUSD", "TOK"), ("GBPUSD", "TOK")}        # 00:00-01:00 UTC missing in 2011-2017/18


def combos():
    for sym in core.SYMS:
        for sess in core.SESSIONS:
            if (sym, sess) in NO_DATA:
                continue
            for orb in core.ORB_MIN:
                yield sym, sess, orb


# ------------------------------------------------------------------ filters (past-only)
def trailing_rank(x, n=100, min_n=20):
    """Percentile (0-100) of x[i] among the previous n values (strictly earlier sessions)."""
    out = np.full(len(x), np.nan)
    for i in range(len(x)):
        w = x[max(0, i - n):i]
        if len(w) >= min_n:
            out[i] = 100.0 * (w < x[i]).mean()
    return out


def regime_ratio(x, n=250, min_n=60):
    """x[i] / median of the previous n values."""
    out = np.full(len(x), np.nan)
    for i in range(len(x)):
        w = x[max(0, i - n):i]
        if len(w) >= min_n:
            out[i] = x[i] / np.median(w)
    return out


_cache = {}


def filter_mask(M, sess, orb, spec):
    D = M.days(sess, orb)
    m = np.ones(len(D["orh"]), bool)
    if not spec:
        return m
    for part in spec.split(";"):
        kind, rng = part.split(":")
        lo, hi = map(float, rng.split("~"))
        key = (M.sym, sess, orb, kind)
        if key not in _cache:
            _cache[key] = trailing_rank(D["w_atr"]) if kind == "w" else regime_ratio(D["atrD"])
        x = _cache[key]
        m &= np.isfinite(x) & (x >= lo) & (x <= hi)
    return m


# ------------------------------------------------------------------ stages
BIAS = [("close", 0.25), ("body", 0.25), ("neutral", 0.25), ("neutral", 0.5), ("slope", 0.25)]


def stage_tasks(stage):
    T = []
    if stage == "E0":
        for tg in (0.0, 1.5, 2.0, 2.5, 3.0):
            T.append((dict(entry=0, buf=0.0, stop=0, tgt=tg), "", None))
    elif stage == "E1":
        entries = [dict(entry=0), dict(entry=1), dict(entry=2, tol=0.1), dict(entry=2, tol=0.25), dict(entry=2, tol=0.5)]
        stops = [dict(stop=0), dict(stop=1), dict(stop=2, stop_k=2.0), dict(stop=3)]
        for e, st, buf, tg in itertools.product(entries, stops, (0.0, 0.05, 0.1, 0.2), (0.0, 1.5, 2.0, 2.5, 3.0)):
            T.append((dict(**e, **st, buf=buf, tgt=tg), "", None))
    elif stage == "E2":
        entries = [dict(entry=0), dict(entry=1), dict(entry=2, tol=0.25)]
        for e, stp, buf, tg, (kind, z), ema in itertools.product(entries, (0, 3), (0.0, 0.1), (0.0, 1.5, 2.0, 3.0),
                                                              BIAS, (20, 50, 100)):
            T.append((dict(**e, stop=stp, buf=buf, tgt=tg, bias=1), "", dict(period=ema, kind=kind, z=z)))
    elif stage == "E3":
        pbs = [dict(entry=3, pb_k=k, pb_hi=ph) for k in (1, 2, 3) for ph in (0, 1)] + \
              [dict(entry=4, pb_atr=x) for x in (0.25, 0.5, 0.75, 1.0)]
        stops = [dict(stop=0), dict(stop=1), dict(stop=2, stop_k=2.0)]
        for pb, disp, st, tg, b in itertools.product(pbs, (0.0, 0.5, 1.0), stops, (0.0, 1.5, 2.0, 3.0), (0, 1)):
            T.append((dict(**pb, disp=disp, **st, tgt=tg, bias=b), "",
                      dict(period=50, kind="body", z=0.25) if b else None))
    elif stage == "E6":
        for mf, st, tg, buf in itertools.product((1, 2), (dict(stop=1), dict(stop=2, stop_k=2.0)),
                                                 (0.0, 1.0, 1.5, 2.0), (0.0, 0.1)):
            T.append((dict(entry=5, min_fails=mf, **st, tgt=tg, buf=buf), "", None))
    else:
        raise ValueError(stage)
    return T


# ------------------------------------------------------------------ worker
COLS_Y = ["n", "s", "ss", "pos", "neg", "c"]


def aggregate(tr, years, cost):
    y = years[tr["d"]]
    r = tr["r"]; c = cost / tr["dist"]
    row = {}
    for yy in YEARS:
        k = y == yy
        rk = r[k]
        row[f"n_{yy}"] = int(k.sum()); row[f"s_{yy}"] = float(rk.sum()); row[f"ss_{yy}"] = float((rk ** 2).sum())
        row[f"pos_{yy}"] = float(rk[rk > 0].sum()); row[f"neg_{yy}"] = float(-rk[rk < 0].sum())
        row[f"c_{yy}"] = float(c[k].sum())
        row[f"nl_{yy}"] = int((k & (tr["side"] > 0)).sum()); row[f"sl_{yy}"] = float(r[k & (tr["side"] > 0)].sum())
    return row


def run_one(M, sess, orb, cfg, filt, bias_cfg, cost=None):
    D = M.days(sess, orb)
    allow = (D["year"] <= LAST_GRID_YEAR) & filter_mask(M, sess, orb, filt)
    tr = S.run(M, sess, orb, allow=allow, bias_cfg=bias_cfg, cost=cost, **cfg)
    return tr, D


def worker(job):
    sym, tasks = job
    M = core.Market(sym)
    rows = []
    t0 = time.time()
    for (eid, stage, sess, orb, cfg, filt, bias_cfg) in tasks:
        tr, D = run_one(M, sess, orb, cfg, filt, bias_cfg)
        row = dict(id=eid, stage=stage, sym=sym, session=sess, orb=orb, filt=filt,
                   bias_kind=bias_cfg["kind"] if bias_cfg else "", bias_ema=bias_cfg["period"] if bias_cfg else 0,
                   bias_z=bias_cfg["z"] if bias_cfg else 0.0)
        row.update({k: v for k, v in S.params(**cfg).items()})
        row.update(aggregate(tr, D["year"], M.cost))
        rows.append(row)
    print(f"  {sym}: {len(tasks)} runs in {time.time() - t0:.0f}s", flush=True)
    return rows


def run_stage(stage, extra=None, procs=4):
    """extra: optional list of (sym, sess, orb, cfg, filt, bias_cfg) to run instead of the grid."""
    jobs = {s: [] for s in core.SYMS}
    eid = 0
    if extra is None:
        T = stage_tasks(stage)
        for sym, sess, orb in combos():
            for cfg, filt, b in T:
                jobs[sym].append((f"{stage}-{eid}", stage, sess, orb, cfg, filt, b)); eid += 1
    else:
        for sym, sess, orb, cfg, filt, b in extra:
            jobs[sym].append((f"{stage}-{eid}", stage, sess, orb, cfg, filt, b)); eid += 1
    order = sorted(jobs, key=lambda s: -len(jobs[s]))
    with Pool(min(procs, len(order))) as pool:
        parts = pool.map(worker, [(s, jobs[s]) for s in order if jobs[s]])
    rows = [r for p in parts for r in p]
    write_log(stage, rows)
    return rows


def write_log(stage, rows):
    path = os.path.join(RES, "orb_experiments", f"{stage}.csv.gz")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    keys = list(rows[0].keys())
    with gzip.open(path, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    print(f"{stage}: {len(rows)} experiments logged -> {path}", flush=True)


if __name__ == "__main__":
    for st in sys.argv[1:]:
        t0 = time.time()
        run_stage(st)
        print(f"{st} done in {time.time() - t0:.0f}s", flush=True)
