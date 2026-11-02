"""Batch 01, candidate 9: month-end rebalancing by pension and balanced funds, conditional on the month's move.
Rules fixed 2026-11-02 BEFORE any result.

Payer: funds that hold a fixed equity weight (60/40, target-date, pension schedules) rebalance at month-end: after equities
rose during the month they sell equities, after they fell they buy. Direction is known before the window: against the
month-to-date move. (The unconditional turn of the month was rejected earlier, tom_indices_v2; this one is conditional.)
Coded per market at its cash close (local time, DST-aware): US500 and NAS100 16:00 New York (NYSE calendar), GER40 17:30
Frankfurt (Xetra calendar), UK100 16:30 London (LSE calendar); weekdays that are not exchange holidays (US early closes
skipped: day after Thanksgiving, 24 Dec, 3 Jul).
  MTD     close on the entry day / close on the previous month's last business day - 1.
  entry   market order at the close, N business days before the month's last business day (N = 3 or 1), AGAINST the
          month-to-date move (sell after a rise, buy after a fall). No trade if MTD = 0 or a bar is missing.
  filter  all: every month; strong: only if |MTD| >= the median |monthly return| of the previous 24 months (prior months only).
  exit    at the close of the month's last business day; stop 1.5 x the average daily range of the previous 20 weekdays.
  CONTROL the same rule around the 10th business day of the month (entry N days before it, exit at its close), in
          research/batch01/controls.py; never selected.
Grid: N [3, 1] x filter [all, strong] = 4 configurations; US500, NAS100, GER40, UK100 (the four cash indices with data).
Costs: RoboForex Prime published for US500 / NAS100 / GER40 (0.5 / 0.97 / 0.99 points); UK100 is not on Prime: lab standard
  1.5 points (estimate). Overnight swaps: the lab's index swaps (estimates); the lab also reports a swap-free profile.
Priors (told to the owner): index calendar ideas all rejected so far (turn of month, option expiry, payday, oil->equity).
  This one differs: the direction comes from the month's move, i.e. from the payer's obligation (P22).
"""
import os, sys, json, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np

NAME = "monthend_rebalance_v1"
HYPOTHESIS = ("Fixed-weight funds rebalance against the month's equity move in the last days of the month, so index CFDs "
              "reverse the month-to-date move into month-end by more than costs and swaps.")
RULES = __doc__
FAMILY = ["calendar", "flow", "payer", "index", "month-end", "rebalancing", "reversal", "batch01"]
MARKETS = ["US500", "NAS100", "GER40", "UK100"]
TIMEFRAMES = ["M30"]
GRID = {"n_before": [3, 1], "filter": ["all", "strong"]}
MANAGEMENT = {"tgt": [0.0], "trail": [0.0], "bias": [0]}
TIME_STOP = 500
STOP_CAP_ATR = 1e9
ATR_DAYS, STOP_MULT, MED_MONTHS, CONTROL_BD = 20, 1.5, 24, 10
_here = os.path.dirname(os.path.abspath(__file__))
_rf = json.load(open(os.path.join(_here, "..", "costs_roboforex_prime.json")))["realistic"]
COSTS = {m: _rf[m] for m in MARKETS if m in _rf}
sys.path.insert(0, os.path.join(_here, ".."))
import executors

VENUE = {"US500": ("America/New_York", (16, 0), "NYSE"), "NAS100": ("America/New_York", (16, 0), "NYSE"),
         "GER40": ("Europe/Berlin", (17, 30), "XETR"), "UK100": ("Europe/London", (16, 30), "XLON")}
_CAL = {}


def business_days(cal, y0=2010, y1=2027):
    if cal not in _CAL:
        import holidays
        hol = holidays.financial_holidays(cal, years=range(y0, y1 + 1))
        early = set()
        if cal == "NYSE":
            for y in range(y0, y1 + 1):
                th = [d for d, n in holidays.financial_holidays("NYSE", years=y).items() if "Thanksgiving" in n]
                early |= {t + dt.timedelta(days=1) for t in th} | {dt.date(y, 12, 24), dt.date(y, 7, 3)}
        out, d = [], dt.date(y0, 1, 1)
        while d <= dt.date(y1, 12, 31):
            if d.weekday() < 5 and d not in hol and d not in early:
                out.append(d)
            d += dt.timedelta(days=1)
        _CAL[cal] = out
    return _CAL[cal]


def _close_utc(sym, D):
    tz, (h, m), _ = VENUE[sym]
    return int(dt.datetime(D.year, D.month, D.day, h, m, tzinfo=ZoneInfo(tz)).timestamp())


def _months(sym):
    """{(year, month): [business days]} for the market's exchange."""
    out = {}
    for D in business_days(VENUE[sym][2]):
        out.setdefault((D.year, D.month), []).append(D)
    return out


def _anchor_day(days, sample):
    return days[-1] if sample == "flow" else (days[CONTROL_BD - 1] if len(days) >= CONTROL_BD else None)


def _day_ranges(sym, t, h, l):
    tz = ZoneInfo(VENUE[sym][0])
    ud, inv = np.unique(t // 86400, return_inverse=True)
    off = np.array([int(dt.datetime.fromtimestamp(int(d) * 86400 + 43200, tz=tz).utcoffset().total_seconds()) for d in ud])[inv]
    days = (t + off) // 86400
    u, inv2 = np.unique(days, return_inverse=True)
    hi = np.full(len(u), -np.inf); lo = np.full(len(u), np.inf)
    np.maximum.at(hi, inv2, h); np.minimum.at(lo, inv2, l)
    wk = ((u + 3) % 7) < 5
    u, rng = u[wk], (hi - lo)[wk]
    return {int(u[i]) + 719163: float(rng[i - ATR_DAYS:i].mean()) for i in range(ATR_DAYS, len(u))}


def signals(B, p, M):
    sym = M.sym
    t = np.asarray(B["t"], np.int64); c = np.asarray(B["c"], float)
    h = np.asarray(B["h"], float); l = np.asarray(B["l"], float)
    if len(t) == 0:
        return []
    idx = {int(x): i for i, x in enumerate(t)}
    atr = _day_ranges(sym, t, h, l)
    sample = p.get("sample", "flow")
    close = lambda D: idx.get(_close_utc(sym, D) - 1800)            # the M30 bar that closes at the cash close
    first = dt.datetime.utcfromtimestamp(int(t[0])).date(); last = dt.datetime.utcfromtimestamp(int(t[-1])).date()
    months = sorted(_months(sym).items())
    rows, mret = [], []                                               # mret: |monthly returns| known so far
    for k in range(1, len(months)):
        (_, prev_days), (_, days) = months[k - 1], months[k]
        if days[-1] < first or days[0] > last:
            continue
        b_prev = close(prev_days[-1])
        anchor = _anchor_day(days, sample)
        if anchor is None:
            continue
        j = days.index(anchor) - p["n_before"]
        if j < 0:
            continue
        b_in = close(days[j])
        prior = list(mret)                                            # months closed before this one
        b_end = close(days[-1])
        if b_prev is None or b_in is None:
            _record(mret, c, b_prev, b_end); continue
        mtd = c[b_in] / c[b_prev] - 1.0
        a = atr.get(days[j].toordinal())
        ok = mtd != 0 and a is not None
        if ok and p["filter"] == "strong":
            ok = len(prior) >= MED_MONTHS and abs(mtd) >= float(np.median(prior[-MED_MONTHS:]))
        if ok:
            side = -1 if mtd > 0 else 1
            rows.append((int(b_in), side, float(c[b_in] - side * STOP_MULT * a)))
        _record(mret, c, b_prev, b_end)
    return rows


def _record(mret, c, b_prev, b_end):
    if b_prev is not None and b_end is not None:
        mret.append(abs(c[b_end] / c[b_prev] - 1.0))


def _make_exit():
    def exit_bars(B, p, sym):
        t = np.asarray(B["t"], np.int64)
        sample = p.get("sample", "flow")
        want = []
        for _, days in _months(sym).items():
            a = _anchor_day(days, sample)
            if a is not None:
                want.append(_close_utc(sym, a) - 1800)
        xb = np.flatnonzero(np.isin(t, np.array(want, np.int64)))
        return xb, xb
    return exit_bars


_EXIT = _make_exit()


def EXECUTOR(M, B, C, p, **kw):
    return executors.exit_when(lambda B_, p_: _EXIT(B_, p_, M.sym))(M, B, C, p, **kw)
