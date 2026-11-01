"""SEESARE router Phase 1: tests of the Python twin (tools/seesare_verify.py) and of its agreement with the MQL5 source.

    python3 -m unittest research/truth/tests/test_seesare_phase1.py -v

The MQL5 code cannot be compiled here. These tests check (1) the twin's DST rules against the IANA time-zone database,
(2) the ledger's rules, tamper detection and envelope guard, (3) that the MQL5 source carries the same tables as the twin,
and (4) that the vectors embedded in the MQL5 self-test script are the ones the twin generates today.
"""
import os
import re
import sys
import tempfile
import unittest
import datetime as dt
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import seesare_verify as S  # noqa: E402

MQL = os.path.join(ROOT, "mt5", "Seesare")
TZ = {S.LONDON: ZoneInfo("Europe/London"), S.FRANKFURT: ZoneInfo("Europe/Berlin"),
      S.NEW_YORK: ZoneInfo("America/New_York"), S.TOKYO: ZoneInfo("Asia/Tokyo")}


def zone_offset(v, t):
    return int(dt.datetime.fromtimestamp(t, TZ[v]).utcoffset().total_seconds())


def zone_local_to_utc(v, local):
    naive = dt.datetime.fromtimestamp(local, dt.timezone.utc).replace(tzinfo=None)
    return int(naive.replace(tzinfo=TZ[v], fold=0).timestamp())


def sample_times():
    """Every hour 2011-2035, plus every 15 minutes within two days of each DST switch."""
    t0, t1 = S.date(2011, 1, 1), S.date(2036, 1, 1)
    ts = set(range(t0, t1, 3600))
    for y in range(2011, 2036):
        for sw in (S.us_start(y), S.us_end(y), S.eu_start(y), S.eu_end(y)):
            ts.update(range(sw - 2 * S.DAY, sw + 2 * S.DAY, 900))
    return sorted(ts)


class Clock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.times = sample_times()

    def test_utc_to_venue_matches_tz_database(self):
        for v in TZ:
            bad = [t for t in self.times if S.venue_offset(v, t) != zone_offset(v, t)]
            self.assertEqual(bad[:3], [], f"{v}: {len(bad)} offsets differ, first at {[S.iso(t) for t in bad[:3]]}")

    def test_venue_to_utc_matches_tz_database_fold0(self):
        for v in TZ:
            bad = [t for t in self.times if S.venue_to_utc(v, t) != zone_local_to_utc(v, t)]
            self.assertEqual(bad[:3], [], f"{v}: {len(bad)} local times convert differently")

    def test_server_schemes_round_trip(self):
        for scheme, summer in ((S.GMT2_EU, S.eu_summer), (S.GMT2_US, S.us_summer)):
            for u in self.times:
                back = S.server_to_utc(scheme, S.utc_to_server(scheme, u))
                # the server clock repeats one hour in autumn: its second pass maps to the first
                second_pass = (not summer(u)) and summer(u - 3600)
                second_pass |= (not summer(u)) and S.utc_to_server(scheme, u) < S.utc_to_server(scheme, u - 3600) + 3600
                self.assertTrue(back == u or (second_pass and back == u - 3600), f"{scheme} {S.iso(u)}")
        for u in self.times[::50]:
            self.assertEqual(S.server_to_utc(S.GMT0, u), u)
            self.assertEqual(S.server_to_utc(S.FIXED, S.utc_to_server(S.FIXED, u, 330), 330), u)

    def test_mismatch_weeks(self):
        # 2026: US summer from 8 March, Europe from 29 March; Europe back on 25 October, US on 1 November
        m = S.Matrix()
        moc, wmr = m.find("NY_MOC"), m.find("WMR_FIX")
        self.assertEqual(S.iso(m.resolve(moc, S.date(2026, 3, 10))[2]), "2026-03-10T19:50:00Z")
        self.assertEqual(S.iso(m.resolve(wmr, S.date(2026, 3, 10))[2]), "2026-03-10T15:30:00Z")
        self.assertEqual(S.iso(m.resolve(moc, S.date(2026, 10, 28))[2]), "2026-10-28T19:50:00Z")
        self.assertEqual(S.iso(m.resolve(wmr, S.date(2026, 10, 28))[2]), "2026-10-28T15:30:00Z")
        self.assertEqual(S.iso(m.resolve(moc, S.date(2026, 12, 2))[2]), "2026-12-02T20:50:00Z")

    def test_tokyo_fix_window_is_the_research_window(self):
        m = S.Matrix()
        r = m.resolve(m.find("TOKYO_FIX"), S.date(2026, 7, 1))       # Wednesday in Tokyo
        self.assertEqual((S.iso(r[2]), S.iso(r[3])), ("2026-06-30T23:00:00Z", "2026-07-01T00:55:00Z"))
        self.assertIsNone(m.resolve(m.find("TOKYO_FIX"), S.date(2026, 7, 4)))   # Saturday in Tokyo

    def test_wrapping_window(self):
        m = S.Matrix()
        i = m.find("FUNDING_00")
        r = m.active_at(i, S.date(2026, 7, 2, 0, 5))
        self.assertEqual((S.iso(r[2]), S.iso(r[3])), ("2026-07-01T23:50:00Z", "2026-07-02T00:10:00Z"))
        self.assertIsNone(m.active_at(i, S.date(2026, 7, 2, 0, 10)))

    def test_iso_and_hhmm_parsers_are_strict(self):
        self.assertEqual(S.iso_to_time("2026-11-01T00:00:00Z"), S.date(2026, 11, 1))
        for bad in ("2026-02-30T00:00:00Z", "2026-11-01 00:00:00Z", "2026-11-01T00:00:00", "2026-11-01T24:00:00Z"):
            self.assertIsNone(S.iso_to_time(bad), bad)
        self.assertEqual(S.parse_hhmm("09:55"), 595)
        for bad in ("24:00", "9:55", "09:60", "0955"):
            self.assertEqual(S.parse_hhmm(bad), -1, bad)


class Ladder(unittest.TestCase):
    """Drawdown-keyed ladder (format 2): level = whole $2.25 bands of drawdown; plan = 0.30 x weight x room left."""

    def test_levels_from_drawdown(self):
        for dd, lv in ((0.0, 0), (2.2499, 0), (2.25, 1), (2.263, 1), (4.4999, 1), (4.5, 2), (12.923, 5), (33.7499, 14),
                       (33.75, 15), (36.0, 15), (50.0, 15), (-1.0, 0)):
            self.assertEqual(S.level_from_dd(dd), lv, dd)
        self.assertEqual(S.level_from_dd(0.1 + 0.2 + 1.95), 1)       # 2.25 reached by a float sum lands in the next band

    def test_plans(self):
        for lv, w, want in ((0, 1.0, "10.1250"), (1, 1.0, "9.4500"), (14, 1.0, "0.6750"), (15, 1.0, "0.0000"),
                            (0, 0.57, "5.7712"), (2, 0.25, "2.1937"), (0, 0.01, "0.1012")):
            self.assertEqual(S.plan_text(lv, w), want, (lv, w))

    def test_ladder_holds_the_envelope_by_construction(self):
        """For any drawdown inside a level's band, drawdown + 10/3 x the plan at weight 1.00 stays within $36: a REAL event
        (risk <= plan) can never open past the cap, and even a gap losing 3.33 times the plan cannot cross it."""
        for lv in range(S.LEVELS - 1):
            top = S.BAND_USD * (lv + 1) - 0.0001
            for w in (0.01, 0.25, 0.57, 1.0):
                plan = float(S.plan_text(lv, w))
                self.assertLessEqual(top + plan, 36.0, (lv, w))
                self.assertLessEqual(top + 3.33 * plan, 36.0, (lv, w))
        self.assertEqual(S.plan_text(S.LEVELS - 1, 1.0), "0.0000")

    def test_floor_dp_is_exact_on_ties(self):
        self.assertEqual(S.num(S.floor_dp(S.plan_usd(2, 0.25), 4), 4), "2.1937")   # 2.19375 exactly
        self.assertEqual(S.num(S.floor_dp(S.plan_usd(0, 1.0), 4), 4), "10.1250")   # 10.125 exactly
        self.assertEqual(S.num(S.floor_dp(1.368, 4), 4), "1.3680")

    def test_classify(self):
        self.assertEqual(S.BUILD_POLICY, "GAIN_POSITIVE_LOSS_NEGATIVE")
        self.assertEqual(S.classify("TIME", 0.3), 1)                               # the build's rule: a gain climbs
        self.assertEqual(S.classify("TIME", -0.3), -1)                             # a loss descends
        self.assertEqual(S.classify("TIME", 0.0), 0)                               # exactly 0: manual
        self.assertEqual(S.classify("TIME", 0.3, "LOSS_NEGATIVE"), 0)              # Phase 2 rule (research, old lifecycles)
        self.assertEqual(S.classify("TIME", -0.3, "LOSS_NEGATIVE"), -1)
        self.assertEqual(S.classify("TIME", -0.3, "MANUAL"), 0)                    # Phase 1 mandate
        self.assertEqual(S.classify("TIME", 0.3, "MANUAL"), 0)
        for pol in S.POLICIES:
            self.assertEqual(S.classify("STOP", 0.1, pol), -1)
            self.assertEqual(S.classify("BROKER", -5, pol), -1)
            self.assertEqual(S.classify("TARGET", 0.5, pol), 1)
            self.assertEqual(S.classify("HUMAN", -0.5, pol), 0)
            self.assertEqual(S.classify("HUMAN", 0.5, pol), 0)
        with self.assertRaises(ValueError):
            S.classify("TIME", 0.3, "ASCEND")


def rehash_from(lines, start):
    """Forger's tool: recompute every hash from line `start` on (what anyone can do to a keyless chain)."""
    out = list(lines)
    prev = S.split_line(out[start - 1])[1]
    for i in range(start, len(out)):
        c, _ = S.split_line(out[i])
        c = re.sub(r"\|prev=[0-9a-f]{64}$", f"|prev={prev}", c)
        prev = S.sha(c)
        out[i] = f"{c}|hash={prev}"
    return out


class LedgerRules(unittest.TestCase):
    def setUp(self):
        self.L, _ = S.build_selftest()
        self.lines = list(self.L.lines)

    def test_replay_equals_recording(self):
        R = S.verify(self.lines, self.L.anchors)
        for f in ("head", "level", "n", "shadow", "cycle", "l_net", "l_dd", "anchors"):
            self.assertEqual(getattr(R, f), getattr(self.L, f), f)
        self.assertEqual((R.level, R.n, R.shadow, R.cycle), (5, 12, 8, 2))   # the stop-out gap ends at drawdown 12.9230 = L5
        self.assertEqual(S.num(R.drawdown(), 4), "12.9230")

    def test_shadow_events_never_move_the_level(self):
        for line in self.lines[1:]:
            kv = S.parse(S.split_line(line)[0])[1]
            if kv["mode"] == "SHADOW":
                self.assertEqual(kv["lvl_before"], kv["lvl_after"])
                self.assertEqual(kv["risk"], "0.0000")

    def test_changed_character_is_caught(self):
        bad = list(self.lines)
        bad[5] = bad[5].replace("delta=", "delta=1", 1)
        with self.assertRaisesRegex(S.LedgerError, "hash mismatch"):
            S.verify(bad)

    def test_deleted_or_swapped_lines_are_caught(self):
        with self.assertRaises(S.LedgerError):
            S.verify(self.lines[:7] + self.lines[8:])
        swapped = list(self.lines)
        swapped[7], swapped[8] = swapped[8], swapped[7]
        with self.assertRaises(S.LedgerError):
            S.verify(swapped)

    def test_full_rehash_passes_alone_but_changes_the_head(self):
        forger = S.Ledger(S.SELFTEST_LIFE)                 # a forger rebuilds the whole lifecycle with a smaller loss at k=2
        forger.genesis_line(S.SELFTEST_CREATED)
        for i in range(len(S.SAMPLE)):
            e = S.sample_event(i)
            if i == 1:
                e["delta"] = -2.9
            forger.record(e)
        R = S.verify(forger.lines)                 # a keyless chain can be recomputed...
        self.assertNotEqual(R.head, self.L.head)   # ...so only a head published elsewhere exposes the forgery
        with self.assertRaises(S.LedgerError):     # the published anchors catch it
            S.verify(forger.lines, self.L.anchors)

    def test_rehashed_amount_change_breaks_the_next_drawdown(self):
        forged = list(self.lines)
        forged[2] = forged[2].replace("delta=-3.0000", "delta=-2.9000")
        with self.assertRaisesRegex(S.LedgerError, "dd is not the lifecycle drawdown"):
            S.verify(rehash_from(forged, 2))

    def test_rehashed_ladder_cheat_is_still_caught(self):
        forged = list(self.lines)
        self.assertIn("lvl_before=0|lvl_after=1|", forged[2])
        forged[2] = forged[2].replace("lvl_before=0|lvl_after=1|", "lvl_before=0|lvl_after=0|")
        with self.assertRaisesRegex(S.LedgerError, "drawdown level rule broken"):
            S.verify(rehash_from(forged, 2))

    def test_rehashed_resolution_cheat_is_still_caught(self):
        forged = list(self.lines)
        self.assertIn("by=TIME|res=NEGATIVE|", forged[6])     # k=6: the losing time exit
        forged[6] = forged[6].replace("by=TIME|res=NEGATIVE|", "by=TIME|res=MANUAL|")
        with self.assertRaisesRegex(S.LedgerError, "exit rule"):
            S.verify(rehash_from(forged, 6))

    def test_build_refuses_lifecycles_under_an_earlier_time_rule(self):
        for old in ("MANUAL", "LOSS_NEGATIVE"):
            M = S.Ledger("OLDRULE", time_policy=old)
            g = M.genesis_line(S.date(2026, 11, 1))
            self.assertIn(f"time_policy={old}|", g)
            with self.assertRaisesRegex(S.LedgerError, "policy"):
                S.Ledger("OLDRULE").apply_line(g)
            S.verify([g])                                     # the public verifier still reads every rule
        self.assertIn("time_policy=GAIN_POSITIVE_LOSS_NEGATIVE|", self.lines[0])

    def test_a_line_written_under_the_old_rule_is_refused(self):
        forged = list(self.lines)
        self.assertIn("by=TIME|res=POSITIVE|dd=0.0000|lvl_before=0|lvl_after=0|", forged[1])   # k=1: gain at L0
        forged[1] = forged[1].replace("by=TIME|res=POSITIVE", "by=TIME|res=MANUAL")
        with self.assertRaisesRegex(S.LedgerError, "exit rule"):
            S.verify(rehash_from(forged, 1))

    def test_rehashed_plan_cheat_is_still_caught(self):
        forged = list(self.lines)
        forged[1] = forged[1].replace("plan=10.1250", "plan=20.2500")
        with self.assertRaisesRegex(S.LedgerError, "planned risk"):
            S.verify(rehash_from(forged, 1))

    def test_real_risk_above_the_plan_is_refused(self):
        L = S.Ledger("RISK")
        L.genesis_line(S.date(2026, 11, 1))
        e = S.sample_event(0)
        e["risk"] = 10.1251
        with self.assertRaisesRegex(S.LedgerError, "above the ladder's plan"):
            L.record(e)
        e["risk"] = 10.125
        L.record(e)

    def test_weight_outside_the_range_is_refused(self):
        for w in (0.0, 1.01, 2.0):
            L = S.Ledger("WEIGHT")
            L.genesis_line(S.date(2026, 11, 1))
            e = S.sample_event(0)
            e["weight"], e["risk"] = w, 0.5
            with self.assertRaisesRegex(S.LedgerError, "weight out of range"):
                L.record(e)
        self.assertEqual(L.plan_at(1.01), -1.0)

    def test_truncated_ledger_is_caught_by_anchors(self):
        with self.assertRaisesRegex(S.LedgerError, "more cycles"):
            S.verify(self.lines[:17], self.L.anchors)       # the cycle closed at k=17
        S.verify(self.lines[:18], self.L.anchors)

    def test_changed_anchor_is_caught(self):
        self.assertIn("|net=-1.4909|", self.L.anchors[0])
        a = self.L.anchors[0].replace("|net=-1.4909|", "|net=9.8907|")
        with self.assertRaisesRegex(S.LedgerError, "hash mismatch"):
            S.verify(self.lines, [a])

    def test_extra_or_reordered_fields_are_refused(self):
        c, _ = S.split_line(self.lines[1])
        for bad in (c.replace("|deals=", "|note=x|deals="), c.replace("mode=REAL|n=1", "n=1|mode=REAL")):
            with self.assertRaises(S.LedgerError):
                S.verify([self.lines[0], f"{bad}|hash={S.sha(bad)}"])

    def test_events_must_move_forward_in_time(self):
        L = S.Ledger("T1")
        L.genesis_line(S.date(2026, 11, 1))
        L.record(S.sample_event(1))
        with self.assertRaisesRegex(S.LedgerError, "time order"):
            L.record(S.sample_event(0))

    def test_room_mult_cannot_change_inside_a_lifecycle(self):
        L = S.Ledger(S.SELFTEST_LIFE, room_mult=0.2)
        with self.assertRaisesRegex(S.LedgerError, "room_mult differs"):
            L.apply_line(self.lines[0])
        S.verify(self.lines)                       # the verifier reads the constants from the genesis line

    def test_lifecycle_stops_inside_the_cap(self):
        L, n = S.stop_run()
        self.assertTrue(L.stopped())
        self.assertEqual((n, L.level, S.num(L.drawdown(), 4)), (9, 15, "33.7500"))
        self.assertLessEqual(L.l_dd, 36.0)
        self.assertEqual(L.violations, [])
        self.assertEqual(L.plan_at(1.0), 0.0)

    def test_lifecycle_locks_at_360(self):
        L = S.Ledger("LOCK")
        L.genesis_line(S.date(2026, 11, 1))
        for i in range(S.LIFECYCLE_EVENTS):
            L.record(S.lock_event(i))
        self.assertTrue(L.locked)
        self.assertEqual((L.n, len(L.anchors), L.cycle), (360, 36, 37))
        with self.assertRaisesRegex(S.LedgerError, "lock"):
            L.record(S.lock_event(360))
        self.assertFalse(L.allows_real_risk(1.0))


def path(loss_of, guard, events=S.LIFECYCLE_EVENTS):
    """Runs a lifecycle at weight 1.00 where event i loses loss_of(i, plan) (negative = a gain), risk = plan, until it locks
    or stops. Returns (worst real drawdown in USD, real events, shadow events, envelope violations)."""
    L = S.Ledger("PATH")
    L.genesis_line(S.date(2026, 11, 1))
    worst = 0.0
    for i in range(events):
        if L.locked or L.stopped():
            break
        plan = L.plan_at(1.0)
        loss = round(loss_of(i, plan), 4)
        real = (not guard) or L.allows_real_risk(plan)
        t0 = S.date(2027, 1, 4, 23) + i * S.DAY
        L.record(dict(mode="REAL" if real else "SHADOW", module="PATH", domain="forex", symbol="USDJPY", side=1,
                      digits=3, open=t0, close=t0 + 3600, by="STOP" if loss > 0 else "TIME", weight=1.0,
                      risk=plan if real else 0.0, vol=0.01, entry=151.234, lower=151.084, upper=151.759, exit=151.144,
                      delta=-loss, deals=f"{i + 1}" if real else "-"))
        worst = max(worst, L.drawdown())
    return worst, L.n, L.shadow, len(L.violations)


class EnvelopeGuard(unittest.TestCase):
    """Paths that broke the retired win/loss ladder (P24), now run without the guard: the drawdown-keyed ladder alone holds."""

    def test_bleeding_time_exits(self):
        worst, real, shadow, viol = path(lambda i, plan: 0.6 * plan, guard=False)
        self.assertLessEqual(worst, 36.0)
        self.assertEqual(viol, 0)

    def test_stop_then_two_tiny_wins(self):
        worst, real, shadow, viol = path(lambda i, plan: plan if i % 3 == 0 else -0.01, guard=False)
        self.assertLessEqual(worst, 36.0)
        self.assertEqual(viol, 0)

    def test_gaps_up_to_three_point_three_times_the_plan(self):
        worst, real, shadow, viol = path(lambda i, plan: 3.33 * plan, guard=False)
        self.assertLessEqual(worst, 36.0)

    def test_a_bigger_gap_at_the_band_edge_can_cross(self):
        worst, real, shadow, viol = path(lambda i, plan: 2.2499 if i == 0 else 3.5 * plan, guard=False, events=2)
        self.assertGreater(worst, 36.0)        # 2.2499 + 3.5 x 10.125: only a gap above 3.33 x the plan gets past the cap
        self.assertEqual(viol, 0)              # no event opened past the cap: the excess is the gap itself

    def test_guard_matches_the_record_check(self):
        L = S.Ledger("EDGE")
        L.genesis_line(S.date(2026, 11, 1))
        L.l_peak, L.l_net = 0.0, -34.9
        self.assertTrue(L.allows_real_risk(1.1))
        self.assertFalse(L.allows_real_risk(1.10006))


class MqlSourceAgreement(unittest.TestCase):
    def read(self, *parts):
        with open(os.path.join(MQL, *parts), encoding="utf-8") as f:
            return f.read()

    def test_default_windows_match(self):
        src = self.read("Include", "Seesare", "Core", "Clock.mqh")
        got = re.findall(r'Add\("(\w+)",\s*SEESARE_VENUE_(\w+),\s*"(\d\d:\d\d)",\s*"(\d\d:\d\d)",\s*SEESARE_MASK_(\w+)\)', src)
        self.assertEqual([tuple(x) for x in got], [tuple(w) for w in S.DEFAULT_WINDOWS])

    def test_ladder_constants_match(self):
        src = self.read("Include", "Seesare", "Ledger", "CycleLedger.mqh")
        self.assertEqual(re.search(r'#define SEESARE_FORMAT\s+"(\d+)"', src).group(1), S.FORMAT)
        self.assertEqual(re.search(r'#define SEESARE_SIZING_NAME\s+"(\w+)"', src).group(1), S.SIZING)
        self.assertEqual(set(re.findall(r'domain == "(\w+)"', src)), set(S.DOMAINS))
        for name, want in (("SEESARE_BASELINE_USD", S.BASELINE), ("SEESARE_ENVELOPE_PCT", S.ENVELOPE_PCT),
                           ("SEESARE_CYCLE_EVENTS", S.CYCLE_EVENTS), ("SEESARE_LIFECYCLE_EVENTS", S.LIFECYCLE_EVENTS),
                           ("SEESARE_LEVELS", S.LEVELS), ("SEESARE_BAND_USD", S.BAND_USD),
                           ("SEESARE_BAND_UNITS", S.BAND_UNITS), ("SEESARE_ROOM_MULT", S.ROOM_MULT),
                           ("SEESARE_MAX_WEIGHT", S.MAX_WEIGHT)):
            self.assertEqual(float(re.search(rf"#define {name}\s+([0-9.]+)", src).group(1)), float(want), name)
        for name, keys in (("SEESARE_EVENT_KEYS", S.EVENT_KEYS), ("SEESARE_GENESIS_KEYS", S.GENESIS_KEYS),
                           ("SEESARE_AUDIT_KEYS", S.AUDIT_KEYS)):
            self.assertEqual(re.search(rf'#define {name}\s+"([^"]+)"', src).group(1).split(","), keys, name)

    def test_selftest_vectors_are_current(self):
        src = self.read("Scripts", "SeesarePhase1SelfTest.mq5")
        m = re.search(r"//--- BEGIN GENERATED VECTORS.*?//--- END GENERATED VECTORS", src, re.S)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(0), S.mql_block(), "regenerate with: python3 tools/seesare_verify.py --mql")

    def test_balanced_braces(self):
        for dirpath, _, files in os.walk(MQL):
            for fn in files:
                if fn.endswith((".mqh", ".mq5")):
                    with open(os.path.join(dirpath, fn), encoding="utf-8") as f:
                        code = re.sub(r'"(\\.|[^"\\])*"', '""', f.read())
                    code = re.sub(r"//[^\n]*", "", code)
                    code = re.sub(r"'(\\.|[^'\\])'", "' '", code)
                    for a, b in ("{}", "()", "[]"):
                        self.assertEqual(code.count(a), code.count(b), f"{fn}: {a}{b} unbalanced")


class Cli(unittest.TestCase):
    def test_exit_codes(self):
        L, _ = S.build_selftest()
        with tempfile.TemporaryDirectory() as d:
            led, anc = os.path.join(d, "ledger.txt"), os.path.join(d, "anchors.txt")
            with open(led, "w", newline="\r\n") as f:
                f.write("\n".join(L.lines) + "\n")
            with open(anc, "w", newline="\r\n") as f:
                f.write("\n".join(L.anchors) + "\n")
            self.assertEqual(S.main(["x", led, anc]), 0)
            with open(led, "a") as f:
                f.write("garbage\n")
            self.assertEqual(S.main(["x", led, anc]), 1)


if __name__ == "__main__":
    unittest.main()
