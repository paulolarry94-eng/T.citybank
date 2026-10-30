"""Unit tests for North Star pattern detection and execution logic.
Run: cd research/northstar && python3 -m unittest discover -s tests -v
"""
import os, sys, unittest
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import core, patterns as P
import risk

DAY = 86400
MON = 4 * DAY          # 1970-01-05 is a Monday (epoch day 4)


def bars(o, h, l, c, t0=MON + 9 * 3600, step=60, atr=1.0):
    """Degenerate bar set: one minute per bar, so bar index == minute index."""
    n = len(o)
    B = dict(o=np.asarray(o, float), h=np.asarray(h, float), l=np.asarray(l, float), c=np.asarray(c, float),
             t=(t0 + step * np.arange(n)).astype(np.int64), minutes=step // 60,
             first=np.arange(n, dtype=np.int64), nxt=np.arange(1, n + 1, dtype=np.int64), atr=np.full(n, atr))
    return B


class FakeM:
    def __init__(self, B, cost=0.01, swap=0.0):
        self.o, self.h, self.l = B["o"], B["h"], B["l"]
        self.ts = B["t"]; self.cost = cost; self.swap = swap; self.gaps = np.zeros(0, np.int64)

    def bias_at(self, t):
        return np.ones(len(t), np.int64)


def zigzag(points, per=4, seed=0):
    """Close path through the given turning points; bars with small wicks."""
    c = []
    for a, b in zip(points[:-1], points[1:]):
        c += list(np.linspace(a, b, per, endpoint=False))
    c.append(points[-1]); c = np.array(c)
    o = c.copy()                                  # doji bars: highs/lows follow closes, so peaks are strict
    h = c + 0.05; l = c - 0.05
    return o, h, l, c


class TestFVG(unittest.TestCase):
    def test_bullish_and_bearish_gap_edges(self):
        B = bars(o=[9, 10, 12, 12, 11, 9], h=[10, 12, 13, 12.5, 11, 9.5], l=[9, 10, 11, 11.5, 9, 7], c=[10, 12, 12.5, 12, 9.2, 7.5], atr=1.0)
        ev = P.fvg_events(B, 0.3)
        self.assertIn((2, 1, 10.0, 11.0, 9.0), ev)             # bull: low[2]=11 > high[0]=10
        bears = [e for e in ev if e[1] == -1]
        self.assertTrue(any(e[0] == 5 and e[2] == 9.5 and e[3] == 11.5 for e in bears))   # high[5]=9.5 < low[3]=11.5

    def test_minimum_width_rejects_narrow_gaps(self):
        B = bars(o=[9, 10, 10.2], h=[10, 10.5, 10.6], l=[9, 10, 10.2], c=[10, 10.4, 10.5], atr=1.0)
        self.assertEqual([e for e in P.fvg_events(B, 0.3) if e[1] == 1], [])
        self.assertEqual(len([e for e in P.fvg_events(B, 0.1) if e[1] == 1]), 1)

    def test_model_b_needs_pullback_then_confirmation(self):
        # gap [10, 11] at bar 2; bar 3 trades into it bullish (no pullback); bar 4 bearish with low in gap (pullback);
        # bar 5 closes above bar 4's high -> trigger at bar 5
        o = [9, 10, 12, 12, 11.8, 11.0]; c = [10, 12, 12.5, 11.9, 11.1, 12.2]
        h = [10, 12, 13, 12.2, 11.9, 12.3]; l = [9, 10, 11, 10.8, 10.5, 10.9]
        B = bars(o, h, l, c)
        self.assertEqual(P._fvg_b_scan(B["o"], B["h"], B["l"], B["c"], 2, 1, 10.0, 11.0, 10), 5)

    def test_model_b_dies_on_close_beyond_far_edge(self):
        o = [9, 10, 12, 12, 10.5]; c = [10, 12, 12.5, 11.0, 9.5]
        h = [10, 12, 13, 12.1, 10.6]; l = [9, 10, 11, 10.8, 9.4]
        B = bars(o, h, l, c)
        self.assertEqual(P._fvg_b_scan(B["o"], B["h"], B["l"], B["c"], 2, 1, 10.0, 11.0, 10), -1)


class TestSupplyDemand(unittest.TestCase):
    def test_rbr_detected_with_base_levels(self):
        # leg-in up (body 1.5), base of 2 small candles, leg-out up closing 0.3 above the base high
        o = [10, 10.0, 11.6, 11.5, 11.7]; c = [10, 11.5, 11.5, 11.6, 13.4]
        h = [10.1, 11.6, 11.8, 11.9, 13.5]; l = [9.9, 9.9, 11.4, 11.4, 11.6]
        B = bars(o, h, l, c, atr=1.0)
        ev = P.sd_events(B, 2, 1.0)
        self.assertIn((4, "RBR", 11.9, 11.4), ev)

    def test_dbr_reversal(self):
        o = [12, 12.0, 10.4, 10.5, 10.3]; c = [12, 10.5, 10.5, 10.4, 12.4]
        h = [12.1, 12.1, 10.6, 10.6, 12.5]; l = [11.9, 10.4, 10.3, 10.2, 10.2]
        ev = P.sd_events(bars(o, h, l, c), 2, 1.0)
        self.assertIn((4, "DBR", 10.6, 10.2), ev)

    def test_leg_out_needs_a_close_beyond_the_base(self):
        o = [10, 10.0, 11.6, 11.5, 11.7]; c = [10, 11.5, 11.5, 11.6, 11.85]    # close inside base: no pattern
        h = [10.1, 11.6, 11.8, 11.9, 13.5]; l = [9.9, 9.9, 11.4, 11.4, 11.6]
        self.assertEqual([e for e in P.sd_events(bars(o, h, l, c), 2, 0.1) if e[1] == "RBR"], [])


class TestQuasimodo(unittest.TestCase):
    PTS = [10, 14, 11, 16, 12, 15, 9, 13, 11.5, 15.5, 15.5]          # ... L1=12? see test

    def test_bullish_qm_armed_after_h2_and_triggers_on_break(self):
        # pivots (k=2): H 16, L 12 (L1), H 15 (H1), L 9 (L2 < L1), H 13 (H2 < H1), then a rally above 13
        o, h, l, c = zigzag([14, 16, 12, 15, 9, 13, 11.5, 15.5, 15.6], per=4)
        B = bars(o, h, l, c, atr=1.0)
        ev = P.qm_events(B, 2, 0.25)
        bull = [e for e in ev if e[1] == 1]
        self.assertTrue(bull, "bullish QM not detected")
        t, side, L1, L2, H2, H1, sid = bull[0]
        self.assertAlmostEqual(L1, 12 - 0.05, places=6); self.assertAlmostEqual(L2, 9 - 0.05, places=6)
        self.assertGreaterEqual(t, int(np.argmax(np.isclose(B["c"], 13.0))) + 2, "armed before H2 was confirmed")
        self.assertLess(H2, H1)
        trig = P.qm_triggers(B, 2, 0.25, "near")
        self.assertTrue(any(u > t and B["c"][u] > H2 for u, s, q, hd in trig if s == 1))

    def test_prefix_invariance_no_lookahead(self):
        rng = np.random.default_rng(5)
        c = np.cumsum(rng.normal(0, 1, 600)) + 100
        o = np.r_[c[0], c[:-1]]; h = np.maximum(o, c) + rng.uniform(0, 0.5, 600); l = np.minimum(o, c) - rng.uniform(0, 0.5, 600)
        full = bars(o, h, l, c)
        for T in (150, 300, 450):
            pre = bars(o[:T], h[:T], l[:T], c[:T])
            a = [e[:6] for e in P.qm_events(full, 3, 0.25) if e[0] < T - 1]
            b = [e[:6] for e in P.qm_events(pre, 3, 0.25) if e[0] < T - 1]
            self.assertEqual(a, b, f"QM arming changed when future bars were added (T={T})")
            self.assertEqual([e for e in P.fvg_events(full, 0.1) if e[0] < T], P.fvg_events(pre, 0.1))
            self.assertEqual([e for e in P.sd_events(full, 2, 1.0) if e[0] < T], P.sd_events(pre, 2, 1.0))
            sf = P.swing_levels(full, 3); sp = P.swing_levels(pre, 3)
            np.testing.assert_array_equal(sf[0][:T], sp[0]); np.testing.assert_array_equal(sf[1][:T], sp[1])


class TestExecution(unittest.TestCase):
    def test_limit_fill_needs_trade_through_and_respects_block(self):
        o = [12, 11.5, 11.2, 11.0]; h = [12, 11.6, 11.3, 11.1]; l = [11.6, 11.0, 10.98, 10.5]; c = [11.6, 11.2, 11.0, 10.8]
        B = bars(o, h, l, c)
        k, px, u = core.limit_scan(B["o"], B["h"], B["l"], B["t"], B["first"], B["nxt"], B["c"], 1, 4, 1, 11.0, 9.0, 0.01, 0.001, 0, 0)
        self.assertEqual(k, 2)                       # long limit is an ask price: bar 1 (ask low 11.01) no; bar 2 (ask low 10.99) fills
        self.assertAlmostEqual(px, 11.0)
        Bb = bars(o, h, l, c, t0=MON + 21 * 3600)    # 21:00 UTC: inside the rollover block
        k2, _, _ = core.limit_scan(Bb["o"], Bb["h"], Bb["l"], Bb["t"], Bb["first"], Bb["nxt"], Bb["c"], 1, 4, 1, 11.0, 9.0, 0.01, 0.001,
                                   core.BLOCK[0], core.BLOCK[1])
        self.assertEqual(k2, -1)

    def test_limit_cancelled_by_close_beyond(self):
        o = [12, 11.5, 9.5]; h = [12, 11.6, 9.6]; l = [11.6, 11.4, 9.0]; c = [11.6, 11.45, 9.2]
        B = bars(o, h, l, c)
        k, _, _ = core.limit_scan(B["o"], B["h"], B["l"], B["t"], B["first"], B["nxt"], B["c"], 1, 3, 1, 11.0, 11.5, 0.01, 0.001, 0, 0)
        self.assertEqual(k, -1)                      # bar 1 closes below the cancel level before any fill

    def _book(self, B, k0, side, entry, stop, tgt, cost=0.01, swap=0.0):
        A = lambda x, t=np.float64: np.asarray(x, t)
        return core.run_book(B["o"], B["h"], B["l"], B["t"], B["nxt"], B["h"], B["l"], B["atr"], A(k0, np.int64), A(side, np.int64),
                             A(entry), A(stop), A([k for k in k0], np.int64), A([max(k - 1, 0) for k in k0], np.int64), A([10.0] * len(k0)),
                             cost, tgt, 0.0, 50, np.zeros(0, np.int64), swap, 2 ** 62, 0, 0, 0)

    def test_same_minute_stop_and_target_is_a_loss(self):
        o = [10, 10, 10] + [10] * 5; h = [10, 10, 13] + [10] * 5; l = [10, 10, 8] + [10] * 5; c = [10] * 8
        B = bars(o, h, l, c, atr=5.0)
        r = self._book(B, [1], [1], [-1.0], [9.01], 2.0)
        self.assertAlmostEqual(r[0, 3], -1.0, places=9)

    def test_gapped_stop_fills_at_worse_open(self):
        o = [10, 10, 8.5] + [8.5] * 5; h = [10, 10.2, 8.6] + [8.6] * 5; l = [10, 9.9, 8.4] + [8.4] * 5; c = [10, 10, 8.5] + [8.5] * 5
        B = bars(o, h, l, c, atr=5.0)
        r = self._book(B, [1], [1], [-1.0], [9.0], 0.0)
        self.assertAlmostEqual(r[0, 3], (8.5 - 10.01) / (10.01 - 9.0), places=9)

    def test_no_duplicate_entries_while_in_a_trade(self):
        n = 20
        B = bars([10] * n, [10.05] * n, [9.95] * n, [10] * n, atr=5.0)
        r = self._book(B, [1, 3, 5], [1, 1, 1], [-1.0, -1.0, -1.0], [9.0, 9.0, 9.0], 0.0)
        self.assertEqual(len(r), 1)

    def test_financing_nights_with_wednesday_triple(self):
        tue = MON + DAY
        self.assertEqual(core.nights_held(tue + 21 * 3600, tue + 2 * DAY + 23 * 3600), 1 + 3 + 1)
        self.assertEqual(core.nights_held(tue + 10 * 3600, tue + 20 * 3600), 0)

    def test_market_entry_blocked_in_rollover_window(self):
        B = bars([10] * 8, [10.05] * 8, [9.95] * 8, [10] * 8, t0=MON + 21 * 3600, atr=5.0)
        A = lambda x, t=np.float64: np.asarray(x, t)
        r = core.run_book(B["o"], B["h"], B["l"], B["t"], B["nxt"], B["h"], B["l"], B["atr"], A([1], np.int64), A([1], np.int64),
                          A([-1.0]), A([9.0]), A([1], np.int64), A([0], np.int64), A([10.0]), 0.01, 0.0, 0.0, 50,
                          np.zeros(0, np.int64), 0.0, 2 ** 62, core.BLOCK[0], core.BLOCK[1], 0)
        self.assertEqual(len(r), 0)



def trades(r, t0=1600041600, gap=86400, hold=3600, inst=None, side=None, legs=None, w=None, same_time=False):
    n = len(r); t = np.full(n, t0, np.int64) if same_time else t0 + np.arange(n, dtype=np.int64) * gap
    return dict(t_in=t, t_out=t + hold, side=np.asarray(side if side is not None else np.ones(n), np.int64),
                r=np.asarray(r, float), leg=np.asarray(legs if legs is not None else np.zeros(n), np.int64),
                inst=np.asarray(inst if inst is not None else np.zeros(n), np.int64), usd=np.ones(n, np.int64),
                w=np.asarray(w if w is not None else np.ones(n), float))


class TestRiskManager(unittest.TestCase):
    def test_fixed_fractional_compounds_on_current_equity(self):
        s = risk.simulate(trades([1.0] * 10 + [-1.0] * 5), 0.01, "FF")
        self.assertAlmostEqual(s["final"], 1.01 ** 10 * 0.99 ** 5, places=12)

    def test_leg_weight_scales_risk(self):
        s = risk.simulate(trades([1.0], w=[0.5]), 0.02, "FF")
        self.assertAlmostEqual(s["final"], 1.01, places=12)

    def test_same_instrument_same_direction_cap(self):
        s = risk.simulate(trades([1.0] * 6, same_time=True, legs=range(6)), 0.01, "FF+CAPS")
        self.assertEqual(s["taken"], 3)                      # 3% same instrument + direction

    def test_total_open_risk_cap(self):
        T = trades([1.0] * 12, same_time=True, legs=range(12), inst=[i % 6 for i in range(12)], side=[1, -1] * 6)
        T["usd"] = np.zeros(12, np.int64)                    # isolate the 10% total cap from the USD cap
        self.assertEqual(risk.simulate(T, 0.01, "FF+CAPS")["taken"], 10)

    def test_net_usd_direction_cap(self):
        T = trades([1.0] * 8, same_time=True, legs=range(8), inst=[0, 1, 2, 3, 0, 1, 2, 3])
        T["usd"] = np.ones(8, np.int64)                      # all longs USD-short: 6% net cap -> 6 trades at 1%
        self.assertEqual(risk.simulate(T, 0.01, "FF+CAPS")["taken"], 6)

    def test_per_trade_cap(self):
        s = risk.simulate(trades([1.0]), 0.05, "FF+CAPS")
        self.assertAlmostEqual(s["final"], 1.02, places=12)

    def test_amber_halves_risk_after_ten_percent_drawdown(self):
        r = [-1.0] * 6 + [1.0]                                 # 6 x 2% losses 3 days apart -> DD 11.4%, next trade at 1%
        s = risk.simulate(trades(r, gap=3 * 86400, legs=range(7)), 0.02, "RAG")
        self.assertAlmostEqual(s["final"], 0.98 ** 6 * 1.01, places=12)

    def test_amber_on_five_day_loss(self):
        r = [-1.0] * 6 + [1.0]                                 # daily 2% losses: after 4 the 5-day loss is 7.8% -> AMBER
        s = risk.simulate(trades(r, legs=range(7)), 0.02, "RAG")
        self.assertAlmostEqual(s["final"], 0.98 ** 4 * 0.99 ** 2 * 1.01, places=12)

    def test_red_pauses_entries_and_rearms_after_further_loss(self):
        s = risk.simulate(trades([-1.0] * 40, legs=range(40)), 0.02, "RAG")
        # 4 losses at 2%, then 1% (AMBER) until DD >= 20% at trade 19 -> RED, 14-day pause, resume in AMBER,
        # RED again only after a further 5% loss from the equity at acknowledgement (amendment 2)
        self.assertEqual(s["red_episodes"], 2)
        self.assertGreater(s["skipped"], 14)

    def test_ff_red_never_changes_size_for_amber(self):
        r = [-1.0] * 6 + [1.0]
        s = risk.simulate(trades(r, legs=range(7)), 0.02, "FF+RED")
        self.assertAlmostEqual(s["final"], 0.98 ** 6 * 1.02, places=12)
        self.assertGreater(s["amber_entries"], 0)           # shadow AMBER recorded

    def test_day_loss_red(self):
        T = trades([-1.0] * 4 + [1.0] * 3, gap=1800, hold=600, legs=range(7), inst=[0, 1, 2, 3, 0, 1, 2])
        s = risk.simulate(T, 0.02, "FF+RED")                  # 4 x 2% in one day = 7.8% >= 6% -> RED
        self.assertEqual(s["red_episodes"], 1)
        self.assertEqual(s["taken"], 4)


if __name__ == "__main__":
    unittest.main()
