"""Liquidity-grab study: candidate generators (PREREGISTRATION.md) + grid on the North Star execution core.

    python3 lg.py -> ../results/liquidity_grab/grid.csv.gz
"""
import os, sys, time, itertools
from multiprocessing import Pool
import numpy as np
import pandas as pd
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "northstar")); sys.path.insert(0, os.path.join(HERE, "..", "scanner"))
import core
from grid import agg, MGMT, SYMS

OUT = os.path.join(HERE, "..", "results", "liquidity_grab")
TFS = ["M30", "H1", "H4", "D1"]
CAP = 3.0


@njit(cache=True)
def _sweeps(h, l, c, atr, k, age, depth, tol, pool):
    """LG1 (pool=False) / LG2 (pool=True). Returns arrays (bar, side, stop). Sweeps are evaluated on bar t
    using only swing points confirmed at or before bar t-1."""
    n = len(h)
    hj = np.empty(n, np.int64); hp = np.empty(n); nh = 0
    lj = np.empty(n, np.int64); lp = np.empty(n); nl = 0
    ob = np.empty(n, np.int64); os_ = np.empty(n, np.int64); ost = np.empty(n); m = 0
    for t in range(2 * k, n):
        A = atr[t]
        # ---------- highs swept at bar t
        lo_sw = 1e300; hi_sw = -1e300; pooled = False; any_el = False
        keep = 0
        for i in range(nh):
            if h[t] > hp[i]:
                if t - hj[i] >= age:
                    any_el = True
                    if hp[i] < lo_sw: lo_sw = hp[i]
                    if hp[i] > hi_sw: hi_sw = hp[i]
                    if pool and A > 0:
                        for q in range(nh):
                            if q != i and abs(hp[q] - hp[i]) <= tol * A:
                                pooled = True
            else:
                hj[keep] = hj[i]; hp[keep] = hp[i]; keep += 1
        nh = keep
        if any_el and A > 0 and c[t] < lo_sw and h[t] - hi_sw <= depth * A and (pooled or not pool):
            ob[m] = t; os_[m] = -1; ost[m] = h[t] + 0.1 * A; m += 1
        # ---------- lows swept at bar t
        lo_sw = 1e300; hi_sw = -1e300; pooled = False; any_el = False
        keep = 0
        for i in range(nl):
            if l[t] < lp[i]:
                if t - lj[i] >= age:
                    any_el = True
                    if lp[i] < lo_sw: lo_sw = lp[i]
                    if lp[i] > hi_sw: hi_sw = lp[i]
                    if pool and A > 0:
                        for q in range(nl):
                            if q != i and abs(lp[q] - lp[i]) <= tol * A:
                                pooled = True
            else:
                lj[keep] = lj[i]; lp[keep] = lp[i]; keep += 1
        nl = keep
        if any_el and A > 0 and c[t] > hi_sw and lo_sw - l[t] <= depth * A and (pooled or not pool):
            ob[m] = t; os_[m] = 1; ost[m] = l[t] - 0.1 * A; m += 1
        # ---------- swing points confirmed at the close of bar t (usable from t+1)
        j = t - k
        isH = True; isL = True
        for q in range(j - k, j + k + 1):
            if q != j:
                if h[q] >= h[j]: isH = False
                if l[q] <= l[j]: isL = False
        if isH:
            hj[nh] = j; hp[nh] = h[j]; nh += 1
        if isL:
            lj[nl] = j; lp[nl] = l[j]; nl += 1
    return ob[:m], os_[:m], ost[:m]


@njit(cache=True)
def _mss(h, l, c, atr, k, win):
    """LG3: sweep of a resting swing high (age >= 5) arms a short; first close below the last strength-2 swing low
    within `win` bars triggers; a close above the running sweep extreme cancels. Mirror for lows."""
    n = len(h)
    hj = np.empty(n, np.int64); hp = np.empty(n); nh = 0
    lj = np.empty(n, np.int64); lp = np.empty(n); nl = 0
    last_sl = np.nan; last_sh = np.nan                     # last strength-2 swing low / high (confirmed)
    ob = np.empty(n, np.int64); os_ = np.empty(n, np.int64); ost = np.empty(n); m = 0
    armS = -1; extS = 0.0; lvlS = 0.0; armL = -1; extL = 0.0; lvlL = 0.0
    for t in range(2 * k, n):
        A = atr[t]
        # manage armed setups first (they were armed on earlier bars)
        if armS >= 0:
            if c[t] > extS:                                # close above the sweep extreme so far: cancelled
                armS = -1
            elif c[t] < lvlS and A > 0:
                ob[m] = t; os_[m] = -1; ost[m] = extS + 0.1 * A; m += 1; armS = -1
            elif t - armS >= win:
                armS = -1
            if armS >= 0 and h[t] > extS:
                extS = h[t]
        if armL >= 0:
            if c[t] < extL:
                armL = -1
            elif c[t] > lvlL and A > 0:
                ob[m] = t; os_[m] = 1; ost[m] = extL - 0.1 * A; m += 1; armL = -1
            elif t - armL >= win:
                armL = -1
            if armL >= 0 and l[t] < extL:
                extL = l[t]
        # new sweeps at bar t
        swH = False; keep = 0
        for i in range(nh):
            if h[t] > hp[i]:
                if t - hj[i] >= 5: swH = True
            else:
                hj[keep] = hj[i]; hp[keep] = hp[i]; keep += 1
        nh = keep
        swL = False; keep = 0
        for i in range(nl):
            if l[t] < lp[i]:
                if t - lj[i] >= 5: swL = True
            else:
                lj[keep] = lj[i]; lp[keep] = lp[i]; keep += 1
        nl = keep
        if swH and armS < 0 and not np.isnan(last_sl) and c[t] >= last_sl:
            armS = t; extS = h[t]; lvlS = last_sl
        if swL and armL < 0 and not np.isnan(last_sh) and c[t] <= last_sh:
            armL = t; extL = l[t]; lvlL = last_sh
        # confirmations at the close of bar t
        j = t - k
        isH = True; isL = True
        for q in range(j - k, j + k + 1):
            if q != j:
                if h[q] >= h[j]: isH = False
                if l[q] <= l[j]: isL = False
        if isH:
            hj[nh] = j; hp[nh] = h[j]; nh += 1
        if isL:
            lj[nl] = j; lp[nl] = l[j]; nl += 1
        j2 = t - 2
        if j2 >= 2:
            if h[j2] > max(h[j2 - 2], h[j2 - 1], h[j2 + 1], h[j2 + 2]):
                last_sh = h[j2]
            if l[j2] < min(l[j2 - 2], l[j2 - 1], l[j2 + 1], l[j2 + 2]):
                last_sl = l[j2]
    return ob[:m], os_[:m], ost[:m]


def pack(B, bars, sides, stops, cap=CAP):
    ok = bars + 2 < len(B["c"])
    bars, sides, stops = bars[ok], sides[ok], stops[ok]
    return dict(k0=B["nxt"][bars].astype(np.int64), side=sides.astype(np.int64), entry=np.full(len(bars), -1.0), stop=stops.astype(np.float64),
                jb=(bars + 1).astype(np.int64), sig=bars.astype(np.int64), cap=np.full(len(bars), cap),
                dec_t=(B["t"][bars] + B["minutes"] * 60).astype(np.int64))


def lg4(M):
    """New York sweeps the London-morning range (M15)."""
    from candidates import london_offset
    B = M.bars("M15"); D = M.bars("D1")
    bt, h, l, c = B["t"], B["h"], B["l"], B["c"]
    off = london_offset(bt); lt = bt + off; ld = lt // 86400; ls = (lt % 86400) // 60; lc = ls + 15
    kD = np.clip(np.searchsorted(D["t"] + 1440 * 60, bt + 900, side="right") - 1, 0, None); A = D["atr"][kD]
    rows = []
    bounds = np.flatnonzero(np.diff(ld)) + 1
    for s, e in zip(np.r_[0, bounds], np.r_[bounds, len(bt)]):
        idx = np.arange(s, e); morn = idx[(ls[idx] >= 480) & (lc[idx] <= 720)]
        if len(morn) < 12:
            continue
        H, L = h[morn].max(), l[morn].min(); hs = np.maximum.accumulate(h[idx]); los = np.minimum.accumulate(l[idx])
        done = set()
        for jj, i in enumerate(idx):
            if not (780 <= lc[i] <= 960) or A[i] <= 0:
                continue
            for sd, cond, stop in ((-1, h[i] > H and c[i] < H, hs[jj] + 0.05 * A[i]), (1, l[i] < L and c[i] > L, los[jj] - 0.05 * A[i])):
                if cond and sd not in done:
                    est = abs(c[i] - stop)
                    if max(0.10 * A[i], 3 * M.cost) <= est <= A[i]:
                        rows.append((i, sd, stop))
                    done.add(sd)
    if not rows:
        return pack(B, np.zeros(0, np.int64), np.zeros(0, np.int64), np.zeros(0))
    R = np.array(rows)
    return pack(B, R[:, 0].astype(np.int64), R[:, 1].astype(np.int64), R[:, 2], cap=1e9)


def candidate_sets(M):
    for tf in TFS:
        B = M.bars(tf); h, l, c, a = B["h"], B["l"], B["c"], B["atr"]
        for k, age, depth in itertools.product((3, 5), (5, 20), (0.5, 1.0)):
            yield "LG1", dict(tf=tf, k=k, age=age, depth=depth), B, pack(B, *_sweeps(h, l, c, a, k, age, depth, 0.0, False))
        for k, tol in itertools.product((3, 5), (0.1, 0.25)):
            yield "LG2", dict(tf=tf, k=k, tol=tol), B, pack(B, *_sweeps(h, l, c, a, k, 5, 1.0, tol, True))
        for k, win in itertools.product((3, 5), (5, 10)):
            yield "LG3", dict(tf=tf, k=k, win=win), B, pack(B, *_mss(h, l, c, a, k, win))
    yield "LG4", dict(tf="M15"), M.bars("M15"), lg4(M)


def build(M, mod, cfg):
    for m, prm, B, C in candidate_sets_for(M, mod, cfg):
        return B, C


def candidate_sets_for(M, mod, cfg):
    if mod == "LG4":
        yield "LG4", cfg, M.bars("M15"), lg4(M); return
    B = M.bars(cfg["tf"]); h, l, c, a = B["h"], B["l"], B["c"], B["atr"]; k = int(cfg["k"])
    if mod == "LG1":
        yield mod, cfg, B, pack(B, *_sweeps(h, l, c, a, k, int(cfg["age"]), float(cfg["depth"]), 0.0, False))
    elif mod == "LG2":
        yield mod, cfg, B, pack(B, *_sweeps(h, l, c, a, k, 5, 1.0, float(cfg["tol"]), True))
    else:
        yield mod, cfg, B, pack(B, *_mss(h, l, c, a, k, int(cfg["win"])))


def run(M, mod, cfg, cut=core.CUT, **kw):
    B, C = build(M, mod, cfg)
    old = core.TIME_STOP
    core.TIME_STOP = 24 if mod == "LG4" else 50
    try:
        return core.execute(M, B, C, cfg["tgt"], cfg["trail"], cut=cut, bias=bool(cfg["bias"]), **kw)
    finally:
        core.TIME_STOP = old


def worker(sym):
    M = core.Mkt(sym); rows = []; t0 = time.time()
    for mod, prm, B, C in candidate_sets(M):
        core.TIME_STOP = 24 if mod == "LG4" else 50
        for (tgt, trail), bias in itertools.product(MGMT, (False, True)):
            tr = core.execute(M, B, C, tgt, trail, bias=bias)
            rows.append(dict(module=mod, sym=sym, **prm, tgt=tgt, trail=trail, bias=int(bias), n_cands=len(C["k0"]), **agg(tr)))
    core.TIME_STOP = 50
    print(f"{sym}: {len(rows)} rows in {time.time() - t0:.0f}s", flush=True)
    return rows


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with Pool(4) as p:
        res = p.map(worker, SYMS)
    df = pd.DataFrame([r for rr in res for r in rr])
    df.to_csv(os.path.join(OUT, "grid.csv.gz"), index=False)
    print(df.groupby("module").size().to_string())
