# Body-engulf range v5: strict vs loose engulfing, timeframe layering, and the 2023-25 test (2026-11-08)

**Verdict: rejected, and the unseen 2023-25 data confirms it.** All 4 settings chosen in advance from 2011-22 lost money
in 2023-25 (-0.07R to -0.38R a trade). Loose engulfing finds about 3 times as many trades, but each one loses about the same.
Layering (the big timeframe and the small one agree, entry on the small) cuts the loss by a little (+0.03 to +0.06R a trade)
but throws away 98-99% of the trades and turns nothing positive. Of 448 settings with at least 100 trades in 2023-25, 16
were positive (4%), all on H4 without layering; the best made +0.05R a trade (t 1.1) and lost -0.10R a trade in 2011-22.

- Pre-registered before any v5 result: `research/body4/PREREGISTRATION_V5.md`.
- Truth Lab: `research/results/truth/body4_range_v5/REPORT.md` (0 of 768 settings pass the development gate).
- All tables: `TABLES.md` (built from the saved results by `research/body4/tables_v5.py`).
- The 2023-25 look: `LOOK_2023_25.json` (the 4 settings were written to it before any 2023-25 number was computed) and
  `research/results/truth/body4_range_v5/oos_log.json` (all 768 settings logged once).
- **2023-25 is now used up for the body-engulf family.** The only unseen data left is January-October 2026.

## What was tested
| Item | Rule |
|---|---|
| Strict engulf ("body") | candles 2 and 4 open at or beyond the previous close and close beyond the previous open (the whole previous body is covered) |
| Loose engulf | candles 2 and 4 only close beyond the previous candle's open (a gap at the open is allowed, as in your silver chart) |
| Layering | the small-timeframe setup counts only if the same-direction setup formed on the bigger timeframe, its candle 4 closing at most 2 big candles earlier. Pairs: M1 with M15, M5 with H1, M15/M30/H1 with H4, H4 with D1. Entry, stop and target come from the small setup |
| Everything else | safe window (setups 07:00-19:00 UTC, no US news days, everything flat at 20:30 UTC); entry at 50%; stop at the range end or 20% beyond; targets 2R, 3R, 5R, 10R; breakeven at 75% of the target on/off; lookback 3 of 5 on/off (dojis bullish) |
| Size | 768 settings x 12 markets (XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225), M1-H4 |
| Costs | RoboForex Prime published spread and commission, slippage on stops. Swaps are zero: nothing is held past 20:30 UTC, so the swap-free result is the same number. Before costs (a zero-cost account) is in `TABLES.md` section 3 |

## 1. Strict vs loose engulfing: loose is not better
Each pair is the same timeframe and settings, with only the engulf rule changed (both sides at least 100 trades).
| Period | Pairs | Loose better in | Change in R per trade |
|---|---|---|---|
| 2011-19 | 240 | 26% | -0.013R |
| 2020-22 | 182 | 56% | +0.004R |
| 2023-25 | 176 | 55% | +0.005R |

At the main 2R settings (all timeframes, 2011-22), loose engulfing gave 154,638 trades against 52,151 for strict, about 3
times as many, at the same loss per trade (M5: -0.257R vs -0.240R in 2011-19). More trades of a losing setup lose more.

## 2. Layering: a small improvement on very few trades, still negative
| Period | Pairs | Layering better in | Change in R per trade |
|---|---|---|---|
| 2011-19 | 176 | 62% | +0.030R |
| 2020-22 | 102 | 75% | +0.060R |
| 2023-25 | 96 | 56% | +0.027R |

| Main 2R settings, all timeframes | Trades 2011-22 | Trades 2023-25 |
|---|---|---|
| Strict engulf, no layering | 52,151 | 13,376 |
| Strict engulf + layering | 360 (0.7% kept) | 65 |
| Loose engulf, no layering | 154,638 | 48,889 |
| Loose engulf + layering | 2,578 (1.7% kept) | 835 |

With strict engulfing, layering leaves about 30 trades a year across all 12 markets and 6 timeframes: too few to judge or
to trade. With loose engulfing, M5 + H1 is the busiest pair (379 trades in 2011-19, about 3.5 a market a year).
**Before costs** (main settings, `TABLES.md` section 3), 23 of 96 cells were positive in both 2011-19 and 2020-22, all
small: where a cell had more than 100 trades, at most +0.17R a trade with t below 2. Examples: M15 without layering (+0.005 to
+0.108R; M15 costs about 0.18R a trade) and loose + layering on M5 at 3R-10R (+0.11 to +0.17R, t 1.2-1.9, then +0.03 to
+0.08R, t 0.3-0.6; M5 costs about 0.2-0.26R, so after costs it lost: at 2R -0.11R in 2011-19, -0.19R in 2020-22, -0.26R in
2023-25).
Only one cell beat its costs in both periods: **M15 strict + layering (H4 big) at 3R and 5R**, after costs +0.07 to +0.21R
in 2011-19 and +0.09 to +0.56R in 2020-22, but on 25-28 and 11 trades (t below 1), about 3 trades a year across all 12
markets. That is too few to tell from luck, and below the 300 trades the pre-registration required for a primary. In
2023-25 it had 5 trades and lost (-0.12R to -0.20R a trade).

## 3. The 2023-25 test (one logged look, decided by you)
The 4 PRIMARY settings: for each engulf x layering combination, the best edge quality on 2011-22 with at least 300 trades,
chosen and saved before the look. "R a year" = R per trade x trades a year, 12 markets together (at 1% risk a trade, about
the same number in % of the account, before compounding).
| Combination | Setting | 2011-19 | 2020-22 | 2023-25 | t (2023-25) | R a year (2023-25) | Markets positive (2023-25) |
|---|---|---|---|---|---|---|---|
| Strict, no layering | M15, 10R, breakeven on, stop 20% beyond, lookback on | -0.085R (3,688) | -0.017R (1,292) | **-0.129R** (1,236) | -2.43 | -53R | 1 of 12 |
| Strict + layering | M1 (M15 big), 10R, breakeven on, stop 20% beyond, lookback on | -0.241R (232) | +0.016R (102) | **-0.384R** (74) | -1.18 | -9R | 4 of 12 |
| Loose, no layering | H1, 10R, breakeven off, stop at the range end, lookback off | -0.098R (5,060) | -0.015R (1,831) | **-0.133R** (1,836) | -3.29 | -81R | 1 of 12 |
| Loose + layering | M5 (H1 big), 5R, breakeven off, stop 20% beyond, lookback on | -0.034R (501) | +0.213R (233) | **-0.067R** (229) | -0.50 | -5R | 4 of 12 |

The one setting that looked good in 2020-22 (loose + layering, +0.213R) lost in 2023-25: its 2020-22 result was luck, as
P10 warns. Per-market results are in `TABLES.md` section 4.

**All 768 settings in 2023-25 (description only; picking one from this list would be hindsight):**
| Group | Settings with >= 100 trades | Positive | Median R per trade |
|---|---|---|---|
| Strict, no layering | 160 | 0 | -0.192R |
| Strict + layering | 16 | 0 | -0.200R |
| Loose, no layering | 192 | 16 | -0.125R |
| Loose + layering | 80 | 0 | -0.245R |
| All | 448 | 16 (4%) | -0.178R |

By timeframe (median R per trade, 2023-25): M1 -0.38R, M5 -0.22R, M15 -0.13R, M30 -0.06R, H1 -0.15R, H4 -0.004R. H4 is
about zero because its costs are smallest (0.06R a trade): 16 of its 32 settings were positive, a coin flip. The best of
all, H4 loose 2R (+0.052R, 331 trades, t 1.12), lost -0.099R a trade over 1,368 trades in 2011-22 (t -4.77).

## 4. The cycle goal
+2% per 10-trade cycle inside a 3.6% drawdown needs an edge quality of about 0.42 a trade (P28). The 4 primaries scored
-0.03 to -0.14 in 2023-25. There is nothing here to size.

## 5. Where this leaves the body-engulf range
- Five versions, 5,184 settings, 12 markets, M1-H4, 2011-2025: every version lost after costs, about zero before costs, and
  the unseen 2023-25 check failed. Strict or loose engulfing, layering, lookback, dojis, breakeven, 1R-10R targets, buffers
  and safe windows were all tried. With that many tries, a lucky setting needs a t of about 4 to count; the best in
  2023-25 had 1.1.
- The pattern family is closed in backtests. If you see an edge by eye, the honest test is a forward log: mark each setup
  (entry, stop, target, and why you take or skip it) before the outcome, and score about 100 of them.
