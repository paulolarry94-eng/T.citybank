# The most timeless mix of the survivors (built by research/goal/timeless_mix.py)

Pre-registered: research/goal/PREREGISTRATION_TIMELESS.md. Exness Zero costs + swaps unless marked; every leg keeps its weight. Risk per trade for the 3.6% and 8% caps is set on 2011-22 and applied unchanged later. Recommendation by the pre-registered rule: **Timeless mix**.

Lab legs re-run with unchanged settings (2011-25 must equal the lab's parity trades): tokyo_fix_gotobi_v1: 1072 of 1072 trades, sum 51.478 vs 51.478; eurusd_close_beyond_reversal_v1: 453 of 453 trades, sum 14.084 vs 14.084

## Which legs are timeless (R per trade after costs and swaps, trades)

| Leg | 2011-14 | 2015-18 | 2019-22 | Timeless |
|---|---|---|---|---|
| EUR_EuroHours_short_TueThu | +0.048 (612) | +0.081 (623) | +0.058 (622) | yes |
| XAU_S1_reversion_H1M30M20 | +0.066 (25) | +0.447 (20) | +0.426 (30) | yes |
| JPY_VolBreakout_D1_k0.7 | +0.128 (398) | -0.023 (386) | +0.085 (398) | no |
| XAU_Donchian20_H4_turtle | +0.134 (166) | +0.073 (156) | +0.082 (185) | yes |
| JPY_S2_Donchian20_H4_long | +0.257 (43) | +0.197 (30) | +0.414 (26) | yes |
| XAU_EMA20-50_H4 | +0.602 (34) | +0.383 (25) | +0.104 (39) | yes |
| GBP_WeeklySweep_FollowThrough | +0.067 (15) | +0.372 (16) | +0.575 (11) | yes |
| JPY_Donchian55_D1_trail | +0.506 (20) | -0.161 (22) | +0.238 (23) | no |
| JPY_RSI2_D1_lo5 | +0.203 (30) | +0.027 (42) | +0.108 (32) | yes |
| GBPJPY_Donchian20_H4_trail | +0.033 (181) | +0.159 (169) | +0.075 (174) | yes |
| EURGBP_Bollinger_D1_k1.5 | +0.119 (96) | -0.071 (103) | -0.019 (116) | no |
| tokyo_fix_gotobi_v1 | +0.051 (287) | +0.027 (287) | +0.064 (284) | yes |
| eurusd_close_beyond_reversal_v1 | +0.054 (127) | +0.052 (105) | +0.042 (109) | yes |

## The mixes, two-week cycles

| Mix | Period | Trades / 2 weeks | Fortnights positive | Fortnight Sharpe | % a year at 1% risk | 3.6% cap: % a year (max drawdown) | 8% cap: % a year (max drawdown) |
|---|---|---|---|---|---|---|---|
| Timeless mix | swaps | 2011-22 | 14.38 | 61% | 0.373 | 13.1 | 6.0 (4.26) | 13.3 (9.46) |
| Timeless mix | swaps | 2023-25 | 14.5 | 54% | 0.237 | 10.3 | 4.7 (3.2) | 10.6 (7.11) |
| Timeless mix | swaps | Jan-Oct 2026 | 14.18 | 50% | 0.027 | 0.8 | 0.4 (2.2) | 0.8 (4.88) |
| All 13 survivors | swaps | 2011-22 | 19.37 | 64% | 0.358 | 14.9 | 5.8 (4.4) | 13.0 (9.78) |
| All 13 survivors | swaps | 2023-25 | 19.54 | 57% | 0.22 | 10.9 | 4.3 (3.75) | 9.5 (8.33) |
| All 13 survivors | swaps | Jan-Oct 2026 | 18.95 | 41% | 0.009 | 0.4 | 0.1 (2.64) | 0.3 (5.86) |
| 11-leg book | swaps | 2011-22 | 15.54 | 57% | 0.293 | 11.5 | 4.7 (3.31) | 10.5 (7.35) |
| 11-leg book | swaps | 2023-25 | 15.45 | 61% | 0.177 | 7.8 | 3.2 (4.14) | 7.1 (9.21) |
| 11-leg book | swaps | Jan-Oct 2026 | 15.14 | 50% | -0.046 | -1.4 | -0.6 (2.21) | -1.3 (4.9) |
| Timeless mix | swap-free | 2011-22 | 14.38 | 63% | 0.429 | 15.2 | 7.6 (4.47) | 16.9 (9.93) |
| Timeless mix | swap-free | 2023-25 | 14.5 | 57% | 0.273 | 12.0 | 6.0 (3.33) | 13.4 (7.39) |
| Timeless mix | swap-free | Jan-Oct 2026 | 14.18 | 50% | 0.068 | 2.1 | 1.0 (2.34) | 2.3 (5.2) |
| All 13 survivors | swap-free | 2011-22 | 19.37 | 67% | 0.44 | 18.4 | 8.3 (4.47) | 18.5 (9.92) |
| All 13 survivors | swap-free | 2023-25 | 19.54 | 62% | 0.283 | 14.1 | 6.4 (4.01) | 14.1 (8.91) |
| All 13 survivors | swap-free | Jan-Oct 2026 | 18.95 | 55% | 0.082 | 3.3 | 1.5 (2.9) | 3.3 (6.45) |
| 11-leg book | swap-free | 2011-22 | 15.54 | 62% | 0.374 | 14.9 | 7.1 (3.16) | 15.8 (7.02) |
| 11-leg book | swap-free | 2023-25 | 15.45 | 65% | 0.238 | 10.6 | 5.1 (4.11) | 11.3 (9.14) |
| 11-leg book | swap-free | Jan-Oct 2026 | 15.14 | 55% | 0.036 | 1.1 | 0.5 (2.5) | 1.2 (5.55) |

Fortnight Sharpe over 2023 - October 2026: Timeless mix | swaps 0.201; All 13 survivors | swaps 0.181; 11-leg book | swaps 0.139; Timeless mix | swap-free 0.237; All 13 survivors | swap-free 0.245; 11-leg book | swap-free 0.203

## Calendar years at the 3.6% cap (%; 2026 = January-October)

| Mix | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Timeless mix | +3.4 | +5.2 | +7.3 | +7.2 | +5.0 | +10.2 | +4.8 | +3.7 | +7.0 | +2.3 | +5.1 | +10.6 | +3.0 | +4.3 | +7.0 | +0.3 |
| All 13 survivors | +3.0 | +6.1 | +10.4 | +8.8 | +2.7 | +7.7 | +2.2 | +4.2 | +6.6 | +2.2 | +4.2 | +12.1 | +3.7 | +5.3 | +3.8 | +0.1 |
| 11-leg book | +0.1 | +5.1 | +8.1 | +9.7 | +1.6 | +6.6 | -0.1 | +5.3 | +5.5 | +1.5 | +2.9 | +10.1 | +2.0 | +4.5 | +3.1 | -0.5 |
