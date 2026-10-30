"""Hunt 2, step 2b: pre-declared seasonal legs, per-year detail and cost sensitivity.
Gold uses the UTC clock and hours 01-20 only (00 UTC is missing in its tick-built years; 21-23 is
the rollover). Costs shown at 1.0x (research assumption), 0.66x and 0.5x."""
import os, sys, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "orb"))
import core
from windows import day_hours

UTC = dt.timezone.utc


def leg(sym, tz, a, b, side, X, yr, c):
    w = X[:, a:b]; ok = ~np.isnan(w).any(axis=1)
    mv = side * w[ok].sum(axis=1) / c; y = yr[ok]
    out = {}
    for k in (1.0, 0.66, 0.5):
        n = mv - k
        IS, OS = n[y <= 2018], n[y >= 2019]
        out[k] = (n.mean(), IS.mean() / IS.std() * np.sqrt(len(IS)), OS.mean() / OS.std() * np.sqrt(len(OS)),
                  n.mean() / n.std() * np.sqrt(252))
    per = [(mv[y == q] - 1.0).mean() for q in range(2011, 2026)]
    return out, per, mv, y


if __name__ == "__main__":
    M = core.Market("XAUUSD"); X, yr, ud = day_hours(M, UTC)
    c = M.cost
    best = []
    for a in range(1, 20):
        for b in range(a + 1, 21):
            w = X[:, a:b]; ok = ~np.isnan(w).any(axis=1); mv = w[ok].sum(axis=1) / c; y = yr[ok]
            IS = mv[y <= 2018]; s = np.sign(IS.mean()); n = s * IS - 1
            best.append((n.mean() / n.std() * np.sqrt(len(n)), a, b, s))
    best.sort(reverse=True)
    print("gold UTC windows, top 6 by in-sample t (net 1 cost):")
    for t, a, b, s in best[:6]:
        out, per, _, _ = leg("XAUUSD", UTC, a, b, s, X, yr, c)
        print(f"  {a:02d}-{b:02d} UTC {'long ' if s > 0 else 'short'} IS t {out[1.0][1]:+.2f} OOS t {out[1.0][2]:+.2f} | net/day {out[1.0][0]:+.2f}c  yrs+ {sum(p > 0 for p in per)}/15")
    for sym, (a, b, side) in (("EURUSD", (9, 13, -1)), ("EURUSD", (7, 13, -1)), ("XAUUSD", (1, 4, 1))):
        tz = UTC if sym == "XAUUSD" else ZoneInfo("Europe/London")
        M = core.Market(sym); X, yr, ud = day_hours(M, tz)
        out, per, mv, y = leg(sym, tz, a, b, side, X, yr, M.cost)
        print(f"\n{sym} {a:02d}-{b:02d} {'UTC' if tz is UTC else 'London'} {'long' if side > 0 else 'short'}: gross {mv.mean():+.2f} cost/day ({mv.mean()*M.cost/core.PIP[sym]:+.2f} pips)")
        for k, (m, t1, t2, sh) in out.items():
            print(f"   cost x{k:<4}: net {m:+.3f} c/day  IS t {t1:+.2f}  OOS t {t2:+.2f}  daily-Sharpe(ann) {sh:.2f}")
        print("   per-year net @1x: " + " ".join(f"{11+i:02d}:{p:+.2f}" for i, p in enumerate(per)))
