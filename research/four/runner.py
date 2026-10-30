"""Four strategies: execution + the management grid + per-year logging.

Management factorial applied to every entry set:
  stop   atr1.5 | atr2.5 (k x ATR14 of the signal bar from the fill) | struct (the family's level)
  tgt    none, 1, 1.5, 2, 3, 5 R
  be     none, 0.5, 1, 1.5, 2 R (stop moves to the entry price once that much is reached)
  trail  none, chandelier 2 / 3 / 4 x ATR14 (highest high of the last 22 bars - k ATR, updated at
         each bar close, never loosens)
  time stop 100 bars; one position at a time per strategy and market.
Fills (same law as all studies): entry at the open of the bar after the signal (ask = bid + cost
for longs), minute-by-minute stop/target checks, same-minute stop+target = stop, gaps fill at the
worse open, BE and trail changes act from the next minute. Stops nearer than 3x cost or farther
than 5 ATR skip the trade. Grid runs only see signals before 2023-01-01.
"""
import os, sys, csv, gzip, time, itertools
from multiprocessing import Pool
import numpy as np
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "orb"))
import engine as E, gold_lab as GL
from execution import manage
import signals as SG

SYMS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
TFS = ["H1", "H4", "D1"]
STOPS = ["atr1.5", "atr2.5", "struct"]
TGTS = [0.0, 1.0, 1.5, 2.0, 3.0, 5.0]
BES = [0.0, 0.5, 1.0, 1.5, 2.0]
TRAILS = [0.0, 2.0, 3.0, 4.0]
YEARS = list(range(2011, 2026))
CUT = 1672531200          # 2023-01-01 UTC
LOG = os.path.join(HERE, "..", "results", "four")


@njit(cache=True)
def run_book(o, h, l, ts, bnxt, bh, bl, batr, sig, side, stop_abs, dist_k, cost, tgt, be, trail, tstop, gaps):
    n = len(sig); out = np.zeros((n, 6)); m = 0; busy = -1; nb = len(bnxt); g = 0
    for s in range(n):
        i = sig[s]
        if i + 1 >= nb:
            continue
        k0 = bnxt[i]
        if k0 <= busy or k0 >= len(o) - 2:
            continue
        kend = bnxt[min(i + tstop, nb - 1)]
        if kend >= len(o):
            kend = len(o) - 1
        while g < len(gaps) and gaps[g] < k0:
            g += 1
        if g < len(gaps) and gaps[g] < kend:
            continue
        sd = side[s]
        entry = o[k0] + cost if sd > 0 else o[k0]
        a = batr[i]
        if dist_k > 0:
            stop = entry - sd * dist_k * a
        else:
            stop = stop_abs[s]
        dist = (entry - stop) if sd > 0 else (stop - entry)
        if dist < 3 * cost or dist <= 0 or dist > 5 * a:
            continue
        kx, r, why, mfe = manage(o, h, l, k0, kend, sd, entry, stop, dist, cost, tgt, be, 0.0, 1.0,
                                 trail, 22, bh, bl, bnxt, batr, i + 1, True)
        out[m, 0] = ts[k0]; out[m, 1] = ts[kx]; out[m, 2] = sd; out[m, 3] = r; out[m, 4] = dist; out[m, 5] = cost / dist
        m += 1; busy = kx
    return out[:m]


def year_index(t):
    # UTC year from epoch seconds without datetime (valid 1970-2100)
    days = t // 86400
    y = (days * 400 // 146097 + 1970).astype(np.int64)
    starts = np.array([(np.datetime64(f"{yy}-01-01") - np.datetime64("1970-01-01")).astype(int) for yy in range(1970, 2101)])
    return np.searchsorted(starts, days, side="right") - 1 + 1970


def aggregate(tr):
    row = {}
    y = year_index(tr[:, 0].astype(np.int64)) if len(tr) else np.zeros(0, np.int64)
    r = tr[:, 3] if len(tr) else np.zeros(0)
    for yy in YEARS:
        k = y == yy; rk = r[k]
        row[f"n_{yy}"] = int(k.sum()); row[f"s_{yy}"] = float(rk.sum()); row[f"ss_{yy}"] = float((rk ** 2).sum())
        row[f"c_{yy}"] = float(tr[k, 5].sum()) if len(tr) else 0.0
        lk = k & (tr[:, 2] > 0) if len(tr) else k
        row[f"nl_{yy}"] = int(lk.sum()); row[f"sl_{yy}"] = float(r[lk].sum()) if len(tr) else 0.0
    return row


class Mkt:
    def __init__(self, sym):
        self.G = GL.Market(sym); self.sym = sym; self.cost = self.G.cost

    def bars(self, tf):
        B = self.G.tf(tf)
        B["atr"] = np.nan_to_num(B["atr"], nan=0.0)
        return B

    def run(self, B, sig, side, stop, mgmt, cut=CUT):
        st, tgt, be, trail = mgmt
        keep = (B["t"][sig] + B["minutes"] * 60) < cut if cut else np.ones(len(sig), bool)
        sig, side, stop = sig[keep], side[keep], stop[keep]
        dk = 0.0 if st == "struct" else float(st[3:])
        G = self.G
        return run_book(G.o, G.h, G.l, G.ts, B["nxt"].astype(np.int64), B["h"], B["l"], B["atr"], sig, side, stop, dk,
                        self.cost, tgt, be, trail, 100, G.gaps)


def mgmt_grid():
    return list(itertools.product(STOPS, TGTS, BES, TRAILS))


def worker(sym):
    M = Mkt(sym); rows = []; t0 = time.time()
    for tf in TFS:
        B = M.bars(tf)
        for fam, var, fn in SG.entry_sets():
            sig, side, stop = fn(B)
            if len(sig) < 20:
                continue
            for mg in mgmt_grid():
                tr = M.run(B, sig, side, stop, mg)
                row = dict(sym=sym, tf=tf, fam=fam, var=var, stop=mg[0], tgt=mg[1], be=mg[2], trail=mg[3])
                row.update(aggregate(tr)); rows.append(row)
        print(f"  {sym} {tf}: {len(rows)} runs, {time.time() - t0:.0f}s", flush=True)
    return rows


def write(rows, name):
    os.makedirs(LOG, exist_ok=True)
    with gzip.open(os.path.join(LOG, name), "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    with Pool(4) as p:
        parts = p.map(worker, SYMS)
    rows = [r for p in parts for r in p]
    write(rows, "grid.csv.gz")
    print(len(rows), "runs logged")
