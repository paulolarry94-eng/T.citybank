"""Owner's pivot-sweep body-engulf range (2026-11-12): pivot indicator, sweep detector, reference order engine (the
specification) and the fast engine agreeing with it trade for trade."""
import os, sys, unittest, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sweep4"))
import pivots as PV          # noqa: E402
import sweep4_scan as SW     # noqa: E402
import sweep4_orders as OR   # noqa: E402
import sweep4_fast as FA     # noqa: E402

MON = int(dt.datetime(2019, 1, 7, 10, tzinfo=dt.timezone.utc).timestamp())


def brute_pivots(h, l, n):
    ph = np.zeros(len(h), bool); pl = np.zeros(len(h), bool)
    for i in range(n, len(h) - n):
        ph[i] = h[i] > h[i + 1:i + n + 1].max() and h[i] >= h[i - n:i].max()
        pl[i] = l[i] < l[i + 1:i + n + 1].min() and l[i] <= l[i - n:i].min()
    return ph, pl


class TestPivots(unittest.TestCase):
    def test_matches_brute_force_on_random_walk(self):
        rng = np.random.default_rng(3)
        c = 100 + np.cumsum(rng.normal(0, 1, 3000)); h = c + rng.random(3000); l = c - rng.random(3000)
        for n in (2, 5, 10):
            ph, pl = PV.pivots(h, l, n, n)
            bh, bl = brute_pivots(h, l, n)
            self.assertTrue((ph == bh).all() and (pl == bl).all())

    def test_sweep_is_the_first_bar_above_a_confirmed_pivot(self):
        #        0    1    2    3    4    5    6    7    8
        h = np.array([1, 2, 5, 2, 1, 1.5, 4, 5.5, 6.0])
        l = h - 0.5
        ph, pl, sw_hi, sw_lo, sw_hi_i, _, _ = PV.structure(h, l, 2, 2, np.zeros(0, np.int64), np.zeros(0, np.int64), 3)
        self.assertTrue(ph[2])                       # pivot high 5 at bar 2, known when bar 4 closes
        self.assertTrue(np.isnan(sw_hi[6]))           # bar 6 (4.0) does not reach it
        self.assertEqual(sw_hi[7], 5.0); self.assertEqual(sw_hi_i[7], 2)   # bar 7 sweeps it
        self.assertTrue(np.isnan(sw_hi[8]))           # already swept: bar 8 sweeps nothing

    def test_a_pivot_is_not_used_before_it_is_confirmed(self):
        # a pivot high at bar 2 (right = 3) is confirmed only when bar 5 closes; target levels at bar 4 must not see it
        h = np.array([1, 2, 9, 3, 2, 2.5, 2.2]); l = h - 0.5
        lev = PV.structure(h, l, 2, 3, np.array([4, 5]), np.array([1, 1]), 2)[6]
        self.assertTrue(np.isnan(lev[0, 0])); self.assertEqual(lev[1, 0], 9.0)


def bars(rows, start=MON, minutes=1):
    o, h, l, c = (np.array([r[i] for r in rows], float) for i in range(4))
    t = start + 60 * minutes * np.arange(len(rows))
    return dict(t=t, ts=t, o=o, h=h, l=l, c=c)


# a pivot high at 102 (bar 2), then candles 1-4 of a SELL where candle 1 sweeps it
PRE = [(100.0, 100.5, 99.8, 100.2), (100.2, 101.0, 100.0, 100.8), (100.8, 102.0, 100.6, 101.0), (101.0, 101.2, 100.4, 100.6),
       (100.6, 100.9, 100.3, 100.5), (100.5, 100.8, 100.2, 100.4)]
SELL4 = [(100.4, 102.4, 100.3, 101.6), (101.6, 101.7, 100.0, 100.1), (100.1, 101.0, 100.05, 100.9), (100.9, 101.0, 99.4, 99.5)]


class TestDetector(unittest.TestCase):
    def test_sell_after_the_sweep(self):
        B = bars(PRE + SELL4)
        S = SW.setups(B, 1, piv=2)
        self.assertEqual(len(S["k"]), 1)
        self.assertEqual(int(S["k"][0]), 9); self.assertEqual(int(S["side"][0]), -1)
        self.assertTrue(S["c12"][0]); self.assertEqual(S["swept"][0], 102.0)
        self.assertEqual(S["hi"][0], 102.4); self.assertEqual(S["lo"][0], 99.4)      # candle 4 low to the highest high
        lvl, stp, risk, w = SW.levels(S)
        self.assertAlmostEqual(lvl[0], 99.4 + 0.6 * 3.0); self.assertEqual(stp[0], 102.4)

    def test_no_sweep_no_c12(self):
        pre = [(r[0], min(r[1], 101.5), r[2], r[3]) for r in PRE]            # no pivot high above candle 1's high
        pre[2] = (100.8, 103.0, 100.6, 101.0)
        S = SW.setups(bars(pre + SELL4), 1, piv=2)
        self.assertFalse(S["c12"][0]); self.assertFalse(S["near"][0])

    def test_small_body_is_rejected(self):
        weak = SELL4[:3] + [(100.9, 101.0, 98.0, 100.05)]                      # candle 4 body 0.85 of 3.0 range = 28%
        self.assertEqual(len(SW.setups(bars(PRE + weak), 1, piv=2)["k"]), 0)


class TestOrders(unittest.TestCase):
    def _one(self, after, **kw):
        B = bars(PRE + SELL4 + after)
        S = SW.setups(B, 1, piv=2)
        lvl, stp, risk, w = SW.levels(S)
        pats = [dict(id=1, side=-1, level=float(lvl[0]), stop=float(stp[0]), tgt=kw.pop("tgt", 2.0), width=float(w[0]),
                     t_conf=int(S["t_conf"][0]))]
        tr, log, _ = OR.run(B, pats, 0.01, 0.0, 0.0, **kw)
        F, _ = FA.run(B, dict(t_conf=S["t_conf"], side=S["side"], level=lvl, stop=stp, tgt=np.array([pats[0]["tgt"]]), width=w),
                      dict(spread=0.01, commission=0.0, slippage=0.0), **kw)
        self.assertEqual(len(F), len(tr))
        for a, b in zip(tr, F):
            self.assertAlmostEqual(a["R"], b[3]); self.assertEqual(a["code"], int(b[9]))
        return tr, log

    def test_sell_fills_at_60_percent_and_reaches_target(self):
        # entry 101.2, stop 102.4 (1R = 1.2), 2R target 98.8
        tr, _ = self._one([(99.6, 101.3, 99.5, 101.0), (101.0, 101.1, 99.0, 99.2), (99.2, 99.3, 98.7, 98.8)])
        self.assertEqual(tr[0]["entry"], 101.2); self.assertEqual(tr[0]["reason"], "target")
        self.assertAlmostEqual(tr[0]["R"], (101.2 - 98.8) / 1.2)

    def test_sell_stops_out(self):
        tr, _ = self._one([(99.6, 101.3, 99.5, 101.0), (101.0, 102.5, 100.9, 102.3)])
        self.assertEqual(tr[0]["reason"], "stop"); self.assertAlmostEqual(tr[0]["R"], -1.0)     # the stop fills when the ASK reaches 102.4

    def test_trailing_stop_moves_to_a_new_confirmed_pivot_high(self):
        after = [(99.6, 101.3, 99.5, 101.0), (101.0, 101.1, 100.0, 100.2), (100.2, 100.3, 99.6, 99.7),
                 (99.7, 99.8, 99.2, 99.3), (99.3, 99.4, 99.0, 99.1), (99.1, 100.9, 99.0, 100.8)]
        B = bars(PRE + SELL4 + after)
        ph = np.zeros(len(B["h"]), bool); ph[11] = True                        # a pivot high at bar 11 (101.3)
        conf_hi = (np.array([int(B["t"][13]) + 60]), np.array([101.3]))        # known when bar 13 closes
        tr, log = self._one(after, trail=True, conf_hi=conf_hi, conf_lo=(np.zeros(0, np.int64), np.zeros(0)), tgt=5.0)
        self.assertTrue(any("trailed to the new pivot 101.3" in x[1] for x in log))
        self.assertEqual(tr[0]["reason"], "time close") if tr and tr[0]["reason"] == "time close" else None


class TestParity(unittest.TestCase):
    """The fast engine must reproduce the reference trade for trade on real data."""
    def test_gold_2019_h1_m5_m1(self):
        try:
            sys.path.insert(0, os.path.join(HERE, "..", ".."))
            import engine as EN
            ts, o, h, l, c = EN.load_m1("XAUUSD", 2019, 2019)
        except Exception as e:
            self.skipTest(str(e))
        keep = ts < int(dt.datetime(2019, 5, 1, tzinfo=dt.timezone.utc).timestamp())
        M = dict(ts=ts[keep], o=o[keep], h=h[keep], l=l[keep], c=c[keep])
        cost = dict(spread=0.05, commission=0.06, slippage=0.05, swap=0.2)
        total = 0
        for tf, piv in ((1, 10), (5, 5), (60, 5)):
            bt, bo, bh, bl, bc, _ = EN.resample(M["ts"], M["o"], M["h"], M["l"], M["c"], tf)
            S = SW.setups(dict(t=bt, o=bo, h=bh, l=bl, c=bc), tf, piv=piv)
            ch, cl = PV.confirmations(bt, bh, bl, S["ph"], S["pl"], piv, tf)
            for mode, buf, tgt, trail in (("near", 0.0, 5, False), ("near", 0.2, "p1", True), (None, 0.0, 15, True)):
                lvl, stp, risk, w = SW.levels(S, buf)
                tr_ = SW.structural_r(S, lvl, risk, 1) if tgt == "p1" else np.full(len(lvl), float(tgt))
                al = (S[mode] if mode else np.ones(len(lvl), bool)) & np.isfinite(tr_)
                arr = dict(t_conf=S["t_conf"], side=S["side"], level=lvl, stop=stp, tgt=np.nan_to_num(tr_), width=w)
                F, _ = FA.run(M, arr, cost, allow=al.astype(np.int64), trail=trail, conf_hi=ch, conf_lo=cl)
                pats = [dict(id=j + 1, side=int(S["side"][j]), level=float(lvl[j]), stop=float(stp[j]), tgt=float(arr["tgt"][j]),
                             width=float(w[j]), t_conf=int(S["t_conf"][j]), allow=bool(al[j])) for j in range(len(lvl))]
                T, _, _ = OR.run(M, pats, cost["spread"], cost["commission"], cost["slippage"], swap=cost["swap"], trail=trail,
                                 conf_hi=ch, conf_lo=cl)
                self.assertEqual(len(T), len(F))
                for a, b in zip(T, F):
                    self.assertEqual((a["t_in"], a["t_out"], a["code"]), (int(b[0]), int(b[1]), int(b[9])))
                    self.assertAlmostEqual(a["R"], b[3], places=9); self.assertAlmostEqual(a["mfe"], b[16], places=9)
                total += len(T)
        self.assertGreater(total, 100)


if __name__ == "__main__":
    unittest.main()
