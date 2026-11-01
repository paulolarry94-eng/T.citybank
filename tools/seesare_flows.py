"""SEESARE router, Phase 2: Python twin of the flow modules' calendars and clocks, of the volume rounding, and generator of
the MQL5 Phase 2 self-test vectors and of the Japanese holiday table in Calendar.mqh.

    python3 tools/seesare_flows.py --vectors     print the reference vectors
    python3 tools/seesare_flows.py --mql         print the generated block of SeesarePhase2SelfTest.mq5
    python3 tools/seesare_flows.py --holidays    print the generated holiday table of Calendar.mqh

Evidence behind each module (see mt5/Seesare/README.md):
  TOKYO_FIX   research/results/truth/tokyo_fix_gotobi_v1 (Tier B forward-test candidate; 2023-25 +0.052R, 214 trades)
  LDN_FIX     research/results/truth/wmr_fix_reversion_v1 (rejected: 0 of 4 configurations; -0.017 to -0.12R)
  US_CLOSE    untested: the NYSE/Nasdaq closing-imbalance figures are not in MT5 or in research/data
"""
import sys
import os
import math
import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seesare_verify as S  # noqa: E402

HOLIDAY_FIRST, HOLIDAY_LAST = 2024, 2035
DAY = 86400


# ------------------------------------------------------------------------------------------------ calendar (Calendar.mqh)
def jp_holidays(y0=HOLIDAY_FIRST, y1=HOLIDAY_LAST):
    import holidays
    return sorted(holidays.Japan(years=range(y0, y1 + 1)))


_JP = None


def _jp():
    global _JP
    if _JP is None:
        _JP = set(jp_holidays())
    return _JP


def covered(d):
    return HOLIDAY_FIRST <= d.year <= HOLIDAY_LAST


def tokyo_business(d):
    """Weekday, not a Japanese holiday, not the bank year-end (31 Dec - 3 Jan): the research rule."""
    return d.weekday() < 5 and d not in _jp() and not (d.month == 12 and d.day == 31) and not (d.month == 1 and d.day <= 3)


def previous_business(d):
    while not tokyo_business(d):
        d -= dt.timedelta(days=1)
    return d


def last_day(y, m):
    nxt = dt.date(y + (m == 12), 1 if m == 12 else m + 1, 1)
    return (nxt - dt.timedelta(days=1)).day


def is_gotobi_fix(d):
    """CSeesareCalendar::IsGotobiFix: d (a Tokyo date) is the fix date of the 5th, 10th, 15th, 20th, 25th or the last day of
    its month, or of the next month's 5th moved back (a candidate on a non-business day moves to the previous business
    day). Returns (is_gotobi, known); known is False outside the holiday table."""
    nm = (d.year + (d.month == 12), 1 if d.month == 12 else d.month + 1)
    if not (covered(d) and HOLIDAY_FIRST <= nm[0] <= HOLIDAY_LAST):
        return False, False
    for y, m in ((d.year, d.month), nm):
        for day in (5, 10, 15, 20, 25, last_day(y, m)):
            if previous_business(dt.date(y, m, day)) == d:
                return True, True
    return False, True


def last_weekday_of_month(d):
    """A weekday whose next weekday falls in another month (weekend days are never it)."""
    if d.weekday() >= 5:
        return False
    nxt = d + dt.timedelta(days=1)
    while nxt.weekday() >= 5:
        nxt += dt.timedelta(days=1)
    return nxt.month != d.month


# ------------------------------------------------------------------------------------------------ module clocks (Flows/*.mqh)
MODULES = ["TOKYO_FIX", "LDN_FIX", "US_CLOSE"]


def _d(t):
    return dt.datetime.utcfromtimestamp(t).date()


def slot(module, utc_day):
    """(entry_utc, exit_utc) of the module's slot that opens on this UTC day, or None. utc_day: any time on that day."""
    d0 = S.midnight(utc_day)
    D = _d(d0)
    if module == "TOKYO_FIX":                         # buy 23:00 UTC = 08:00 JST of the fix date, sell at the 00:55 UTC fix
        fix = D + dt.timedelta(days=1)
        ok, known = is_gotobi_fix(fix)
        if not (ok and known):
            return None
        return d0 + 23 * 3600, d0 + DAY + 55 * 60
    if D.weekday() >= 5:
        return None
    if module == "LDN_FIX":                           # owner's spec: fade 15:30-15:55 London, enter 15:55, out 16:05
        return S.venue_to_utc(S.LONDON, d0 + 15 * 3600 + 55 * 60), S.venue_to_utc(S.LONDON, d0 + 16 * 3600 + 5 * 60)
    if module == "US_CLOSE":                          # owner's spec: imbalance published 15:50 New York, out 16:00
        return S.venue_to_utc(S.NEW_YORK, d0 + 15 * 3600 + 50 * 60), S.venue_to_utc(S.NEW_YORK, d0 + 16 * 3600)
    raise ValueError(module)


# ------------------------------------------------------------------------------------------------ sizing (Risk/Exposure.mqh)
def size(plan_usd, per_lot_usd, step, vmin, vmax):
    """CSeesareExposure::Volume: lots = floor((plan / loss per lot) / step) x step, never rounded up; feasible if >= the
    broker minimum. Returns (feasible, volume, virtual volume)."""
    if plan_usd <= 0 or per_lot_usd <= 0 or step <= 0:
        return False, 0.0, 0.0
    virtual = plan_usd / per_lot_usd
    vol = math.floor(virtual / step + 1e-9) * step
    vol = min(vol, vmax)
    return vol >= vmin - 1e-12, vol, virtual


# ------------------------------------------------------------------------------------------------ vectors
SLOT_DAYS = [(2026, 11, 4), (2026, 11, 8), (2026, 11, 9), (2026, 11, 13), (2026, 11, 29), (2026, 12, 29), (2026, 12, 30),
             (2027, 3, 10), (2027, 3, 30), (2027, 4, 29), (2027, 10, 27), (2027, 11, 3)]
# (plan USD, loss per 1.0 lot at the stop incl. commission USD, step, min, max). USDJPY at the research stop (0.3% of price)
# loses $300 per lot + $7 commission; EURUSD 10 and 5 pips lose $100 and $50 per lot + $7.
SIZE_CASES = [(0.1206, 307.0, 0.01, 0.01, 100.0), (1.368, 307.0, 0.01, 0.01, 100.0), (2.052, 307.0, 0.01, 0.01, 100.0),
              (1.368, 107.0, 0.01, 0.01, 100.0), (1.368, 57.0, 0.01, 0.01, 100.0), (0.03, 1.0, 0.01, 0.01, 100.0),
              (0.0, 107.0, 0.01, 0.01, 100.0), (5000.0, 1.0, 0.01, 0.01, 100.0)]
BUSINESS_CASES = [(2026, 1, 2), (2026, 1, 5), (2026, 9, 22), (2026, 5, 6), (2026, 12, 31), (2026, 11, 23), (2026, 11, 24)]
LASTWD_CASES = [(2026, 10, 30), (2026, 10, 29), (2026, 1, 30), (2026, 5, 29), (2026, 5, 31), (2027, 7, 30)]


def gotobi_list(y):
    out = []
    d = dt.date(y, 1, 1)
    while d.year == y:
        ok, _ = is_gotobi_fix(d)
        if ok:
            out.append(d.strftime("%m%d"))
        d += dt.timedelta(days=1)
    return ",".join(out)


def vectors():
    out = {}
    for y in (2026, 2027):
        out[f"gotobi {y}"] = gotobi_list(y)
    for a in BUSINESS_CASES:
        out[f"tokyo business {dt.date(*a)}"] = tokyo_business(dt.date(*a))
    for a in LASTWD_CASES:
        out[f"last weekday {dt.date(*a)}"] = last_weekday_of_month(dt.date(*a))
    for m in MODULES:
        for a in SLOT_DAYS:
            r = slot(m, S.date(*a))
            out[f"slot {m} {dt.date(*a)}"] = f"{S.iso(r[0])}/{S.iso(r[1])}" if r else "none"
    for c in SIZE_CASES:
        f, v, w = size(*c)
        out[f"size {c}"] = f"{'feasible' if f else 'shadow'} {v:.2f}"
    return out


def _q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def mql_block():
    v = vectors()
    o = ["//--- BEGIN GENERATED VECTORS: python3 tools/seesare_flows.py --mql  (do not edit by hand)",
         "void GeneratedVectors(void)", "  {"]
    t = o.append
    for y in (2026, 2027):
        t(f"   T_Str(\"gotobi fix dates {y}\", GotobiList({y}), {_q(v[f'gotobi {y}'])});")
    for a in BUSINESS_CASES:
        k = f"tokyo business {dt.date(*a)}"
        t(f"   T_Bool({_q(k)}, CSeesareCalendar::IsTokyoBusinessDay(CSeesareDst::Date({a[0]}, {a[1]}, {a[2]})) == "
          f"{'true' if v[k] else 'false'}, \"\");")
    for a in LASTWD_CASES:
        k = f"last weekday {dt.date(*a)}"
        t(f"   T_Bool({_q(k)}, CSeesareCalendar::IsLastWeekdayOfMonth(CSeesareDst::Date({a[0]}, {a[1]}, {a[2]})) == "
          f"{'true' if v[k] else 'false'}, \"\");")
    for i, m in enumerate(MODULES):
        for a in SLOT_DAYS:
            k = f"slot {m} {dt.date(*a)}"
            t(f"   T_Str({_q(k)}, SlotText({i}, CSeesareDst::Date({a[0]}, {a[1]}, {a[2]})), {_q(v[k])});")
    for c in SIZE_CASES:
        k = f"size {c}"
        t(f"   T_Str({_q('volume plan ' + str(c[0]) + ' per lot ' + str(c[1]))}, SizeText({c[0]!r}, {c[1]!r}, {c[2]!r}, "
          f"{c[3]!r}, {c[4]!r}), {_q(v[k])});")
    o += ["  }", "//--- END GENERATED VECTORS"]
    return "\n".join(o)


def holiday_block():
    days = [d.strftime("%Y%m%d") for d in jp_holidays()]
    lines = ["//--- BEGIN GENERATED HOLIDAYS: python3 tools/seesare_flows.py --holidays  (Japanese public holidays, "
             f"holidays.Japan, {HOLIDAY_FIRST}-{HOLIDAY_LAST})",
             f"#define SEESARE_JP_FIRST_YEAR {HOLIDAY_FIRST}", f"#define SEESARE_JP_LAST_YEAR  {HOLIDAY_LAST}",
             f"#define SEESARE_JP_COUNT      {len(days)}",
             "const int SEESARE_JP_HOLIDAYS[SEESARE_JP_COUNT] ="]
    rows = [", ".join(days[i:i + 10]) for i in range(0, len(days), 10)]
    lines.append("  {")
    for i, r in enumerate(rows):
        lines.append("   " + r + ("," if i < len(rows) - 1 else ""))
    lines += ["  };", "//--- END GENERATED HOLIDAYS"]
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mql":
        print(mql_block())
    elif len(sys.argv) > 1 and sys.argv[1] == "--holidays":
        print(holiday_block())
    else:
        for k, val in vectors().items():
            print(f"{k} = {val}")
