"""North Star grid: every pre-registered configuration of the SD, FVG and QM modules and the three
declared combination filters, per market, aggregated per year 2011-2022 (fills from 2023 masked).

    python3 grid.py            -> results/northstar/grid.csv.gz
"""
import os, sys, time, itertools
from multiprocessing import Pool
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import core, patterns as P

SYMS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
YEARS = list(range(2011, 2023))
MGMT = [(2.0, 0.0), (3.0, 0.0), (0.0, 0.0), (2.0, 3.0), (3.0, 3.0), (0.0, 3.0)]
OUT = os.path.join(HERE, "..", "results", "northstar")
TF_SD = ["M5", "M15", "M30", "H1", "H4"]
TF_FVG = ["M5", "M15", "M30", "H1"]
TF_QM = ["M15", "M30", "H1", "H4"]
_STARTS = np.array([(np.datetime64(f"{y}-01-01") - np.datetime64("1970-01-01")).astype(int) for y in range(1970, 2101)])


def year_index(t):
    return np.searchsorted(_STARTS, np.asarray(t, np.int64) // 86400, side="right") - 1 + 1970


def agg(tr):
    """Per-year sufficient statistics: trades, sum R, sum R^2, sum cost R, sum financing R, long n and sum."""
    row = {}
    y = year_index(tr[:, 0]) if len(tr) else np.zeros(0, np.int64)
    for yy in YEARS:
        k = y == yy; r = tr[k, 3] if len(tr) else np.zeros(0)
        lk = k & (tr[:, 2] > 0) if len(tr) else k
        row[f"n_{yy}"] = int(k.sum()); row[f"s_{yy}"] = float(r.sum()); row[f"ss_{yy}"] = float((r ** 2).sum())
        row[f"c_{yy}"] = float(tr[k, 5].sum()) if len(tr) else 0.0
        row[f"f_{yy}"] = float(tr[k, 7].sum()) if len(tr) else 0.0
        row[f"nl_{yy}"] = int(lk.sum()); row[f"sl_{yy}"] = float(tr[lk, 3].sum()) if len(tr) else 0.0
    return row


def fvg_flags(B, window=10):
    return P.recent_flags(B, [(i, s) for i, s, *_ in P.fvg_events(B, 0.1)], window)


def qm_flags(B, window=30):
    return P.recent_flags(B, [(u, s) for u, s, *_ in P.qm_triggers(B, 3, 0.25, "near")], window)


def candidate_sets(M):
    """Yields (module, params, B, cands, keep) for every pattern configuration of every module."""
    for tf in TF_SD:
        B = M.bars(tf); ff = fvg_flags(B); qf = qm_flags(B)
        for k, nb, entry in itertools.product((1.0, 1.5), (1, 2, 3), ("break", "retest")):
            for mod, kinds in (("SDC", ("RBR", "DBD")), ("SDR", ("DBR", "RBD"))):
                C = P.sd_candidates(M, B, nb, k, kinds, entry)
                prm = dict(tf=tf, k=k, nb=nb, entry=entry)
                yield mod, prm, B, C, None
                if mod == "SDC":
                    yield "SDC+FVG", prm, B, C, P.filter_keep(C, B, ff)
                    yield "SDC+QM", prm, B, C, P.filter_keep(C, B, qf)
    for tf in TF_FVG:
        B = M.bars(tf); sw = P.swing_levels(B, 3)
        for w in (0.1, 0.3):
            for d, b, g in itertools.product((0.0, 0.5), (0.0, 0.1), (10, 30)):
                yield "FVG-A", dict(tf=tf, w=w, d=d, b=b, g=g), B, P.fvg_candidates(M, B, "A", w, d, b, g), None
            for g in (10, 30):
                yield "FVG-B", dict(tf=tf, w=w, g=g), B, P.fvg_candidates(M, B, "B", w, age=g), None
            yield "FVG-C", dict(tf=tf, w=w), B, P.fvg_candidates(M, B, "C", w, 0.0, 0.0, 30, swings=sw), None
    for tf in TF_QM:
        B = M.bars(tf); ff = fvg_flags(B)
        for k, m, level in itertools.product((2, 3, 5), (0.25, 0.5), ("near", "far")):
            for entry, t in (("break", 0.0), ("retest", 0.0), ("retest", 0.25)):
                C = P.qm_candidates(M, B, k, m, level, entry, t)
                prm = dict(tf=tf, qk=k, m=m, level=level, entry=entry, t=t)
                yield "QM", prm, B, C, None
                yield "QM+FVG", prm, B, C, P.filter_keep(C, B, ff)


def worker(sym):
    M = core.Mkt(sym); rows = []; t0 = time.time()
    for mod, prm, B, C, keep in candidate_sets(M):
        for (tgt, trail), bias in itertools.product(MGMT, (False, True)):
            tr = core.execute(M, B, C, tgt, trail, bias=bias, keep=keep)
            rows.append(dict(module=mod, sym=sym, **prm, tgt=tgt, trail=trail, bias=int(bias), **agg(tr)))
    print(f"{sym}: {len(rows)} rows in {time.time() - t0:.0f}s", flush=True)
    return rows


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with Pool(4) as pool:
        res = pool.map(worker, SYMS)
    df = pd.DataFrame([r for rr in res for r in rr])
    df.to_csv(os.path.join(OUT, "grid.csv.gz"), index=False)
    print(df.groupby("module").size().to_string())
