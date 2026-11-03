"""Tests of ema4_flip_v2 exits (trailing stop, EMA exit):  python3 -m unittest research/truth/tests/test_ema4_v2.py -v"""
import os, sys, types, unittest, importlib.util, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "..", "northstar"))
sys.path.insert(0, os.path.join(HERE, "..", "..")); sys.path.insert(0, HERE)
import engine as E
import test_owner330 as T1

_spec = importlib.util.spec_from_file_location("e4v2", os.path.join(HERE, "..", "strategies", "ema4_flip_v2.py"))
S = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S)
T0 = int(dt.datetime(2024, 1, 10, 8, 0, tzinfo=dt.timezone.utc).timestamp())
FLAT = [(1.0, 1.001, 0.999, 1.0)] * 40
SELL4 = [(0.99, 1.031, 0.989, 1.03), (1.02, 1.021, 0.989, 0.99), (0.99, 1.021, 0.985, 1.02), (1.02, 1.03, 0.96, 0.97)]  # 4th < 3rd low


def run(after, exit_, entry="close"):
    ts, o, h, l, c = T1.m1_from_m5(FLAT + SELL4 + after, T0)
    M = types.SimpleNamespace(sym="V%d%s" % (len(after), exit_), ts=ts, o=o, h=h, l=l, gaps=E.data_gaps(ts), cost=0.001)
    bt, bo, bh, bl, bc, nxt = E.resample(ts, o, h, l, c, 5, 0)
    B = dict(t=bt.astype(np.int64), o=bo, h=bh, l=bl, c=bc, nxt=nxt.astype(np.int64), minutes=5, atr=np.full(len(bc), 0.02))
    S._CACHE.clear()
    p = dict(tf="M5", entry=entry, stop="c4", buffer=0.0, exit=exit_, grade="AB")
    return S.setups(B, p, M), S.detail(M, B, p)


class TestExits(unittest.TestCase):
    def test_full_engulf_is_found(self):
        st, _ = run([(0.97, 0.975, 0.965, 0.97)] * 5, "1R")
        self.assertEqual(int(st["grade"][-1]), 1)

    def test_trailing_stop(self):
        # falls to 0.90, then bounces 0.03 (> 1 x ATR 0.02): trailing stop at 0.90 + 0.02 (+cost) closes the trade
        path = [(0.97, 0.97, 0.94, 0.94), (0.94, 0.94, 0.90, 0.90), (0.90, 0.93, 0.90, 0.93)] + [(0.93, 0.931, 0.929, 0.93)] * 10
        _, tr = run(path, "trail1")
        self.assertEqual(S.REASON[int(tr[0, 12])], "trailing stop")
        self.assertAlmostEqual(tr[0, 11], 0.90 + 0.001 + 0.02, places=6)
        self.assertGreater(tr[0, 3], 0.5)

    def test_ema_exit(self):
        # falls, then a candle closes back above the EMA: out at the next minute
        path = [(0.97, 0.97, 0.95, 0.95), (0.95, 0.95, 0.94, 0.94)] + [(0.94, 1.02, 0.94, 1.02)] + [(1.02, 1.021, 1.019, 1.02)] * 5
        _, tr = run(path, "ema")
        self.assertEqual(S.REASON[int(tr[0, 12])], "EMA exit")


if __name__ == "__main__":
    unittest.main()
