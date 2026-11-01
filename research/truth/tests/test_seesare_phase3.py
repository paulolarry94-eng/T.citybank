"""SEESARE router Phase 3: tests of the Telegram outbox twin and the cent-account sizing twin (tools/seesare_outbox.py), and of
their agreement with the MQL5 source.

    python3 -m unittest research/truth/tests/test_seesare_phase3.py -v

MQL5 cannot be compiled here. These tests check (1) that every message the ledger can emit formats into short ASCII lines with
the record at the end and survives the relay's checksum, (2) the cent-account level tables, (3) that the MQL5 source carries the
same constants, deal-reason mapping and currency list as the twin, (4) that the Phase 3 self-test's vectors are the twin's, and
(5) simple MQL5 hazards in the new files (non-ASCII text, string literal + string literal, missing include files).
"""
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import seesare_outbox as O  # noqa: E402
import seesare_verify as S  # noqa: E402

MQL = os.path.join(ROOT, "mt5", "Seesare")
INC = os.path.join(MQL, "Include", "Seesare")
NEW_FILES = [os.path.join(INC, "Ledger", "Telegram.mqh"), os.path.join(INC, "Ledger", "Outbox.mqh"),
             os.path.join(INC, "Exec", "DealReader.mqh"), os.path.join(INC, "Risk", "Exposure.mqh"),
             os.path.join(INC, "Exec", "PaperBook.mqh"), os.path.join(MQL, "Scripts", "SeesarePhase3SelfTest.mq5"),
             os.path.join(MQL, "Experts", "SeesareRouter.mq5")]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def call_args(src, name):
    """Top-level arguments of every call (or declaration) `name(...)`, brackets balanced."""
    out = []
    i = src.find(name)
    while i >= 0:
        j, depth, args, cur = i + len(name), 1, [], ""
        while depth:
            c = src[j]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            if c == "," and depth == 1:
                args.append(cur.strip())
                cur = ""
            elif depth:
                cur += c
            j += 1
        args.append(cur.strip())
        out.append(args)
        i = src.find(name, j)
    return out


def all_records():
    """Every kind of line the ledger writes: the Phase 1 self-test lifecycle (genesis, 20 events, 1 anchor) and a locked one."""
    L, lines = S.build_selftest()
    out = [("GENESIS", L.lines[0])] + [("EVENT", x) for x in lines] + [("AUDIT", a) for a in L.anchors]
    lock = S.Ledger("SELFTEST_LOCK")
    lock.genesis_line(S.SELFTEST_CREATED)
    for i in range(S.LIFECYCLE_EVENTS):
        lock.record(S.lock_event(i))
    out += [("AUDIT", a) for a in lock.anchors] + [("LIFECYCLE", O.lifecycle_summary(lock))]
    return out


class Formatter(unittest.TestCase):
    def test_every_record_formats_into_ascii_lines_ending_with_the_record(self):
        recs = all_records()
        self.assertGreater(len(recs), 50)
        for kind, rec in recs:
            body = O.message_body(kind, rec)
            lines = body.split("\n")
            self.assertEqual(lines[-1], "Record: " + rec)
            self.assertTrue(all(ord(c) < 128 for c in body), kind)
            self.assertTrue(all(ln.strip() != "" for ln in lines), "empty lines are skipped by ReadLines")
            self.assertNotIn("\r", body)
            self.assertLessEqual(len(body), O.MAX_TELEGRAM)

    def test_real_events_carry_cycle_step_and_deal_tickets(self):
        for kind, rec in all_records():
            if kind != "EVENT":
                continue
            kv = S.parse(S.split_line(rec)[0])[1]
            head, deals = O.fmt_event(rec).split("\n")[0], O.fmt_event(rec).split("\n")[6]
            if kv["mode"] == "REAL":
                self.assertIn(f"Cycle {kv['cycle']}/36 | Step {kv['step']}/10 | REAL", head)
                self.assertEqual(deals, "Deals " + kv["deals"].replace(";", ", "))
                self.assertTrue(re.fullmatch(r"Deals [0-9]+(, [0-9]+)*", deals))
            else:
                self.assertIn("SHADOW (paper, not counted)", head)
                self.assertEqual(deals, "Deals none (paper)")

    def test_formatter_reprints_no_number(self):
        """Every number in the text is copied from the record: each digit run of the text occurs in the record."""
        for kind, rec in all_records():
            text = {"GENESIS": O.fmt_genesis, "EVENT": O.fmt_event, "AUDIT": O.fmt_audit,
                    "LIFECYCLE": O.fmt_lifecycle}[kind](rec)
            for tok in re.findall(r"-?[0-9]+(?:\.[0-9]+)?", text):
                if tok in ("26", "36", "10", "1", "2"):        # "P26", "/36", "/10", "Step 1", "L1" style labels
                    continue
                self.assertIn(tok.lstrip("-"), rec, f"{kind}: {tok}")

    def test_worst_case_event_fits_one_telegram_message(self):
        L = S.Ledger("L" * 32)
        L.genesis_line(S.SELFTEST_CREATED)
        e = S.sample_event(0)
        e.update(module="M" * 32, deals=";".join(str(10 ** 18 + i) for i in range(10)))
        self.assertLessEqual(len(e["deals"]), 200)
        line = L.record(e)
        msg = O.outbox_message(10 ** 9, "EVENT", L.life, 1, S.iso(e["close"]), line)
        self.assertLessEqual(len(O.relay_text(msg)), O.MAX_TELEGRAM)

    def test_signed(self):
        for a, b in O.SIGNED:
            self.assertEqual(O.signed(a), b)

    def test_malformed_records_are_refused(self):
        for bad in ("v=1||k=2", "", "|v=1", "v=1|k=1|k=2"):
            with self.assertRaises((ValueError, KeyError)):
                O.message_body("EVENT", bad)
        rec = S.build_selftest()[1][0]
        with self.assertRaises(ValueError):
            O.fmt_event(rec[:-70])                       # an event without its hash
        with self.assertRaises(KeyError):
            O.message_body("NOTE", rec)


class OutboxMessage(unittest.TestCase):
    def test_relay_reads_back_the_body(self):
        rec = S.build_selftest()[1][0]
        msg = O.outbox_message(1, "EVENT", "SELFTEST", 1, "2026-11-05T00:55:00Z", rec)
        self.assertTrue(msg.startswith(O.OUTBOX_FORMAT + "\nseq=0000000001\nkind=EVENT\n"))
        self.assertEqual(O.relay_text(msg), O.message_body("EVENT", rec))

    def test_relay_refuses_a_changed_message(self):
        rec = S.build_selftest()[1][0]
        msg = O.outbox_message(1, "EVENT", "SELFTEST", 1, "2026-11-05T00:55:00Z", rec)
        with self.assertRaises(ValueError):
            O.relay_text(msg.replace("+0.4321 USD", "+4.4321 USD"))

    def test_cent_case_outbox_message(self):
        line, msg = O.cent_case()
        lines = msg.rstrip("\n").split("\n")
        self.assertEqual(lines[7], "SEESARE P26 | P3SELFTEST | Cycle 1/36 | Step 1/10 | REAL")
        self.assertEqual(lines[10], "Result MANUAL | +0.3080 USD | level L0 -> L0 | negative run 0")
        self.assertEqual(lines[13], "Deals 50001000, 50001001")
        self.assertIn("|delta=0.3080|deals=50001000;50001001|", line)


class CentSizing(unittest.TestCase):
    def test_units_per_usd(self):
        for c, u in O.CURRENCIES:
            self.assertEqual(O.units_per_usd(c), u)

    def test_cent_lot_loss_at_the_tokyo_stop(self):
        """One cent lot = 1,000 USDJPY units: a 0.3% stop loses about $3.01 (the tables use $3.00)."""
        entry = 150.0
        stop = entry * (1 - 0.003)
        self.assertAlmostEqual(1000.0 * (entry - stop) / stop, 3.009, places=3)

    def test_tokyo_on_a_cent_account_is_real_only_at_the_top_four_levels(self):
        rows = O.level_table(1.04, 0.05, 3.00, 0.01, 0.01)
        self.assertEqual(O.lowest_feasible(rows), 3)
        self.assertEqual([r[2] for r in rows[:4]], [0.04, 0.02, 0.01, 0.01])

    def test_standard_account_is_never_real_at_these_plans(self):
        self.assertEqual(O.lowest_feasible(O.level_table(3.5, 0.05, 300.0, 0.01, 0.01)), -1)

    def test_volumes_never_round_up(self):
        for ratio in (0.5, 1.04, 2.0, 3.5, 5.0, 8.5):
            for per_lot in (0.37, 1.0, 3.0, 3.07, 10.0):
                for lv, plan, vol, ok in O.level_table(ratio, 0.05, per_lot, 0.01, 0.01):
                    self.assertLessEqual(vol * per_lot, plan + 1e-12)
                    self.assertEqual(ok, vol >= 0.01 - 1e-12)


class MqlSource(unittest.TestCase):
    def test_selftest_vectors_are_current(self):
        src = read(os.path.join(MQL, "Scripts", "SeesarePhase3SelfTest.mq5"))
        m = re.search(r"//--- BEGIN GENERATED VECTORS.*?//--- END GENERATED VECTORS", src, re.S)
        self.assertEqual(m.group(0), O.mql_block(), "regenerate with: python3 tools/seesare_outbox.py --mql")

    def test_constants_match_the_twin(self):
        tg = read(os.path.join(INC, "Ledger", "Telegram.mqh"))
        ob = read(os.path.join(INC, "Ledger", "Outbox.mqh"))
        self.assertIn(f'#define SEESARE_TG_HEAD   "{O.HEAD}"', tg)
        self.assertIn(f"#define SEESARE_TG_MAX    {O.MAX_TELEGRAM}", tg)
        self.assertIn(f'#define SEESARE_OUTBOX_FORMAT "{O.OUTBOX_FORMAT}"', ob)
        self.assertIn("#include <Seesare\\Ledger\\Telegram.mqh>", ob)
        self.assertIn("string body = CSeesareTelegram::Body(kind, record);", ob)

    def test_phase1_selftest_reads_the_new_format(self):
        src = read(os.path.join(MQL, "Scripts", "SeesarePhase1SelfTest.mq5"))
        self.assertIn(f'"{O.OUTBOX_FORMAT}"', src)
        self.assertIn("msg[nm - 2] : \"\"), want_record);", src)
        self.assertNotIn("msg[7] : \"\"), VEC_EVENT1", src)

    def test_deal_reasons_match_the_twin(self):
        src = read(os.path.join(INC, "Exec", "DealReader.mqh"))
        body = src[src.index("static ENUM_SEESARE_CLOSE CloseFromReason"):src.index("static double     NetUsd")]
        got = {}
        for cond, by in re.findall(r"if\((.*?)\)\s*return SEESARE_BY_([A-Z]+);", body):
            for r in re.findall(r"DEAL_REASON_[A-Z]+", cond):
                got[r] = by
        default = re.findall(r"return SEESARE_BY_([A-Z]+);\s*}", body)[-1]
        for reason, by in O.DEAL_REASONS:
            self.assertEqual(got.get(reason, default), by, reason)
        self.assertEqual(default, "BROKER")

    def test_currency_list_matches_the_twin(self):
        src = read(os.path.join(INC, "Risk", "Exposure.mqh"))
        body = src[src.index("static double     UnitsPerUsd"):src.index("static double     AccountUnitsPerUsd")]
        cents = set(re.findall(r'c == "([A-Z ]+)"', body.split("return 1.0;")[1]))
        self.assertEqual(cents, {"USC", "USX", "USCENT", "US CENT", "CENT"})
        self.assertIn('if(c == "USD")\n         return 1.0;', body)

    def test_callers_pass_the_account_units(self):
        router = read(os.path.join(MQL, "Experts", "SeesareRouter.mq5"))
        self.assertIn("LossPerLot(m.Market(), plan.side, entry, stop, g_units, loss_per_lot)", router)
        self.assertIn("InpCommissionLot, g_units, sz)", router)
        self.assertIn("g_paper.Init(g_root, g_units)", router)
        p2 = read(os.path.join(MQL, "Scripts", "SeesarePhase2SelfTest.mq5"))
        self.assertIn("LossPerLot(sym, 1, tick.ask, stop, units, loss)", p2)
        n = 0
        for src in (router, p2, read(os.path.join(INC, "Risk", "Exposure.mqh"))):
            for args in call_args(src, "LossPerLot("):
                self.assertEqual(len(args), 6, args)              # symbol, side, entry, stop, units, loss
                n += 1
        self.assertGreaterEqual(n, 4)
        for args in call_args(read(os.path.join(INC, "Exec", "PaperBook.mqh")), "PnlPerLot("):
            self.assertEqual(len(args), 7, args)                  # symbol, side, entry, exit, commission, units, pnl

    def test_includes_exist(self):
        for path in NEW_FILES:
            for inc in re.findall(r"#include <Seesare\\(.*?)>", read(path)):
                self.assertTrue(os.path.exists(os.path.join(INC, *inc.split("\\"))), f"{path}: {inc}")

    def test_no_mql5_hazards_in_new_files(self):
        for path in NEW_FILES:
            src = read(path)
            self.assertTrue(all(ord(c) < 128 for c in src), f"non-ASCII in {path}")
            code = re.sub(r"//[^\n]*", "", src)
            self.assertIsNone(re.search(r'"(?:[^"\\\n]|\\.)*"\s*\+\s*"', code), f"literal + literal in {path}")
            self.assertIsNone(re.search(r'"(?:[^"\\\n]|\\.)*"\s*\n\s*"', code), f"adjacent literals in {path}")


if __name__ == "__main__":
    unittest.main()
