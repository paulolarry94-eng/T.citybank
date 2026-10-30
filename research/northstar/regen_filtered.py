"""Regenerates the three filtered book legs from their base trade files (the original filter code was not
committed; the rules below are the ones written in research/REPORT.md, "Daily structure, round two").

  JPY_S2_weekbreak   keep long breakouts whose entry is above the previous Monday-Friday UTC week's high
  JPY_VBO_beyondPD   keep breakouts whose entry is beyond the previous UTC day's high (long) / low (short)
  XAU_EMA_insidePD   keep crosses whose entry is inside the previous UTC day's range

    python3 regen_filtered.py   -> prints match counts against the stored files (exact match expected for the
                                   first two; the gold rule reproduces 113 of 118 stored trades)
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
import gold_lab as GL
DAY = 86400


def prev_day(D, t):
    k = np.searchsorted(D["t"], t, side="right") - 2
    return k, D["h"][np.clip(k, 0, None)], D["l"][np.clip(k, 0, None)]


def prev_week_high(D, t):
    wk = (D["t"] // DAY + 3) // 7
    s = np.flatnonzero(np.r_[True, wk[1:] != wk[:-1]])
    Wt, Wh = D["t"][s], np.maximum.reduceat(D["h"], s)
    k = np.searchsorted(Wt, t, side="right") - 2
    return k, Wh[np.clip(k, 0, None)]


def regen():
    out = {}
    jpy = GL.Market("USDJPY").tf("D1", offset=0)
    b = np.load(os.path.join(ROOT, "trades", "TR_USDJPY_H4_atr2_long_off120.npy"))
    k, H = prev_week_high(jpy, b["t_in"]); out["JPY_S2_weekbreak"] = b[(k >= 0) & (b["entry"] > H)]
    b = np.load(os.path.join(ROOT, "trades", "multi", "USDJPY_VBO_D1_k0.7.npy"))
    k, H, L = prev_day(jpy, b["t_in"]); out["JPY_VBO_beyondPD"] = b[(k >= 0) & np.where(b["side"] > 0, b["entry"] > H, b["entry"] < L)]
    xau = GL.Market("XAUUSD").tf("D1", offset=0)
    b = np.load(os.path.join(ROOT, "trades", "multi", "XAUUSD_MAX_H4_20-50.npy"))
    k, H, L = prev_day(xau, b["t_in"]); out["XAU_EMA_insidePD"] = b[(k >= 0) & (b["entry"] >= L) & (b["entry"] <= H)]
    return out


if __name__ == "__main__":
    for name, x in regen().items():
        st = np.load(os.path.join(ROOT, "trades", "filtered", f"{name}.npy"))
        a, s = set(x["t_in"].tolist()), set(st["t_in"].tolist())
        print(f"{name:18s} regenerated {len(a):5d}  stored {len(s):5d}  common {len(a & s):5d}  exact={'yes' if a == s else 'no'}")
