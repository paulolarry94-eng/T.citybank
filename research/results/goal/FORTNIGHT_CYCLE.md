# The cycle goal with a 2-week cycle (owner question, 2026-11-06)

Code `research/goal/fortnight_cycle.py`, numbers `fortnight_cycle.json`. Cycle = 14 days of trading; lifecycle = 36 cycles
(about 17 months); risk per trade set so 95% of bootstrapped lifecycles stay inside the drawdown cap (measured trade by
trade). Survivor trades 2011-2025 (seen before), Exness Zero costs + swaps; swap-free separately.

## What the goal needs (fortnight Sharpe = mean / spread of fortnight returns)
| Goal per 2 weeks | inside 3.6% | inside 5% | inside 8% |
|---|---|---|---|
| +2% | 1.17 | 1.00 | 0.79 |
| +5% | 1.75 | 1.53 | 1.24 |
| +7% | 1.98 | 1.76 | 1.44 |
(Drawdown checked at fortnight ends only, so these are slightly lenient. 1.17 a fortnight = about 6 a year; the best
funds manage 1-2 a year.)

## Where we are
| Set (with swaps) | Trades / 2 weeks | Fortnight Sharpe | Per 2 weeks at 3.6% | Positive fortnights | Fortnights >= +2% | % a year at 3.6% / 5% / 8% |
|---|---|---|---|---|---|---|
| All 13 survivors, leg weights | 19.5 | 0.33 | +0.19% | 63% | 1% | 4.9 / 6.8 / 10.8 |
| All 13, every trade 1R | 19.5 | 0.26 | +0.14% | 56% | 1.5% | 3.7 / 5.1 / 8.1 |
| 11-leg book, leg weights | 15.6 | 0.27 | +0.15% | 58% | 1% | 3.9 / 5.4 / 8.6 |
| Tokyo fix | 2.7 | 0.15 | +0.06% | 59% | 0.3% | 1.6 / 2.3 / 3.7 |
| EURUSD reversal | 1.2 | 0.14 | +0.05% | 62% | 0% | 1.2 / 1.7 / 2.7 |
| 11-leg book, untouched Jan-Oct 2026 | - | -0.05 to +0.04 | about 0 | - | - | about 0 |
Swap-free (separately): all 13 with leg weights 0.40, +0.27% per 2 weeks, 6.9 / 9.6 / 15.4% a year.

## Reading
- With a 2-week cycle the best mix is **3.6x short** of the +2% goal in Sharpe (0.33 vs 1.17) and **about 10x short in
  return** (+0.19% vs +2% per cycle). With the 10-trade cycle it was 6.7x short in edge quality: the gap looks smaller
  because 20 trades fit in a fortnight, but the money is the same, about 5% a year at a 3.6% cap.
- Widening the cap to 8% gives about 11% a year (backtest) with 2-week cycles positive 63% of the time; +2% fortnights
  happen about 1 time in 10.
- The 2026 forward data is about flat, so even these numbers are the backtest's best case (P11).
