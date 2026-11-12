# Portfolio Pareto (owner, 2026-11-12) — pre-registered in research/sweep5/PREREGISTRATION.md

Exness Zero costs + swaps for the 13 survivors; RoboForex Prime costs + swaps for the three pivot-sweep v2 legs. Risk per
trade for each cap set on 2011-22 only (95% of bootstrapped 36-fortnight lifecycles = the cap); then kept for 2023-25 and
Jan-Oct 2026. Integrity = share of calendar years 2011-2025 positive. Heat = average open risk. R figures are weighted R.

## All mixes at the 3.6% envelope

| Mix | integrity | two-week Sharpe 2011-22 / 2023-25 / 2026 | % a year 2011-22 / 2023-25 / Jan-Oct 2026 | worst drawdown 2011-22 / 2023-25 | heat | cap needed for 80% / 120% a year |
|---|---|---|---|---|---|---|
| Timeless 10 | 100% | 0.373 / 0.237 / 0.027 | 6.0 / 4.7 / 0.4 (10 months) | 4.26% / 3.2% | 0.38% | 48% / 72% |
| All 13 | 100% | 0.358 / 0.22 / 0.009 | 5.8 / 4.3 / 0.1 (10 months) | 4.4% / 3.75% | 0.54% | 50% / 74% |
| Book 11 | 93% | 0.293 / 0.177 / -0.046 | 4.7 / 3.2 / -0.6 (10 months) | 3.31% / 4.14% | 0.45% | 61% / 92% |
| Timeless 10 + v2 | 100% | 0.392 / 0.269 / 0.079 | 6.5 / 5.3 / 1.0 (10 months) | 4.18% / 3.07% | 0.36% | 44% / 66% |
| All 13 + v2 | 100% | 0.371 / 0.244 / 0.046 | 6.1 / 4.7 / 0.7 (10 months) | 4.02% / 3.52% | 0.51% | 47% / 71% |
| Book 11 + v2 | 100% | 0.31 / 0.203 / 0.002 | 4.9 / 3.6 / 0.0 (10 months) | 3.02% / 3.4% | 0.41% | 59% / 88% |

## A. Max timelessness: Book 11 + v2
Chosen by the rule: highest integrity, then the lowest 2011-22 drawdown.

Mix: 14 legs, win rate 46%, average win 0.32R / loss -0.22R (weighted), expectancy +0.031R a trade, profit factor 1.26, 36 trades a month; integrity 100%; heat 0.41% average open risk.

| Cap (envelope) | base risk a trade | % per two weeks 2011-22 / 2023-25 / 2026 | % a year 2011-22 / 2023-25 / Jan-Oct 2026 | worst drawdown 2011-22 |
|---|---|---|---|---|
| 3.6% | 0.367% x leg weight | 0.189 / 0.134 / 0.001 | 4.9 / 3.6 / 0.0 | 3.02% |
| 8% | 0.815% x leg weight | 0.421 / 0.298 / 0.002 | 11.0 / 7.9 / 0.1 | 6.7% |
| 15% | 1.528% x leg weight | 0.789 / 0.559 / 0.004 | 20.6 / 14.9 / 0.1 | 12.57% |
| 25% | 2.547% x leg weight | 1.315 / 0.931 / 0.007 | 34.3 / 24.8 / 0.2 | 20.95% |

| Magic | Leg | Pair | Timeframe | weight | avg risk at 3.6% | win | avg win / loss R | expectancy R | PF | trades/month | 2023-25 expectancy (n) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | EUR_EuroHours_short_TueThu | EURUSD | clock 09-13 London | 0.33 | 0.121% | 54% | 0.54 / -0.5 | +0.063 | 1.27 | 12.9 | 0.033 (464) |
| 2 | XAU_S1_reversion_H1M30M20 | XAUUSD | H1/M30/M20 | 0.63 | 0.232% | 64% | 1.03 / -0.96 | +0.312 | 1.91 | 0.52 | 0.152 (23) |
| 3 | JPY_VolBreakout_D1_k0.7 | USDJPY | D1 | 0.21 | 0.078% | 42% | 1.15 / -0.73 | +0.064 | 1.15 | 8.21 | -0.017 (296) |
| 4 | XAU_Donchian20_H4_turtle | XAUUSD | H4 | 0.21 | 0.077% | 31% | 2.11 / -0.81 | +0.096 | 1.17 | 3.52 | 0.179 (141) |
| 5 | JPY_S2_Donchian20_H4_long | USDJPY | H4 | 0.37 | 0.134% | 41% | 2.15 / -1.04 | +0.280 | 1.46 | 0.69 | 0.287 (18) |
| 6 | XAU_EMA20-50_H4 | XAUUSD | H4 | 0.34 | 0.123% | 29% | 2.54 / -0.62 | +0.296 | 1.68 | 0.67 | 1.213 (21) |
| 7 | GBP_WeeklySweep_FollowThrough | GBPUSD | H1 | 0.93 | 0.339% | 55% | 0.94 / -0.44 | +0.316 | 2.58 | 0.29 | -0.082 (13) |
| 8 | JPY_Donchian55_D1_trail | USDJPY | D1 | 0.42 | 0.154% | 42% | 1.87 / -1.08 | +0.169 | 1.27 | 0.44 | 0.345 (16) |
| 9 | JPY_RSI2_D1_lo5 | USDJPY | D1 | 1.0 | 0.367% | 66% | 0.47 / -0.63 | +0.103 | 1.49 | 0.72 | -0.004 (27) |
| 10 | GBPJPY_Donchian20_H4_trail | GBPJPY | H4 | 0.25 | 0.09% | 42% | 1.59 / -1.0 | +0.084 | 1.14 | 3.63 | 0.001 (126) |
| 11 | EURGBP_Bollinger_D1_k1.5 | EURGBP | D1 | 0.56 | 0.205% | 58% | 0.7 / -0.97 | +0.005 | 1.01 | 2.18 | 0.009 (91) |
| 12 | v2_GBPUSD_M15 | GBPUSD | M15 | 0.26 | 0.095% | 31% | 2.59 / -1.04 | +0.089 | 1.12 | 1.25 | 0.034 (38) |
| 13 | v2_EURGBP_H1 | EURGBP | H1 | 0.27 | 0.1% | 44% | 2.23 / -0.95 | +0.454 | 1.85 | 0.71 | 0.403 (28) |
| 14 | v2_NAS100_H1 | NAS100 | H1 | 0.16 | 0.057% | 30% | 3.94 / -1.11 | +0.417 | 1.54 | 0.69 | 0.733 (20) |

## B. Balanced: Timeless 10 + v2
Chosen by the rule: best two-week Sharpe on 2023-Oct 2026 among mixes with integrity >= 90%.

Mix: 13 legs, win rate 51%, average win 0.28R / loss -0.22R (weighted), expectancy +0.037R a trade, profit factor 1.35, 34 trades a month; integrity 100%; heat 0.36% average open risk.

| Cap (envelope) | base risk a trade | % per two weeks 2011-22 / 2023-25 / 2026 | % a year 2011-22 / 2023-25 / Jan-Oct 2026 | worst drawdown 2011-22 |
|---|---|---|---|---|
| 3.6% | 0.432% x leg weight | 0.248 / 0.198 / 0.038 | 6.5 / 5.3 / 1.0 | 4.18% |
| 8% | 0.959% x leg weight | 0.552 / 0.441 / 0.085 | 14.4 / 11.7 / 2.2 | 9.3% |
| 15% | 1.798% x leg weight | 1.035 / 0.826 / 0.158 | 27.0 / 22.0 / 4.2 | 17.43% |
| 25% | 2.997% x leg weight | 1.725 / 1.377 / 0.264 | 45.0 / 36.7 / 7.0 | 29.06% |

| Magic | Leg | Pair | Timeframe | weight | avg risk at 3.6% | win | avg win / loss R | expectancy R | PF | trades/month | 2023-25 expectancy (n) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | EUR_EuroHours_short_TueThu | EURUSD | clock 09-13 London | 0.33 | 0.142% | 54% | 0.54 / -0.5 | +0.063 | 1.27 | 12.9 | 0.033 (464) |
| 2 | XAU_S1_reversion_H1M30M20 | XAUUSD | H1/M30/M20 | 0.63 | 0.273% | 64% | 1.03 / -0.96 | +0.312 | 1.91 | 0.52 | 0.152 (23) |
| 3 | XAU_Donchian20_H4_turtle | XAUUSD | H4 | 0.21 | 0.091% | 31% | 2.11 / -0.81 | +0.096 | 1.17 | 3.52 | 0.179 (141) |
| 4 | JPY_S2_Donchian20_H4_long | USDJPY | H4 | 0.37 | 0.158% | 41% | 2.15 / -1.04 | +0.280 | 1.46 | 0.69 | 0.287 (18) |
| 5 | XAU_EMA20-50_H4 | XAUUSD | H4 | 0.34 | 0.145% | 29% | 2.54 / -0.62 | +0.296 | 1.68 | 0.67 | 1.213 (21) |
| 6 | GBP_WeeklySweep_FollowThrough | GBPUSD | H1 | 0.93 | 0.399% | 55% | 0.94 / -0.44 | +0.316 | 2.58 | 0.29 | -0.082 (13) |
| 7 | JPY_RSI2_D1_lo5 | USDJPY | D1 | 1.0 | 0.432% | 66% | 0.47 / -0.63 | +0.103 | 1.49 | 0.72 | -0.004 (27) |
| 8 | GBPJPY_Donchian20_H4_trail | GBPJPY | H4 | 0.25 | 0.106% | 42% | 1.59 / -1.0 | +0.084 | 1.14 | 3.63 | 0.001 (126) |
| 9 | tokyo_fix_gotobi_v1 | USDJPY | M5 clock 23:00-00:55 UTC | 0.57 | 0.247% | 54% | 0.37 / -0.33 | +0.047 | 1.31 | 5.96 | 0.052 (214) |
| 10 | eurusd_close_beyond_reversal_v1 | EURUSD | D1 | 1.0 | 0.432% | 91% | 0.15 / -0.98 | +0.050 | 1.57 | 2.36 | 0.024 (113) |
| 11 | v2_GBPUSD_M15 | GBPUSD | M15 | 0.26 | 0.111% | 31% | 2.59 / -1.04 | +0.089 | 1.12 | 1.25 | 0.034 (38) |
| 12 | v2_EURGBP_H1 | EURGBP | H1 | 0.27 | 0.118% | 44% | 2.23 / -0.95 | +0.454 | 1.85 | 0.71 | 0.403 (28) |
| 13 | v2_NAS100_H1 | NAS100 | H1 | 0.16 | 0.067% | 30% | 3.94 / -1.11 | +0.417 | 1.54 | 0.69 | 0.733 (20) |

## C. Max return inside the walls: Timeless 10 + v2
Chosen by the rule: highest % a year at 3.6% (2011-22) with integrity >= 90%.

Mix: 13 legs, win rate 51%, average win 0.28R / loss -0.22R (weighted), expectancy +0.037R a trade, profit factor 1.35, 34 trades a month; integrity 100%; heat 0.36% average open risk.

| Cap (envelope) | base risk a trade | % per two weeks 2011-22 / 2023-25 / 2026 | % a year 2011-22 / 2023-25 / Jan-Oct 2026 | worst drawdown 2011-22 |
|---|---|---|---|---|
| 3.6% | 0.432% x leg weight | 0.248 / 0.198 / 0.038 | 6.5 / 5.3 / 1.0 | 4.18% |
| 8% | 0.959% x leg weight | 0.552 / 0.441 / 0.085 | 14.4 / 11.7 / 2.2 | 9.3% |
| 15% | 1.798% x leg weight | 1.035 / 0.826 / 0.158 | 27.0 / 22.0 / 4.2 | 17.43% |
| 25% | 2.997% x leg weight | 1.725 / 1.377 / 0.264 | 45.0 / 36.7 / 7.0 | 29.06% |

| Magic | Leg | Pair | Timeframe | weight | avg risk at 3.6% | win | avg win / loss R | expectancy R | PF | trades/month | 2023-25 expectancy (n) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | EUR_EuroHours_short_TueThu | EURUSD | clock 09-13 London | 0.33 | 0.142% | 54% | 0.54 / -0.5 | +0.063 | 1.27 | 12.9 | 0.033 (464) |
| 2 | XAU_S1_reversion_H1M30M20 | XAUUSD | H1/M30/M20 | 0.63 | 0.273% | 64% | 1.03 / -0.96 | +0.312 | 1.91 | 0.52 | 0.152 (23) |
| 3 | XAU_Donchian20_H4_turtle | XAUUSD | H4 | 0.21 | 0.091% | 31% | 2.11 / -0.81 | +0.096 | 1.17 | 3.52 | 0.179 (141) |
| 4 | JPY_S2_Donchian20_H4_long | USDJPY | H4 | 0.37 | 0.158% | 41% | 2.15 / -1.04 | +0.280 | 1.46 | 0.69 | 0.287 (18) |
| 5 | XAU_EMA20-50_H4 | XAUUSD | H4 | 0.34 | 0.145% | 29% | 2.54 / -0.62 | +0.296 | 1.68 | 0.67 | 1.213 (21) |
| 6 | GBP_WeeklySweep_FollowThrough | GBPUSD | H1 | 0.93 | 0.399% | 55% | 0.94 / -0.44 | +0.316 | 2.58 | 0.29 | -0.082 (13) |
| 7 | JPY_RSI2_D1_lo5 | USDJPY | D1 | 1.0 | 0.432% | 66% | 0.47 / -0.63 | +0.103 | 1.49 | 0.72 | -0.004 (27) |
| 8 | GBPJPY_Donchian20_H4_trail | GBPJPY | H4 | 0.25 | 0.106% | 42% | 1.59 / -1.0 | +0.084 | 1.14 | 3.63 | 0.001 (126) |
| 9 | tokyo_fix_gotobi_v1 | USDJPY | M5 clock 23:00-00:55 UTC | 0.57 | 0.247% | 54% | 0.37 / -0.33 | +0.047 | 1.31 | 5.96 | 0.052 (214) |
| 10 | eurusd_close_beyond_reversal_v1 | EURUSD | D1 | 1.0 | 0.432% | 91% | 0.15 / -0.98 | +0.050 | 1.57 | 2.36 | 0.024 (113) |
| 11 | v2_GBPUSD_M15 | GBPUSD | M15 | 0.26 | 0.111% | 31% | 2.59 / -1.04 | +0.089 | 1.12 | 1.25 | 0.034 (38) |
| 12 | v2_EURGBP_H1 | EURGBP | H1 | 0.27 | 0.118% | 44% | 2.23 / -0.95 | +0.454 | 1.85 | 0.71 | 0.403 (28) |
| 13 | v2_NAS100_H1 | NAS100 | H1 | 0.16 | 0.067% | 30% | 3.94 / -1.11 | +0.417 | 1.54 | 0.69 | 0.733 (20) |

## Treatment common to A, B and C
- Multiplier: none. Fixed fractional risk (base risk x leg weight, on current equity). No martingale, no ladder that
  raises risk after wins or losses (P8, P24-P26). The envelope guard (pre-trade check: skip a trade if a full stop-out would
  breach the cap from the lifecycle high-water mark) is what holds the envelope (P24).
- Harvest: at each two-week close, pay out profit above the high-water mark minus a buffer of one envelope (3.6%); nothing
  is paid in a losing fortnight (about 40-45% of fortnights).
- 80-120% a year inside 3.6% is not possible with these edges: return is linear in the cap, and 80% a year needs a 44-61%
  drawdown envelope (120%: 66-92%), where losing streaks and live edge decay (P11: 30-50% weaker) make ruin likely. The
  maximum inside 3.6% is about 5-6.5% a year in backtest; about 1% in Jan-Oct 2026.
