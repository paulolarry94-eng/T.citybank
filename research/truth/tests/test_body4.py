"""Owner's body-engulf 4-candle range (Q30, rules of 2026-11-08): detector, reference order engine (the specification)
on hand-made 1-minute candles, and the fast engine agreeing with the reference trade for trade."""
import os, sys, unittest, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "body4"))
import body4_scan as SC     # noqa: E402
import body4_orders as OR   # noqa: E402
import body4_fast as FA     # noqa: E402

LOOK = [(101.5, 101.6, 101.0, 101.1)] * 5          # five bearish candles before candle 1 (o, h, l, c)
SELL4 = [(100.0, 101.2, 99.9, 101.0), (101.0, 101.3, 99.4, 99.5), (99.5, 100.6, 99.45, 100.5), (100.5, 100.6, 99.3, 99.4)]
COST0 = dict(spread=0.01, commission=0.0, slippage=0.0)
MON = int(dt.datetime(2019, 1, 7, 10, tzinfo=dt.timezone.utc).timestamp())


def market(rows, start):
    o, h, l, c = (np.array([r[i] for r in rows], float) for i in range(4))
    t = start + 60 * np.arange(len(rows))
    return dict(t=t, ts=t, o=o, h=h, l=l, c=c)


def ref(M, cost=COST0, **kw):
    return OR.run(M, OR.patterns(M, 1), cost["spread"], cost["commission"], cost["slippage"], **kw)


class TestDetector(unittest.TestCase):
    def test_wick_does_not_engulf(self):
        o = np.array([100.0, 101.0]); c = np.array([101.0, 100.05])
        self.assertFalse(SC.body_engulf(o, c, 1, -1))           # body closes above candle 1's open: no engulf
        self.assertTrue(SC.body_engulf(o, np.array([101.0, 99.9]), 1, -1))

    def test_doji_counts_for_neither_side(self):
        look = [(101.5, 101.6, 101.0, 101.1)] * 2 + [(101.2, 101.4, 101.0, 101.2)] + [(101.0, 101.6, 100.9, 101.5)] * 2
        M = market(look + SELL4, MON)
        P = SC.setups(M, 1)
        self.assertEqual(int(P["lookback"][0]), 2)             # 2 bearish, 1 doji, 2 bullish -> 2, not 3

    def test_v6_body_share_and_two_candle_lookback(self):
        """v6 (owner, 2026-11-09): candles 2 and 4 need a body of 60% of their own high-low; the 2 candles right before
        candle 1 must both go the trade's way (dojis bullish)."""
        P = SC.setups(market(LOOK + SELL4, MON), 1, doji_bullish=True)
        self.assertAlmostEqual(float(P["body2"][-1]), 1.5 / 1.9, places=6)
        self.assertAlmostEqual(float(P["body4"][-1]), 1.1 / 1.3, places=6)
        self.assertEqual(int(P["lookback2"][-1]), 2)
        wick2 = [SELL4[0], (101.0, 101.3, 97.0, 99.5)] + SELL4[2:]          # candle 2: long lower wick, body 35% of its size
        self.assertLess(float(SC.setups(market(LOOK + wick2, MON), 1, doji_bullish=True)["body2"][-1]), 0.6)
        mixed = LOOK[:3] + [(101.0, 101.6, 100.9, 101.5), LOOK[0]]          # candle before 1 bearish, the one before bullish
        P = SC.setups(market(mixed + SELL4, MON), 1, doji_bullish=True)
        self.assertEqual(int(P["lookback2"][-1]), 1)                        # 1 of 2: not valid
        self.assertEqual(int(P["lookback"][-1]), 4)                         # the old 5-candle count was 4 of 5
        buy4 = [(101.0, 101.1, 99.9, 100.0), (100.0, 101.3, 99.9, 101.1), (101.1, 101.2, 100.4, 100.5), (100.5, 101.9, 100.4, 101.8)]
        look = [(101.0, 101.1, 100.4, 100.5)] * 3 + [(100.5, 100.7, 100.3, 100.5), (100.0, 100.6, 99.9, 100.5)]   # doji, bullish
        self.assertEqual(int(SC.setups(market(look + buy4, MON), 1, doji_bullish=True)["lookback2"][-1]), 2)
        self.assertEqual(int(SC.setups(market(look + buy4, MON), 1)["lookback2"][-1]), 1)

    def test_doji_bullish_mode(self):
        """v3 (owner, 2026-11-08): a doji counts as bullish in the lookback (close >= open)."""
        buy4 = [(101.0, 101.1, 99.9, 100.0), (100.0, 101.3, 99.9, 101.1), (101.1, 101.2, 100.4, 100.5), (100.5, 101.9, 100.4, 101.8)]
        look = [(100.0, 100.6, 99.9, 100.5)] * 2 + [(100.5, 100.7, 100.3, 100.5)] + [(101.0, 101.1, 100.4, 100.5)] * 2
        M = market(look + buy4, MON)
        self.assertEqual(int(SC.setups(M, 1)["lookback"][0]), 2)                     # doji neutral
        self.assertEqual(int(SC.setups(M, 1, doji_bullish=True)["lookback"][0]), 3)  # doji bullish -> 3 of 5

    def test_owner_image_7_lookback_is_3_with_dojis_bullish(self):
        try:
            sys.path.insert(0, os.path.join(HERE, "..", ".."))
            import engine as EN
            ts, o, h, l, c = EN.load_m1("XAUUSD", 2019, 2019)
        except Exception as e:
            self.skipTest(str(e))
        bt, bo, bh, bl, bc, _ = EN.resample(ts, o, h, l, c, 5)
        B = dict(t=bt, o=bo, h=bh, l=bl, c=bc)
        t4 = int(dt.datetime(2019, 1, 2, 8, 35, tzinfo=dt.timezone.utc).timestamp())     # candle 4 of the image-7 buy
        for mode, want in ((False, 2), (True, 3)):
            P = SC.setups(B, 5, doji_bullish=mode)
            j = int(np.flatnonzero(bt[P["k"]] == t4)[0])
            self.assertEqual((int(P["side"][j]), int(P["lookback"][j])), (1, want))

    def test_loose_engulf_allows_a_gap_at_the_open(self):
        """v5 (owner's silver chart): candle 2 opens below candle 1's close but closes below candle 1's open."""
        gap = [(100.0, 101.2, 99.9, 101.0), (100.8, 100.9, 99.4, 99.5), (99.5, 100.6, 99.45, 100.5), (100.5, 100.6, 99.3, 99.4)]
        M = market(LOOK + gap, MON)
        self.assertEqual(len(SC.setups(M, 1)["k"]), 0)                      # strict: 100.8 < 101.0, no full body cover
        L = SC.setups(M, 1, engulf="loose")
        self.assertEqual((len(L["k"]), int(L["side"][0])), (1, -1))

    def test_layer_mask(self):
        """A small setup counts only if a same-direction big setup closed at most `window` earlier."""
        big_t, big_s = np.array([1000, 5000]), np.array([-1, 1])
        small_t = np.array([999, 1000, 1500, 3500, 5100, 5100])
        small_s = np.array([-1, -1, -1, -1, 1, -1])
        self.assertEqual(SC.layer_mask(small_t, small_s, big_t, big_s, 2000).tolist(), [0, 1, 1, 0, 1, 0])

    def test_control_sample_has_no_engulfing(self):
        rows = LOOK + [(100.0, 101.2, 99.9, 101.0), (101.0, 101.3, 100.2, 100.4), (100.4, 100.9, 100.3, 100.8), (100.8, 100.9, 100.5, 100.6)]
        M = market(rows, MON)
        self.assertEqual(len(SC.setups(M, 1)["k"]), 0)
        C = SC.setups(M, 1, sample="control")                 # the sell shape, and a buy shape one candle earlier
        self.assertEqual(sorted(zip(C["k"].tolist(), C["side"].tolist())), [(7, 1), (8, -1)])


class TestOrders(unittest.TestCase):
    def test_sell_limit_breakeven_then_target(self):
        after = [(99.6, 100.4, 99.5, 100.0), (100.0, 100.1, 98.0, 98.2), (98.2, 98.3, 96.2, 96.4)]
        M = market(LOOK + SELL4 + after, MON)
        P = OR.patterns(M, 1)
        # candles 3, 4 and the next two form a second valid sell (overlapping); it arrives while the trade is open
        self.assertEqual([(p["side"], round(p["mid"], 2), p["lookback"]) for p in P], [(-1, 100.3, 5), (-1, 99.3, 4)])
        tr, log, _ = ref(M)
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0]["entry"], 100.3); self.assertAlmostEqual(tr[0]["R"], 4.0)
        self.assertTrue(any("ignored, a trade is open" in x[1] for x in log))
        self.assertTrue(any("stop moved to the entry" in x[1] for x in log))

    def test_target_needs_the_ask_but_only_the_spread(self):
        """Image 6 (2026-11-08): a sell's target is hit when the ASK reaches it; commission does not move the ask."""
        after = [(99.6, 100.4, 99.5, 100.0), (100.0, 100.1, 96.27, 96.5), (96.5, 96.6, 96.4, 96.5)]   # bid low 96.27
        M = market(LOOK + SELL4 + after, MON)
        cost = dict(spread=0.02, commission=0.10, slippage=0.05)  # total 0.17: bid + total would miss 96.30
        tr, _, _ = ref(M, cost)
        self.assertEqual(tr[0]["reason"], "target (+4R)")
        self.assertAlmostEqual(tr[0]["R"], 4.0 - 0.10 / 1.0)

    def test_skip_when_candle_4_closes_beyond_the_midpoint(self):
        sell = SELL4[:3] + [(100.5, 100.6, 97.0, 99.4)]         # engulfs (below 3's open 99.5) but closes above the mid 99.15
        tr, log, _ = ref(market(LOOK + sell + [(100.35, 100.5, 100.2, 100.3)] * 3, MON))
        self.assertEqual(tr, []); self.assertTrue(any("no intent" in x[1] for x in log))

    def test_entry_level_70_percent_fills(self):
        after = [(99.6, 100.8, 99.5, 100.0), (100.0, 100.1, 97.0, 97.2)] + [(97.2, 97.3, 97.1, 97.2)] * 3
        tr, _, _ = ref(market(LOOK + SELL4 + after, MON), entry=0.7, breakeven=False)
        self.assertAlmostEqual(tr[0]["entry"], 100.7)                 # sell at lo + 0.7 x range
        self.assertAlmostEqual(tr[0]["risk"], 0.6)                    # stop at the range high 101.3

    def test_one_r_target_with_breakeven_at_half(self):
        """v2: target 1R, breakeven at 50% of the target (+0.5R)."""
        after = [(99.6, 100.4, 99.5, 100.0), (100.0, 100.1, 99.75, 99.9), (99.9, 100.35, 99.85, 100.3)]
        tr, log, _ = ref(market(LOOK + SELL4 + after, MON), target_r=1.0, be_r=0.5)
        # sell at 100.3, 1R = 1.0: +0.5R at 99.8 (ask = bid 99.75 + 0.01) -> stop to 100.3; price returns -> breakeven
        self.assertEqual(tr[0]["reason"], "breakeven stop")
        self.assertAlmostEqual(tr[0]["tp"], 99.3)
        after2 = [(99.6, 100.4, 99.5, 100.0), (100.0, 100.1, 99.2, 99.3)]
        tr2, _, _ = ref(market(LOOK + SELL4 + after2, MON), target_r=1.0, be_r=0.5)
        self.assertEqual(tr2[0]["reason"], "target (+1R)"); self.assertAlmostEqual(tr2[0]["R"], 1.0)

    def test_ten_r_target_and_breakeven_at_75_percent(self):
        """v3: target 10R, breakeven at 75% of the way (+7.5R)."""
        down = [(99.6, 100.4, 99.5, 99.0)] + [(99.0 - k, 99.1 - k, 97.9 - k, 98.0 - k) for k in range(0, 6)]   # low 92.9
        back = [(93.0, 100.5, 92.7, 100.4)]                       # reaches 92.71 ask (+7.5R = 92.8) and comes back
        after = [(100.4, 100.6, 100.2, 100.5)] * 3
        tr, log, _ = ref(market(LOOK + SELL4 + down + back + after, MON), target_r=10.0, be_r=7.5)
        self.assertAlmostEqual(tr[0]["tp"], 90.3); self.assertAlmostEqual(tr[0]["be"], 92.8)
        self.assertEqual(tr[0]["reason"], "breakeven stop")
        win = [(99.6, 100.4, 99.5, 99.0)] + [(99.0 - k, 99.1 - k, 97.9 - k, 98.0 - k) for k in range(0, 9)]   # low 89.9
        tr2, _, _ = ref(market(LOOK + SELL4 + win, MON), target_r=10.0, be_r=7.5)
        self.assertEqual(tr2[0]["reason"], "target (+10R)"); self.assertAlmostEqual(tr2[0]["R"], 10.0)

    def test_safe_window_daily_close_and_allow(self):
        """v4 safe mode: everything closes at 20:30 UTC each day; a setup with allow = False never trades."""
        after = [(99.6, 100.4, 99.5, 100.0)] + [(100.0, 100.2, 99.8, 100.0)] * 40
        wed = int(dt.datetime(2019, 1, 9, 20, 0, tzinfo=dt.timezone.utc).timestamp())       # Wednesday 20:00 UTC
        M = market(LOOK + SELL4 + after, wed)
        tr, _, _ = ref(M, day_close=True)
        self.assertEqual(tr[0]["reason"], "daily close")
        self.assertEqual(dt.datetime.fromtimestamp(tr[0]["t_out"], dt.timezone.utc).strftime("%a %H:%M"), "Wed 20:30")
        self.assertEqual(ref(M)[0], [])          # without the daily close the trade is still open when the data ends
        P = OR.patterns(M, 1)
        for p in P:
            p["allow"] = False
        tr2, log2, _ = OR.run(M, P, 0.01, 0.0, 0.0, day_close=True)
        self.assertEqual(tr2, []); self.assertTrue(any("safe window" in x[1] for x in log2))
        F, _ = FA.run(dict(ts=M["ts"], o=M["o"], h=M["h"], l=M["l"], c=M["c"]), SC.setups(M, 1), dict(spread=0.01, commission=0, slippage=0),
                      dict(entry=0.5, buffer=0.0, be=True, lookback=True), day_close=True)
        self.assertEqual((len(F), int(F[0][1])), (1, tr[0]["t_out"]))

    def test_friday_close_and_lookback(self):
        after = [(99.6, 100.4, 99.5, 100.0)] + [(100.0, 100.2, 99.8, 100.0)] * 40
        fri = int(dt.datetime(2019, 1, 11, 20, 0, tzinfo=dt.timezone.utc).timestamp())
        tr, _, _ = ref(market(LOOK + SELL4 + after, fri))
        self.assertEqual(tr[0]["reason"], "Friday close")
        self.assertEqual(dt.datetime.fromtimestamp(tr[0]["t_out"], dt.timezone.utc).strftime("%a %H:%M"), "Fri 20:30")
        bull = [(r[0], r[1], r[2], r[0] + 0.5) for r in LOOK]
        tr2, log2, _ = ref(market(bull + SELL4 + after, fri))
        self.assertEqual(tr2, []); self.assertTrue(any("lookback" in x[1] for x in log2))
        self.assertEqual(len(ref(market(bull + SELL4 + after, fri), use_lookback=False)[0]), 1)

    def _setups(self, rows):
        """Hand-made setups for the order rules: (minute, side, hi, lo, c4)."""
        return [dict(id=n + 1, k=0, side=s, hi=hi, lo=lo, width=hi - lo, mid=(hi + lo) / 2, c4=c4, lookback=5, t1=0,
                     t_conf=MON + 60 * mnt) for n, (mnt, s, hi, lo, c4) in enumerate(rows)]

    def test_same_direction_orders_wait_and_the_first_fill_removes_the_rest(self):
        # buy #1 range 100-102 (limit 101), buy #2 range 101.5-103 (limit 102.25): price falls, #2 fills first
        bars = [(102.6, 102.7, 102.5, 102.6)] * 6 + [(102.6, 102.6, 102.2, 102.3), (102.3, 102.4, 101.5, 101.6)] + [(101.6, 101.7, 101.5, 101.6)] * 5
        M = market(bars, MON)
        pats = self._setups([(1, 1, 102.0, 100.0, 101.8), (3, 1, 103.0, 101.5, 102.9)])
        tr, log, _ = OR.run(M, pats, 0.01, 0.0, 0.0)
        self.assertTrue(any("filled at 102.25; removed pending #1" in x[1] for x in log))
        F, _ = FA.run(dict(ts=M["ts"], o=M["o"], h=M["h"], l=M["l"], c=M["c"]), _arr(pats), dict(spread=0.01, commission=0, slippage=0),
                      dict(entry=0.5, buffer=0.0, be=True, lookback=True))
        self.assertEqual(len(F), len(tr))

    def test_opposite_setup_needs_a_wider_range(self):
        bars = [(102.0, 102.1, 101.9, 102.0)] * 12
        M = market(bars, MON)
        narrow = self._setups([(1, 1, 102.0, 100.0, 101.8), (3, -1, 103.5, 102.2, 102.5)])   # sell range 1.3 < 2.0
        _, log, _ = OR.run(M, narrow, 0.01, 0.0, 0.0)
        self.assertTrue(any("not wider" in x[1] for x in log))
        wide = self._setups([(1, 1, 102.0, 100.0, 101.8), (3, -1, 104.5, 102.2, 102.4)])     # sell range 2.3 > 2.0
        _, log2, _ = OR.run(M, wide, 0.01, 0.0, 0.0)
        self.assertTrue(any("WIDER than every pending order: replaces #1" in x[1] for x in log2))


def _arr(pats):
    keys = ("side", "hi", "lo", "c4", "lookback", "t_conf")
    return {k: np.array([p[k] for p in pats]) for k in keys}


class TestParity(unittest.TestCase):
    """The fast engine must reproduce the reference trade for trade on real data."""
    def test_gold_2019_m5_and_m1(self):
        try:
            sys.path.insert(0, os.path.join(HERE, "..", ".."))
            import engine as EN
            ts, o, h, l, c = EN.load_m1("XAUUSD", 2019, 2019)
        except Exception as e:                                     # data not present
            self.skipTest(str(e))
        keep = ts < int(dt.datetime(2019, 4, 1, tzinfo=dt.timezone.utc).timestamp())
        ts, o, h, l, c = ts[keep], o[keep], h[keep], l[keep], c[keep]
        M = dict(ts=ts, o=o, h=h, l=l, c=c)
        cost = dict(spread=0.05, commission=0.06, slippage=0.05, swap=0.2)
        total = 0
        for tf in (5, 1):
            bt, bo, bh, bl, bc, _ = EN.resample(ts, o, h, l, c, tf)
            B = dict(t=bt, o=bo, h=bh, l=bl, c=bc)
            S = SC.setups(B, tf)
            for p in (dict(entry=0.5, buffer=0.0, be=True, lookback=True), dict(entry=0.7, buffer=0.1, be=False, lookback=False),
                      dict(entry=0.5, buffer=0.2, be=True, lookback=False), dict(entry=0.5, buffer=0.0, be=True, lookback=True, target=2),
                      dict(entry=0.7, buffer=0.05, be=True, lookback=False, target=1),
                      dict(entry=0.5, buffer=0.0, be=True, lookback=True, target=10, be_frac=0.75, doji=True),
                      dict(entry=0.7, buffer=0.1, be=True, lookback=True, target=2, be_frac=0.75, doji=True)):
                tgt = p.get("target", 4); dj = p.get("doji", False)
                tr, _, _ = OR.run(M, OR.patterns(B, tf, doji_bullish=dj), cost["spread"], cost["commission"], cost["slippage"],
                                  swap=cost["swap"], entry=p["entry"], buffer=p["buffer"], breakeven=p["be"],
                                  use_lookback=p["lookback"], target_r=tgt, be_r=p.get("be_frac", 0.5) * tgt)
                F, _ = FA.run(M, SC.setups(B, tf, doji_bullish=dj) if dj else S, cost, p)
                if p.get("target") == 10:                    # the same setting in the safe-window mode (daily close + allow)
                    Sd = SC.setups(B, tf, doji_bullish=dj)
                    al = ((Sd["t_conf"] % 86400 >= 7 * 3600) & (Sd["t_conf"] % 86400 < 19 * 3600)).astype(np.int64)
                    pats = OR.patterns(B, tf, doji_bullish=dj)
                    for q, a in zip(pats, al):
                        q["allow"] = bool(a)
                    tr2, _, _ = OR.run(M, pats, cost["spread"], cost["commission"], cost["slippage"], swap=cost["swap"],
                                       entry=p["entry"], buffer=p["buffer"], breakeven=p["be"], use_lookback=p["lookback"],
                                       target_r=10, be_r=7.5, day_close=True)
                    F2, _ = FA.run(M, Sd, cost, p, allow=al, day_close=True)
                    self.assertEqual(len(F2), len(tr2), ("safe", tf))
                    for a2, b2 in zip(tr2, F2):
                        self.assertEqual((a2["t_in"], a2["t_out"]), (int(b2[0]), int(b2[1])))
                        self.assertAlmostEqual(a2["R"], b2[3], places=9)
                    total += len(tr2)
                self.assertEqual(len(F), len(tr), (tf, p))
                total += len(tr)
                for a, b in zip(tr, F):
                    self.assertEqual((a["t_in"], a["t_out"], a["side"]), (int(b[0]), int(b[1]), int(b[2])))
                    self.assertAlmostEqual(a["R"], b[3], places=9)
        self.assertGreater(total, 300)          # the comparison covers hundreds of trades


if __name__ == "__main__":
    unittest.main()
