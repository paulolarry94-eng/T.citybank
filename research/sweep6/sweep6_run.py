"""Deep M1 study, step 1: every M1 setup of the superset on the 12 markets, 2011-2025 (no 2026), simulated alone and
frictionless (research/sweep6/PREREGISTRATION.md). Saves one npz per market (features + outcomes, pessimistic and
optimistic same-minute ordering) to $SWEEP6_DIR (default: research/results/sweep6/_cells, git-ignored).
    python3 research/sweep6/sweep6_run.py
"""
import os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "truth")); sys.path.insert(0, HERE)
import protocol as P              # noqa: E402
import sweep6_scan as SC          # noqa: E402
import sweep6_outcomes as OC      # noqa: E402

MARKETS = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "EURGBP", "WTI", "US500", "NAS100", "GER40", "UK100", "JP225"]
DIR = os.environ.get("SWEEP6_DIR", os.path.join(ROOT, "research", "results", "sweep6", "_cells"))
LIFE = 60


def one(sym):
    t0 = time.time()
    M = P.market(sym)
    B = M.bars("M1")
    S, L = SC.setups(B, 1, sym)
    O = SC.orders(S, L, LIFE)
    M1 = dict(ts=M.ts, o=M.o, h=M.h, l=M.l, c=M.G.c)
    out = OC.run(M1, O, L, gaps=M.gaps)
    opt = OC.run(M1, O, L, optimistic=True, post_min=0, gaps=M.gaps)
    keep = {k: v for k, v in S.items()}
    keep.update({f"o_{k}": v for k, v in out.items()})
    keep["o_R_opt"] = opt["R"]
    os.makedirs(DIR, exist_ok=True)
    np.savez_compressed(os.path.join(DIR, f"{sym}_M1.npz"), **{k: np.asarray(v) for k, v in keep.items()})
    n_f = int((out["status"] == 3).sum())
    print(f"{sym}: {len(S['k'])} setups, {n_f} filled, {time.time() - t0:.0f}s", flush=True)
    return sym, len(S["k"]), n_f


if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(3) as pool:
        res = list(pool.imap_unordered(one, MARKETS))
    print(res)
