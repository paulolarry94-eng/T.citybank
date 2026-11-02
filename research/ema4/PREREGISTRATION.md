# Owner's 4-flip EMA pattern — pre-registration (2026-11-02, before any backtest result)

Pattern, detector, replay of the owner's six charts: `research/ema4/README.md`. Strategy: `research/truth/strategies/ema4_flip_v1.py`.
Tests: `research/truth/tests/test_ema4.py` (detector, 6), `test_ema4_strategy.py` (orders, 4).

## Owner's answers (2026-11-02)
| Question | Owner | Rule |
|---|---|---|
| 1 Entry | "test both 50% and close" | `mid50`: limit at 50% of the 4th candle, live 3 candles of the pattern timeframe; `close`: market at the 4th candle's close |
| 2 Doji on the EMA | "no" | a candle needs a body to count as a breakout |
| 3 Stop | "test it out" | 4th candle extreme (`c4`) or all four candles' extreme (`all4`), + 0 / 0.1 / 0.25 / 0.5 ATR(14) |
| 4 After the target | "close daily" | target, stop, or the daily close at 20:30 UTC (before the rollover) |
| 5/6 Hours, timeframes, markets | "All hours, all timeframes, all markets ... find where, how and what time it works most" | M5 M15 M30 H1 H4, 12 markets, 24 hours; plus the where/when study below |
| 7 A+ / B+ | "test both" | `A` (A+ only) and `AB` (A+ and B+) |
| 8 Overlaps | "after a new order is found in an opposite direction the previous is deleted" | a new pattern deletes the pending order (a newer same-direction pattern replaces it too); one position per market, patterns while it is open are skipped |
| 9 News | "skip" | NFP, CPI, FOMC days skipped |
| 10 Minimum stop | "yes" | stop >= 3 x the round-trip cost |
Targets: 1R-4R (owner's message). Costs: RoboForex Prime published averages; no swaps (closed daily).

## Test 1: the Truth Lab (unchanged protocol)
640 configurations (5 timeframes x entry 2 x stop 2 x buffer 4 x target 4 x grade 2), 12 markets, fills before 2023; gate,
neighbours, validation 2020-22, walk-forward, stress, deflated Sharpe over 640; one 2023-25 look only for a configuration that
passes; selection by edge quality s (cycle-centric). Control: the same trade on rejected four-flips (`controls.py`). Cycle
league of all 640 (`cycles_league.py`).

## Test 2: where and when (`research/ema4/where_when.py`), learn-then-check, fixed now
Cells: market (12) x timeframe (5) x session of the 4th candle's close (Asia 23:00-07:00, London 07:00-12:00, New York
12:00-20:30 UTC) = 180 cells; inside each cell the 128 trade settings. Also the 24 hours of the day (pooled markets).
- LEARN on 2011-19 only: per cell, the setting with the highest t after costs among those with >= 100 trades.
- PASS if that t >= 3 AND, untouched by the choice, the same setting in 2020-22 has mean R > 0 with t >= 2 (>= 30 trades).
- Expected by luck: with no edge anywhere, about 2% of cells that reach t >= 3 in-sample pass 2020-22 at t >= 2; the report
  states how many cells reached each step, so luck can be compared.
- Passing cells get Jan-Oct 2026 (Exness data for XAUUSD/EURUSD/GBPUSD/USDJPY, HistData EURGBP) and are proposed for the
  one 2023-25 look (made only after the owner sees the list; the look is logged).
- Descriptive only (no selection): results by hour of day, session, market and timeframe for the lab's selected setting.

## Priors
Every earlier idea of this family was rejected (owner's 4-leg engulfing SOP, Leg 34, the 3:30 retest; M5 EMA/engulfing
patterns with limit entries): about zero before costs; costs 0.1-0.2R (P1, P2, P14). The pocket scan of Leg 34 over 11
markets x 6 timeframes x 3 sessions found no surviving cell (P21). Expectation: rejection.
