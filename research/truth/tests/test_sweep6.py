"""Deep M1 study engine (research/sweep6): frictionless per-setup outcomes for every payout structure, breakeven at 75% of
the journey, TP2 at the fill, pessimistic vs optimistic same-minute ordering, and agreement with the plain-Python spec."""
import os, sys, unittest, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sweep6"))
import sweep6_scan as SC       # noqa: E402
import sweep6_outcomes as OC   # noqa: E402

MON = int(dt.datetime(2019, 1, 7, 10, tzinfo=dt.timezone.utc).timestamp())
Q = {n: i for i, n in enumerate(OC.NAMES)}


def case(bars, levels, level=101.2, stop=101.6, side=-1, life=30):
    o, h, l, c = (np.array([b[i] for b in bars], float) for i in range(4))
    t = MON + 60 * np.arange(len(bars))
    M1 = dict(ts=t, o=o, h=h, l=l, c=c)
    LL = np.tile(np.array(levels + [np.nan] * (3 - len(levels)), float), (len(bars), 1))
    L = dict(bt=t, LH=np.full_like(LL, np.nan), LL=LL, minutes=1)
    O = dict(t_conf=np.array([t[1]]), side=np.array([side]), level=np.array([level]), stop=np.array([stop]),
             t_exp=np.array([t[1] + 60 * life]))
    return M1, O, L


class TestOutcomes(unittest.TestCase):
    def test_fixed_targets_and_tp2(self):
        # sell limit 101.2, stop 101.6 (1R = 0.4); fill, then price falls to 99.6 (4R) and stops there
        bars = [(101.0, 101.1, 100.9, 101.0)] * 2 + [(101.0, 101.25, 100.95, 101.0), (101.0, 101.0, 100.0, 100.1),
                (100.1, 100.15, 99.6, 99.7)] + [(99.7, 99.8, 99.65, 99.7)] * 3
        M1, O, L = case(bars, [100.4, 99.9])
        out = OC.run(M1, O, L)
        R = out["R"][0]
        self.assertAlmostEqual(R[Q["3R"]], 3.0); self.assertAlmostEqual(R[Q["4R"]], 4.0)
        self.assertTrue(bool(np.isnan(R[Q["5R"]])))                            # still open when the data ends: unresolved (nan)
        self.assertAlmostEqual(R[Q["TP1"]], 2.0); self.assertAlmostEqual(R[Q["TP2"]], (101.2 - 99.9) / 0.4)
        self.assertAlmostEqual(R[Q["P60"]], 0.6 * 2.0 + 0.4 * (101.2 - 99.9) / 0.4)

    def test_breakeven_at_75_percent_of_the_journey(self):
        # 4R target = 99.6; 75% of the journey = 3R = 100.0: reached, then price returns to the entry -> 0R; without BE: -1R
        bars = [(101.0, 101.1, 100.9, 101.0)] * 2 + [(101.0, 101.25, 100.95, 101.0), (101.0, 101.0, 99.95, 100.0),
                (100.0, 101.3, 100.0, 101.25), (101.25, 101.7, 101.2, 101.65)]
        M1, O, L = case(bars, [100.4, 99.9])
        R = OC.run(M1, O, L)["R"][0]
        self.assertAlmostEqual(R[Q["4R-BE75"]], 0.0); self.assertAlmostEqual(R[Q["4R"]], -1.0)
        self.assertAlmostEqual(R[Q["3R"]], 3.0)

    def test_same_minute_stop_and_target_is_pessimistic_unless_optimistic(self):
        bars = [(101.0, 101.1, 100.9, 101.0)] * 2 + [(101.0, 101.25, 100.95, 101.0), (101.0, 101.7, 100.7, 101.0)]
        M1, O, L = case(bars, [100.4, 99.9])
        self.assertAlmostEqual(OC.run(M1, O, L)["R"][0][Q["1R"]], -1.0)
        self.assertAlmostEqual(OC.run(M1, O, L, optimistic=True)["R"][0][Q["1R"]], 1.0)

    def test_order_cancelled_when_life_ends(self):
        bars = [(101.0, 101.1, 100.9, 101.0)] * 40
        M1, O, L = case(bars, [100.4, 99.9], life=5)
        self.assertEqual(int(OC.run(M1, O, L)["status"][0]), 1)


class TestSpec(unittest.TestCase):
    def test_fast_matches_reference_on_real_data(self):
        try:
            sys.path.insert(0, os.path.join(HERE, "..", ".."))
            import engine as EN
            ts, o, h, l, c = EN.load_m1("GBPUSD", 2018, 2018)
        except Exception as e:
            self.skipTest(str(e))
        keep = ts < int(dt.datetime(2018, 4, 1, tzinfo=dt.timezone.utc).timestamp())
        ts, o, h, l, c = ts[keep], o[keep], h[keep], l[keep], c[keep]
        bt, bo, bh, bl, bc, _ = EN.resample(ts, o, h, l, c, 1)
        B = dict(t=bt, o=bo, h=bh, l=bl, c=bc, atr=np.nan_to_num(EN.atr_sma(bh, bl, bc, 14)))
        S, L = SC.setups(B, 1, "GBPUSD"); O = SC.orders(S, L, 60)
        M1 = dict(ts=ts, o=o, h=h, l=l, c=c)
        for opt in (False, True):
            out = OC.run(M1, O, L, optimistic=opt)
            idx = np.flatnonzero(out["status"] >= 1)[::7][:150]
            for p in idx:
                for q in range(len(OC.NAMES)):
                    st, r, w, _ = OC.reference(M1, O, L, int(p), q, optimistic=opt)
                    a = out["R"][p, q]
                    self.assertEqual(r is None, bool(np.isnan(a)))
                    if r is not None:
                        self.assertAlmostEqual(r, float(a), places=4); self.assertEqual(w, int(out["why"][p, q]))


if __name__ == "__main__":
    unittest.main()


class TestFixedModePortfolioEngine(unittest.TestCase):
    """The v2 portfolio engines' fixed-R mode (used by sweep6_scanner_v1): fast = reference, with and without breakeven."""
    def test_fixed_mode_parity_on_real_data(self):
        try:
            sys.path.insert(0, os.path.join(HERE, "..", ".."))
            sys.path.insert(0, os.path.join(HERE, "..", "..", "sweep5"))
            import engine as EN
            import sweep5_orders as OR5
            import sweep5_fast as FA5
            ts, o, h, l, c = EN.load_m1("EURUSD", 2019, 2019)
        except Exception as e:
            self.skipTest(str(e))
        keep = ts < int(dt.datetime(2019, 3, 1, tzinfo=dt.timezone.utc).timestamp())
        ts, o, h, l, c = ts[keep], o[keep], h[keep], l[keep], c[keep]
        M = dict(ts=ts, o=o, h=h, l=l, c=c)
        n = 0
        for tf in (1, 5):
            bt, bo, bh, bl, bc, _ = EN.resample(ts, o, h, l, c, tf)
            S, L = SC.setups(dict(t=bt, o=bo, h=bh, l=bl, c=bc, atr=np.nan_to_num(EN.atr_sma(bh, bl, bc, 14))), tf, "EURUSD")
            O = dict(t_conf=S["t_conf"], side=S["side"], level=S["level"], stop=S["stop"], width=S["hi"] - S["lo"],
                     t_exp=S["t_conf"] + 60 * tf * 60)
            allow = (S["hour"] >= 12) & (S["hour"] < 16)
            for tgt, be in ((20.0, 0.0), (5.0, 0.75), (3.0, 0.0)):
                cost = dict(spread=1e-5, commission=2.5e-5, slippage=2e-5, swap=1e-5)
                T = OR5.run(M, O, L, cost["spread"], cost["commission"], cost["slippage"], cost["swap"], "fixed", allow=allow, tgt_r=tgt, be_frac=be)
                F = FA5.run(M, O, L, cost, "fixed", allow=allow, tgt_r=tgt, be_frac=be)
                self.assertEqual(len(T), len(F))
                for a, b in zip(T, F):
                    self.assertEqual((a["t_in"], a["t_out"], a["why"]), (int(b[0]), int(b[1]), int(b[9])))
                    self.assertAlmostEqual(a["R"], b[3], places=9)
                n += len(T)
        self.assertGreater(n, 50)
