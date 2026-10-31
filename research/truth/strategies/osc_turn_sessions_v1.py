"""Owner's request after the Dark Mimas review (2026-10-31): give the oscillator bot active hours, risk at most 1% per
trade, test several timeframes, and keep only what is timeless.

Rules: on each closed bar, a smooth oscillator of the median price (period 15, LWMA) changes colour -> an arrow.
  follow: buy a green arrow / sell a red arrow (Dark Mimas strategy 1); fade: the reverse (Dark Mimas strategy 2).
  Enter at the next bar's open only if the arrow's bar closed inside the session window (UTC):
    all; asia 23-07; london 07-12; overlap 12-16; ny 16-20; london_ny 07-16. (Rollover 20:30-23:00 is always blocked.)
  Protective stop 2 x ATR14 from the signal close (this is 1R, so a 1%-risk position is sized from it).
  Exit at the next arrow (next bar's open), whatever the session, or at the stop. One position at a time.
Oscillators: R1 slope of LWMA(median, 15); R2 LWMA of a CCI-like score (15); R3 TSI-like double-smoothed momentum
  (the same reconstructions as research/gridbot/dark_mimas_sim.py; the real Dark Oscillator formula is secret).
Costs: Exness Zero realistic (measured Zero spreads + high-end published commission + slippage,
  research/truth/costs_exness_zero.json) and the lab's swaps.
HINDSIGHT NOTE: this session already saw how this family behaves on 2011-2025 (dark_mimas_sim.py, dark_mimas_time.py),
  including that the fade direction is less bad before costs. The 2023-25 look is therefore not clean; any survivor needs
  a fresh forward test before it can be trusted.
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import executors

NAME = "osc_turn_sessions_v1"
HYPOTHESIS = ("Turns of a smooth oscillator start intraday swings; trading them only in the session when that market "
              "moves (follow) or ranges (fade) keeps the trades whose follow-through pays for costs.")
RULES = __doc__
FAMILY = ["oscillator", "intraday", "session", "time-filter", "third-party-ea"]
MARKETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
TIMEFRAMES = ["M15", "H1", "H4"]
GRID = {"osc": ["R1", "R2", "R3"],
        "window": ["all", "asia", "london", "overlap", "ny", "london_ny"],
        "mode": ["follow", "fade"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}       # exits are the next arrow or the stop (executor)
_cz = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "costs_exness_zero.json")))["realistic"]
COSTS = {s: _cz[s] for s in MARKETS}
STOP_CAP_ATR = 1e9
N = 15
WINDOWS = {"all": lambda hh: np.ones(len(hh), bool), "asia": lambda hh: (hh >= 23) | (hh < 7),
           "london": lambda hh: (hh >= 7) & (hh < 12), "overlap": lambda hh: (hh >= 12) & (hh < 16),
           "ny": lambda hh: (hh >= 16) & (hh < 20), "london_ny": lambda hh: (hh >= 7) & (hh < 16)}


def _lwma(x, n):
    w = np.arange(1, n + 1, dtype=float); out = np.full(len(x), np.nan)
    if len(x) >= n:
        out[n - 1:] = np.convolve(x, w[::-1], mode="valid") / w.sum()
    return out


def _sma(x, n):
    c = np.cumsum(np.r_[0.0, x]); out = np.full(len(x), np.nan)
    if len(x) >= n:
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def oscillator(kind, h, l, n=N):
    p = (np.asarray(h, float) + np.asarray(l, float)) / 2
    if kind == "R1":
        return _lwma(p, n)
    if kind == "R2":
        m = _sma(p, n); md = np.full(len(p), np.nan)
        if len(p) >= n:
            win = np.lib.stride_tricks.sliding_window_view(p, n)
            md[n - 1:] = np.mean(np.abs(win - m[n - 1:, None]), axis=1)
        cci = np.nan_to_num((p - m) / (0.015 * np.where(md > 0, md, np.nan)))
        return _lwma(cci, n)
    dp = np.r_[0.0, np.diff(p)]
    num = _lwma(np.nan_to_num(_lwma(dp, n)), n); den = _lwma(np.nan_to_num(_lwma(np.abs(dp), n)), n)
    return 100 * num / np.where(den > 0, den, np.nan)


def arrows(line):
    """+1 green arrow (turned up), -1 red arrow (turned down); causal (flat steps keep the last colour)."""
    x = np.nan_to_num(np.asarray(line, float)); dl = np.diff(x, prepend=x[:1])
    tol = 1e-9 * np.maximum(1.0, np.abs(x))
    d = np.where(np.abs(dl) > tol, np.sign(dl), 0.0); d[~np.isfinite(line)] = 0.0
    idx = np.where(d != 0, np.arange(len(d)), -1); idx = np.maximum.accumulate(idx)
    col = np.where(idx >= 0, d[np.maximum(idx, 0)], 0.0)
    prev = np.r_[0.0, col[:-1]]
    a = np.zeros(len(d), np.int64); a[(col > 0) & (prev < 0)] = 1; a[(col < 0) & (prev > 0)] = -1
    return a


def _arrow_bars(B, p):
    return np.flatnonzero(arrows(oscillator(p["osc"], B["h"], B["l"])) != 0)


EXECUTOR = executors.next_arrow(_arrow_bars)


def signals(B, p, M):
    a = arrows(oscillator(p["osc"], B["h"], B["l"]))
    hh = ((np.asarray(B["t"]) + B["minutes"] * 60) % 86400) // 3600
    ok = WINDOWS[p["window"]](hh)
    rows = []
    sgn = 1 if p["mode"] == "follow" else -1
    for i in np.flatnonzero((a != 0) & ok):
        atr = B["atr"][i]
        if not np.isfinite(atr) or atr <= 0:
            continue
        side = int(sgn * a[i])
        rows.append((int(i), side, float(B["c"][i] - side * 2.0 * atr)))
    return rows
