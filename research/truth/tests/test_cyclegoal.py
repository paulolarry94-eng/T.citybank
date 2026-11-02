"""Tests of the cycle-goal calculator:  python3 -m unittest discover -s research/truth/tests -v"""
import os, sys, unittest
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import cyclegoal as G
import protocol as P


class TestNeeded(unittest.TestCase):
    def test_two_percent_inside_3_6(self):
        self.assertAlmostEqual(G.needed_s(0.02, 0.036), 0.42, delta=0.01)

    def test_monotonic(self):
        for D in G.CAPS:
            xs = [G.needed_s(C, D) for C in G.TARGETS]
            self.assertEqual(xs, sorted(xs))                      # a bigger target needs more quality
        for C in G.TARGETS:
            xs = [G.needed_s(C, D) for D in G.CAPS]
            self.assertEqual(xs, sorted(xs, reverse=True))        # a looser cap needs less

    def test_simulation_agrees_with_map(self):
        self.assertAlmostEqual(G.needed_s_sim(0.02, 0.036, sims=2000), G.needed_s(0.02, 0.036), delta=0.04)

    def test_map_rescales_with_target(self):
        t2, t5 = G.map_table(0.02), G.map_table(0.05)
        self.assertAlmostEqual(t5[(0.55, 2.0)], t2[(0.55, 2.0)] * 2.5, delta=0.02)

    def test_trades_to_prove(self):
        self.assertEqual(G.trades_to_prove(0.5), 36)
        self.assertIsNone(G.trades_to_prove(0.0))


class TestScore(unittest.TestCase):
    def test_binary_strategy(self):
        rng = np.random.default_rng(3)
        R = np.where(rng.random(20000) < 0.55, 2.0, -1.0)          # 55% wins at 2:1: s about 0.435
        sc = G.score(R)
        self.assertAlmostEqual(sc["s"], 0.435, delta=0.02)
        self.assertAlmostEqual(sc["cycle_mean_pct_at_cap"]["3.6"], 2.0 * 3.6 / 3.38, delta=0.25)
        self.assertIn("2% at 3.6%", sc["meets"])

    def test_no_edge_meets_nothing(self):
        rng = np.random.default_rng(4)
        sc = G.score(rng.standard_normal(5000) * 0.0 + np.where(rng.random(5000) < 0.5, 1.0, -1.0))
        self.assertEqual(sc["meets"], [])

    def test_too_few(self):
        self.assertIn("note", G.score([1.0, -1.0]))


class TestCostLadder(unittest.TestCase):
    def test_reprices_trades(self):
        # one EURUSD trade: net +0.5 R after a 0.0001 cost on a 0.0035 stop distance
        T = np.array([[0, 0, 1, 0.5, 0.0035, 0.0001 / 0.0035, 0, 0, 0]] * 3)
        L = G.cost_ladder(T, ["EURUSD"], {"all": np.array([True] * 3)})
        self.assertAlmostEqual(L["gross"]["all"]["E"], 0.5 + 0.0001 / 0.0035, places=4)
        rf = G.profiles()["roboforex_prime"]["EURUSD"]
        self.assertAlmostEqual(L["roboforex_prime"]["all"]["E"], 0.5 + (0.0001 - rf) / 0.0035, places=4)


class TestReport(unittest.TestCase):
    def test_goal_lines_render(self):
        sc = G.score(np.where(np.random.default_rng(5).random(3000) < 0.55, 2.0, -1.0))
        r = dict(cycle_goal={"2011-19": sc, "2020-22": dict(trades=3, note="too few trades")},
                 cost_ladder={"gross": {"2011-19": dict(n=1, E=0.1, t=1.0), "2020-22": dict(n=1, E=0.2, t=2.0)}})
        txt = "\n".join(P._goal_lines(r))
        self.assertIn("Cycle goal", txt); self.assertIn("Cost ladder", txt); self.assertIn("| 2020-22 | 3 |", txt)



class TestMemoryRerun(unittest.TestCase):
    def test_rerun_keeps_first_date(self):
        import tempfile
        import memory as M
        old = (M.MEM, M.LEDGER)
        M.MEM = tempfile.mkdtemp(); M.LEDGER = os.path.join(M.MEM, "ledger.jsonl")
        try:
            M.record(dict(name="x", fingerprint="f", date="2026-01-01", verdict="Rejected"))
            M.record(dict(name="x", fingerprint="f", date="2026-02-01", verdict="Rejected"))
            rows = M.load()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["date"], "2026-01-01"); self.assertEqual(rows[0]["last_run"], "2026-02-01")
        finally:
            M.MEM, M.LEDGER = old


if __name__ == "__main__":
    unittest.main()
