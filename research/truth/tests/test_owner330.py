"""Tests of the owner's 3:30 EMA retest scanner on hand-built price paths:
    python3 -m unittest research/truth/tests/test_owner330.py -v"""
import os, sys, types, unittest, datetime as dt, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "..", "northstar"))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import engine as E

_spec = importlib.util.spec_from_file_location("o330", os.path.join(HERE, "..", "strategies", "owner330_ema_retest_v1.py"))
S = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S)

DAY = dt.date(2024, 1, 10)                          # a Wednesday; not an NFP / CPI / FOMC day; New York on winter time
T0 = int(dt.datetime(DAY.year, DAY.month, DAY.day, 8, 0, tzinfo=dt.timezone.utc).timestamp())


def m1_from_m5(bars, t0=T0):
    """M5 bars (o, h, l, c) -> five M1 bars each that resample back to the same M5 bar."""
    ts, o, h, l, c = [], [], [], [], []
    for k, (O, Hh, Ll, C) in enumerate(bars):
        base = t0 + k * 300
        path = [(O, O, O, O), (O, Hh, O, Hh), (Hh, Hh, Ll, Ll), (Ll, Ll, Ll, Ll), (Ll, max(Ll, C), min(Ll, C), C)]
        for m, (a, b, d, e) in enumerate(path):
            ts.append(base + 60 * m); o.append(a); h.append(b); l.append(d); c.append(e)
    return (np.array(ts, np.int64), np.array(o, float), np.array(h, float), np.array(l, float), np.array(c, float))


def market(bars, cost=0.01, t0=T0):
    ts, o, h, l, c = m1_from_m5(bars, t0)
    M = types.SimpleNamespace(sym="TEST%d" % len(bars), ts=ts, o=o, h=h, l=l, gaps=E.data_gaps(ts), cost=cost,
                              G=types.SimpleNamespace(c=c))
    bt, bo, bh, bl, bc, nxt = E.resample(ts, o, h, l, c, 5, 0)
    B = dict(t=bt.astype(np.int64), o=bo, h=bh, l=bl, c=bc, nxt=nxt.astype(np.int64), minutes=5)
    return M, B


def base_day(after):
    """08:00-14:30 UTC flat at 100, the 14:30 M30 anchor opens 100.2 (above the EMA) and closes 99.5 (below), then `after`."""
    flat = [(100.0, 100.05, 99.95, 100.0)] * 78                       # 6.5 hours of M5 candles
    anchor = [(100.2, 100.3, 100.0, 100.0), (100.0, 100.0, 99.8, 99.8), (99.8, 99.8, 99.7, 99.7),
              (99.7, 99.7, 99.6, 99.6), (99.6, 99.6, 99.55, 99.55), (99.55, 99.6, 99.4, 99.5)]
    return flat + anchor + after


RALLY = (99.5, 100.05, 99.5, 100.0)                                   # 15:00 closes back above the M5 EMA
REF = (99.75, 99.75, 99.55, 99.6)                                     # 15:05 crosses back below, inside the range: reference
FALL = [(99.6, 99.6, 99.5, 99.5), (99.5, 99.5, 99.3, 99.3), (99.3, 99.3, 99.1, 99.1), (99.1, 99.1, 99.0, 99.0)]
QUIET = [(99.5, 99.52, 99.48, 99.5)] * 80                             # drifts sideways until after 21:00 UTC


def p(entry="A", target=2, be=0, anchor="wat1530"):
    return dict(tf="M5", anchor=anchor, entry=entry, target=target, be=be)


def run(bars, **kw):
    S._CACHE.clear()
    M, B = market(bars)
    q = p(**kw)
    return S.setups(B, q, M), S.detail(M, B, q)


class TestSetups(unittest.TestCase):
    def test_sell_day_reference(self):
        st, tr = run(base_day([RALLY, REF] + FALL + QUIET))
        self.assertEqual(len(st["j"]), 1)
        self.assertEqual(int(st["side"][0]), -1)
        self.assertAlmostEqual(st["rhi"][0], 99.75); self.assertAlmostEqual(st["rlo"][0], 99.55)
        self.assertAlmostEqual(st["H"][0], 100.3); self.assertAlmostEqual(st["L"][0], 99.4)
        self.assertFalse(bool(st["disp"][0]))

    def test_anchor_must_cross(self):
        bars = base_day([RALLY, REF] + FALL + QUIET)
        bars[78] = (99.9, 100.0, 99.8, 99.85)                          # the anchor now opens BELOW the EMA: no cross
        st, _ = run(bars)
        self.assertEqual(len(st["j"]), 0)

    def test_close_beyond_range_cancels(self):
        st, _ = run(base_day([(99.5, 100.5, 99.5, 100.4), REF] + FALL + QUIET))   # closes above the range high 100.3
        self.assertEqual(len(st["j"]), 0)

    def test_wick_beyond_range_does_not_cancel(self):
        st, _ = run(base_day([(99.5, 100.5, 99.5, 100.0), REF] + FALL + QUIET))   # wick to 100.5, close 100.0 inside
        self.assertEqual(len(st["j"]), 1)

    def test_news_day_skipped(self):
        S._CACHE.clear()
        nfp = dt.date(2024, 1, 5)
        t0 = int(dt.datetime(2024, 1, 5, 8, 0, tzinfo=dt.timezone.utc).timestamp())
        M, B = market(base_day([RALLY, REF] + FALL + QUIET), t0=t0)
        self.assertIn(nfp, S.NEWS)
        self.assertEqual(len(S.setups(B, p(), M)["j"]), 0)

    def test_reference_touching_the_range_counts(self):
        # crosses below the EMA and closes below the range low (99.4), but its high reaches into the range: valid
        st, _ = run(base_day([RALLY, (99.6, 99.62, 99.3, 99.35)] + FALL + QUIET))
        self.assertEqual(len(st["j"]), 1)

    def test_reference_outside_the_range_does_not_count(self):
        # first cross below happens entirely under the range (high 99.38 < low 99.4): not a reference
        bars = base_day([(99.5, 99.55, 99.3, 99.32), (99.32, 99.36, 99.2, 99.36), (99.36, 99.38, 99.1, 99.12)] + QUIET)
        st, _ = run(bars)
        self.assertEqual(len(st["j"]), 0)


class TestOrders(unittest.TestCase):
    def test_entry_a_hits_target(self):
        _, tr = run(base_day([RALLY, REF] + FALL + QUIET), entry="A", target=2)
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0, 8], 99.55)                       # sell stop at the reference low
        self.assertAlmostEqual(tr[0, 9], 99.75)                       # stop at the reference high
        self.assertEqual(int(tr[0, 12]), 2); self.assertAlmostEqual(tr[0, 3], 2.0)

    def test_entry_b_needs_a_pullback(self):
        _, tr = run(base_day([RALLY, REF] + FALL + QUIET), entry="B3")
        self.assertEqual(len(tr), 0)                                  # broke and kept falling: no pullback, no trade

    def test_entry_b_fills_on_pullback(self):
        back = [(99.6, 99.6, 99.5, 99.5), (99.5, 99.6, 99.5, 99.58), (99.58, 99.58, 99.3, 99.3),
                (99.3, 99.3, 99.1, 99.1), (99.1, 99.1, 99.0, 99.0)]
        _, tr = run(base_day([RALLY, REF] + back + QUIET), entry="B3", target=2)
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0, 8], 99.55); self.assertEqual(int(tr[0, 12]), 2)

    def test_displaced_reference_enters_at_mid(self):
        big = (100.05, 100.05, 99.55, 99.6)                           # range 0.5 vs about 0.2 before: displaced
        up = [(99.6, 99.85, 99.6, 99.8)] + FALL[1:] + [(99.0, 99.0, 98.8, 98.8)]
        st, tr = run(base_day([RALLY, big] + up + QUIET), entry="A", target=2)
        self.assertTrue(bool(st["disp"][0]))
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0, 8], 99.8)                        # sell limit at the 50% level (100.05 + 99.55) / 2

    def test_time_exit_and_no_overnight(self):
        stall = [(99.6, 99.6, 99.5, 99.5)] + QUIET
        _, tr = run(base_day([RALLY, REF] + stall), entry="A", target=4)
        self.assertEqual(len(tr), 1)
        self.assertEqual(int(tr[0, 12]), 3)                           # neither stop nor 4R: closed at 16:00 New York
        t_out = dt.datetime.fromtimestamp(int(tr[0, 1]), S.NY)
        self.assertEqual((t_out.hour, t_out.minute), (16, 0))

    def test_breakeven(self):
        path = [(99.6, 99.6, 99.3, 99.3), (99.3, 99.8, 99.3, 99.8)] + QUIET   # +1R reached, then back above the entry
        _, tr0 = run(base_day([RALLY, REF] + path), entry="A", target=3, be=0)
        _, tr1 = run(base_day([RALLY, REF] + path), entry="A", target=3, be=1)
        self.assertEqual(int(tr0[0, 12]), 1); self.assertAlmostEqual(tr0[0, 3], -1.0, places=6)
        self.assertEqual(int(tr1[0, 12]), 4); self.assertAlmostEqual(tr1[0, 3], 0.0, places=6)    # out at the entry


if __name__ == "__main__":
    unittest.main()
