"""awesome-systematic-trading strategies that run on our CFDs through the d1 engine (PREREG.md section D).

ath_trend (trend-following-effect-in-stocks, Wilcox & Crittenden): enter at the next open when the daily close is at
or above the highest close of the prior 2,520 bars (all the history we have before 2021); stop = close - 1 x ATR(10)
(simple average of the true range, the LEAN default), raised every day and never lowered, checked intrabar.
"""
import os, sys
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d1
from d1 import Rule, prev


class ATHTrend(Rule):
    def prepare(self, mk, views):
        Rule.prepare(self, mk, views)
        V = views[1]
        tr = d1.true_range(V.h, V.l, V.c)
        self.atr10 = pd.Series(tr).rolling(10, min_periods=10).mean().to_numpy()
        self.top = {}
        for s in (1, -1):
            W = views[s]
            self.top[s] = W.get(("ath2520",), lambda: prev(pd.Series(W.c).rolling(2520, min_periods=1).max().to_numpy()))

    def entry(self, u, s):
        V = self.V[s]
        if not (V.c[u] >= self.top[s][u]) or not np.isfinite(self.atr10[u]):
            return None
        return dict(w=1.0, u=u, ref_stop_v=float(V.c[u] - self.atr10[u]))

    def on_fill(self, mk, pos, u, sig):
        ev = pos.s * pos.units[0][1]
        stop = sig["ref_stop_v"]; d = ev - stop
        if d < 3 * mk.cost:
            return False
        pos.stop_v = stop; pos.st["d"] = d
        return True

    def on_close(self, mk, pos, u):
        V = self.V[pos.s]
        x = V.c[u] - self.atr10[u]
        if np.isfinite(x) and x > pos.stop_v:
            pos.stop_v = x


def make_rule(p, sym):
    return ATHTrend()


def sides_of(p):
    return (1,) if p.get("side", "long") == "long" else (1, -1)
