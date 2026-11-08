"""Owner's body-engulf 4-candle range (Q30): detector and reference order engine on hand-made 1-minute candles."""
import os, sys, unittest, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "body4"))
import body4_scan as SC   # noqa: E402
import body4_orders as OR   # noqa: E402

LOOK = [(101.5, 101.6, 101.0, 101.1)] * 5          # five bearish candles before candle 1 (o, h, l, c)
SELL4 = [(100.0, 101.2, 99.9, 101.0), (101.0, 101.3, 99.4, 99.5), (99.5, 100.6, 99.45, 100.5), (100.5, 100.6, 99.3, 99.4)]


def market(rows, start):
    o, h, l, c = (np.array([r[i] for r in rows], float) for i in range(4))
    t = start + 60 * np.arange(len(rows))
    return dict(t=t, ts=t, o=o, h=h, l=l, c=c)


class TestBody4(unittest.TestCase):
    def test_wick_does_not_engulf(self):
        o = np.array([100.0, 101.0]); c = np.array([101.0, 100.05])
        self.assertFalse(SC.body_engulf(o, c, 1, -1))           # body closes above candle 1's open: no engulf
        c2 = np.array([101.0, 99.9])
        self.assertTrue(SC.body_engulf(o, c2, 1, -1))

    def test_sell_limit_breakeven_then_target(self):
        after = [(99.6, 100.4, 99.5, 100.0), (100.0, 100.1, 98.0, 98.2), (98.2, 98.3, 96.2, 96.4)]
        start = int(dt.datetime(2019, 1, 7, 10, tzinfo=dt.timezone.utc).timestamp())
        M = market(LOOK + SELL4 + after, start)
        P = OR.patterns(M, 1)
        # candles 3, 4 and the next two form a second valid sell (overlapping); it arrives while the trade is open
        self.assertEqual([(p["side"], round(p["mid"], 2), p["lookback"]) for p in P], [(-1, 100.3, 5), (-1, 99.3, 4)])
        tr, log = OR.run(M, P, cost=0.01)
        self.assertTrue(any("ignored, a trade is open" in x[1] for x in log))
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0]["entry"], 100.3); self.assertAlmostEqual(tr[0]["R"], 4.0)
        self.assertTrue(any("breakeven" in x[1] for x in log))

    def test_lookback_and_friday_close(self):
        after = [(99.6, 100.4, 99.5, 100.0)] + [(100.0, 100.2, 99.8, 100.0)] * 40
        start = int(dt.datetime(2019, 1, 11, 20, 0, tzinfo=dt.timezone.utc).timestamp())   # Friday 20:00 UTC
        M = market(LOOK + SELL4 + after, start)
        tr, log = OR.run(M, OR.patterns(M, 1), cost=0.01)
        self.assertEqual(tr[0]["reason"], "Friday close")
        self.assertEqual(dt.datetime.fromtimestamp(tr[0]["t_out"], dt.timezone.utc).strftime("%a %H:%M"), "Fri 20:30")
        bull = [(r[0], r[1], r[2], r[0] + 0.5) for r in LOOK]                # lookback now bullish: sell rejected
        M2 = market(bull + SELL4 + after, start)
        tr2, log2 = OR.run(M2, OR.patterns(M2, 1), cost=0.01)
        self.assertEqual(tr2, []); self.assertTrue(any("lookback" in x[1] for x in log2))
        tr3, _ = OR.run(M2, OR.patterns(M2, 1), cost=0.01, use_lookback=False)
        self.assertEqual(len(tr3), 1)


if __name__ == "__main__":
    unittest.main()
