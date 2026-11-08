# Gold body-engulf: the best characteristics, learned on 2019 (2026-11-08)

**Verdict: rejected. No characteristic makes this pattern pay on gold.** 2019 had 11,782 setups and 5,761 trades (all
timeframes). Every one of the 65 characteristic groups with 100+ trades lost money after costs in 2019, and in the 14
other years every group lost too, except H4 (+0.03R a trade, 261 trades, about zero). Before costs, in those 14 years,
every group sits between -0.09R and +0.05R a trade: the pattern has no edge for any characteristic to bring out. The rule learned on 2019
(M30 and loose engulf) lost -0.02R a trade over 14 years (positive in 6 of them) and -0.07R on unseen January-October 2026.

- Pre-registered before any result: `research/body4/PREREGISTRATION_GOLD.md` (commit f8e48d7).
- Code: `research/body4/gold_traits.py`. All numbers: `traits.json`; all tables: `TABLES.md`.
- Every setup is traded on its own: limit at 50% of the range, stop at the range end, target 2R, no breakeven, everything
  closed at 20:30 UTC (no overnight holds, so no swaps; the swap-free result is the same). RoboForex Prime gold costs
  ($0.16 an ounce a round trip).
- Conditions tried: 70 (65 single, 5 second-step). January-October 2026 was looked at once, here.

## How many trades
| | 2019 | 14 check years (2011-18, 2020-25) | Jan-Oct 2026 (unseen) |
|---|---|---|---|
| Trades | 5,761 (M1 3,803, M5 1,204, M15 434, M30 202, H1 82, H4 36) | 90,709 | 7,419 |
| R per trade after costs | -0.476R | -0.359R | -0.114R |
| R per trade before costs | -0.078R | -0.050R | -0.044R |
| Hits 2R | 24.6% (33% is pure chance at 2R) | 26.8% | 29.9% |

2026 loses less only because gold's candles were much bigger (gold traded $3,870-5,593; a typical one-minute candle was
$2.04 tall against $0.18 in 2019), so the fixed cost is a smaller part of each trade; before costs it is still below zero.

## Every characteristic (after costs; the full table with 2019 and before-cost numbers is in `TABLES.md`)
| Characteristic | Least bad group (14 check years) | Worst group | What it means |
|---|---|---|---|
| Timeframe | H4 +0.03R (261), M30 -0.03R, H1 -0.03R | M1 -0.44R (63,373) | costs: a bigger candle makes the cost a smaller part of 1R |
| Cost as a share of 1R | lowest third -0.16R | highest third -0.75R | the same cost effect |
| Session (candle 4 closes) | London-New York overlap 12-16 UTC -0.26R | Asia 23-07 -0.41R | costs again: small Asian ranges |
| Volatility | high -0.28R | low -0.42R | costs again |
| Your lookback (bullish candles of 5) | 0 of 5: -0.29R | 4 of 5: -0.38R | no help: 3, 4 or 5 of 5 do no better than 0-2 |
| Trend (own timeframe, H4, daily) | -0.35R | -0.38R | no difference |
| Strict vs loose engulf | loose -0.35R | strict -0.37R | no difference |
| Engulf size (candle 4 vs candle 3) | biggest third -0.33R | smallest third -0.38R | tiny |
| Candle 4 closes past candle 2 | furthest third -0.32R | least -0.38R | tiny |
| Where in today's range | -0.34R | -0.37R | no difference |
| Buy vs sell, weekday, US news day | -0.35 to -0.36R | -0.36R | no difference |

## The rule learned on 2019, checked
| Selection | 2019 | 14 check years | Years positive | Jan-Oct 2026 |
|---|---|---|---|---|
| All setups | -0.476R (5,761) | -0.359R (90,709) | 0 of 14 | -0.114R (7,419) |
| **Rule: M30 and loose engulf** | -0.085R (109) | -0.022R (1,840; t -0.7) | 6 of 14 | -0.066R (136) |
| Best single: M30 | -0.126R (202) | -0.031R (2,872) | 6 of 14 | -0.057R (194) |
| Lookback 5 of 5 | -0.315R (169) | -0.373R (2,316) | 0 of 14 | +0.235R (203) |

The rule beats random selections (p 0.001) only because it skips the expensive M1 trades that make up most of the pool;
it still loses. "Lookback 5 of 5" made money in 2026 but lost in all 14 other years: a lucky stretch, not a characteristic
(P10).

## What this means
- The pattern's results on gold are decided by costs, not by any feature of the setup. Moving to bigger timeframes or
  bigger candles only brings the loss toward zero (H4 and M30 end near zero); nothing found turns it positive.
- This is the same answer as the gold Leg 34 study (P21): when a setup has no edge before costs, the winners look like the
  losers, and no characteristic separates them.
- The body-engulf range is closed on gold as well as across the 12 markets (5,184 settings in v1-v5 plus these 70
  conditions).
