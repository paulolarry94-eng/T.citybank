"""Shared definitions for the sizing studies."""
import numpy as np
import portfolio as P

U6 = np.array([3.0, 2.0, 1.33, 0.86, 0.56, 0.24]) / 100          # the brief's hierarchy
U12 = np.r_[U6, 0.24 / 100 * 0.6 ** np.arange(1, 7)]              # same top, deeper floor
FIX = np.array([1.0]) / 100                                       # fixed fractional reference
LADDERS = {"user6": U6, "user12": U12, "fixed": FIX}

PORTS = {
    "P1_strict": ["S1_XAUUSD_H1+M30_long", "TR_USDJPY_H4_atr2_long"],
    "P2_original": ["S1_XAUUSD_M20+M30_long", "S1_EURUSD_M20+M30_long", "TR_USDJPY_H4_atr2_long",
                    "TR_XAUUSD_H4_atr3_both"],
    "P3_strict+gold_trend": ["S1_XAUUSD_H1+M30_long", "TR_USDJPY_H4_atr2_long",
                             "TR_XAUUSD_H4_atr3_long"],
}


def weights(names, scheme):
    """formula: (ratio/3.5)^2.5 with S1 at 1R and trend at 1.5R | exempt: S1 forced to 1.0 |
    data: S1 1.0 vs trend 0.4 (the ratio of their measured Kelly fractions, ~2.6:1)."""
    out = []
    for n in names:
        s1 = n.startswith("S1")
        if scheme == "formula":
            out.append(P.multiplier(1.0) if s1 else P.multiplier(1.5))
        elif scheme == "exempt":
            out.append(1.0 if s1 else P.multiplier(1.5))
        elif scheme == "data":
            out.append(1.0 if s1 else 0.4)
        else:
            out.append(1.0)
    return out
