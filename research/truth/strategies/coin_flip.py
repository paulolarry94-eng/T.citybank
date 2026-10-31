"""CONTROL: random entries. The lab must reject this; if it ever passes, the lab is broken."""
import numpy as np

NAME = "coin_flip_control_v1"
HYPOTHESIS = "None — random direction at random bars. Exists to prove the lab rejects noise."
RULES = "Every bar whose open-time hash falls in 1-in-every bucket: random side, stop 2 ATR."
TIMEFRAMES = ["H1", "H4"]
GRID = {"every": [20, 40]}


def signals(B, p, M):
    t, c, a = B["t"], B["c"], B["atr"]
    hsh = (t.astype(np.int64) * 2654435761) % 1000003                   # deterministic, depends on the bar only
    pick = np.flatnonzero((hsh % int(p["every"]) == 0) & (a > 0))
    side = np.where((hsh[pick] // 7) % 2 == 0, 1, -1)
    return [(i, int(s), c[i] - s * 2.0 * a[i]) for i, s in zip(pick, side)]
