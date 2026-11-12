# Pivot-sweep range: the owner's EURUSD M5 setting, one logged look at 2023-25 and 2026 (owner, 2026-11-12)
Written and committed before any 2023-2026 number of this setting, and before any 2011-22 number of its target rule.

Owner (after seeing `research/results/sweep4/RESULT.md`): "the target can be two pivot points above after entry: you pass
the first pivot, then the next pivot is TP ... those charts were from 2026 ... test 2026 too ... if M5 EU works let's test
it proper ... we can always find the trading fees that align the most" (+ a pasted list of copy-trading brokers).

## The one setting (PRIMARY)
EURUSD, M5, Pivot Points High Low 10/10, the sweep by candle 1 or 2, candles 2 and 4 >= 60% body (strict body engulf),
range = candle 4's end to the extreme of the four, limit at 60% of the range, target = the SECOND live pivot beyond the
entry on the target side (`pv2`: no minimum or maximum R; no trade if fewer than two live pivots), Friday close, RoboForex
Prime costs + swaps. Stop: chosen by a fixed rule on 2011-22 only = the stop style (range end / range end + 20% / pivot
trailing) with the best edge quality (mean R / sd) on EURUSD M5 2011-22 at Prime costs. The script prints and stores that
choice before it opens any later data.

## Hindsight, said plainly
- EURUSD M5 was chosen AFTER seeing 2011-22: it was the best of 1,403 market x timeframe cells (P10). A pass is weak
  evidence; a fail closes it.
- The `pv2` target is the owner's rule, given after the owner saw the p1/p2 results (it differs from p2: no 3R minimum).

## The look (once; `research/sweep4/look.py` aborts if `research/results/sweep4/LOOK.json` exists)
- 2023-25: EURUSD M1 data (Dukascopy/Exness seams as in Q4), seen before for the body-engulf family (v5) but never with
  the pivot-sweep rule. Jan-Oct 2026: Exness ticks (EURUSD), seen by v7's look (a different rule).
- PASS = R a trade after Prime costs above 0 in 2023-25 AND in Jan-Oct 2026. Pass -> forward demo candidate (Tier B
  at most, given the hindsight). Otherwise FAILS.
- Reported with it (not part of the decision): the same costs at Exness Zero (measured 0.05 pip + estimated 0.7 + 0.2
  slippage), Tickmill Raw and Pepperstone Razor at the owner's pasted figures (0.11 + 0.6 + 0.2; 0.1 + 0.7 + 0.2 pip,
  unverified), and at zero cost; win rate; 10-trade rounds. Also described: the same rule on GBPUSD, USDJPY, EURGBP,
  XAUUSD (Exness 2026) and GER40 (HistData 2026, downloaded 2026-11-12, includes November) on M5, and EURUSD on M1-H1.
- After the look: replay the owner's two 2026 screenshots in our 2026 data.
