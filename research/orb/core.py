"""ORB 50 — data, sessions, higher-timeframe bias and per-day session tables.

Prices are 1-minute BID bars in UTC (Dukascopy). Sessions are defined in the financial
centre's local time with daylight saving (zoneinfo) and converted to UTC day by day.
"""
import os, sys, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import engine as E                                   # noqa: E402

SYMS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
COST = dict(E.COST)          # all-in round trip (spread + commission + slippage), price units
PIP = dict(E.PIP)
SESSIONS = {                 # name: (time zone, open, close) in local time
    "TOK": ("Asia/Tokyo", (9, 0), (15, 0)),
    "LDN": ("Europe/London", (8, 0), (16, 30)),
    "NY8": ("America/New_York", (8, 0), (16, 0)),
    "NY930": ("America/New_York", (9, 30), (16, 0)),
}
ORB_MIN = (5, 15, 30, 60)
SPLITS = {"dev": (2011, 2019), "val": (2020, 2022), "oos": (2023, 2025)}   # 9 / 3 / 3 years = 60/20/20
ENTRY_WINDOW_H = 3.0         # no new entries (and pending orders expire) at session open + 3h
CONTRACT = {"XAUUSD": 100.0, "EURUSD": 1e5, "GBPUSD": 1e5, "USDJPY": 1e5}


def load_m1_full(sym, y0=2011, y1=2025):
    """Same rules as engine.load_m1 (sorted, duplicate minutes and flat no-tick filler bars
    dropped) plus activity (tick count, or the export's volume) and median spread where the
    year was built from ticks (NaN otherwise). OHLC made self-consistent (2024-10-09/10 feed
    glitch of <= 0.3 pip)."""
    P = []
    for y in range(y0, y1 + 1):
        d = np.load(os.path.join(E.DATA, f"{sym}_M1_bid_{y}.npz"))
        n = len(d["ts"])
        vol = d["n_ticks"].astype(np.float64) if "n_ticks" in d.files else d["v"].astype(np.float64)
        spr = d["spr_med"].astype(np.float64) if "spr_med" in d.files else np.full(n, np.nan)
        P.append((d["ts"] // 1000, d["o"], d["h"], d["l"], d["c"], vol, spr))
    ts = np.concatenate([p[0] for p in P]).astype(np.int64)
    arr = [np.concatenate([p[i] for p in P]).astype(np.float64) for i in range(1, 7)]
    order = np.argsort(ts, kind="stable")
    ts = ts[order]; o, h, l, c, v, s = (a[order] for a in arr)
    keep = np.ones(len(ts), bool); keep[1:] = ts[1:] != ts[:-1]
    flat = (o == h) & (h == l) & (l == c); flat[1:] &= o[1:] == c[:-1]; flat[0] = False
    keep &= ~flat
    ts, o, h, l, c, v, s = (a[keep] for a in (ts, o, h, l, c, v, s))
    h = np.maximum(h, np.maximum(o, c)); l = np.minimum(l, np.minimum(o, c))
    return ts, o, h, l, c, v, s


class Market:
    def __init__(self, sym, tfm=5):
        self.sym, self.tfm = sym, tfm
        self.cost = COST[sym]
        self.ts, self.o, self.h, self.l, self.c, self.v, self.spr = load_m1_full(sym)
        self.gaps = E.data_gaps(self.ts)
        bt, bo, bh, bl, bc, nxt = E.resample(self.ts, self.o, self.h, self.l, self.c, tfm, 0)
        nxt = nxt.astype(np.int64)
        self.B = dict(t=bt.astype(np.int64), o=bo, h=bh, l=bl, c=bc, nxt=nxt,
                      first=np.r_[0, nxt[:-1]].astype(np.int64))
        cs = np.r_[0.0, np.cumsum(self.v)]
        self.B["v"] = cs[nxt] - cs[self.B["first"]]
        self.atr = {p: np.nan_to_num(E.atr_sma(bh, bl, bc, p), nan=0.0) for p in (10, 14, 20)}
        dt_, do, dh, dl, dc, _ = E.resample(self.ts, self.o, self.h, self.l, self.c, 1440, 0)
        self.D = dict(t=dt_, o=do, h=dh, l=dl, c=dc, atr=E.atr_sma(dh, dl, dc, 14))
        # broker-clock H4 (GMT+2 server: bars at 22,02,06,10,14,18 UTC) as an MT5 chart would draw them
        h4t, h4o, h4h, h4l, h4c, _ = E.resample(self.ts, self.o, self.h, self.l, self.c, 240, 120)
        self.H4 = dict(t=h4t, o=h4o, h=h4h, l=h4l, c=h4c, atr=E.atr_sma(h4h, h4l, h4c, 14))
        self._bias, self._days, self._rvol = {}, {}, {}

    # ---------------------------------------------------------------- bias (Model B)
    def bias(self, period=50, kind="body", z=0.25, slope_n=3):
        """Directional bias for every execution bar, taken from the LAST H4 BAR THAT HAD
        CLOSED when the execution bar closed. Nothing from an unfinished H4 bar is used.
        kind: close  sign(close - EMA)
              body   +1 if the whole body is above the EMA, -1 if wholly below, else 0
              neutral sign(close - EMA) only if |close - EMA| > z * ATR14(H4), else 0
              slope  sign(close - EMA) only if it agrees with the EMA slope over slope_n bars"""
        key = (period, kind, z, slope_n)
        if key in self._bias:
            return self._bias[key]
        H = self.H4; em = E.ema(H["c"], period)
        close_t = H["t"] + 240 * 60
        k = np.searchsorted(close_t, self.B["t"] + self.tfm * 60, side="right") - 1
        kk = np.clip(k, 0, len(em) - 1)
        valid = (k >= 0) & np.isfinite(em[kk]) & np.isfinite(H["atr"][kk])
        c, o, e, a = H["c"][kk], H["o"][kk], em[kk], H["atr"][kk]
        if kind == "close":
            b = np.sign(c - e)
        elif kind == "body":
            b = np.where(np.minimum(o, c) > e, 1, np.where(np.maximum(o, c) < e, -1, 0))
        elif kind == "neutral":
            b = np.where(c - e > z * a, 1, np.where(c - e < -z * a, -1, 0))
        elif kind == "slope":
            prev = em[np.clip(kk - slope_n, 0, None)]
            sl = np.sign(e - prev)
            b = np.where(np.sign(c - e) == sl, sl, 0)
        else:
            raise ValueError(kind)
        b = np.where(valid, b, 0).astype(np.int64)
        self._bias[key] = b
        return b

    # ---------------------------------------------------------------- relative volume
    def rvol(self, n=48):
        """Execution-bar activity / mean activity of the previous n bars (past only).
        0 where the instrument-year has no activity field (filter then cannot pass)."""
        if n not in self._rvol:
            v = self.B["v"]; cs = np.r_[0.0, np.cumsum(v)]
            idx = np.arange(len(v))
            prev = (cs[idx] - cs[np.maximum(idx - n, 0)]) / np.maximum(np.minimum(idx, n), 1)
            self._rvol[n] = np.where(prev > 0, v / np.where(prev > 0, prev, 1), 0.0)
        return self._rvol[n]

    # ---------------------------------------------------------------- day table
    def days(self, session, orb_min):
        key = (session, orb_min)
        if key in self._days:
            return self._days[key]
        tzname, (oh, om), (eh, em_) = SESSIONS[session]
        tz = ZoneInfo(tzname)
        ts, bt = self.ts, self.B["t"]
        rows = []
        d, d1 = dt.date(2011, 1, 3), dt.date(2025, 12, 31)
        while d <= d1:
            if d.weekday() < 5:
                t_open = int(dt.datetime(d.year, d.month, d.day, oh, om, tzinfo=tz).timestamp())
                t_end = int(dt.datetime(d.year, d.month, d.day, eh, em_, tzinfo=tz).timestamp())
                t_or = t_open + orb_min * 60
                a = np.searchsorted(ts, t_open); b = np.searchsorted(ts, t_or)
                iend = np.searchsorted(ts, t_end)
                ok = (b - a >= max(1, int(0.8 * orb_min)) and iend < len(ts)
                      and ts[iend] - t_end <= 3600 and ts[iend - 1] >= t_or)
                if ok:
                    orh, orl = self.h[a:b].max(), self.l[a:b].min()
                    kd = np.searchsorted(self.D["t"] + 86400, t_open, side="right") - 1   # last closed UTC day
                    atrD = self.D["atr"][kd] if kd >= 0 else np.nan
                    b0 = np.searchsorted(bt, t_or)
                    bcut = np.searchsorted(bt, t_open + int(ENTRY_WINDOW_H * 3600))
                    gap = np.searchsorted(self.gaps, a)
                    crosses = gap < len(self.gaps) and self.gaps[gap] < iend
                    if np.isfinite(atrD) and orh > orl and bcut > b0 and not crosses:
                        rows.append((t_open, orh, orl, b0, bcut, iend, atrD, d.year, a))
            d += dt.timedelta(days=1)
        A = np.array(rows, dtype=np.float64)
        D = dict(t_open=A[:, 0].astype(np.int64), orh=A[:, 1], orl=A[:, 2], b0=A[:, 3].astype(np.int64),
                 bcut=A[:, 4].astype(np.int64), iend=A[:, 5].astype(np.int64), atrD=A[:, 6],
                 year=A[:, 7].astype(np.int64), i_open=A[:, 8].astype(np.int64))
        D["w_atr"] = (D["orh"] - D["orl"]) / D["atrD"]            # OR width in daily-ATR units
        self._days[key] = D
        return D


def year_mask(years, split):
    y0, y1 = SPLITS[split] if isinstance(split, str) else split
    return (years >= y0) & (years <= y1)
