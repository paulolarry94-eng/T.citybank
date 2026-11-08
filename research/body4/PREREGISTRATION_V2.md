# Body-engulf 4-candle range, version 2: 1:2 and 1:1 targets — pre-registration (2026-11-08, before any v2 result)

Owner: "try 1:2R and 1:1R" (after v1 at 4R was rejected: research/results/body4/RESULT.md).
Strategy `research/truth/strategies/body4_range_v2.py` = v1 (`PREREGISTRATION.md`) with ONE change: the target is 2R or 1R
instead of 4R, and the breakeven level stays at 50% of the target (the owner's rule): +1R for 2R, +0.5R for 1R.
Everything else is unchanged: pattern, lookback, "no intent" skip, 50% / 70% entry, stop buffers, waiting orders (first fill
removes the others), wider opposite range wins, cancel when price reaches the target before the order fills, Friday close,
RoboForex Prime costs (spread decides fills, commission per trade, slippage on stops), the lab's swaps.

Known effect of the rules, stated before the run: with a small target the target can sit INSIDE the range (70% entry: 1R
target = low + 0.4 x range for a sell; 2R = low + 0.1 x range), so price is often already past it when candle 4 closes and
the owner's cancel rule removes the order at once. Small targets therefore trade less (Jan-Mar 2019 gold M5, main settings:
68 trades at 4R, 48 at 2R, 27 at 1R; 6 at 1R with the 70% entry). Counts only; no result was looked at.

Grid: 6 timeframes (M1-H4) x target 2 x entry 2 x breakeven 2 x buffer 4 x lookback 2 = 384 configurations, 12 markets.
The Truth Lab decides (gate on 2011-19, selection by edge quality, validation 2020-22, walk-forward, stress, deflated
Sharpe over 384) and logs ONE 2023-25 look only for a gate-passing selection. Reported, never used to select: main settings
(50%, buffer 0, breakeven on, lookback on) at 4R (v1), 2R and 1R side by side with win rates against the win rate each
target needs after costs; paired comparisons (breakeven on/off within each target, 2R vs 1R); before-cost results.
