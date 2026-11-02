"""Tests of the owner's corrected 3:30 scanner (v2: pullback touch, stop placement, 1R):
    python3 -m unittest research/truth/tests/test_owner330_v2.py -v"""
import os, sys, unittest, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_owner330 as T1                      # the hand-built price-path helpers

_spec = importlib.util.spec_from_file_location("o330v2", os.path.join(HERE, "..", "strategies", "owner330_ema_retest_v2.py"))
S = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S)

# sell day: anchor range 99.4-100.3. Price drops below the range, a pullback candle closes back above the M5 EMA and its
# high wicks into the range (99.45), then a candle crosses back below the EMA entirely under the range (high 99.35).
DROP = [(99.5, 99.5, 99.2, 99.2), (99.2, 99.2, 99.0, 99.0), (99.0, 99.0, 98.9, 98.9), (98.9, 98.95, 98.85, 98.9)]
PULL = (98.9, 99.45, 98.9, 99.38)                # closes above the M5 EMA, wick touches the range low 99.4
CROSS = (99.38, 99.38, 98.95, 99.0)              # closes back below the EMA, never touches the range
DOWN = [(99.0, 99.2, 98.7, 98.7), (98.7, 98.7, 98.4, 98.4), (98.4, 98.4, 98.2, 98.2)]


def run(bars, stop="candle", buffer=0.0, anchor="wat1530"):
    S._CACHE.clear()
    M, B = T1.market(bars)
    q = dict(tf="M5", anchor=anchor, stop=stop, buffer=buffer)
    return S.setups(B, q, M), S.detail(M, B, q), B


class TestV2(unittest.TestCase):
    def test_pullback_touch_makes_the_reference(self):
        bars = T1.base_day(DROP + [PULL, CROSS] + DOWN + T1.QUIET)
        st, _, B = run(bars)
        self.assertEqual(len(st["j"]), 1)
        self.assertEqual(int(st["side"][0]), -1)
        j = int(st["j"][0])
        self.assertAlmostEqual(B["h"][j], 99.38)                    # the cross candle itself
        self.assertAlmostEqual(st["phi"][0], 99.45)                 # the pullback's high (touched the range)
        # v1 rule (the cross candle must touch the range) finds nothing here
        T1.S._CACHE.clear(); M, B1 = T1.market(bars)
        self.assertEqual(len(T1.S.setups(B1, T1.p(), M)["j"]), 0)

    def test_stop_choices(self):
        bars = T1.base_day(DROP + [PULL, CROSS] + DOWN + T1.QUIET)
        st, _, _ = run(bars)
        a = st["atr"][0]
        for stop, buf, want in (("candle", 0.0, 99.38), ("swing", 0.0, 99.45), ("swing", 0.25, 99.45 + 0.25 * a),
                                ("candle", 0.5, 99.38 + 0.5 * a)):
            x = S.stops(st, dict(stop=stop, buffer=buf))[0]
            self.assertAlmostEqual(x, want)

    def test_one_to_one_target(self):
        _, tr, _ = run(T1.base_day(DROP + [PULL, CROSS] + DOWN + T1.QUIET), stop="swing")
        self.assertEqual(len(tr), 1)
        e, sl, tp = tr[0, 8], tr[0, 9], tr[0, 10]
        self.assertAlmostEqual(e - tp, sl - e)                     # 1:1
        self.assertEqual(int(tr[0, 13]), 1)                         # big cross candle: limit at its 50% level
        self.assertAlmostEqual(e, 0.5 * (99.38 + 98.95))
        self.assertAlmostEqual(sl, 99.45)                          # swing stop: the pullback high
        self.assertEqual(S.REASON[int(tr[0, 12])], "target")
        self.assertAlmostEqual(tr[0, 3], 1.0)


if __name__ == "__main__":
    unittest.main()
