# Body-engulf range, version 6: 60% bodies, 2-candle lookback, 4R-6R, and the best two-week mix (2026-11-09)
Pre-registration, written and committed before any v6 result.

Owner: "the second and last candle must be 60% body and above ... no tiny body ... the lookback updated to just 2 candles:
if it's a sell setup, the lookback must be two bearish candles before the setup ... test if 60% body is better than just
two bearish candles ... hammer down everywhere on all markets ... find the best architecture mix, even if it gives 2 wins
every 2 weeks it's cool, at minimum 1:4 RR ... test 5R, 6R ... give me the examples to be sure you understand."

Priors told to the owner first: v1-v5 and the gold characteristics study were all rejected (5,254 settings and
conditions); in the gold study the body share of the candles and the 3-of-5 lookback made no difference; in v4 the hit
rates at 4R-6R were at chance.

## Rules
- Pattern as before: candles 1-4 alternate; candles 2 and 4 body-engulf candles 1 and 3 (strict: open at or beyond the
  previous close, close beyond the previous open; the owner's original rule); range = high-low of the four candles;
  skip when candle 4 closes beyond the midpoint (intent).
- NEW `body60` (on/off): candles 2 and 4 each have a body of at least 60% of their own high-low.
- NEW `lb2` (on/off): the 2 candles right before candle 1 both go the trade's way (sell: both bearish, close below open;
  buy: both bullish, close at or above open, dojis bullish as the owner ruled). Replaces the 3-of-5 lookback.
- Orders: limit at 50% of the range, stop at the range end, target 4R, 5R or 6R, no breakeven ("when it gives, it gives");
  same-direction orders wait and the first fill removes the others; a wider opposite range replaces them; an order is
  cancelled if the target is reached before the fill.
- Safe window (the owner's standing rule since v4): candle 4 closes 07:00-19:00 UTC, no US news days (NFP, CPI, FOMC),
  everything flat at 20:30 UTC (so no swaps).
- 12 markets (XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225), M1-H4.
  RoboForex Prime published costs (the spread decides fills, commission per trade, slippage on stop and time exits).
- Grid: body60 2 x lb2 2 x target 3 = 12 configurations x 6 timeframes = 72 (lab).

## Order of work
1. Ten examples: the main configuration (body60 on, lb2 on, 5R) at random with a fixed seed, plus setups rejected only by
   the new rules (candle 2 body below 60%, candle 4 body below 60%, lookback 1 of 2).
2. Truth Lab with `--no-look` (2023-25 was used up for this family by v5).
3. Study on 2011-19 (learn), 2020-22 (check) and 2023-25 (seen data, extra check):
   - 60% body vs 2-candle lookback: the four combinations side by side, paired comparisons.
   - Target hit rates against what each target needs (before costs 4R 20%, 5R 16.7%, 6R 14.3%; after costs more).
   - The best two-week mix ("architecture"): for each of the 12 configurations, its legs are the market x timeframe cells
     with at least 50 trades in 2011-19 and R per trade after costs above 0 in 2011-19. The mix takes every trade of its
     legs at 1R. The best mix is the one with the highest fortnight Sharpe in 2011-19 (fortnights: 14-day blocks from
     Monday 2011-01-03; a trade counts in the fortnight it closes). Reported for each period: trades and wins (target hits)
     per fortnight, share of fortnights with at least 2 wins, share positive, mean and worst fortnight in R. Also reported
     without any selection: every leg of each configuration ("everywhere").
   If no cell qualifies for any configuration, there is no mix and the version is rejected.
4. Final, one logged look at unseen January-October 2026 (Exness ticks): the best mix from step 3 exactly as chosen, run
   only after the owner confirms that the examples match the rules. If the owner corrects the rules instead, the corrected
   version gets a new name and this look is not taken for v6.

## Pass (all needed)
The best mix: mean fortnight R above 0 in 2011-19, 2020-22 and 2023-25, t >= 2 over 2020-25 pooled, and above 0 on
January-October 2026. Otherwise v6 is rejected.
