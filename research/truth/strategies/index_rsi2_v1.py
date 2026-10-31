"""OPEN_QUESTIONS Q5 (watch-list since the futures study: equity-index RSI(2) mean reversion +0.41 Sharpe) and the book's
JPY_RSI2_D1 leg family, tested on the two equity-index CFDs now in data/. Declared before any run on these markets.
Rules (classic RSI(2), with a disaster stop so a trade has a 1R size):
  Long when RSI(2) closes below `lo` and the close is above its `trend`-day SMA; short when RSI(2) closes above 100-lo
  and the close is below that SMA. Exit at the next open after the first daily close back above (long) / below (short)
  the 5-day SMA, or at the stop: 3 x ATR(14) from the signal close. One position per market.
Costs and swaps: the lab's conservative estimates (costs.json); CFD financing included."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import executors

NAME = "index_rsi2_v1"
HYPOTHESIS = ("Short-term sell-offs in equity indices overshoot (liquidity demand from forced and impatient sellers) and "
              "revert within days; buying them in an uptrend earns that liquidity premium plus the equity drift.")
FAMILY = ["mean-reversion", "dip-buying", "rsi2", "index", "daily", "breadth"]
RULES = __doc__
MARKETS = ["US500", "GER40"]
TIMEFRAMES = ["D1"]
GRID = {"lo": [5, 10], "trend": [100, 200]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
STOP_CAP_ATR = 1e9


def _sma(x, n):
    c = np.cumsum(np.r_[0.0, x]); out = np.full(len(x), np.nan)
    if len(x) >= n:
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def rsi(c, n=2):
    """Wilder RSI, causal."""
    d = np.diff(c, prepend=c[0]); up = np.where(d > 0, d, 0.0); dn = np.where(d < 0, -d, 0.0)
    au = np.zeros(len(c)); ad = np.zeros(len(c))
    for i in range(1, len(c)):
        au[i] = (au[i - 1] * (n - 1) + up[i]) / n if i > n else up[1:i + 1].mean()
        ad[i] = (ad[i - 1] * (n - 1) + dn[i]) / n if i > n else dn[1:i + 1].mean()
    r = np.full(len(c), np.nan); ok = (au + ad) > 0
    r[ok] = 100 * au[ok] / (au[ok] + ad[ok])
    r[:n] = np.nan
    return r


def _exits(B, p):
    c = np.asarray(B["c"], float); m5 = _sma(c, 5)
    return np.flatnonzero(c > m5), np.flatnonzero(c < m5)


EXECUTOR = executors.exit_when(_exits)


def signals(B, p, M):
    c, a = np.asarray(B["c"], float), B["atr"]
    r = rsi(c); t = _sma(c, int(p["trend"])); lo = float(p["lo"])
    rows = []
    for i in np.flatnonzero(np.isfinite(r) & np.isfinite(t) & (a > 0)):
        if r[i] < lo and c[i] > t[i]:
            rows.append((int(i), 1, float(c[i] - 3.0 * a[i])))
        elif r[i] > 100 - lo and c[i] < t[i]:
            rows.append((int(i), -1, float(c[i] + 3.0 * a[i])))
    return rows
