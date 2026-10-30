"""Daily London scanner, step 1: every candidate setup of the 8 families (PREREGISTRATION.md §2) on every
London day 2011-2025, each simulated on its own (no portfolio interaction yet) with the North Star fill
law. Also a stressed outcome: costs x1.5 and entry delayed by one minute.

    python3 candidates.py -> ../results/scanner/candidates.csv.gz
"""
import os, sys, datetime as dt, time
from zoneinfo import ZoneInfo
from multiprocessing import Pool
import numpy as np
import pandas as pd
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "northstar")); sys.path.insert(0, os.path.join(HERE, ".."))
import core
import engine as E

SYMS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
FAMS = ["ABO", "AFD", "PDB", "PDF", "TPB", "OMO", "EUH", "MRX"]
LDN = ZoneInfo("Europe/London")
OUT = os.path.join(HERE, "..", "results", "scanner")


def london_offset(t):
    days = np.asarray(t, np.int64) // 86400
    ud, inv = np.unique(days, return_inverse=True)
    off = np.array([int(dt.datetime.fromtimestamp(int(d) * 86400 + 43200, tz=LDN).utcoffset().total_seconds()) for d in ud])
    return off[inv]


@njit(cache=True)
def simulate(o, h, l, ts, k0, side, stop, tgt, kend, cost, gaps, delay):
    """Each candidate on its own. Returns r, t_in, t_out, dist (nan r = not executable)."""
    n = len(k0); r = np.full(n, np.nan); tin = np.zeros(n, np.int64); tout = np.zeros(n, np.int64); dist = np.zeros(n)
    for j in range(n):
        i0 = k0[j] + delay; i1 = kend[j]
        if i0 >= len(o) - 1 or i1 <= i0 or i1 >= len(o):
            continue
        p = np.searchsorted(gaps, i0)
        if p < len(gaps) and gaps[p] < i1:
            continue
        sd = side[j]; sl = stop[j]
        entry = o[i0] + cost if sd > 0 else o[i0]
        d = entry - sl if sd > 0 else sl - entry
        if d <= 0:
            continue
        tp = 0.0
        if tgt[j] > 0:
            tp = entry + tgt[j] * d if sd > 0 else entry - tgt[j] * d
        px = 0.0; xi = i1; done = False
        for i in range(i0, i1):
            if sd > 0:
                if l[i] <= sl:
                    px = sl if (o[i] > sl or i == i0) else o[i]; px = min(px, sl); xi = i; done = True; break
                if tp > 0 and h[i] >= tp:
                    px = tp; xi = i; done = True; break
            else:
                if h[i] + cost >= sl:
                    ao = o[i] + cost
                    px = sl if (ao < sl or i == i0) else ao; px = max(px, sl); xi = i; done = True; break
                if tp > 0 and l[i] + cost <= tp:
                    px = tp; xi = i; done = True; break
        if not done:
            px = o[i1] if sd > 0 else o[i1] + cost
        r[j] = (px - entry) / d if sd > 0 else (entry - px) / d
        tin[j] = ts[i0]; tout[j] = ts[xi]; dist[j] = d
    return r, tin, tout, dist


def build(sym):
    t0 = time.time()
    M = core.Mkt(sym); B = M.bars("M15"); D = M.bars("D1")
    bt, o, h, l, c, nxt = B["t"], B["o"], B["h"], B["l"], B["c"], B["nxt"]
    dec_t = bt + 900
    off = london_offset(bt); lt = bt + off
    ldate = lt // 86400; lstart = (lt % 86400) // 60; lclose = lstart + 15
    kD = np.searchsorted(D["t"] + 1440 * 60, dec_t, side="right") - 1
    okD = kD >= 0; kD = np.clip(kD, 0, None)
    A = np.where(okD, D["atr"][kD], 0.0); PDH = D["h"][kD]; PDL = D["l"][kD]
    T = np.sign(E.ema(D["c"], 20) - E.ema(D["c"], 50)); T[~np.isfinite(T)] = 0; T = T[kD].astype(int)
    em = E.ema(c, 20)
    cost = M.cost
    rows = []

    def add(fam, i, side, stop, tgt, exit_lmin):
        a = A[i]
        est = abs(c[i] - stop)
        if a <= 0 or est < max(0.10 * a, 3 * cost) or est > 1.0 * a:
            return
        d0 = int(ldate[i]); t_exit = d0 * 86400 + exit_lmin * 60 - int(off[i])
        rows.append((fam, int(side), int(side == T[i]), int(dec_t[i]), int(nxt[i]), float(stop), float(tgt), t_exit, float(a), d0))

    bounds = np.flatnonzero(np.diff(ldate)) + 1
    starts = np.r_[0, bounds]; ends = np.r_[bounds, len(bt)]
    for s, e in zip(starts, ends):
        d0 = ldate[s]; wd = (d0 + 3) % 7
        if wd >= 5 or e - s < 40:
            continue
        idx = np.arange(s, e); ls, lc = lstart[idx], lclose[idx]
        asian = idx[(ls >= 0) & (lc <= 420)]
        if len(asian) < 8:
            continue
        AH, AL = h[asian].max(), l[asian].min(); mid = (AH + AL) / 2
        day_open = o[s]
        hi_sofar = np.maximum.accumulate(h[idx]); lo_sofar = np.minimum.accumulate(l[idx])
        done = set()
        bar08 = idx[ls == 480]
        for jj, i in enumerate(idx):
            cl = lc[jj]
            if cl < 480 or cl > 900 or not okD[i]:
                continue
            a = A[i]
            if a <= 0:
                continue
            # ABO: first close beyond the Asian range, 08:00-11:00
            if cl <= 660 and "ABO" not in done and AH - AL >= 0.1 * a:
                if c[i] > AH:
                    add("ABO", i, 1, max(mid, c[i] - 0.5 * a), 1.5, 990); done.add("ABO")
                elif c[i] < AL:
                    add("ABO", i, -1, min(mid, c[i] + 0.5 * a), 1.5, 990); done.add("ABO")
            # AFD: sweep of the Asian high/low and close back inside, 08:00-11:00, first per side
            if cl <= 660:
                if "AFD-" not in done and h[i] > AH and AL < c[i] < AH:
                    add("AFD", i, -1, hi_sofar[jj] + 0.05 * a, 1.5, 990); done.add("AFD-")
                if "AFD+" not in done and l[i] < AL and AL < c[i] < AH:
                    add("AFD", i, 1, lo_sofar[jj] - 0.05 * a, 1.5, 990); done.add("AFD+")
            # PDB: first close beyond PDH / PDL, first per side
            if "PDB+" not in done and c[i] > PDH[i]:
                add("PDB", i, 1, c[i] - 0.3 * a, 1.5, 990); done.add("PDB+")
            if "PDB-" not in done and c[i] < PDL[i]:
                add("PDB", i, -1, c[i] + 0.3 * a, 1.5, 990); done.add("PDB-")
            # PDF: sweep of PDH / PDL and close back inside, first per side
            if "PDF-" not in done and h[i] > PDH[i] and c[i] < PDH[i]:
                add("PDF", i, -1, hi_sofar[jj] + 0.05 * a, 1.5, 990); done.add("PDF-")
            if "PDF+" not in done and l[i] < PDL[i] and c[i] > PDL[i]:
                add("PDF", i, 1, lo_sofar[jj] - 0.05 * a, 1.5, 990); done.add("PDF+")
            # TPB: trend pullback reclaiming the M15 EMA20, 09:00-14:00, first per day
            if 540 <= cl <= 840 and "TPB" not in done and T[i] != 0 and jj >= 4:
                if T[i] > 0 and c[i - 1] < em[i - 1] and c[i] > em[i]:
                    add("TPB", i, 1, l[i - 3:i + 1].min() - 0.05 * a, 2.0, 990); done.add("TPB")
                elif T[i] < 0 and c[i - 1] > em[i - 1] and c[i] < em[i]:
                    add("TPB", i, -1, h[i - 3:i + 1].max() + 0.05 * a, 2.0, 990); done.add("TPB")
            # OMO: opening momentum at 09:00
            if cl == 540 and len(bar08):
                mv = c[i] - o[bar08[0]]
                if abs(mv) >= 0.25 * a:
                    sd = 1 if mv > 0 else -1
                    add("OMO", i, sd, c[i] - sd * 0.3 * a, 2.0, 990)
            # EUH: EURUSD short 09:00-13:00 London, Tue-Thu
            if sym == "EURUSD" and cl == 540 and wd in (1, 2, 3):
                add("EUH", i, -1, c[i] + 0.5 * a, 0.0, 780)
            # MRX: extension fade 12:00-14:00, first per day
            if 720 <= cl <= 840 and "MRX" not in done and abs(c[i] - day_open) >= 0.8 * a:
                sd = -1 if c[i] > day_open else 1
                add("MRX", i, sd, c[i] - sd * 0.4 * a, 1.0, 990); done.add("MRX")
    C = pd.DataFrame(rows, columns=["fam", "side", "aligned", "dec_t", "k0", "stop", "tgt", "t_exit", "A", "ldate"])
    C["sym"] = sym
    kend = np.searchsorted(M.ts, C.t_exit.values).astype(np.int64)
    args = (M.o, M.h, M.l, M.ts, C.k0.values.astype(np.int64), C.side.values.astype(np.int64), C.stop.values, C.tgt.values, kend, M.cost, M.gaps)
    r, tin, tout, dist = simulate(*args, 0)
    rs, tins, touts, dists = simulate(*args, 1)
    C["r"], C["t_in"], C["t_out"], C["dist"] = r, tin, tout, dist
    C["cost_R"] = np.where(dist > 0, M.cost / np.where(dist > 0, dist, 1), np.nan)
    C["r_stress"] = rs - 0.5 * M.cost / np.where(dists > 0, dists, np.nan)
    C["t_out_stress"] = touts
    C = C[np.isfinite(C.r)].reset_index(drop=True)
    print(f"{sym}: {len(C)} candidates in {time.time() - t0:.0f}s", flush=True)
    return C


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with Pool(4) as p:
        parts = p.map(build, SYMS)
    C = pd.concat(parts, ignore_index=True).sort_values(["dec_t", "sym", "fam"]).reset_index(drop=True)
    C.to_csv(os.path.join(OUT, "candidates.csv.gz"), index=False)
    y = pd.to_datetime(C.dec_t, unit="s").dt.year
    print(C.groupby(["fam", "sym"]).size().unstack().to_string())
    print("days with >= 1 candidate:", C.ldate.nunique(), "candidates per day:", round(len(C) / C.ldate.nunique(), 1))
