"""Tests of the owner's 4-flip EMA pattern scanner (research/ema4/scanner.py):
    python3 -m unittest research/truth/tests/test_ema4.py -v"""
import os, sys, unittest
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "ema4"))
import scanner as S


def bars(seq, flat=1.0, n_flat=30):
    """Flat history at `flat` (EMA settles there), then candles (o, c); highs/lows a hair outside the body."""
    oc = [(flat, flat)] * n_flat + list(seq)
    o = np.array([x[0] for x in oc]); c = np.array([x[1] for x in oc])
    return o, np.maximum(o, c) + 0.01, np.minimum(o, c) - 0.01, c


class TestScanner(unittest.TestCase):
    def run_(self, seq, **kw):
        o, h, l, c = bars(seq)
        return S.detect(o, h, l, c, **kw), len(o)

    def test_sell_b_plus(self):
        # 1 up across 1.0, 2 down (closes 0.99, NOT below 1's open 0.98), 3 up (opens 0.99), 4 down below 3's open
        P, n = self.run_([(0.98, 1.03), (1.02, 0.99), (0.99, 1.02), (1.02, 0.97)])
        k = np.flatnonzero((P["i4"] == n - 1) & (P["side"] == -1))
        self.assertEqual(len(k), 1); self.assertEqual(int(P["grade"][k[0]]), 1)
        self.assertAlmostEqual(P["entry50"][k[0]], 0.5 * (1.03 + 0.96))

    def test_sell_a_plus(self):
        P, n = self.run_([(0.99, 1.03), (1.02, 0.98), (0.98, 1.02), (1.02, 0.97)])     # 2 closes below 1's open too
        k = np.flatnonzero((P["i4"] == n - 1) & (P["side"] == -1))
        self.assertEqual(int(P["grade"][k[0]]), 2)

    def test_only_second_engulfs_is_rejected(self):
        P, n = self.run_([(0.99, 1.03), (1.02, 0.98), (0.98, 1.03), (1.02, 0.995)])   # 4 closes above 3's open 0.98
        k = np.flatnonzero((P["i4"] == n - 1) & (P["side"] == -1))
        self.assertEqual(int(P["grade"][k[0]]), 0)

    def test_buy_mirror(self):
        P, n = self.run_([(1.02, 0.97), (0.98, 1.01), (1.01, 0.98), (0.98, 1.03)])
        k = np.flatnonzero((P["i4"] == n - 1) & (P["side"] == 1))
        self.assertEqual(len(k), 1); self.assertEqual(int(P["grade"][k[0]]), 1)

    def test_doji_breaks_the_chain(self):
        P, n = self.run_([(0.98, 1.03), (1.02, 0.99), (1.0, 1.0), (1.02, 0.97)])
        self.assertFalse(((P["i4"] == n - 1) & (P["side"] == -1)).any())

    def test_overlapping_windows(self):
        # five alternating flips: a sell on 1-4 and a buy on 2-5 (owner's 20 Oct chart)
        P, n = self.run_([(0.99, 1.03), (1.02, 0.98), (0.98, 1.02), (1.02, 0.97), (0.97, 1.03)])
        self.assertTrue(((P["i4"] == n - 2) & (P["side"] == -1)).any())
        self.assertTrue(((P["i4"] == n - 1) & (P["side"] == 1)).any())


if __name__ == "__main__":
    unittest.main()
