# Pivot-sweep v2 (the owner's chart reading) + portfolio Pareto (2026-11-12)

Pre-registration: `research/sweep5/PREREGISTRATION.md` (7b6add8). Lab: `research/results/truth/sweep5_pivot_v2/`. Study:
`study.json`. Look: `LOOK.json` (rule committed before it ran). Pareto: `PARETO.md`, `pareto.json`. Tests: `test_sweep5.py`.

## Outcome
- **The "issue" was the rule reading, not a coding error.** Our pivots match your TradingView labels to 0-0.7 pip (your chart
  clock is UTC+1). v1 missed your trades because of five readings: strict engulf (you use "closes beyond the open"), 60%
  bodies, dojis counted as neither colour, the sweep only on candle 1-2, and targets fixed at candle 4 with the order
  cancelled when price reached that target first. v2 follows your charts: your 28-29 Oct night trade is reproduced exactly
  (sell 1.11582 at 02:09 UTC, stop 1.11600, TP1 1.11340, TP2 1.11226, +21.5R). The 29 Oct 11:25 trade misses by 0.2 pip in our
  feed (our high 1.11503, entry 1.11505). Your 5 Nov trade is not a setup in our feed (candle 4 body 47%) and was stopped at
  17:40 UTC on your own chart before the drop. 11-12 Nov has no data yet.
- **Found and fixed while testing:** a bug in the new engines' partial mode (first exit aimed at TP2); caught by a unit test
  before any result was used; both engines fixed and re-run; 7 tests pass, fast = reference trade for trade.
- **The pattern still loses after costs.** v2 gives many more trades (M5 ~700 a year on 12 markets vs ~70 in v1), but 0 of 120
  settings pass the lab and none is positive in 2011-19 pooled. Before costs about breakeven (profit factor 0.94-1.03); after
  costs 0.54-0.82. Win rates 12-20% with average wins of 3.5-7.5R.
- **Bigger stop:** the wide stop (+0.5 x range) loses less (median -0.19R vs -0.28R a trade) but stays negative. 55% of stopped
  M5 trades do reach TP1 within a day, but first run a median 2.9R past the stop; a stop 1R wider saves only 14% of them.
- **Three thin legs survive** the era rule and the logged look (EURGBP H1, NAS100 H1, GBPUSD M15; 8-15 trades a year each;
  picked from 1,440 cells, about the number luck would pass at the era step). Added to the 10-leg timeless mix they lift the
  two-week Sharpe from 0.20 to 0.24 on 2023-Oct 2026 and keep every year 2011-25 positive. Weak candidates for a demo, not proof.
- **80-120% a year inside a 3.6% envelope is not possible** with any edge found: the best mix makes about 6.5% a year in
  backtest at 3.6% (5.3% in 2023-25, 1.0% in Jan-Oct 2026); 80% a year needs a 44% drawdown envelope.

## v2 by timeframe (12 markets pooled, 2011-19, sweep in the last 6 candles, range stop, 96-candle order life)
| Timeframe | trades | win | avg win / loss R | R a trade after costs | PF | before costs R / PF |
|---|---|---|---|---|---|---|
| M1 | 35,649 | 12% | 5.13 / -1.33 | -0.54 | 0.54 | -0.02 / 0.96 |
| M5 | 10,027 | 14% | 4.87 / -1.22 | -0.35 | 0.66 | +0.01 / 1.02 |
| M15 | 3,785 | 16% | 4.24 / -1.16 | -0.29 | 0.70 | -0.03 / 0.96 |
| M30 | 1,852 | 16% | 4.32 / -1.13 | -0.25 | 0.73 | -0.02 / 0.98 |
| H1 | 835 | 20% | 3.46 / -1.07 | -0.18 | 0.79 | +0.00 / 1.01 |
(Partial 60/40 exit shown; all-at-TP1 and all-at-TP2 within 0.03R of it.)

## The logged look (20 candidate cells; pass = positive in 2023-25 and in Jan-Oct 2026 where data exists)
| Cell | 2011-22 | 2023-25 | Jan-Oct 2026 | |
|---|---|---|---|---|
| GBPUSD M15 · sweep=now, stop=range, life=24, exit=partial | +0.14R (180) | -0.15R (38) | +1.00R (12) | fail |
| GBPUSD M15 · sweep=now, stop=range, life=24, exit=tp1 | +0.11R (180) | -0.12R (38) | +0.69R (12) | fail |
| GBPUSD M15 · sweep=now, stop=range, life=96, exit=partial | +0.11R (205) | -0.25R (45) | +0.98R (15) | fail |
| GBPUSD M15 · sweep=now, stop=range, life=96, exit=tp1 | +0.09R (205) | -0.22R (45) | +0.91R (15) | fail |
| GBPUSD M15 · sweep=now, stop=wide, life=24, exit=partial | +0.09R (180) | +0.03R (38) | +0.27R (12) | PASS |
| GBPUSD M30 · sweep=recent, stop=wide, life=24, exit=partial | +0.34R (187) | -0.29R (38) | -0.14R (11) | fail |
| GBPUSD M30 · sweep=recent, stop=wide, life=24, exit=tp1 | +0.27R (189) | -0.19R (39) | -0.20R (11) | fail |
| GBPUSD M30 · sweep=recent, stop=wide, life=24, exit=tp2 | +0.41R (186) | -0.19R (38) | -0.06R (11) | fail |
| GBPUSD M30 · sweep=recent, stop=wide, life=96, exit=partial | +0.29R (222) | -0.22R (49) | -0.14R (11) | fail |
| GBPUSD M30 · sweep=recent, stop=wide, life=96, exit=tp1 | +0.22R (223) | -0.16R (50) | -0.20R (11) | fail |
| GBPUSD M30 · sweep=recent, stop=wide, life=96, exit=tp2 | +0.39R (221) | -0.13R (49) | -0.06R (11) | fail |
| EURGBP H1 · sweep=recent, stop=wide, life=24, exit=partial | +0.44R (102) | +0.31R (28) | +0.11R (7) | PASS |
| EURGBP H1 · sweep=recent, stop=wide, life=24, exit=tp1 | +0.45R (102) | +0.40R (28) | +0.22R (7) | PASS |
| EURGBP H1 · sweep=recent, stop=wide, life=24, exit=tp2 | +0.47R (102) | +0.19R (28) | -0.12R (7) | fail |
| EURGBP H1 · sweep=recent, stop=wide, life=96, exit=partial | +0.35R (115) | +0.22R (32) | +0.11R (7) | PASS |
| EURGBP H1 · sweep=recent, stop=wide, life=96, exit=tp1 | +0.36R (115) | +0.32R (32) | +0.22R (7) | PASS |
| EURGBP H1 · sweep=recent, stop=wide, life=96, exit=tp2 | +0.37R (115) | +0.05R (32) | -0.12R (7) | fail |
| WTI M15 · sweep=now, stop=wide, life=24, exit=tp2 | +0.13R (135) | -0.15R (40) | no data | fail |
| NAS100 H1 · sweep=recent, stop=range, life=24, exit=tp1 | +0.38R (92) | +0.82R (19) | no data | PASS |
| NAS100 H1 · sweep=recent, stop=range, life=96, exit=tp1 | +0.42R (99) | +0.73R (20) | no data | PASS |

Legs (best 2011-22 edge quality per market x timeframe among the passing cells): GBPUSD | M15 | sweep=now, stop=wide|life=24|exit=partial; EURGBP | H1 | sweep=recent|stop=wide|life=24|exit=tp1; NAS100 | H1 | sweep=recent|stop=range|life=96|exit=tp1.

## Loser study (stopped trades, all-at-TP2 setting, range stop)
| Timeframe, sweep | stopped | reached TP1 within a day | median R past the stop first | saved by a stop +1R / +3R wider |
|---|---|---|---|---|
| M1 | now | 17901 | 74% | 4.06 | 15% / 31% |
| M1 | recent | 47057 | 75% | 4.25 | 15% / 31% |
| M5 | now | 4553 | 55% | 2.98 | 14% / 28% |
| M5 | recent | 12831 | 55% | 2.88 | 14% / 28% |
| M15 | now | 1578 | 34% | 1.99 | 10% / 23% |
| M15 | recent | 4459 | 35% | 1.87 | 11% / 23% |
| M30 | now | 709 | 20% | 1.45 | 9% / 15% |
| M30 | recent | 2171 | 22% | 1.24 | 10% / 17% |
| H1 | now | 322 | 10% | 1.39 | 4% / 8% |
| H1 | recent | 923 | 12% | 1.09 | 5% / 9% |

## Portfolio Pareto
See `PARETO.md` (A / B / C with every leg's pair, timeframe, weight, win rate, average win/loss, expectancy, PF, trades a
month, base and average risk, projections at 3.6%, 8%, 15%, 25%).

## Disclosed
- The v2 replay of 26 Oct-6 Nov 2026 EURUSD M5 (to check the owner's trades) also showed 5 other trades, all losses.
- 2023-25 and 2026 had been seen for this family (v1 look on EURUSD M5); the v2 look covered different markets/timeframes.
- v2 legs use RoboForex Prime costs; the survivors Exness Zero; WTI/NAS100 have no 2026 data.
