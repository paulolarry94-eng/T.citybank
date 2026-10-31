"""Tests of the Truth Lab itself:  python3 -m unittest discover -s research/truth/tests -v"""
import os, sys, json, types, tempfile, unittest
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))
import protocol as P
import parity_check as PC
import memory as MEMORY

_TMP_MEM = tempfile.mkdtemp()                       # tests never touch the real memory
MEMORY.MEM = _TMP_MEM; MEMORY.LEDGER = os.path.join(_TMP_MEM, "ledger.jsonl")


def fake_bars(n=400, seed=1):
    rng = np.random.default_rng(seed)
    c = 100 + np.cumsum(rng.normal(0, 1, n)); o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + 0.5; l = np.minimum(o, c) - 0.5
    return dict(t=np.arange(n, dtype=np.int64) * 3600 + 1_600_000_000, o=o, h=h, l=l, c=c, atr=np.full(n, 2.0),
                nxt=np.arange(1, n + 1, dtype=np.int64) * 60, first=np.arange(n, dtype=np.int64) * 60, minutes=60)


class FakeM:
    def __init__(self):
        self.B = fake_bars(); self.cost = 0.01

    def bars(self, tf):
        return self.B


def strategy(signals, name="t"):
    return types.SimpleNamespace(NAME=name, TIMEFRAMES=["H1"], GRID={"n": [5]}, signals=signals)


class TestLookahead(unittest.TestCase):
    def test_honest_strategy_passes(self):
        def sig(B, p, M):
            c = B["c"]; return [(i, 1, c[i] - 2) for i in range(5, len(c)) if c[i] > c[i - 5:i].max()]
        ok, rep = P.lookahead_check(strategy(sig), FakeM())
        self.assertTrue(ok)

    def test_peeking_strategy_is_caught(self):
        def sig(B, p, M):                                  # uses the NEXT bar's close: future information
            c = B["c"]; return [(i, 1, c[i] - 2) for i in range(len(c) - 1) if c[i + 1] > c[i] + 1]
        ok, rep = P.lookahead_check(strategy(sig), FakeM())
        self.assertFalse(ok)

    def test_whole_series_normalisation_is_caught(self):
        def sig(B, p, M):                                  # z-score with the FULL-history mean: classic hidden leak
            c = B["c"]; z = (c - c.mean()) / c.std()
            return [(i, 1, c[i] - 2) for i in range(len(c)) if z[i] > 1.0]
        ok, rep = P.lookahead_check(strategy(sig), FakeM())
        self.assertFalse(ok)


class TestCandidates(unittest.TestCase):
    def test_market_row_enters_next_bar(self):
        B = fake_bars(); M = FakeM()
        C = P.to_candidates(B, [(10, 1, 95.0)], M, 5.0)
        self.assertEqual(int(C["k0"][0]), int(B["nxt"][10])); self.assertEqual(int(C["jb"][0]), 11)
        self.assertEqual(int(C["sig"][0]), 10); self.assertEqual(float(C["entry"][0]), -1.0)

    def test_bad_rows_are_dropped(self):
        B = fake_bars(); M = FakeM()
        C = P.to_candidates(B, [(len(B["c"]) - 1, 1, 95.0), (10, 0, 95.0), (10, 1, np.nan)], M, 5.0)
        self.assertEqual(len(C["k0"]), 0)


class TestFingerprint(unittest.TestCase):
    def test_changed_rules_after_final_look_are_refused(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "s.py")
            open(f, "w").write('NAME="fp_test"\nHYPOTHESIS="x"\nTIMEFRAMES=["H1"]\nGRID={"n":[1]}\ndef signals(B,p,M):\n    return []\n')
            old = P.RES; P.RES = d
            try:
                os.makedirs(os.path.join(d, "fp_test"))
                json.dump([dict(fingerprint="something-else", config="{}", time="t", oos={}, per_market={})],
                          open(os.path.join(d, "fp_test", "oos_log.json"), "w"))
                with self.assertRaises(SystemExit):
                    P.run(f)
            finally:
                P.RES = old


class TestReports(unittest.TestCase):
    def test_worthy_strategy_gets_an_ea_spec(self):
        with tempfile.TemporaryDirectory() as d:
            S = types.SimpleNamespace(NAME="x", HYPOTHESIS="h", RULES="r", MARKETS=["XAUUSD"], TIME_STOP=50, signals=lambda *a: [])
            rec = dict(name="x", fingerprint="0" * 64, started="now", markets=["XAUUSD"], timeframes=["H4"], params={}, management={},
                       verdict="Tier B: forward-test candidate", tier="B",
                       selection=dict(candidate=dict(tf="H4", tgt=0.0, trail=3.0, bias=0)))
            P.finish(S, rec, d)
            self.assertTrue(os.path.exists(os.path.join(d, "EA_SPEC.md")))
            self.assertIn("TruthEA", open(os.path.join(d, "EA_SPEC.md")).read())

    def test_rejected_strategy_gets_no_ea_spec(self):
        with tempfile.TemporaryDirectory() as d:
            S = types.SimpleNamespace(NAME="x", HYPOTHESIS="h", MARKETS=["XAUUSD"], TIME_STOP=50, signals=lambda *a: [])
            rec = dict(name="x", fingerprint="0" * 64, started="now", markets=["XAUUSD"], timeframes=["H4"], params={}, management={},
                       verdict="Rejected: no configuration passed the development gate", lookahead=dict(ok=True, checks=[]))
            P.finish(S, rec, d)
            self.assertFalse(os.path.exists(os.path.join(d, "EA_SPEC.md")))


class TestParity(unittest.TestCase):
    def test_identical_trades_pass_and_missing_trades_fail(self):
        t = pd.date_range("2024-01-01", periods=40, freq="D")
        R = pd.DataFrame(dict(t=t, side=1, r=np.linspace(-1, 2, 40)))
        X = R.copy(); X["t"] = X.t + pd.Timedelta(minutes=30); X["r"] = X.r + 0.02
        self.assertTrue(PC.check(R, X, 240)["passed"])
        self.assertFalse(PC.check(R, X.iloc[:30].reset_index(drop=True), 240)["passed"])



class TestMemory(unittest.TestCase):
    def setUp(self):
        for f in os.listdir(_TMP_MEM):
            os.remove(os.path.join(_TMP_MEM, f))

    def test_record_replaces_same_fingerprint_and_keeps_others(self):
        MEMORY.record(dict(date="2026-01-01", name="a", fingerprint="1", family=["trend"], verdict="Rejected"))
        MEMORY.record(dict(date="2026-01-02", name="a", fingerprint="1", family=["trend"], verdict="Tier B: forward-test candidate"))
        MEMORY.record(dict(date="2026-01-03", name="b", fingerprint="2", family=["liquidity"], verdict="Rejected"))
        rows = MEMORY.load()
        self.assertEqual(len(rows), 2)
        self.assertEqual([r["verdict"] for r in rows if r["name"] == "a"], ["Tier B: forward-test candidate"])
        self.assertTrue(os.path.exists(os.path.join(_TMP_MEM, "LESSONS.md")))

    def test_priors_and_survivor_logic(self):
        MEMORY.record(dict(date="2026-01-01", name="x", fingerprint="1", family=["Liquidity", "reversal"], verdict="Rejected"))
        MEMORY.record(dict(date="2026-01-02", name="y", fingerprint="2", family=["trend"], verdict="Survivor (futures only)"))
        self.assertEqual([e["name"] for e in MEMORY.priors(["liquidity"])], ["x"])
        self.assertFalse(MEMORY.survived(MEMORY.load()[0])); self.assertTrue(MEMORY.survived(MEMORY.load()[1]))
        self.assertFalse(MEMORY.survived(dict(verdict="Rejected (equity-index RSI2 on watch)")))

    def test_lab_run_is_recorded_in_memory(self):
        with tempfile.TemporaryDirectory() as d:
            S = types.SimpleNamespace(NAME="mem_test", HYPOTHESIS="h", FAMILY=["trend"], MARKETS=["XAUUSD"], TIME_STOP=50, signals=lambda *a: [])
            rec = dict(name="mem_test", fingerprint="f" * 64, started="now", markets=["XAUUSD"], timeframes=["H4"], params={}, management={},
                       verdict="Rejected: no configuration passed the development gate", lookahead=dict(ok=True, checks=[]),
                       grid_summary=dict(configs=12, passed_gate=0, share_dev_positive=0.1, median_dev_E=-0.1, share_dev_and_val_positive=0.0))
            P.finish(S, rec, d)
        e = [r for r in MEMORY.load() if r["name"] == "mem_test"]
        self.assertEqual(len(e), 1); self.assertEqual(e[0]["family"], ["trend"]); self.assertEqual(e[0]["configs"], 12)



class TestStopEntryAndBailout(unittest.TestCase):
    def _minutes(self, closes, t0=1704923000):        # 2024-01-10 21:43:20 UTC ~ 16:43 New York (EST)
        c = np.asarray(closes, float); o = np.r_[c[0], c[:-1]]
        h = np.maximum(o, c) + 0.00005; l = np.minimum(o, c) - 0.00005
        ts = (t0 - t0 % 60) + np.arange(len(c), dtype=np.int64) * 60
        return o, h, l, c, ts

    def test_buy_stop_fills_when_the_ask_reaches_the_level(self):
        o, h, l, c, ts = self._minutes([1.1000, 1.1003, 1.1006, 1.1012, 1.1015])
        first = np.array([0], np.int64); nxt = np.array([5], np.int64)
        k, px, u = P.stop_scan(o, h, l, ts, first, nxt, 0, 1, 1, 1.1010, 0.0002, 0, 0)
        self.assertEqual(k, 3)                             # minute 2: ask high 1.10085 < 1.1010; minute 3: 1.10145 >= 1.1010
        self.assertAlmostEqual(px, 1.1010, places=9)       # fills at the level (no gap)

    def test_bailout_exits_on_first_profitable_minute_in_the_new_york_window(self):
        import executors as X
        closes = [1.1000] * 3 + [1.0998, 1.1004, 1.1006, 1.1010] + [1.1010] * 20
        o, h, l, c, ts = self._minutes(closes)
        bail = X.ny_window(ts, 16 * 60 + 45, 16 * 60 + 55)
        self.assertTrue(bail[2] or bail[3])                  # the window starts ~16:45 New York
        res = X._bailout(o, h, l, c, ts, np.zeros(0, np.int64), bail, np.array([1], np.int64), np.array([1], np.int64),
                         np.array([1.1001]), np.array([0.0250]), 0.0002, 0.0, 2 ** 62, 0)
        self.assertEqual(len(res), 1)
        first_profit = next(i for i in range(2, len(c)) if bail[i] and c[i] > 1.1001)
        self.assertEqual(int(res[0, 1]), int(ts[first_profit]))
        self.assertAlmostEqual(res[0, 3], (c[first_profit] - 1.1001) / 0.0250, places=9)

    def test_bailout_stop_with_gap_fills_at_worse_open(self):
        import executors as X
        o, h, l, c, ts = self._minutes([1.1000, 1.1000, 1.0700, 1.0700])
        o[2] = 1.0700; h[2] = 1.0705; l[2] = 1.0695
        res = X._bailout(o, h, l, c, ts, np.zeros(0, np.int64), np.zeros(len(c), np.bool_), np.array([1], np.int64),
                         np.array([1], np.int64), np.array([1.1000]), np.array([0.0250]), 0.0002, 0.0, 2 ** 62, 0)
        self.assertAlmostEqual(res[0, 3], (1.0700 - 1.1000) / 0.0250, places=9)   # gapped through the 250-pip stop


if __name__ == "__main__":
    unittest.main()
