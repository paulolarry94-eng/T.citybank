"""Tests of executors.bracket_prices (per-trade target price with a minimum-R floor)."""
import os, sys, unittest
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "..", "northstar"))
import executors as X


def path(prices):
    p = np.asarray(prices, float)
    return p, p + 0.0, p - 0.0, p                                  # o, h, l, c (flat minutes)


class TestBracketPx(unittest.TestCase):
    def run_one(self, prices, side, entry, stop, tp, min_r=2.0, max_min=10 ** 6):
        o, h, l, c = path(prices)
        ts = np.arange(len(o), dtype=np.int64) * 60
        return X._bracket_px(o, h, l, c, ts, np.zeros(0, np.int64), np.array([0], np.int64), np.array([side], np.int64),
                             np.array([entry]), np.array([stop]), np.array([tp]), min_r, 0.0, 0.0, 2 ** 62, 0, max_min)

    def test_far_target_is_kept(self):
        r = self.run_one([100, 99, 97, 95, 94, 90, 90, 90], -1, 100.0, 101.0, 94.0)   # target 6R away: hit at 94
        self.assertAlmostEqual(r[0, 3], 6.0)

    def test_near_target_moves_to_two_r(self):
        r = self.run_one([100, 99.5, 99, 98.5, 98, 97, 97, 97], -1, 100.0, 101.0, 99.5)  # 0.5R target -> floor 2R at 98
        self.assertAlmostEqual(r[0, 3], 2.0)

    def test_gapped_stop_fills_at_the_worse_open(self):
        r = self.run_one([100, 100.5, 101.2, 99, 99, 99], -1, 100.0, 101.0, 95.0)   # jumps over 101: filled at 101.2
        self.assertAlmostEqual(r[0, 3], -1.2)

    def test_stop_exact(self):
        r = self.run_one([100, 100.5, 101.0, 99, 99, 99], -1, 100.0, 101.0, 95.0)
        self.assertAlmostEqual(r[0, 3], -1.0)

    def test_long_mirror(self):
        r = self.run_one([100, 101, 102, 103, 103, 103], 1, 100.0, 99.0, 101.0)     # floor 2R at 102
        self.assertAlmostEqual(r[0, 3], 2.0)


if __name__ == "__main__":
    unittest.main()
