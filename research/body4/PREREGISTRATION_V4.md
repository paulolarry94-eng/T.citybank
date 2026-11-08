# Body-engulf range, version 4 + loss attribution + hit-rate curve — pre-registration (2026-11-08, before any v4 result)

Owner: "what made the biggest loser, the cost, what cost goes high, Asians and news and what, avoid them all; I said test
2RR all the way to 10RR; trade only on safe windows; find the RR that hits 50% of the time and the config that makes that
possible."

## 1. Loss attribution (on v3, already run; descriptive)
v3 main settings (50% entry, stop at the range end, breakeven at 75%, lookback on, 10R), all 12 markets x M1-H4, 2011-22.
Each trade's result split into: price move (bid to bid, gaps included), spread, commission, slippage, swaps; and the gap
part of stop/target fills. Grouped by entry session (Asia 23:00-07:00, London 07:00-12:00, overlap 12:00-16:00, New York
16:00-20:30 UTC), US news day (NFP/CPI/FOMC, New York date) or not, held overnight or not, timeframe, market. The 50
biggest losers classified (overnight gap, news day, Asian session, data hole).

## 2. v4 (`research/truth/strategies/body4_range_v4.py`)
v3 with targets 2R, 3R, ..., 10R and a window: "all" (v3) or "safe" = setups only when candle 4 closes 07:00-19:00 UTC,
none on US news days, every order cancelled and every trade closed at 20:30 UTC daily (no overnight holds, swaps, gaps or
Asian session). Window fixed from market structure (liquidity, rollover, news), NOT picked from results.
Grid: 6 timeframes x 9 targets x 2 windows x entry 2 x breakeven 2 x buffer 4 x lookback 2 = 3,456 configurations, 12
markets. Truth Lab protocol; one 2023-25 look only for a gate-passing selection.

## 3. Which RR is hit 50% of the time
(a) Curve: safe and all windows, breakeven off, no target, entry 50%, buffer 0, lookback on; per timeframe, 12 markets
pooled, 2011-19 and 2020-22: share of trades whose favourable move (bid/ask-correct; the fill minute and the exit minute
left out, the cautious reading) reaches 0.5R, 1R, 1.5R, 2R, 3R ... 10R before the stop or the time exit; and the RR where
it crosses 50%.
(b) Config search: for each target 2R-10R, the configuration (window, entry, breakeven, buffer, lookback, timeframe; 12
markets pooled, >= 200 trades) with the highest share of trades reaching the target in 2011-19, and its hit rate and R per
trade in 2020-22 (learn-then-check). A config "makes 50% possible" only if it hits >= 50% in both periods.
