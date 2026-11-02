"""HistData clock check and fix (found 2026-11-02 while replaying the owner's EURGBP chart of 23 Oct 2026).

HistData's free M1 files are documented as "EST without daylight saving" (tools/histdata_m1.py converts with UTC = stamp + 5h).
Measured against independent, correctly timed data, the stamps are in fact ONE HOUR LATE during daylight-saving periods:
week by week, the best alignment of HistData minute returns with the reference is -60 minutes in summer and 0 in winter.

    python3 tools/histdata_clock.py --check          # weekly offsets for every HistData file, no changes
    python3 tools/histdata_clock.py --fix            # rewrite the HistData portions with corrected UTC stamps

Finding (2011-2026, all eight HistData markets agree week by week, 98-100%): the stamps are New York local time with US
daylight saving for 2011-2018, and follow UK daylight saving from 2019 on (the change happened in the winter of 2018/19,
when both rules give the same stamps). Fix: UTC = stored stamp - 1 hour whenever that rule's daylight saving is on.

Method (per Monday-Friday trading week): correlate the market's 1-minute returns (EURGBP vs EURUSD/GBPUSD, XAGUSD vs
XAUUSD) or absolute returns (indices, oil vs EURUSD: news bursts hit every market at the same UTC minute) with the
reference at shifts of -60, 0 and +60 minutes; the best shift is the week's offset. The reference markets (XAUUSD, EURUSD,
GBPUSD, USDJPY) are from a different source with correct UTC stamps. Only the HistData part of each file is changed
(GER40 to 2020-01-29 and WTI to 2023-12-01; after that those files are Exness data with correct stamps).
Output: research/results/data/histdata_clock.json (weekly offsets, correlations, what was changed).
"""
import os, sys, json, datetime as dt
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "research", "results", "data")
HISTDATA = {"EURGBP": None, "XAGUSD": None, "US500": None, "NAS100": None, "UK100": None, "JP225": None,
            "GER40": "2020-01-29", "WTI": "2023-12-01"}                 # value = last HistData day (None = all years)
METHOD = {"EURGBP": "returns", "XAGUSD": "returns"}                      # others: absolute returns
SHIFTS = (-60, 0, 60)


def load(sym, y, holdout=False):
    f = os.path.join(DATA, "holdout" if holdout else "", f"{sym}_M1_bid_{y}.npz")
    if not os.path.exists(f):
        return None
    d = np.load(f)
    return {k: d[k] for k in d.files}


def on_grid(ts, c, grid):
    i = np.searchsorted(ts, grid, side="right") - 1
    ok = (i >= 0) & (np.abs(ts[np.clip(i, 0, None)] - grid) < 120)
    return np.where(ok, c[np.clip(i, 0, None)], np.nan)


def reference(sym, y, holdout=False):
    if sym == "EURGBP":
        a, b = load("EURUSD", y, holdout), load("GBPUSD", y, holdout)
        ta, tb = a["ts"] // 1000, b["ts"] // 1000
        grid = np.intersect1d(ta, tb)
        return grid, on_grid(ta, a["c"], grid) / on_grid(tb, b["c"], grid)
    r = load("XAUUSD" if sym == "XAGUSD" else "EURUSD", y, holdout)
    return r["ts"] // 1000, r["c"].astype(float)


def weekly_offsets(sym, y, holdout=False):
    d = load(sym, y, holdout)
    if d is None:
        return []
    ts, c = d["ts"] // 1000, d["c"].astype(float)
    rts, rc = reference(sym, y, holdout)
    absolute = METHOD.get(sym) != "returns"
    out = []
    first = dt.date(y, 1, 1); monday = first - dt.timedelta(days=first.weekday())
    while monday.year <= y:
        t0 = int(dt.datetime(monday.year, monday.month, monday.day, tzinfo=dt.timezone.utc).timestamp())
        t1 = t0 + 5 * 86400
        grid = np.arange(t0, t1, 60)
        ref = np.diff(np.log(on_grid(rts, rc, grid)))
        if absolute:
            ref = np.abs(ref)
        cs = {}
        for s in SHIFTS:
            x = np.diff(np.log(on_grid(ts + s * 60, c, grid)))
            if absolute:
                x = np.abs(x)
            m = np.isfinite(ref) & np.isfinite(x) & (ref != 0) & (x != 0)
            cs[s] = float(np.corrcoef(ref[m], x[m])[0, 1]) if m.sum() > 500 else None
        ok = {k: v for k, v in cs.items() if v is not None}
        if ok:
            best = max(ok, key=ok.get)
            srt = sorted(ok.values(), reverse=True)
            out.append(dict(week=str(monday), best=best, corr={str(k): (round(v, 3) if v is not None else None) for k, v in cs.items()},
                            margin=round(srt[0] - srt[1], 3) if len(srt) > 1 else None))
        monday += dt.timedelta(days=7)
    return out


def check(syms, years):
    res = {}
    for s in syms:
        rows = []
        for y in years:
            rows += weekly_offsets(s, y)
        if s == "EURGBP":
            rows += [dict(r, holdout=True) for r in weekly_offsets(s, 2026, holdout=True)]
        res[s] = rows
        n60 = sum(r["best"] == -60 for r in rows); n0 = sum(r["best"] == 0 for r in rows); np60 = sum(r["best"] == 60 for r in rows)
        print(f"{s}: weeks {len(rows)}  shift -60: {n60}  0: {n0}  +60: {np60}", flush=True)
    return res


def week_map(rows):
    return {r["week"]: r["best"] for r in rows}


SWITCH = int(dt.datetime(2019, 1, 1, tzinfo=dt.timezone.utc).timestamp())


def dst_flags(sec):
    """1 where the HistData rule's daylight saving is on: New York rules before 2019, London rules from 2019."""
    from zoneinfo import ZoneInfo
    ny, ldn = ZoneInfo("America/New_York"), ZoneInfo("Europe/London")
    hours = np.unique(sec // 3600)
    flag = {}
    for hh in hours:
        t = dt.datetime.fromtimestamp(int(hh) * 3600, dt.timezone.utc)
        z = ny if hh * 3600 < SWITCH else ldn
        flag[int(hh)] = 1 if t.astimezone(z).dst() else 0
    return np.array([flag[int(x)] for x in sec // 3600], np.int64)


def apply_fix():
    """Shift the HistData part of each file by -1 hour where the HistData daylight-saving rule is on."""
    log = {}
    for sym, last in HISTDATA.items():
        changed = 0
        files = [(y, False) for y in range(2011, 2026)] + ([(2026, True)] if sym == "EURGBP" else [])
        for y, hold in files:
            d = load(sym, y, hold)
            if d is None:
                continue
            ts = d["ts"].astype(np.int64)
            sec = ts // 1000
            shift = -3600 * 1000 * dst_flags(sec)
            if last is not None:
                shift[sec >= int(dt.datetime.fromisoformat(last).replace(tzinfo=dt.timezone.utc).timestamp()) + 86400] = 0
            if np.any(shift != 0):
                new = ts + shift
                o = np.argsort(new, kind="stable")
                keep = np.r_[True, np.diff(new[o]) > 0]
                arrs = {k: d[k][o][keep] for k in d if k != "ts"}
                f = os.path.join(DATA, "holdout" if hold else "", f"{sym}_M1_bid_{y}.npz")
                np.savez_compressed(f, ts=new[o][keep], **arrs)
                changed += int(np.sum(shift != 0))
        log[sym] = dict(minutes_shifted=changed, histdata_until=last or "all years")
        print(f"{sym}: shifted {changed} minutes back one hour", flush=True)
    return log


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    years = list(range(2011, 2026))
    res = check(list(HISTDATA), years)
    out = dict(note=__doc__, weekly=res)
    if "--fix" in sys.argv:
        out["fix"] = apply_fix()
        out["after"] = check(list(HISTDATA), years)
    json.dump(out, open(os.path.join(OUT, "histdata_clock.json" if "--fix" in sys.argv else "histdata_clock_check.json"), "w"), indent=1)
