"""Tests of the repo-funnel daily engine (research/repofunnel):  python3 -m unittest research/truth/tests/test_repofunnel.py -v"""
import os, sys, unittest
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
RF = os.path.join(HERE, "..", "..", "repofunnel")
for _p in (os.path.join(HERE, ".."), RF, os.path.join(HERE, "..", "..")):
    sys.path.insert(0, _p)
import protocol as P
import engine as E
import d1
import trustdan as TD
import sofus as SF


class FakeMk:
    """A d1 market built from minute arrays (synthetic or a slice of real data)."""

    def __init__(self, ts, o, h, l, c, cost=0.0, swap=0.0, sym="TEST"):
        self.ts = np.asarray(ts, np.int64); self.o = np.asarray(o, float); self.h = np.asarray(h, float)
        self.l = np.asarray(l, float); self.c = np.asarray(c, float); self.cost = cost; self.swap = swap; self.sym = sym
        self.gaps = E.data_gaps(self.ts)
        bt, bo, bh, bl, bc, nxt = E.resample(self.ts, self.o, self.h, self.l, self.c, 1440, 120)
        nxt = nxt.astype(np.int64)
        self.B = dict(t=bt.astype(np.int64), o=bo, h=bh, l=bl, c=bc, nxt=nxt, first=np.r_[0, nxt[:-1]].astype(np.int64))
        self.D = d1.merge_daily(self.B)
        self.views = {s: d1.View(self.D, s) for s in (1, -1)}


def weekday_minutes(days=12, start="2020-01-06", sunday_evening=True, price=100.0):
    """Minute stamps for weekdays (00:00-21:00 UTC) plus Sunday 22:00-24:00, flat price."""
    t0 = int(np.datetime64(start, "s").astype(np.int64)); ts = []
    for dd in range(days):
        day = t0 + dd * 86400; wd = ((day // 86400) + 3) % 7
        if wd < 5:
            ts.extend(range(day, day + 21 * 3600, 60))
        elif wd == 6 and sunday_evening:
            ts.extend(range(day + 22 * 3600, day + 24 * 3600, 60))
    ts = np.asarray(sorted(ts), np.int64)
    p = np.full(len(ts), price)
    return ts, p.copy(), p.copy() + 0.01, p.copy() - 0.01, p.copy()


class Once(d1.Rule):
    """Enter long once at merged bar u_sig with stop entry - dist; optional add / partial exit on later closes."""

    def __init__(self, u_sig, dist=1.0, side=1, add_at=None, exitw_at=None):
        self.u_sig, self.dist, self.side, self.add_at, self.exitw_at = u_sig, dist, side, add_at, exitw_at

    def entry(self, u, s):
        return dict(w=1.0) if (u == self.u_sig and s == self.side) else None

    def on_fill(self, mk, pos, u, sig):
        ev = pos.s * pos.units[0][1]
        pos.st["d"] = self.dist; pos.stop_v = ev - self.dist
        return True

    def on_close(self, mk, pos, u):
        if self.add_at is not None and u == self.add_at:
            pos.add_w = 1.0
        if self.exitw_at is not None and u == self.exitw_at:
            pos.exit_w = 1.0


class TestFillLaw(unittest.TestCase):
    def setUp(self):
        self.ts, self.o, self.h, self.l, self.c = weekday_minutes()

    def mk(self, cost=0.02):
        return FakeMk(self.ts, self.o, self.h, self.l, self.c, cost=cost)

    def test_long_pays_the_ask_and_stops_at_the_level(self):
        mk = self.mk()
        u = 2; k_in = int(mk.D["first"][u + 1])
        k_hit = k_in + 300
        self.l[k_hit] = 98.0                                    # dips through the stop (entry 100.02 - 1 = 99.02)
        mk = self.mk()
        r = d1.simulate(mk, Once(u), (1,), cut=0, warmup=0)
        self.assertEqual(len(r), 1)
        self.assertEqual(int(r[0, 0]), int(mk.ts[k_in]))
        self.assertEqual(int(r[0, 1]), int(mk.ts[k_hit]))
        self.assertAlmostEqual(r[0, 3], (99.02 - 100.02) / 1.0, places=9)    # exactly -1R (cost is inside the fill)

    def test_gap_through_the_stop_fills_at_the_worse_open(self):
        u = 2; mk = self.mk()
        k_hit = int(mk.D["first"][u + 1]) + 500
        self.o[k_hit] = 98.5; self.l[k_hit] = 98.4
        mk = self.mk()
        r = d1.simulate(mk, Once(u), (1,), cut=0, warmup=0)
        self.assertAlmostEqual(r[0, 3], (98.5 - 100.02) / 1.0, places=9)

    def test_market_order_due_in_the_rollover_block_waits_until_23_utc(self):
        mk = self.mk()
        fri = [i for i in range(mk.D["n"]) if mk.D["wd"][i] == 4][0]      # Friday's bar; next tradable minute is Sunday 22:00
        r = d1.simulate(mk, Once(fri), (1,), cut=0, warmup=0)
        self.assertEqual(int(r[0, 0]) % 86400, 23 * 3600)

    def test_first_in_first_out_partial_close(self):
        u = 2; mk = self.mk(cost=0.0)
        k_add = int(mk.D["first"][u + 2])
        self.o[k_add:] = 101.0; self.h[k_add:] = 101.01; self.l[k_add:] = 100.99; self.c[k_add:] = 101.0
        k_x = int(mk.D["first"][u + 3])
        self.o[k_x:] = 102.0; self.h[k_x:] = 102.01; self.l[k_x:] = 101.99; self.c[k_x:] = 102.0
        mk = self.mk(cost=0.0)
        r = d1.simulate(mk, Once(u, dist=1.0, add_at=u + 1, exitw_at=u + 2), (1,), cut=0, warmup=0)
        # unit 1 bought at 100, unit 2 at 101; one unit sold at 102 (closes unit 1: +2), the rest at the end (102: +1)
        self.assertAlmostEqual(r[0, 3], 3.0, places=9)
        self.assertAlmostEqual(r[0, 5], 0.0, places=9)

    def test_short_side_pays_the_ask_on_exit(self):
        u = 2; mk = self.mk()
        k_hit = int(mk.D["first"][u + 1]) + 200
        self.h[k_hit] = 101.5
        mk = self.mk()
        r = d1.simulate(mk, Once(u, side=-1), (-1,), cut=0, warmup=0)
        # short at the bid 100.00, stop 101.00 hit when ask (h + cost) >= 101 -> pays 101.00
        self.assertAlmostEqual(r[0, 3], -1.0, places=9)


class TestIndicators(unittest.TestCase):
    def test_rsi_and_atr_basics(self):
        c = np.arange(1.0, 60.0); h = c + 1; l = c - 1
        self.assertTrue(np.allclose(d1.rsi(c, 14)[20:], 100.0))
        self.assertTrue(np.allclose(d1.atr(h, l, c, 14)[20:], 2.0))

    def test_sar_and_dmi_mirror_exactly(self):
        rng = np.random.default_rng(3); c = 100 + np.cumsum(rng.normal(0, 1, 300))
        h = c + rng.uniform(0.1, 1, 300); l = c - rng.uniform(0.1, 1, 300)
        a = d1.sar(h, l, c, 0.02, 0.02, 0.2); b = d1.sar(-l, -h, -c, 0.02, 0.02, 0.2)
        self.assertTrue(np.allclose(a[1:], -b[1:]))
        p1, m1, x1 = d1.dmi(h, l, c, 14); p2, m2, x2 = d1.dmi(-l, -h, -c, 14)
        ok = np.isfinite(x1)
        self.assertTrue(np.allclose(p1[ok], m2[ok]) and np.allclose(x1[ok], x2[ok]))
        r1 = d1.rsi(c, 14); r2 = d1.rsi(-c, 14); ok = np.isfinite(r1)
        self.assertTrue(np.allclose(r1[ok], 100 - r2[ok]))

    def test_sunday_stub_is_merged_into_monday(self):
        ts, o, h, l, c = weekday_minutes()
        mk = FakeMk(ts, o, h, l, c)
        self.assertFalse(np.any(mk.D["wd"] >= 5))
        self.assertEqual(len(mk.B["t"]) - mk.D["n"], int(np.sum(((mk.B["t"] // 86400) + 3) % 7 >= 5)))


class TestNoPeeking(unittest.TestCase):
    """Trades that closed well before a cut must be identical whether or not the later data exists."""
    RULES = ["core", "alt4", "alt8", "alt9", "alt10", "alt14", "alt17", "alt18", "alt22", "alt24", "alt26", "alt33",
             "alt41", "alt42", "alt43", "alt47"]

    def check(self, sym, rules, frac=0.6):
        M = P.market(sym)
        full = FakeMk(M.ts, M.o, M.h, M.l, M.G.c, cost=M.cost, swap=M.swap, sym=sym)
        K = int(len(M.ts) * frac)
        part = FakeMk(M.ts[:K], M.o[:K], M.h[:K], M.l[:K], M.G.c[:K], cost=M.cost, swap=M.swap, sym=sym)
        lim = int(M.ts[K - 1]) - 5 * 86400
        for name in rules:
            a = d1.simulate(full, TD.make_rule({"rule": name}, sym), (1, -1), cut=0)
            b = d1.simulate(part, TD.make_rule({"rule": name}, sym), (1, -1), cut=0)
            a = a[a[:, 1] < lim]; b = b[b[:, 1] < lim]
            self.assertGreater(len(a), 5, name)
            self.assertEqual(a.shape, b.shape, name)
            self.assertTrue(np.allclose(a, b), name)

    def check_sofus(self, sym, frac=0.6):
        M = P.market(sym)
        full = FakeMk(M.ts, M.o, M.h, M.l, M.G.c, cost=M.cost, swap=M.swap, sym=sym)
        K = int(len(M.ts) * frac)
        part = FakeMk(M.ts[:K], M.o[:K], M.h[:K], M.l[:K], M.G.c[:K], cost=M.cost, swap=M.swap, sym=sym)
        lim = int(M.ts[K - 1]) - 5 * 86400; seen = 0
        for name in SF.NAMES:
            p = {"rule": name, "side": "both"}
            a = d1.simulate(full, SF.make_rule(p, sym), (1, -1), cut=0)
            b = d1.simulate(part, SF.make_rule(p, sym), (1, -1), cut=0)
            a = a[a[:, 1] < lim]; b = b[b[:, 1] < lim]; seen += len(a)
            self.assertEqual(a.shape, b.shape, name)
            self.assertTrue(np.allclose(a, b), name)
        self.assertGreater(seen, 100)

    def test_sofus_rules_gold_and_us500(self):
        self.check_sofus("XAUUSD"); self.check_sofus("US500", frac=0.5)

    def test_trustdan_rules_gold(self):
        self.check("XAUUSD", self.RULES)

    def test_trustdan_rules_eurusd(self):
        self.check("EURUSD", ["core", "alt2", "alt3", "alt12", "alt20", "alt39", "alt46"], frac=0.5)


if __name__ == "__main__":
    unittest.main()
