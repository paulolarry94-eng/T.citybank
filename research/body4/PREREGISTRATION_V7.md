# Body-engulf range, version 7: the curated version (2026-11-09)
Pre-registration, written and committed before any v7 result.

Owner: "also note the lookback candles obey the same above 60% threshold ... how realistic is this cost? ... we can curate
a strategy and timeframe and account that gives better results", with a pasted plan: RoboForex Prime account, M5 entry,
maximum M15, minimum 3R, London-New York crossover 13:00-17:00 UTC, no trading around major news.

Priors told to the owner: v1-v6 and the gold study were all rejected (5,326 settings and conditions); every version is
about zero before costs; in the gold study the 12-16 UTC overlap was the least bad session but still negative (-0.26R a
trade after costs, -0.045R before).

Cost check done before this design (no strategy result involved): our RoboForex Prime model matches the pasted figures for
EURUSD (spread 0.1 + commission 0.25 pip; plus a 0.2 pip slippage allowance on stop and time exits). Median stop of the v6
setups: EURUSD M5 5.1 pips, M15 9.4 pips, so costs are 0.06-0.11R a trade there; more on EURGBP, indices, WTI and JP225.

## Rules
- Pattern as v6: candles 1-4 alternate; candles 2 and 4 body-engulf candles 1 and 3 (strict) and each has a body of at
  least 60% of its own high-low; skip when candle 4 closes beyond the midpoint; the 2 candles right before candle 1 both go
  the trade's way (sell: bearish; buy: bullish, dojis bullish).
- NEW `lbbody` (on/off): those 2 lookback candles also each have a body of at least 60% of their own high-low (off = v6).
- Timeframes M5 and M15 (setups on M5, "maximum M15").
- Hours: candle 4 closes 13:00-17:00 UTC (London-New York crossover); no US news days (NFP, CPI, FOMC: the calendar holds
  dates, not release times, so the whole day is skipped); everything flat at 20:30 UTC.
- Orders: limit at 50% of the range, stop at the range end, target 3R, 4R, 5R or 6R, no breakeven; waiting orders as before.
- Markets: the 10 with a RoboForex Prime price, chosen by the account, not by results: EURUSD, GBPUSD, USDJPY, EURGBP,
  XAUUSD, US500, NAS100, GER40, WTI, JP225 (UK100 is not on Prime; silver has no reliable Prime spread).
- Grid: lbbody 2 x target 4 x timeframe 2 = 16 lab configurations x 10 markets.
- Costs, three views of the SAME trades: Prime as modelled (spread decides fills, commission, slippage on stop and time
  exits); the pasted low-cost view (the same without slippage); zero cost (the price move alone).

## Order of work
1. Ten examples: 7 trades of the main configuration (lbbody on, 3R) at random with a fixed seed, and 3 setups rejected only
   by the new lookback-body rule.
2. Truth Lab with `--no-look` (2023-25 is used up for this family).
3. Study on 2011-19, 2020-22 and 2023-25 (seen data): every configuration at the three cost views, per market and
   timeframe; lbbody on vs off; target hit rates against what each needs; two-week results of the whole curated set.
   PRIMARY: lbbody on, the target with the best 2011-19 edge quality at Prime costs (10 markets, M5 + M15 pooled).
4. One logged look at unseen January-October 2026, on the primary only, and only after the owner confirms the examples.

## Pass (all needed)
The primary at Prime costs: R per trade above 0 in 2011-19, 2020-22 and 2023-25, t >= 2 over 2020-25 pooled, then above 0
on January-October 2026. Otherwise v7 is rejected.
