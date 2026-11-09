# Body-engulf range v6: 60% bodies, 2-candle lookback, 4R-6R, and the best two-week mix (2026-11-09)

**Verdict: rejected.** All 12 combinations lose about -0.35R a trade after costs in every period (12 markets, M1-H4,
2011-2025), and about -0.01 to -0.09R before costs. The 2-candle lookback helps a little (+0.02R a trade); the 60% body
rule does not. Targets of 4R, 5R and 6R are reached less often than even a zero-cost trade needs. The best two-week mix,
chosen on 2011-19, made money there and lost in 2020-22 and 2023-25. "Two wins every two weeks" happens almost every
fortnight when trading everywhere, but with about 7 losers for every winner.

- Pre-registered before any v6 result: `research/body4/PREREGISTRATION_V6.md` (commit b313931).
- Truth Lab: `research/results/truth/body4_range_v6/REPORT.md`: 0 of 72 configurations pass; 4% positive in 2011-19, 0% in
  both 2011-19 and 2020-22; median -0.167R a trade.
- Study: `research/body4/study_v6.py` -> `study_v6.json`. Examples: `examples/` (10 charts, `research/body4/examples_v6.py`).
- Costs: RoboForex Prime published (spread, commission, slippage on stops). No swaps: everything closes at 20:30 UTC, so the
  swap-free result is the same.

## What was tested
| Rule | Setting |
|---|---|
| Pattern | candles 1-4 alternate; candles 2 and 4 body-engulf candles 1 and 3 (strict); skip when candle 4 closes beyond the midpoint |
| 60% body (on/off) | candles 2 and 4 each have a body of at least 60% of their own high-low |
| 2-candle lookback (on/off) | the 2 candles right before candle 1 both go the trade's way (sell: both bearish; buy: both bullish, dojis bullish) |
| Orders | limit at 50% of the range, stop at the range end, target 4R, 5R or 6R, no breakeven |
| Hours | candle 4 closes 07:00-19:00 UTC, no US news days, everything flat at 20:30 UTC |
| Markets | XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225; M1, M5, M15, M30, H1, H4 |

## 1. 60% body vs two candles in the trade's direction
All 12 markets and 6 timeframes together, target 5R (R per trade after costs, before costs in brackets):
| Combination | 2011-19 | 2020-22 | 2023-25 |
|---|---|---|---|
| 60% body + 2-candle lookback | -0.344R (-0.010), 11,220 trades | -0.390R (-0.076), 4,243 | -0.372R (-0.047), 3,764 |
| 60% body only | -0.366R (-0.029), 43,223 | -0.361R (-0.050), 16,218 | -0.372R (-0.046), 14,468 |
| 2-candle lookback only | -0.346R (-0.029), 24,430 | -0.338R (-0.037), 10,284 | -0.351R (-0.043), 9,084 |
| Neither | -0.352R (-0.031), 88,322 | -0.331R (-0.032), 36,792 | -0.345R (-0.035), 32,850 |

Side by side, same timeframe and target, both sides at least 100 trades:
| Change | 2011-19 | 2020-22 | 2023-25 |
|---|---|---|---|
| 60% body on instead of off | better in 53% of 30 pairs, +0.006R | 21% of 24, -0.036R | 42% of 24, -0.041R |
| 2-candle lookback on instead of off | better in 60% of 30, +0.025R | 54% of 24, +0.026R | 54% of 24, +0.016R |
| 60% body alone instead of lookback alone | better in 33% of 15, -0.019R | 20% of 15, -0.071R | 40% of 15, -0.049R |

**Answer: the two candles in the trade's direction are the better rule of the two, but only by about 0.02R a trade, far
too little to pay costs of about 0.35R a trade. The 60% body rule does nothing useful.**

## 2. 4R, 5R, 6R: how often the target is reached
60% body + 2-candle lookback, all markets and timeframes:
| Target | Reached 2011-19 / 2020-22 / 2023-25 | Needed with no costs | Needed after costs |
|---|---|---|---|
| 4R | 15.5% / 14.7% / 14.6% | 20.0% | 26.7% |
| 5R | 12.7% / 11.8% / 12.1% | 16.7% | 22.5% |
| 6R | 10.2% / 9.7% / 10.2% | 14.3% | 19.3% |

The target is reached less often than even a zero-cost trade needs. On M30-H4 it is reached by 0-7% of trades: the 20:30
UTC close ends trades before a big target has time to come. By timeframe at 5R (2011-19 / 2020-22 / 2023-25, after costs):
M1 -0.41 / -0.43 / -0.42R; M5 -0.15 / -0.35 / -0.20R; M15 -0.20 / +0.07 / -0.25R; M30 -0.23 / -0.08 / -0.23R; H1 +0.06 /
-0.42 / -0.48R (109 / 51 / 34 trades); H4 21 / 3 / 6 trades.

## 3. The two-week goal: the best mix
Rule fixed in advance: for each of the 12 configurations, keep the market x timeframe cells with at least 50 trades and a
profit after costs in 2011-19; the best mix is the one with the steadiest two-week results in 2011-19. Every trade at 1R
(at 1% risk a trade, R = % of the account).

Chosen: 60% body + 2-candle lookback, 4R, three cells (WTI M5, UK100 M15, GER40 M5; 3 of 72 cells qualified).
| Per two weeks | 2011-19 (learned) | 2020-22 | 2023-25 |
|---|---|---|---|
| Trades | 1.35 | 1.18 | 1.19 |
| Target hits (wins) | 0.29 | 0.15 | 0.18 |
| Fortnights with 2 or more wins | 3.8% | 0% | 1.3% |
| Fortnights that make money | 31% | 19% | 22% |
| Average R | +0.28R (t 1.9) | -0.36R | -0.18R |
| Worst fortnight | -5.7R | -4.2R | -4.6R |

It lost in both later periods: the three cells were the lucky 3 of 72 in 2011-19 (P10). Every other configuration's mix
did the same (12 mixes: all positive in 2011-19 by construction; 3 positive in 2020-22, 3 in 2023-25, none in both).

**Everywhere** (all 72 cells, 60% body + 2-candle lookback, 5R):
| Per two weeks | 2011-19 | 2020-22 | 2023-25 |
|---|---|---|---|
| Trades | 48 | 54 | 48 |
| Wins (5R hits) | 6.1 | 6.4 | 5.8 |
| Fortnights with 2 or more wins | 97% | 99% | 94% |
| Fortnights that make money | 12% | 10% | 10% |
| Average R | -16.4R | -21.2R | -17.7R |

Two wins every two weeks is easy to get; it is not the goal. At 5R a fortnight needs more than 1 win for every 4.4 trades
after costs (22.5%); this gives about 1 in 8.

## 4. The January-October 2026 check: not taken
The pre-registered pass needs the best mix to make money in 2020-22 and 2023-25; it lost in both, so v6 is rejected and a
2026 look cannot change that. January-October 2026 stays unseen for this pattern family, in case a corrected version is
ever worth one look.

## Where this leaves the body-engulf range
Six versions and a gold study: 5,326 settings and conditions, 12 markets, M1-H4, 2011-2025. Every version loses after costs
and sits at about zero before costs; no body size, lookback, timeframe pairing, engulf type, window or target changes that.
