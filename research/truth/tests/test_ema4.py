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

    def test_full_engulf_needs_close_beyond_low(self):
        # 3rd candle (0.99 -> 1.02) has low 0.98 (wick); 4th closes 0.985: below its open, NOT below its low
        o = np.r_[[1.0] * 30, 0.98, 1.02, 0.99, 1.02]; c = np.r_[[1.0] * 30, 1.03, 0.99, 1.02, 0.985]
        h = np.maximum(o, c) + 0.01; l = np.minimum(o, c) - 0.01
        P1 = S.detect(o, h, l, c, engulf="open"); P2 = S.detect(o, h, l, c, engulf="extreme")
        k1 = (P1["i4"] == len(o) - 1) & (P1["side"] == -1); k2 = (P2["i4"] == len(o) - 1) & (P2["side"] == -1)
        self.assertEqual(int(P1["grade"][k1][0]), 1)                # v1: B+ (close below the 3rd open 0.99)
        self.assertEqual(int(P2["grade"][k2][0]), 0)                # v2: rejected (not below the 3rd low 0.98)
        c2 = c.copy(); c2[-1] = 0.97; l2 = np.minimum(o, c2) - 0.01
        P3 = S.detect(o, h, l2, c2, engulf="extreme"); k3 = (P3["i4"] == len(o) - 1) & (P3["side"] == -1)
        self.assertEqual(int(P3["grade"][k3][0]), 1)                # closes below 0.98: full engulfing B+

    def test_fresh_break_needs_previous_close_on_other_side(self):
        # candle before the "1st" already closed below the EMA: the 1st (opens a hair above, closes below) is no real break
        seq = [(0.98, 1.03), (1.031, 0.97), (1.0005, 0.96), (0.96, 1.03), (1.02, 0.95), (0.95, 1.06)]
        o, h, l, c = bars(seq)
        P0 = S.detect(o, h, l, c); P1 = S.detect(o, h, l, c, fresh=True)
        k0 = (P0["i4"] == len(o) - 1) & (P0["side"] == 1); k1 = (P1["i4"] == len(o) - 1) & (P1["side"] == 1)
        self.assertTrue(k0.any())
        self.assertFalse(k1.any())


if __name__ == "__main__":
    unittest.main()
