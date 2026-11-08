# Body-engulf 4-candle range (owner, Q30) — result (2026-11-08)

**Verdict: rejected.** No setting makes money after costs on any of the 12 markets pooled, on any timeframe from M1 to H4,
in 2011-19 or 2020-22. Before costs the pattern is about zero (M1 and M5 below zero). The 2023-25 holdout stays closed
(no setting passed the development gate, so no look was used).
Pre-registered: `research/body4/PREREGISTRATION.md` (rules and grid fixed before any result). 192 configurations
(6 timeframes x entry 50/70% x breakeven on/off x 4 stop buffers x lookback on/off) x 12 markets, RoboForex Prime costs,
the lab's swaps. Lab report: `research/results/truth/body4_range_v1/REPORT.md`; owner's questions: `study.json`;
before costs: `gross.json`; control: `research/results/truth/body4_range_v1/controls.json`.

## Your main settings (entry 50%, stop at the range end, breakeven at +2R, lookback on), 12 markets pooled
| Timeframe | Trades 2011-19 | R per trade 2011-19 | 2020-22 | Win rate | Before costs 2011-19 / 2020-22 | Markets positive 2011-19 |
|---|---|---|---|---|---|---|
| M1 | 44,500 | -0.47 | -0.44 | 13% | -0.07 / -0.06 | 0 of 12 |
| M5 | 16,375 | -0.28 | -0.26 | 15% | -0.03 / -0.02 | 0 of 12 |
| M15 | 6,835 | -0.16 | -0.17 | 17% | +0.03 / +0.01 | 0 of 12 |
| M30 | 3,856 | -0.19 | -0.25 | 17% | -0.05 / -0.11 | 0 of 12 |
| H1 | 1,891 | -0.14 | -0.08 | 18% | -0.01 / +0.01 | 1 of 12 |
| H4 | 503 | -0.14 | -0.21 | 26% | -0.06 / -0.14 | 3 of 12 |
A 4R target needs about 1 win in 5 just to break even before costs. Round-trip costs per trade: M1 0.43R, M5 0.26R,
M15 0.18R, M30 0.14R, H1 0.12R, H4 0.06R (the ranges are small next to the spread and commission).
Best of all 192 after costs: -0.11R a trade (H4). Before costs 48 of 192 settings were positive in 2011-19 and 31 in both
periods, best t 2.0: what 192 tries of a zero edge produce by chance.

In cycle units (all markets in time order, `research/results/truth/body4_range_v1/CYCLES_LEAGUE.md`): the best of the 192
settings (H1, no breakeven, 5% buffer, 50% entry, lookback off) has edge quality -0.064 and loses about 0.04% per 10-trade
cycle at the 3.6% cap; the goal needs +0.42.

## Your questions (paired: every market x timeframe x other setting, only one thing changed)
| Question | 2011-19 | 2020-22 | Answer |
|---|---|---|---|
| Breakeven at +2R vs none | breakeven had the higher profit factor in 25% of 1,110 pairs; PF -0.03; R per trade +0.001 | 27% of 962; PF -0.03; +0.002 | You are right: breakeven lowers the profit factor (more small losing exits: commission + slippage) and adds nothing per trade |
| Entry 50% vs 70% pull-back | 50% better in 74% of pairs, +0.08R a trade | 70%, +0.05R | 50% is better; the deeper 70% fill picks worse trades |
| Stop buffer 0% vs 20% of the range | 20% better in 75% of pairs, +0.08R | 73%, +0.07R | a wider stop loses less (costs are a smaller part of a bigger 1R), still negative |
| Lookback on vs off | on better in 48% of pairs, -0.007R | 48%, +0.006R | no effect |
| Bigger candles (thirds by body size / ATR) | larger third less negative on M1-M30 (M5 -0.22 vs -0.31R; M15 -0.13 vs -0.19R) | similar | bigger is less bad, never positive in both periods |

## Best market x timeframe (learn on 2011-19, check on 2020-22)
For each of the 64 market x timeframe pairs with 100+ trades, the best of the 32 settings on 2011-19: only 10 were positive
in 2011-19 and 8 in 2020-22. The top four (EURUSD H1 +0.22R, JP225 H1 +0.19R, GBPUSD H1 +0.11R, XAUUSD H1 +0.10R in
2011-19) all lost in 2020-22 (-0.14 to -0.25R). No market or timeframe held.

## Control: the same trades on the same four alternating candles WITHOUT the engulfing
| Timeframe (main settings) | With engulfing 2011-19 | Without | t of the difference | With engulfing 2020-22 | Without |
|---|---|---|---|---|---|
| M1 | -0.47R | -0.52R | 5.5 | -0.44R | -0.48R |
| M5 | -0.28R | -0.34R | 3.6 | -0.26R | -0.29R |
| M15 | -0.16R | -0.25R | 3.5 | -0.17R | -0.16R |
| M30 | -0.19R | -0.20R | 0.4 | -0.25R | -0.14R |
| H1 | -0.14R | -0.14R | -0.1 | -0.08R | -0.12R |
| H4 | -0.14R | -0.20R | 0.8 | -0.21R | +0.00R |
Over all 192 settings the engulfing version lost less than the plain shape in 169 (2011-19) but only 128 (2020-22), mean
+0.04R then -0.005R. The engulfing makes the short timeframes a little less bad (its ranges are bigger, so costs weigh
less), it never makes them positive, and on H1/H4 it makes no difference.

## Notes
- Unclear minutes (M1 data cannot order a fill, stop and target inside one minute; counted against the trade): 20% of
  M1 trades, 7% M5, 4% M15, 2% M30 and H1, 1% H4. Dropping every unclear trade (which flatters the result) still leaves
  the main settings negative in 2011-19: M1 -0.27, M5 -0.24, M15 -0.14, M30 -0.18, H1 -0.14, H4 -0.14R a trade.
- Corrections made before the run (owner, 2026-11-08): the spread alone decides whether a price is reached (your image 6
  reaches its 4R target); dojis count for neither side in the lookback (image 7: 2 of 5, the third "blue" candle was a
  doji my chart drew blue); skip when candle 4 closes beyond the midpoint; every same-direction order waits and the first
  fill removes the others. Corrected example charts: `research/results/body4/examples3/`.
- Swap-free (separately, not instead), main settings 2011-19: M1 -0.47, M5 -0.28, M15 -0.14, M30 -0.17, H1 -0.12,
  H4 -0.10R a trade: swaps cost 0.00-0.04R; still negative everywhere.
