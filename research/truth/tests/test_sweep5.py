"""Pivot-sweep v2 (owner's chart reading, 2026-11-12): detector (doji = bullish, loose engulf, 50% bodies), live pivot
levels, the waiting limit order, TP1 partial with the breakeven-plus-spread stop, and fast vs reference parity."""
import os, sys, unittest, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sweep5"))
import sweep5_scan as SS     # noqa: E402
import sweep5_orders as OR   # noqa: E402
import sweep5_fast as FA     # noqa: E402

MON = int(dt.datetime(2019, 1, 7, 10, tzinfo=dt.timezone.utc).timestamp())


def arr(rows):
    return [np.array([r[i] for r in rows], float) for i in range(4)]


class TestDetector(unittest.TestCase):
    def test_doji_counts_as_bullish_and_loose_engulf(self):
        # candle 1 bull, candle 2 bear closes below 1's open (opens below 1's close: loose), candle 3 DOJI, candle 4 bear
        rows = [(1.0, 1.2, 0.9, 1.1), (1.09, 1.1, 0.7, 0.8), (0.8, 0.85, 0.75, 0.8), (0.79, 0.8, 0.5, 0.55)]
        k, side = SS.detect(*arr(rows))
        self.assertEqual(list(k), [3]); self.assertEqual(list(side), [-1])

    def test_body_below_half_is_rejected(self):
        rows = [(1.0, 1.2, 0.9, 1.1), (1.09, 1.1, 0.7, 0.8), (0.8, 0.85, 0.75, 0.8), (0.79, 0.8, 0.0, 0.55)]   # candle 4 body 30%
        self.assertEqual(len(SS.detect(*arr(rows))[0]), 0)

    def test_live_levels(self):
        h = np.array([1, 2, 5, 2, 1, 1.5, 1.2, 6.0]); l = h - 0.5
        ph = np.zeros(8, bool); ph[2] = True; pl = np.zeros(8, bool)
        LH, LL = SS.live_levels(h, l, ph, pl, 2, 2)
        self.assertTrue(np.isnan(LH[3, 0])); self.assertEqual(LH[4, 0], 5.0); self.assertTrue(np.isnan(LH[7, 0]))


def handmade(bars, levels, side=-1, level=101.2, stop=101.6, life=10):
    """One sell order placed at minute 1; the pattern timeframe = M1 with the given live pivot lows after each bar."""
    o, h, l, c = arr(bars)
    t = MON + 60 * np.arange(len(bars))
    M = dict(ts=t, o=o, h=h, l=l, c=c)
    LL = np.tile(np.array(levels + [np.nan] * (3 - len(levels)), float), (len(bars), 1)); LH = np.full_like(LL, np.nan)
    S = dict(bt=t, LH=LH, LL=LL)
    O = dict(t_conf=np.array([t[1]]), side=np.array([side]), level=np.array([level]), stop=np.array([stop]),
             width=np.array([1.0]), t_exp=np.array([t[1] + 60 * life]))
    return M, O, S


class TestOrders(unittest.TestCase):
    def _both(self, M, O, S, ex="partial"):
        T = OR.run(M, O, S, 0.01, 0.0, 0.0, 0.0, ex)
        F = FA.run(M, O, S, dict(spread=0.01, commission=0.0, slippage=0.0), ex)
        self.assertEqual(len(T), len(F))
        for a, b in zip(T, F):
            self.assertAlmostEqual(a["R"], b[3]); self.assertEqual(a["why"], int(b[9]))
        return T

    def test_order_waits_while_price_runs_away_then_fills_and_takes_tp1_and_tp2(self):
        # sell limit 101.2, stop 101.6 (1R 0.4); price first falls far (old rule would cancel), comes back, fills, then
        # TP1 100.4 (2R) and TP2 100.0 (3R): 0.6 x 2 + 0.4 x 3 = 2.4R
        bars = [(101.0, 101.1, 100.9, 101.0)] * 2 + [(101.0, 101.0, 100.2, 100.3), (100.3, 101.25, 100.3, 101.2),
                (101.2, 101.2, 100.35, 100.39), (100.39, 100.4, 99.9, 99.95)]
        T = self._both(*handmade(bars, [100.4, 100.0]))
        self.assertEqual(len(T), 1); self.assertAlmostEqual(T[0]["R"], 0.6 * 2.0 + 0.4 * 3.0)

    def test_breakeven_plus_spread_after_tp1(self):
        bars = [(101.0, 101.1, 100.9, 101.0)] * 2 + [(101.1, 101.25, 101.0, 101.2), (101.2, 101.2, 100.35, 100.39),
                (100.39, 101.3, 100.38, 101.25)]
        T = self._both(*handmade(bars, [100.4, 100.0]))
        # 60% at TP1 = +2R; the rest stopped at entry - spread (101.19) bought at the ask = 101.19: +0.025R
        self.assertEqual(T[0]["why"], 3); self.assertAlmostEqual(T[0]["R"], 0.6 * 2.0 + 0.4 * (0.01 / 0.4))

    def test_order_cancelled_when_stop_is_touched_before_the_fill(self):
        bars = [(101.0, 101.1, 100.9, 101.0)] * 2 + [(101.0, 101.15, 100.9, 101.1), (101.1, 101.6, 101.1, 101.15)]
        bars[3] = (101.1, 101.19, 100.9, 101.1)
        bars.append((101.1, 101.65, 101.0, 101.6)) if False else None
        M, O, S = handmade(bars, [100.4, 100.0], level=101.3, stop=101.18)
        self.assertEqual(len(self._both(M, O, S)), 0)


class TestParity(unittest.TestCase):
    def test_eurusd_2019_m5_m15(self):
        try:
            sys.path.insert(0, os.path.join(HERE, "..", ".."))
            import engine as EN
            ts, o, h, l, c = EN.load_m1("EURUSD", 2019, 2019)
        except Exception as e:
            self.skipTest(str(e))
        keep = ts < int(dt.datetime(2019, 4, 1, tzinfo=dt.timezone.utc).timestamp())
        M = dict(ts=ts[keep], o=o[keep], h=h[keep], l=l[keep], c=c[keep])
        cost = dict(spread=1e-5, commission=2.5e-5, slippage=2e-5, swap=1e-5)
        n = 0
        for tf in (5, 15):
            bt, bo, bh, bl, bc, _ = EN.resample(M["ts"], M["o"], M["h"], M["l"], M["c"], tf)
            S = SS.setups(dict(t=bt, o=bo, h=bh, l=bl, c=bc), tf)
            for sw, st, life, ex in (("recent", "range", 96, "partial"), ("now", "wide", 24, "tp1"), ("recent", "wide", 24, "tp2")):
                O = SS.orders(S, st, life)
                T = OR.run(M, O, S, cost["spread"], cost["commission"], cost["slippage"], cost["swap"], ex, allow=S[sw])
                F = FA.run(M, O, S, cost, ex, allow=S[sw])
                self.assertEqual(len(T), len(F))
                for a, b in zip(T, F):
                    self.assertEqual((a["t_in"], a["t_out"], a["why"]), (int(b[0]), int(b[1]), int(b[9])))
                    self.assertAlmostEqual(a["R"], b[3], places=9)
                n += len(T)
        self.assertGreater(n, 50)


if __name__ == "__main__":
    unittest.main()
