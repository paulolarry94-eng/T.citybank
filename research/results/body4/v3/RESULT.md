# Body-engulf range v3 (dojis bullish, 1:2 and 1:10, breakeven at 75%) and the bug audit — result (2026-11-08)

**Verdict: rejected, and no bug found.** All 384 settings lose after costs (12 markets pooled, M1-H4, 2011-19 and
2020-22); the best with 200+ trades loses 0.09R a trade. Before costs the pattern is about zero. 10R winners are real:
6.6% of trades reach 10R (M1-H1 5-7%), but a 10R target needs about 9% before costs and more after.
Pre-registered: `research/body4/PREREGISTRATION_V3.md`. Lab: `research/results/truth/body4_range_v3/REPORT.md`.

## Bug audit (`audit.py`, `audit.json`): every check passed
| Check | Scope | Result |
|---|---|---|
| Every detected setup re-checked from the raw candles (colours, body engulfing, range, lookback with dojis bullish) | 464,614 setups, 12 markets x 6 timeframes | 0 broken |
| Independent re-scan for setups the scanner missed | first 100,000 bars of each market x timeframe (44,962 setups) | 0 missed, 0 extra |
| Entries: level not reachable and target not touched between placement and fill; fill at or better than the level | 215,119 trades (10R and 2R) | 0 violations |
| Exits re-scored by a separate first-touch checker (own Friday and swap-night arithmetic) | 215,119 trades | 0 differences in exit time or R |
| Truly unclear minutes (stop and target inside the same minute) | M1 2R 0.22%, M1 10R 0.02%, M5+ <= 0.06% | negligible |
| Price gaps (stop or target filled beyond its level after a gap or a hole in the data) | capping every gap trade at -1.5R / target+0.5R | average moves by 0.01R |
Correction to v1/v2: "a fill and a stop in the same minute" is not unclear. Price has to pass the entry to reach the stop,
so it is a certain loss (19-21% of M1 trades, 5-7% M5, 3-4% M15: tiny ranges are stopped out at once).

## Why the results are negative (what the scan shows, not bugs)
1. No edge before costs: main settings before costs 2011-19 (2020-22): 10R M1 -0.07 (-0.05), M5 -0.03 (-0.07),
   M15 +0.07 (-0.02), M30 0.00 (-0.07), H1 +0.02 (+0.10), H4 -0.10 (-0.18). Of 384 settings 101 were positive before
   costs in 2011-19 and 64 in both periods; best t 2.8: what 384 tries of a zero edge produce.
2. Costs are large next to these ranges: 0.06R (H4) to 0.43R (M1) a trade.
3. Win rate vs target: 10R targets were hit by 5-7% of trades (needed about 9% + costs); 2R by 19-27% (needed 33% + costs).
4. Holding small ranges overnight: swaps and gaps (an index gap through a 2-point stop is 20R).

## Main settings (50% entry, stop at the range end, breakeven at 75%, lookback on, dojis bullish), 12 markets
| Timeframe | 10R after costs 2011-19 (2020-22) | 10R swap-free | 2R after costs | 2R swap-free | Trades 10R / 2R (2011-19) |
|---|---|---|---|---|---|
| M1 | -0.48 (-0.46) | -0.47 | -0.48 (-0.45) | -0.48 | 51,901 / 39,030 |
| M5 | -0.31 (-0.31) | -0.29 | -0.30 (-0.25) | -0.30 | 17,994 / 14,321 |
| M15 | -0.15 (-0.18) | -0.12 | -0.17 (-0.18) | -0.16 | 7,438 / 6,008 |
| M30 | -0.18 (-0.23) | -0.14 | -0.17 (-0.23) | -0.16 | 4,154 / 3,341 |
| H1 | -0.14 (-0.02) | -0.10 | -0.16 (-0.04) | -0.14 | 2,038 / 1,635 |
| H4 | -0.20 (-0.24) | -0.15 | -0.17 (-0.32) | -0.14 | 517 / 438 |

## Paired comparisons (all else equal)
| Question | 2011-19 | 2020-22 |
|---|---|---|
| Breakeven at 75% vs none | breakeven had the higher profit factor in 31% of 2,172 pairs; R per trade unchanged | 36% |
| 10R vs 2R | 10R had the higher profit factor in 71% of pairs; R per trade the same (-0.005R) | 66% |
| Entry 50% vs 70% | 50% better in 80% (+0.10R) | 73% (+0.08R) |
| Stop buffer 0% vs 20% | 20% better in 79% (+0.09R) | 72% (+0.08R) |
| Lookback on vs off (dojis bullish) | no difference (50%) | 48% |
Best market x timeframe (learn 2011-19, check 2020-22): 64 picks, 20 positive in 2011-19, 12 in 2020-22, 6 in both, none
with t above 1.4 (e.g. XAUUSD H1 10R +0.34R on 162 trades, then +0.11R on 78).

## The 10 biggest winners and losers (`best_worst/`, 10R main settings, 2011-22, one per market and day)
All 20 are gap trades: winners +17 to +27R (the target filled at a better price after a jump), losers -12 to -23R (the
stop filled after a jump; #1 is UK100 held into the Brexit vote, 24 June 2016). Two (gold winner #1, GBPUSD loser #6)
jumped over a one-hour hole in the price data (00:00-01:00 UTC). Typical outcomes are not like this: of 121,822 trades,
6.6% hit 10R, 89% were stopped, 2% breakeven, 2% closed on Friday.
