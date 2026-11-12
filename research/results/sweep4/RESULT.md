# Pivot-sweep body-engulf range (owner, 2026-11-12) — REJECTED after costs; the sweep is real but small

Pre-registration: `research/sweep4/PREREGISTRATION.md` (committed 796b079 before any result). Lab: `research/results/truth/sweep4_pivot_v1/`.
Study: `research/sweep4/study.py` -> `study.json`. Examples: `examples/` (2019 trades). Tests: `research/truth/tests/test_sweep4.py`.

## Outcome
- **0 of 504 settings pass the lab** (12 markets pooled; 24% positive in 2011-19, 3% positive in 2011-19 and 2020-22,
  median -0.15R a trade). 6,048 market x timeframe cells; 1,403 had 60+ trades in 2011-19; 149 of those were positive,
  and 37 of the 149 were still positive in 2020-22.
- **The sweep helps a little.** The same 60%-body patterns with no sweep nearby lose more. With the sweep on candle 1 or 2,
  the setting beat its no-sweep twin in 83% of 203 pairs in 2011-19 (+0.12R a trade; +0.09R before costs), but only 60%
  of 175 pairs in 2020-22 (+0.03R; +0.01R before costs). It is the first change in this family with a raw effect, and
  it faded.
- **No bug.** Two independent engines agree trade for trade (2,089 + the test set), the look-ahead check passes, and
  every swept pivot is a real, already-confirmed pivot (a pivot cannot be swept before it is confirmed). The losses are
  costs larger than the raw edge, as in v1-v7 (P1).
- **Why pivots "appear randomly":** a pivot of 10/10 is only known when its 10th right-hand candle closes (50 minutes later
  on M5). TradingView then draws the label back on the pivot candle. The grey triangles on the example charts mark when
  each label could first appear live.

## Timeframes (sweep on candle 1 or 2; median over the 84 settings; 12 markets pooled)
| Timeframe | trades 2011-19 (median) | R a trade 2011-19 | before costs | R a trade 2020-22 | before costs |
|---|---|---|---|---|---|
| M1 | 2,522 | -0.47 | -0.02 | -0.34 | +0.09 |
| M5 | 633 | -0.18 | +0.07 | -0.25 | +0.01 |
| M15 | 222 | -0.17 | +0.04 | -0.29 | -0.14 |
| M30 | 97 | +0.08 | +0.26 | -0.33 | -0.19 |
| H1 | 52 | -0.19 | -0.06 | -0.08 | +0.00 |
| H4 | under 30 | - | - | - | - |
No sweep (control), M5: -0.33R (-0.02R before costs) in 2011-19. M30 is the only timeframe positive in 2011-19, but
it had 4-13 trades per market in nine years, and it reversed in 2020-22.

## Stops (median R a trade over settings with 30+ trades)
| Stop | 2011-19 | share positive | 2020-22 | share positive |
|---|---|---|---|---|
| Range end | -0.20 | 15% | -0.28 | 2% |
| Range end + 20% | -0.19 | 13% | -0.25 | 9% |
| Pivot trailing stop | -0.15 | 17% | -0.28 | 5% |
No stop style makes it positive; the trailing stop loses least in 2011-19, the 20% buffer in 2020-22.

## Targets and win rate (M5, pivots 10/10, sweep on candle 1 or 2, range stop, 12 markets)
| Target | trades 2011-19 | win rate | break-even win rate (no costs) | R a trade | before costs | 10-trade rounds positive | 2020-22 R a trade |
|---|---|---|---|---|---|---|---|
| 3R | 351 | 23% | 25% | -0.21 | +0.04 | 40% | -0.17 |
| 5R | 456 | 17% | 17% | -0.16 | +0.11 | 40% | -0.19 |
| 8R | 511 | 12% | 11% | -0.16 | +0.13 | 29% | -0.04 |
| 10R | 528 | 11% | 9% | -0.12 | +0.18 | 33% | -0.07 |
| 15R | 551 | 9% | 6% | -0.05 | +0.26 | 47% | -0.04 |
| nearest pivot (>= 3R) | 447 | 16% | - | -0.11 | +0.18 | 39% | -0.17 |
| second pivot | 396 | 13% | - | -0.05 | +0.23 | 49% | -0.05 |
Win rates are low by construction: a 3R-15R target is hit 9-23% of the time. About 70 trades a year on 12 markets
(about 2.7 every two weeks); 10 trades take about 4 two-week cycles.

## The best combinations (chosen on 2011-19, then 2020-22 unchanged)
| Cell | 2011-19 trades, R a trade, win | 2020-22 trades, R a trade, win |
|---|---|---|
| EURUSD M5, pivots 10, sweep candle 1/2, range stop, 15R | 98, +1.63R, 19% | 22, +0.32R, 9% |
| EURUSD M5, same, 20% buffer, 10R | 98, +1.17R, 24% | 22, -0.09R, 9% |
| EURUSD M5, same, trailing stop, 15R | 99, +1.39R, 26% | 22, +0.46R, 14% |
| WTI M5, pivots 5, sweep near, range stop, 8R | 76, +0.94R, 25% | 47, -0.41R, 9% |
| EURUSD M15, pivots 5, sweep near, trailing, 10R | 89, +0.72R, 27% | 27, +0.24R, 30% |
EURUSD M5 is the one lead. 35 of its 42 sweep settings were positive in 2011-19, but only 3 were positive in both
periods, and the same rule on GBPUSD (3 of 42), USDJPY (3 of 42), EURGBP (10 of 42) and gold (13 of 42) was not. It was
picked as the best of 1,403 cells; with that many tries the best looks this good by luck (expected best t about 3.8;
its t is about 2.7). Five 15R winners make 45% of its profit.

## What was not opened
2023-25 and Jan-Oct 2026: no setting passed 2011-22, so no look was taken. A single logged look at one setting, named
before looking, stays available for the owner to decide.

## Disclosed
- Before the study, gold Jan-Jun 2019 numbers for 4 settings were seen in the engine parity check (8-14 trades); the grid
  was fixed in the pre-registration and not changed.
- Owner's two screenshots could not be replayed: the DAX chart (about 25,800) is later than our GER40 data, and the EURUSD
  pivot sequence (1.10990, 1.10838, 1.11003) is not in our 2011-25 data.
