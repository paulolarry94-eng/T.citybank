"""Tests of the 4-flip EMA strategy's order handling (research/truth/strategies/ema4_flip_v1.py):
    python3 -m unittest research/truth/tests/test_ema4_strategy.py -v"""
import os, sys, types, unittest, importlib.util, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "..", "northstar"))
sys.path.insert(0, os.path.join(HERE, "..", "..")); sys.path.insert(0, HERE)
import engine as E
import test_owner330 as T1                       # m1_from_m5: M5 bars -> M1 bars

_spec = importlib.util.spec_from_file_location("e4", os.path.join(HERE, "..", "strategies", "ema4_flip_v1.py"))
S = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S)
DAY = dt.date(2024, 1, 10)
T0 = int(dt.datetime(2024, 1, 10, 8, 0, tzinfo=dt.timezone.utc).timestamp())
FLAT = [(1.0, 1.001, 0.999, 1.0)] * 40
SELL4 = [(0.99, 1.031, 0.989, 1.03), (1.02, 1.021, 0.989, 0.99), (0.99, 1.021, 0.989, 1.02), (1.02, 1.03, 0.96, 0.97)]   # B+ sell


def run(after, entry="mid50", target=1, stop="c4", t0=T0):
    ts, o, h, l, c = T1.m1_from_m5(FLAT + SELL4 + after, t0)
    M = types.SimpleNamespace(sym="T%d" % len(after), ts=ts, o=o, h=h, l=l, gaps=E.data_gaps(ts), cost=0.001)
    bt, bo, bh, bl, bc, nxt = E.resample(ts, o, h, l, c, 5, 0)
    B = dict(t=bt.astype(np.int64), o=bo, h=bh, l=bl, c=bc, nxt=nxt.astype(np.int64), minutes=5,
             atr=np.full(len(bc), 0.02))
    S._CACHE.clear()
    p = dict(tf="M5", entry=entry, stop=stop, buffer=0.0, target=target, grade="AB")
    return S.setups(B, p, M), S.detail(M, B, p)


class TestOrders(unittest.TestCase):
    def test_limit_fills_at_50pct_and_hits_1r(self):
        st, tr = run([(0.97, 1.0, 0.97, 0.99), (0.99, 0.99, 0.90, 0.91)] + [(0.91, 0.912, 0.908, 0.91)] * 20)
        self.assertEqual(int(st["grade"][-1]), 1)
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0, 8], 0.995)                    # 50% of 1.03 / 0.96
        self.assertAlmostEqual(tr[0, 9], 1.03)                     # stop at the 4th candle's high
        self.assertEqual(S.REASON[int(tr[0, 12])], "target")

    def test_limit_expires_after_3_candles(self):
        st, tr = run([(0.97, 0.975, 0.95, 0.96)] * 4 + [(0.96, 1.0, 0.96, 0.99)] + [(0.99, 0.99, 0.98, 0.98)] * 10)
        self.assertEqual(len(tr), 0)                               # price returned to 0.995 only in the 5th candle

    def test_market_entry_at_close(self):
        st, tr = run([(0.97, 0.975, 0.90, 0.905)] + [(0.905, 0.906, 0.90, 0.905)] * 20, entry="close")
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0, 8], 0.97)                     # next minute's open (bid)

    def test_daily_close(self):
        t0 = int(dt.datetime(2024, 1, 10, 19, 30, tzinfo=dt.timezone.utc).timestamp()) - 44 * 300
        st, tr = run([(0.97, 0.98, 0.965, 0.97)] * 30, entry="close", target=4, t0=t0)
        self.assertEqual(len(tr), 1)
        self.assertEqual(S.REASON[int(tr[0, 12])], "daily close")
        self.assertEqual(int(tr[0, 1]) % 86400, 20 * 3600 + 1800)


if __name__ == "__main__":
    unittest.main()
