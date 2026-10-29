"""Search the higher-frequency families on every market. Trade lists are saved in the same
place and format as search.py, so funnel.py judges them identically (file suffix _off0 /
_off120 is kept for compatibility: these families use UTC hours, so both are the same)."""
import sys, os, time
import numpy as np
import engine as E, strategies2 as S

TR = os.path.join(os.path.dirname(__file__), "trades")
SESSIONS = [(0, 7), (7, 12), (12, 16), (16, 20), (7, 16), (12, 20), (20, 24)]


def save(key, tr):
    for off in ("0", "120"):
        np.save(os.path.join(TR, f"{key}_off{off}.npy"), tr)


def main(sym):
    m1 = E.load_m1(sym)
    t0 = time.time()
    for a, b in SESSIONS:
        for side, sn in ((1, "long"), (-1, "short")):
            save(f"SE_{sym}_{a:02d}-{b:02d}_{sn}", S.run_session(sym, m1, a, b % 24, side))
    for hs in (12, 16):
        for follow, fn in ((True, "follow"), (False, "fade")):
            save(f"IM_{sym}_{hs}h_{fn}", S.run_intraday_momentum(sym, m1, hs, 20, follow))
    for k in (1.0, 1.5):
        save(f"RV_{sym}_k{k:g}", S.run_reversal(sym, m1, k))
    for lb in (20, 60):
        for sides, sn in (((1, -1), "both"), ((1,), "long"), ((-1,), "short")):
            save(f"TM_{sym}_lb{lb}_{sn}", S.run_tsmom_weekly(sym, m1, lb, sides=sides))
    print(f"{sym} done in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
