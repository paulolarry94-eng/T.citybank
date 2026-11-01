"""SEESARE router Phase 2: tests of the flow-module twin (tools/seesare_flows.py) and of its agreement with the MQL5 source.

    python3 -m unittest research/truth/tests/test_seesare_phase2.py -v

MQL5 cannot be compiled here. These tests check (1) the gotobi calendar against the research rule, (2) the modules' clocks
against the IANA time-zone database, (3) the sizing rule, (4) that the MQL5 source carries the same holiday table, clocks and
constants as the twin and the lab files, and (5) that the Phase 2 self-test's vectors are the twin's.
"""
import os
import re
import sys
import random
import unittest
import datetime as dt
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "research", "truth"), os.path.join(ROOT, "research", "northstar"),
           os.path.join(ROOT, "research", "truth", "strategies")):
    sys.path.insert(0, _p)
import seesare_flows as F  # noqa: E402
import seesare_verify as S  # noqa: E402
import tokyo_fix_gotobi_v1 as TOKYO  # noqa: E402
import wmr_fix_reversion_v1 as WMR  # noqa: E402

MQL = os.path.join(ROOT, "mt5", "Seesare")
INC = os.path.join(MQL, "Include", "Seesare")


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


def days(y0, y1):
    d = dt.date(y0, 1, 1)
    while d <= dt.date(y1, 12, 31):
        yield d
        d += dt.timedelta(days=1)


class Calendar(unittest.TestCase):
    def test_gotobi_rule_equals_the_research_rule(self):
        ref = {x for x in TOKYO.gotobi_days(2023, 2036) if dt.date(2024, 1, 1) <= x <= dt.date(2035, 11, 30)}
        mine = {d for d in days(2024, 2035) if d <= dt.date(2035, 11, 30) and F.is_gotobi_fix(d)[0]}
        self.assertEqual(mine, ref)
        self.assertGreater(len(mine), 800)

    def test_unknown_outside_the_table(self):
        self.assertEqual(F.is_gotobi_fix(dt.date(2036, 1, 5)), (False, False))
        self.assertEqual(F.is_gotobi_fix(dt.date(2035, 12, 10))[1], False)       # next month (2036) is not covered

    def test_tokyo_slots_follow_the_research_entry_day(self):
        ref = TOKYO.gotobi_days(2023, 2036)
        for d in days(2024, 2035):
            if d >= dt.date(2035, 11, 29):
                break
            r = F.slot("TOKYO_FIX", S.date(d.year, d.month, d.day))
            self.assertEqual(r is not None, (d + dt.timedelta(days=1)) in ref, d)
            if r:
                self.assertEqual((S.iso(r[0])[11:16], S.iso(r[1])[11:16]), ("23:00", "00:55"))

    def test_last_weekday_of_month(self):
        self.assertTrue(F.last_weekday_of_month(dt.date(2026, 10, 30)))
        self.assertFalse(F.last_weekday_of_month(dt.date(2026, 10, 29)))
        self.assertFalse(F.last_weekday_of_month(dt.date(2026, 5, 31)))           # a Sunday is never it
        for d in days(2024, 2035):
            if d.weekday() < 5:
                self.assertEqual(F.last_weekday_of_month(d), WMR.last_weekday(d), d)


class Clocks(unittest.TestCase):
    def test_london_and_new_york_slots_follow_the_tz_database(self):
        ldn, ny = ZoneInfo("Europe/London"), ZoneInfo("America/New_York")
        for d in days(2024, 2035):
            if d.weekday() >= 5:
                self.assertIsNone(F.slot("LDN_FIX", S.date(d.year, d.month, d.day)))
                continue
            t = S.date(d.year, d.month, d.day)
            want_l = (int(dt.datetime(d.year, d.month, d.day, 15, 55, tzinfo=ldn).timestamp()),
                      int(dt.datetime(d.year, d.month, d.day, 16, 5, tzinfo=ldn).timestamp()))
            want_n = (int(dt.datetime(d.year, d.month, d.day, 15, 50, tzinfo=ny).timestamp()),
                      int(dt.datetime(d.year, d.month, d.day, 16, 0, tzinfo=ny).timestamp()))
            self.assertEqual(F.slot("LDN_FIX", t), want_l, d)
            self.assertEqual(F.slot("US_CLOSE", t), want_n, d)


class Sizing(unittest.TestCase):
    def test_never_rounds_up(self):
        rnd = random.Random(7)
        for _ in range(20000):
            plan, per_lot = rnd.uniform(0.001, 50.0), rnd.uniform(0.5, 400.0)
            ok, vol, virtual = F.size(plan, per_lot, 0.01, 0.01, 100.0)
            self.assertLessEqual(vol, virtual + 1e-9)
            self.assertGreater(vol + 0.01, virtual - 1e-9)
            self.assertEqual(ok, vol >= 0.01 - 1e-12)

    def test_tokyo_on_the_drawdown_ladder_at_1000(self):
        plan = float(S.plan_text(0, 0.57))                         # Tokyo weight 0.57 (the book's inverse-volatility rule)
        self.assertEqual(plan, 5.7712)
        self.assertTrue(F.size(plan, 300.0 + 7.0, 0.01, 0.01, 100.0)[0])        # one standard 0.01 lot fits at L0
        self.assertFalse(F.size(float(S.plan_text(8, 0.57)), 300.0 + 7.0, 0.01, 0.01, 100.0)[0])   # not at L8
        src = read(INC, "Flows", "FlowTokyoFix.mqh")
        self.assertIn("#define SEESARE_TOKYO_WEIGHT           0.57", src)
        self.assertIn("m_weight       = SEESARE_TOKYO_WEIGHT;", src)


class MqlSourceAgreement(unittest.TestCase):
    def test_holiday_table_is_current(self):
        src = read(INC, "Core", "Calendar.mqh")
        m = re.search(r"//--- BEGIN GENERATED HOLIDAYS.*?//--- END GENERATED HOLIDAYS", src, re.S)
        self.assertEqual(m.group(0), F.holiday_block())
        table = [int(x) for x in re.findall(r"\b(20[0-9]{6})\b", m.group(0))]
        self.assertEqual(table, [int(d.strftime("%Y%m%d")) for d in F.jp_holidays()])
        self.assertEqual(table, sorted(table))                   # the MQL5 lookup is a binary search

    def test_selftest_vectors_are_current(self):
        src = read(MQL, "Scripts", "SeesarePhase2SelfTest.mq5")
        m = re.search(r"//--- BEGIN GENERATED VECTORS.*?//--- END GENERATED VECTORS", src, re.S)
        self.assertEqual(m.group(0), F.mql_block(), "regenerate with: python3 tools/seesare_flows.py --mql")

    def test_tokyo_constants_match_the_research(self):
        src = read(INC, "Flows", "FlowTokyoFix.mqh")
        self.assertIn("#define SEESARE_TOKYO_ENTRY_MIN        (23 * 60)", src)
        self.assertIn("#define SEESARE_TOKYO_EXIT_MIN         55", src)
        self.assertEqual(float(re.search(r"#define SEESARE_TOKYO_STOP_PCT\s+([0-9.]+)", src).group(1)), TOKYO.STOP_PCT)
        self.assertEqual(TOKYO.ENTRY["pre2300"], (22 * 60 + 55, 1, +1))   # signal bar 22:55 -> market entry 23:00
        self.assertEqual(TOKYO.EXIT_BAR["pre2300"], 50)                    # bar 00:50 closes at the 00:55 fix

    def test_london_constants_match_the_lab_file(self):
        src = read(INC, "Flows", "FlowLondonFix.mqh")
        self.assertIn("#define SEESARE_LDN_DRIFT_FROM_MIN    (15 * 60 + 30)", src)
        self.assertIn("#define SEESARE_LDN_ENTRY_MIN         (15 * 60 + 55)", src)
        self.assertIn("#define SEESARE_LDN_EXIT_MIN          (16 * 60 + 5)", src)
        self.assertEqual(WMR.DRIFT_FROM, (15, 30))
        self.assertEqual(WMR.SIGNAL_BAR, (15, 50))                         # closes 15:55 = entry
        self.assertEqual(WMR.TIME_STOP, 2)                                 # 2 M5 bars -> exit 16:05
        self.assertEqual(float(re.search(r"#define SEESARE_LDN_RATIO\s+([0-9.]+)", src).group(1)), WMR.MANAGEMENT["tgt"][0])
        self.assertEqual(float(re.search(r"#define SEESARE_LDN_BUFFER_PIPS\s+([0-9.]+)", src).group(1)) * 0.0001, WMR.PIP)
        self.assertIn("SEESARE_EVIDENCE_REJECTED", src)

    def test_us_close_is_untested_and_tokyo_is_candidate(self):
        self.assertIn("m_evidence     = SEESARE_EVIDENCE_CANDIDATE;", read(INC, "Flows", "FlowTokyoFix.mqh"))
        self.assertIn("m_evidence          = SEESARE_EVIDENCE_UNTESTED;", read(INC, "Flows", "FlowUsClose.mqh"))

    def test_time_policy_is_hardcoded(self):
        src = read(INC, "Ledger", "CycleLedger.mqh")
        self.assertIn("#define SEESARE_TIME_POLICY       SEESARE_TIME_GAIN_POSITIVE", src)
        self.assertIn('#define SEESARE_TIME_POLICY_NAME  "GAIN_POSITIVE_LOSS_NEGATIVE"', src)
        self.assertEqual(S.BUILD_POLICY, "GAIN_POSITIVE_LOSS_NEGATIVE")
        enum = src[src.index("enum ENUM_SEESARE_TIME_POLICY"):src.index("};", src.index("enum ENUM_SEESARE_TIME_POLICY"))]
        self.assertEqual(re.findall(r"SEESARE_TIME_[A-Z_]+\s*=\s*(\d)", enum), ["0", "1", "2"])
        self.assertEqual(len(S.POLICIES), 3)
        st = read(MQL, "Scripts", "SeesarePhase2SelfTest.mq5")
        self.assertIn("Classify(SEESARE_BY_TIME, 0.10, SEESARE_TIME_POLICY), 1);", st)
        self.assertIn("Classify(SEESARE_BY_TIME, 0.0, SEESARE_TIME_POLICY), 0);", st)
        self.assertEqual(S.classify("TIME", 0.10), 1)
        self.assertEqual(S.classify("TIME", 0.0), 0)
        self.assertEqual(S.classify("HUMAN", 0.10), 0)

    def test_router_sends_no_orders(self):
        src = read(MQL, "Experts", "SeesareRouter.mq5")
        for call in ("OrderSend", "CTrade", "PositionOpen", "OrderSendAsync"):
            self.assertNotIn(call, src)


if __name__ == "__main__":
    unittest.main()
