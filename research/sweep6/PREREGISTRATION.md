# Deep M1 study of the pivot-sweep range: payout structure, entry conditions, scanner, portfolio (owner, 2026-11-12)
Written and committed before any result of this study. Code: `research/sweep6/`. Results: `research/results/sweep6/`.

Owner: "a deep, reliable, consistent pattern test on M1 ... take out cost, swaps, any friction ... two ways to win: the
optimal entry conditions and the best payout structure ... Test A: TP2 as the only TP, SL, breakeven at 75% of the journey
... Test B: 3R-10R fixed targets ... most money per 10 trades at a fixed 1% ... then find the entry condition that loses the
least: study the winners (sweep size in pips, candle 2 or 4 sweep, max candles after the sweep, a range from the sweep,
combinations), a pattern the losers don't have ... if nothing, study the losers ... 40%, 50% or 60% body ... then the perfect
scanner on all timeframes and markets, without costs then with costs ... Monte Carlo survivors make the portfolio ...
professional backtest report, examples, optimal account size."

## Priors (told to the owner)
Four earlier winner-anatomy / condition-mining studies were all rejected (Leg 34 hunter steps 1-2, SOP winning conditions,
gold body-engulf characteristics; P21: the anatomy of winners cannot be traded when the setup has no raw edge). What differs
here: friction removed on purpose (a pure search for raw edge), M1 (the most examples), pivot-sweep features never studied
before (sweep depth, sweeping candle, candles since the sweep, stop beyond or inside the sweep wick), and the owner's
corrected rule reading (v2). The base rule had about zero raw edge in v2 (profit factor 0.94-1.03 before costs).

## Data and periods (fixed)
12 markets: XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 (M1 bid bars).
LEARN 2011-2015 (all discovery), CONFIRM 2016-2019 (every finding must hold here), VALIDATE 2020-2022 (reported, never used
to choose), HOLDOUT 2023-2025 + Jan-Oct 2026 (2026 only where data exists: EURUSD, GBPUSD, USDJPY, EURGBP, XAUUSD; GER40 to
6 Nov): one logged look, only for survivors of phases 3-4, rule written before it runs.

## The setup (as v2, the owner's chart reading), studied on M1 candles, executed on M1
SELL (BUY is the mirror): candle 1 bullish (doji = bullish), candle 2 bearish closing below candle 1's open (loose engulf),
candle 3 bullish, candle 4 bearish closing below candle 3's open. Pivots High/Low 10/10. Range = candle 4's low to the highest
high of the four; sell limit at 60% up; stop at the range high. The order waits up to 60 candles and is cancelled if price
reaches the stop first, at Friday 20:30 UTC, or in the weekend window; no fills 20:30-23:00 UTC (as v2).
- Phase 1 base = the owner's current rule: bodies of candles 2 and 4 >= 50%, a live pivot high swept by a candle from 6
  before candle 1 through candle 2.
- Phase 2 superset = bodies >= 40%, a sweep by any candle from 10 before candle 1 through candle 4, plus the setups with no
  sweep in that window (control).
Each setup is simulated ALONE (no one-trade-at-a-time, no order replacement) so every setup has its own outcome.

## Outcomes, frictionless (no spread, commission, slippage or swaps)
All structures are followed in one pass per filled setup, minute by minute, until each is closed, Friday 20:30 UTC (closed
at the last price), or a data hole (trade dropped). Same-minute stop and target: stop first (pessimistic); the share of such
minutes and the target-first (optimistic) result are reported for the headline structures. The fill minute can only stop out.
Structures (R = multiples of entry-to-stop):
- Test A: `TP2` (all at the second live pivot past the entry, known at the fill) and `TP2-BE75` (stop moves to the entry
  once price has covered 75% of the distance to TP2).
- Test B: fixed `3R` ... `10R` (no breakeven) and `3R-BE75` ... `10R-BE75`.
- References: `1R`, `2R`, `15R`, `20R`, `TP1` (all at the nearest live pivot), `P60` (60% at TP1, rest at TP2, stop to the
  entry after TP1).
Also recorded: fill delay, maximum favourable excursion before the stop, adverse excursion, holding time, and for stopped
trades whether price reached TP1 / TP2 / +3R within a day after the stop and how far past the stop it went first.

## Phase 1: payout structure (Phase 1 base, M1, 12 markets pooled)
Per structure and period: trades, win rate, average win and loss, R a trade, R per 10 trades (mean; and over consecutive
10-trade blocks in time order: median, share positive, 10th percentile, worst), longest losing streak. Choice: the highest
frictionless R a trade on LEARN; CONFIRM and VALIDATE reported. The owner's "per 10 trades" examples (10R with 3 wins and 7
losses; 5R with 6 wins and 4 losses) are compared with the measured win counts per 10 trades.

## Phase 2: entry conditions (superset, M1, outcome = R under the Phase 1 structure, frictionless)
Features known when candle 4 closes (fill delay is known at the fill and is used only as an order-expiry rule):
bodies of candles 2 and 4 and their minimum (40/50/60/70% bins); strict-engulf flags; the sweeping candle (candle 4, 3, 2,
1, the candle before 1, 2-4 before, 5-10 before, none); candles from the sweep to candle 4; sweep depth beyond the swept
pivot (in ATR(14) units, in R, and in pips for the four FX pairs: 0-1, 1-2, 2-3, 3-5, 5-10, 10+); sweep candle closed back
inside or not; pivots swept (1, 2, 3+); pivot age; stop beyond or inside the sweep extreme (distance in R); pull-back from the
sweep extreme to candle 4's close (ATR units); range and risk in ATR units; candle 4 / candle 3 and candle 2 / candle 1 size
ratios; candle 4 close position in the range; hour (UTC session buckets) and weekday; momentum over 60 and 1,440 minutes
signed with the trade (ATR / day-range units); volatility regime (ATR14 / ATR over 1,440 minutes); position in the past day's
range; room to TP1 and TP2 at candle 4 (R); a target-side sweep in the window (two-sided); fill delay (candles).
Bins: quintiles set on LEARN (pooled; scale-free units) or the categories above.
Tests:
1. Single conditions: a bin is a CONSISTENT IMPROVEMENT if its mean R beats the rest of its period's setups with t >= 3 in
   LEARN and t >= 2 in CONFIRM, same direction (n >= 300 in LEARN, >= 200 in CONFIRM); a CONSISTENT EDGE if its own mean R
   is above 0 with t >= 3 in LEARN and t >= 2 in CONFIRM.
2. Winners vs losers: standardized mean difference and Kolmogorov-Smirnov distance per feature, LEARN and CONFIRM.
3. Pairs: the 8 features with the widest LEARN bin spread; every pair of their bins; same CONSISTENT EDGE test.
4. Loser anatomy: immediate failures (best excursion < 0.3R), reversals (reached >= 1R first), wick stops (stop exceeded by
   < 0.2R, then +1R within 60 minutes), breakouts (price ran > 3R past the stop within a day); shares by feature bin.
The number of tests and the expected false passes are reported.
Scanner rule (greedy, LEARN only, checked on CONFIRM at each step): start from the superset; add the passing condition
(single or pair, CONSISTENT IMPROVEMENT or EDGE) that raises LEARN R a trade the most; keep it only if CONFIRM R a trade
does not fall; stop when no condition adds >= 0.02R with t >= 3 on LEARN, or after 4 conditions. Then the payout structure is
re-chosen on LEARN for that rule. If no condition passes, the scanner is the Phase 1 base, said plainly.

## Phase 3: the scanner on every timeframe and market (Truth Lab: `research/truth/strategies/sweep6_scanner_v1.py`)
M1, M5, M15, M30, H1, H4 x 12 markets; one trade at a time per market and timeframe (as v2); frictionless table, then
RoboForex Prime costs + swaps (lab standard elsewhere) table; development 2011-19, validation 2020-22 (lab --no-look).

## Phase 4: candidates, Monte Carlo, the look
Candidate cell (market x timeframe): with costs, R a trade > 0 in each of 2011-14, 2015-18, 2019-22 (>= 20 trades each).
Monte Carlo: 10,000 one-year paths resampling the cell's 2011-22 trades at its yearly trade count, 1% risk: survives if the
chance of a losing year <= 20% and the median worst drawdown within a year <= 10%. Survivors get one logged look (2023-25 and
Jan-Oct 2026): pass = R a trade > 0 in 2023-25 and in 2026 where data exists.

## Phase 5: portfolio and report
Portfolio = look survivors + the current best mix (Timeless 10 + v2 legs, PARETO.md C), weights matching the survivors'
volatility, risk per trade set on 2011-22 for 3.6% and 8% envelopes (as timeless_mix.py). Report over every year 2011-Oct
2026 with the holdout marked: equity, drawdowns, yearly and monthly returns, Sharpe/Sortino/Calmar, trade statistics, cost
stress (costs x1.5, swaps x2), swap-free separately, correlation of legs, Monte Carlo, examples (chosen by rule: the first
winners and losers of 2019 on the scanner's best cell, not hand-picked), and account size (the smallest account where 0.01-lot
steps keep each leg within 25% of its target risk on its median stop; contract sizes are standard specifications, to be
confirmed with mt5/NorthStarExport.mq5).
If no new cell survives, the report covers the current best mix, said plainly.

## Addendum (2026-11-12, before any tick result): one-minute resolution check
Phase 1 showed that about 22% of filled M1 trades stop out in the minute they fill, and that minute often also touched
+1R; the engine counts those as losses (pessimistic). To measure the true order, a fixed tick sample: Exness Zero bid ticks
(ticks.ex2archive.com) for EURUSD, GBPUSD and XAUUSD in 2021-03, 2021-09 and 2022-06 (VALIDATE years, not the holdout).
For each month: M1 bid bars are built from the ticks, the Phase 1 base setups are found on those bars, and every setup is
simulated twice with the same engine and rules: on the M1 bars (pessimistic and optimistic) and tick by tick (each tick a
zero-range bar: no same-minute ambiguity). Reported: R a trade by method and structure, and the share of trades whose
outcome differs. If ticks change a structure's R a trade by more than 0.02R, Phase 1 and 2 conclusions are stated with that
correction (M1 bars remain the study's data; the scanner's other timeframes are far less affected).
Script: `research/sweep6/tickcheck.py` -> `research/results/sweep6/tickcheck.json`.
