# Gold body-engulf characteristics: learn on 2019, check everywhere else (2026-11-08)
Pre-registration, written and committed before any result of this study.

Owner: "focus more on gold ... all the setups, so we are looking at over a thousand trades in 2019 ... we can find the
best characteristics". Owner's choice (2026-11-08): learn on 2019.

Priors told to the owner before starting: the same method failed on gold's Leg 34 pattern (P21: the winners' attributes
did not select winners; a top-1% profile did worse than taking every setup); the body-engulf range on gold is about zero
before costs (v1: M30/H1 near breakeven after costs, M1/M5 -0.3 to -0.5R a trade); v1-v5 rejected (5,184 settings).

## Universe
- XAUUSD, every body-engulf setup on M1, M5, M15, M30, H1 and H4, 2011-2025 plus January-October 2026. "Loose" engulf
  defines the universe (candles 2 and 4 close beyond the previous candle's open); "strict" (also opens at or beyond the
  previous close) is a characteristic. Kept rules: candle 4 closes beyond the midpoint in the trade's direction (intent),
  no setups in the weekend window.
- Each setup is traded ALONE (no one-trade-at-a-time interaction), with the lab's M1 engine
  (`research/body4/body4_fast.py`): limit at 50% of the range, stop at the range end, target 2R, no breakeven; the order is
  cancelled if the target is reached before the fill; no fills 20:30-23:00 UTC; everything is closed and cancelled at
  20:30 UTC (no overnight holds, so no swaps).
- Costs: RoboForex Prime gold (spread 0.05 decides fills, commission 0.06, slippage 0.05 on stop and time exits).
- PRIMARY outcome: R per trade after costs. Also reported: R before costs, win rate, 2R hit rate, and how far the trade
  goes before its stop or the 20:30 close (MFE in R, from a run with no target; buys bid high, sells ask low; the fill and
  exit minutes excluded).

## Characteristics (all known when candle 4 closes)
1 timeframe; 2 side; 3 engulf strict or loose only; 4 session of candle 4's close (Asia 23-07, London 07-12, overlap 12-16,
New York 16-20:30, rollover 20:30-23 UTC); 5 weekday of the trading day (from 22:00 UTC); 6 US news day (NFP, CPI, FOMC);
7 lookback count 0-5 (dojis bullish); 8 range in ATR(14) of its timeframe; 9 cost share (all-in cost / planned 1R);
10 candle 2 body / candle 1 body; 11 candle 4 body / candle 3 body; 12 how far candle 4 closes beyond the midpoint (share
of the range); 13 candle 4's close beyond candle 2's close (ATR, trade direction); 14 body share of the four candles
(bodies / high-low lengths); 15 trend on its own timeframe (close vs EMA(50), ATR, trade direction); 16 H4 trend (last
closed H4 close vs H4 EMA(50), H4 ATR, trade direction); 17 daily trend (yesterday's close vs the 20-day average, in
average daily ranges, trade direction); 18 volatility regime (ATR(14) / its median over the last 500 candles); 19 location
in today's range so far (0 = at the day's low for buys, at its high for sells); 20 momentum before the pattern (close 4
candles before candle 1 vs 24 candles before, ATR, trade direction).
Numeric characteristics are split into thirds with cut points from the 2019 trades; categories as they are.

## Learning (2019 only)
- Per characteristic: trades, R after costs, before costs, win rate, 2R hits, median MFE, by third or category.
- The rule: the best single condition (one third or category) by R after costs with at least 100 trades in 2019, then the
  best second condition from another characteristic (at least 100 trades together). The number of conditions tried is
  reported.

## Checking
- The 2-condition rule and the 5 best single conditions on gold 2011-2018 and 2020-2025, each year and pooled, after and
  before costs. 2023-25 was already looked at for this pattern family (v5), so here it counts as seen data.
- Random control: 2,000 random selections of the same size from the same check trades; the rule must beat 95% of them.
- Final, one logged look: unseen January-October 2026 (Exness ticks, `data/holdout/`).

## Pass (all needed)
Check years pooled: R after costs above 0 with t >= 2; positive in at least 9 of the 14 check years; better than 95% of
the random selections; positive after costs on January-October 2026 (fewer than 30 trades there: inconclusive).
Otherwise the gold characteristics are rejected.
