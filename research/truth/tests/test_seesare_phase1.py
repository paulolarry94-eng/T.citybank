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
    def test_transitions(self):
        self.assertEqual(S.ladder_next(0, 0, 1), (0, 0))
        self.assertEqual(S.ladder_next(0, 0, -1), (2, 1))
        self.assertEqual(S.ladder_next(2, 1, -1), (5, 2))
        self.assertEqual(S.ladder_next(5, 2, -1), (9, 3))
        self.assertEqual(S.ladder_next(14, 3, -1), (15, 4))
        self.assertEqual(S.ladder_next(7, 2, 0), (7, 2))
        self.assertEqual(S.ladder_next(7, 2, 1), (6, 0))

    def test_planned_deltas_match_the_blueprint(self):
        got = [float(S.num(S.floor_dp(S.plan_usd(p, 1.0, 0.05), 4), 4)) for p in S.LADDER[:4]]
        self.assertEqual(got, [1.368, 0.9025, 0.589, 0.3895])
        self.assertEqual(S.num(S.floor_dp(S.multiplier(1.0), 4), 4), "0.0820")       # SEESARE floor at 1:1
        self.assertEqual(S.num(S.floor_dp(S.multiplier(10.0), 4), 4), "1.5000")      # cap

    def test_floor_dp_is_exact_on_ties(self):
        self.assertEqual(S.num(S.floor_dp(S.plan_usd(0.0033, 1.0, 0.05), 4), 4), "0.0313")   # 0.03135 exactly
        self.assertEqual(S.num(S.floor_dp(1.368, 4), 4), "1.3680")
        self.assertEqual(S.num(S.floor_dp(S.multiplier(2.45), 4), 4), "0.4900")             # (0.7)^2

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
        for f in ("head", "level", "neg_run", "n", "shadow", "cycle", "l_net", "l_dd", "anchors"):
            self.assertEqual(getattr(R, f), getattr(self.L, f), f)
        self.assertEqual((R.level, R.neg_run, R.n, R.shadow, R.cycle), (14, 2, 12, 8, 2))   # ascension: L11 -> L14 at the end

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
        forged = list(self.lines)
        self.assertIn("by=STOP|res=NEGATIVE", forged[2])     # k=2: a stop; a smaller loss keeps every rule intact
        forged[2] = forged[2].replace("delta=-1.0592", "delta=-0.0592")
        forged = rehash_from(forged, 2)
        R = S.verify(forged)                       # a keyless chain can be recomputed...
        self.assertNotEqual(R.head, self.L.head)   # ...so only a head published elsewhere exposes the forgery
        with self.assertRaises(S.LedgerError):     # the published anchors catch it
            S.verify(forged, self.L.anchors)

    def test_rehashed_ladder_cheat_is_still_caught(self):
        forged = list(self.lines)
        forged[2] = forged[2].replace("lvl_after=2|neg_run=1", "lvl_after=0|neg_run=1")
        with self.assertRaisesRegex(S.LedgerError, "ladder rule broken"):
            S.verify(rehash_from(forged, 2))

    def test_rehashed_resolution_cheat_is_still_caught(self):
        forged = list(self.lines)
        self.assertIn("by=TIME|res=NEGATIVE", forged[6])     # k=6: the losing time exit
        forged[6] = forged[6].replace("by=TIME|res=NEGATIVE|lvl_before=0|lvl_after=2|neg_run=1",
                                      "by=TIME|res=MANUAL|lvl_before=0|lvl_after=0|neg_run=0")
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
        self.assertIn("by=TIME|res=POSITIVE|lvl_before=0|lvl_after=0|neg_run=0", forged[1])   # k=1: gain at L0
        forged[1] = forged[1].replace("by=TIME|res=POSITIVE", "by=TIME|res=MANUAL")
        with self.assertRaisesRegex(S.LedgerError, "exit rule"):
            S.verify(rehash_from(forged, 1))

    def test_rehashed_plan_cheat_is_still_caught(self):
        forged = list(self.lines)
        forged[1] = forged[1].replace("plan=1.3680", "plan=2.7360")
        with self.assertRaisesRegex(S.LedgerError, "planned delta"):
            S.verify(rehash_from(forged, 1))

    def test_truncated_ledger_is_caught_by_anchors(self):
        with self.assertRaisesRegex(S.LedgerError, "more cycles"):
            S.verify(self.lines[:17], self.L.anchors)       # the cycle closed at k=17
        S.verify(self.lines[:18], self.L.anchors)

    def test_changed_anchor_is_caught(self):
        a = self.L.anchors[0].replace("net=0.8907", "net=9.8907")
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

    def test_ladder_cannot_change_inside_a_lifecycle(self):
        other = list(S.LADDER)
        other[0] = 0.15
        L = S.Ledger(S.SELFTEST_LIFE, ladder=other)
        with self.assertRaisesRegex(S.LedgerError, "configured ladder differs"):
            L.apply_line(self.lines[0])

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


def bleed(policy_negative, guard):
    """Owner's worst case for the time-exit mandate: every event exits on time at -0.6R (forex, ratio 3.5).
    Returns (worst real drawdown in USD, real events, shadow events, envelope violations)."""
    L = S.Ledger("BLEED", time_policy="LOSS_NEGATIVE" if policy_negative else "MANUAL")
    L.genesis_line(S.date(2026, 11, 1))
    worst = 0.0
    for i in range(S.LIFECYCLE_EVENTS):
        if L.locked:
            break
        plan = L.plan_at(3.5, "forex")
        loss = round(0.6 * plan, 4)
        real = (not guard) or L.allows_real_risk(plan)
        t0 = S.date(2027, 1, 4, 23) + i * S.DAY
        L.record(dict(mode="REAL" if real else "SHADOW", module="BLEED", domain="forex", symbol="USDJPY", side=1,
                      digits=3, open=t0, close=t0 + 3600, by="TIME", ratio=3.5, risk=plan, vol=0.01,
                      entry=151.234, lower=151.084, upper=151.759, exit=151.144, delta=-loss,
                      deals=f"{i + 1}" if real else "-"))
        worst = max(worst, L.drawdown())
    return worst, L.n, L.shadow, len(L.violations)


def pump(policy, guard, events=S.LIFECYCLE_EVENTS):
    """Adversarial path for the time-exit ascension rule: a full stop, then two winning time exits of one cent each, repeated
    (forex, ratio 3.5). With gains climbing, the two tiny wins put the ladder back at L0 before every stop.
    Returns (worst real drawdown in USD, real events, shadow events, envelope violations)."""
    L = S.Ledger("PUMP", time_policy=policy)
    L.genesis_line(S.date(2026, 11, 1))
    worst = 0.0
    for i in range(events):
        if L.locked:
            break
        plan = L.plan_at(3.5, "forex")
        stop = i % 3 == 0
        real = (not guard) or L.allows_real_risk(plan)
        t0 = S.date(2027, 1, 4, 23) + i * S.DAY
        L.record(dict(mode="REAL" if real else "SHADOW", module="PUMP", domain="forex", symbol="USDJPY", side=1,
                      digits=3, open=t0, close=t0 + 3600, by="STOP" if stop else "TIME", ratio=3.5, risk=plan, vol=0.01,
                      entry=151.234, lower=151.084, upper=151.759, exit=151.084 if stop else 151.236,
                      delta=-plan if stop else 0.01, deals=f"{i + 1}" if real else "-"))
        worst = max(worst, L.drawdown())
    return worst, L.n, L.shadow, len(L.violations)


class EnvelopeGuard(unittest.TestCase):
    def test_ascension_without_guard_breaks_the_envelope(self):
        worst, real, shadow, viol = pump("GAIN_POSITIVE_LOSS_NEGATIVE", guard=False)
        self.assertAlmostEqual(worst, 120 * 1.368 - 119 * 0.02, places=4)    # 161.81 USD = 16.2% of $1,000
        self.assertGreater(viol, 0)

    def test_guard_holds_the_envelope_under_ascension(self):
        worst, real, shadow, viol = pump("GAIN_POSITIVE_LOSS_NEGATIVE", guard=True)
        self.assertLessEqual(worst, 36.0 + 1e-9)
        self.assertEqual(viol, 0)
        self.assertGreater(shadow, 0)          # once the room is used up, stops at L0 are paper; small events stay real
        self.assertEqual((real, shadow), (121, 239))

    def test_same_path_under_the_phase2_rule_stays_small(self):
        worst, real, shadow, viol = pump("LOSS_NEGATIVE", guard=True)
        self.assertAlmostEqual(worst, 2.0993, places=4)   # 0.21%: tiny wins did not climb, so the ladder shrank instead
        self.assertEqual(real, 360)
        self.assertEqual(viol, 0)

    def test_mandate_without_guard_breaks_the_envelope(self):
        worst, real, shadow, viol = bleed(policy_negative=False, guard=False)
        self.assertAlmostEqual(worst, 360 * round(0.6 * 1.368, 4), places=6)    # 295.49 USD = 29.5%
        self.assertGreater(viol, 0)

    def test_guard_holds_the_envelope_under_the_mandate(self):
        worst, real, shadow, viol = bleed(policy_negative=False, guard=True)
        self.assertLessEqual(worst, 36.0 + 1e-9)
        self.assertEqual(viol, 0)
        self.assertGreater(shadow, 0)          # once the room is used up the events continue on paper only

    def test_losing_time_exits_negative_keeps_drawdown_small(self):
        worst, real, shadow, viol = bleed(policy_negative=True, guard=True)
        self.assertLess(worst, 2.0)            # the ladder shrinks the size instead of running into the guard
        self.assertEqual(viol, 0)

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

    def test_ladder_and_friction_match(self):
        src = self.read("Include", "Seesare", "Ledger", "CycleLedger.mqh")
        m = re.search(r"double d\[SEESARE_LEVELS\] = \{([^}]*)\}", src)
        self.assertEqual([float(x) for x in m.group(1).split(",")], S.LADDER)
        fr = dict((k, float(v)) for k, v in re.findall(r'if\(domain == "(\w+)"\)\s*return ([0-9.]+);', src))
        self.assertEqual(fr, S.FRICTION)
        for name, want in (("SEESARE_BASELINE_USD", S.BASELINE), ("SEESARE_ENVELOPE_PCT", S.ENVELOPE_PCT),
                           ("SEESARE_EXPONENT", S.EXPONENT), ("SEESARE_CYCLE_EVENTS", S.CYCLE_EVENTS),
                           ("SEESARE_LIFECYCLE_EVENTS", S.LIFECYCLE_EVENTS)):
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
