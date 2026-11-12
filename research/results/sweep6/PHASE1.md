# Phase 1: payout structure, frictionless, M1, 12 markets (pre-registered: research/sweep6/PREREGISTRATION.md)

Base = the owner's current rule (bodies >= 50%, a sweep from 6 candles before candle 1 through candle 2), every setup
simulated alone with no spread, commission, slippage or swaps. Same trades for every structure: 31,154 (LEARN),
26,647 (CONFIRM), 23,190 (VALIDATE). TP2 sits a median 9.5R from the entry (10-90%: 4.33-21.08R).

| Structure | wins per 10 trades | chance level per 10 (1/(1+T)) | avg win | R a trade LEARN / CONFIRM / VALIDATE | R per 10 trades (LEARN) | 10-trade blocks positive | longest losing streak |
|---|---|---|---|---|---|---|---|
| 1R | 4.16 | 5.00 | +1.13R | -0.109 / -0.127 / -0.092 | -1.09R | 37% | 16 |
| 2R | 2.98 | 3.33 | +2.06R | -0.081 / -0.098 / -0.061 | -0.81R | 36% | 22 |
| 3R | 2.30 | 2.50 | +3.04R | -0.065 / -0.082 / -0.053 | -0.65R | 42% | 35 |
| 4R | 1.86 | 2.00 | +4.03R | -0.060 / -0.077 / -0.045 | -0.60R | 40% | 36 |
| 5R | 1.56 | 1.67 | +5.01R | -0.060 / -0.076 / -0.039 | -0.60R | 47% | 48 |
| 6R | 1.35 | 1.43 | +5.99R | -0.055 / -0.074 / -0.030 | -0.55R | 39% | 48 |
| 7R | 1.20 | 1.25 | +6.95R | -0.046 / -0.075 / -0.016 | -0.46R | 34% | 53 |
| 8R | 1.06 | 1.11 | +7.91R | -0.051 / -0.080 / -0.003 | -0.51R | 30% | 75 |
| 9R | 0.97 | 1.00 | +8.86R | -0.039 / -0.062 / -0.003 | -0.39R | 40% | 75 |
| 10R | 0.89 | 0.91 | +9.78R | -0.037 / -0.061 / -0.009 | -0.37R | 57% | 112 |
| 15R | 0.63 | 0.62 | +14.13R | -0.043 / -0.050 / +0.029 | -0.43R | 44% | 120 |
| 20R | 0.51 | 0.48 | +18.13R | -0.032 / -0.052 / +0.049 | -0.32R | 36% | 137 |
| 3R-BE75 | 2.15 | 2.50 | +3.04R | -0.064 / -0.078 / -0.050 | -0.64R | 39% | 35 |
| 4R-BE75 | 1.77 | 2.00 | +4.03R | -0.053 / -0.079 / -0.049 | -0.53R | 44% | 36 |
| 5R-BE75 | 1.48 | 1.67 | +5.01R | -0.061 / -0.074 / -0.040 | -0.61R | 44% | 48 |
| 6R-BE75 | 1.29 | 1.43 | +5.99R | -0.058 / -0.070 / -0.031 | -0.58R | 37% | 52 |
| 7R-BE75 | 1.15 | 1.25 | +6.95R | -0.047 / -0.073 / -0.012 | -0.47R | 34% | 67 |
| 8R-BE75 | 1.03 | 1.11 | +7.91R | -0.050 / -0.081 / -0.004 | -0.50R | 33% | 75 |
| 9R-BE75 | 0.95 | 1.00 | +8.86R | -0.035 / -0.065 / -0.006 | -0.35R | 44% | 75 |
| 10R-BE75 | 0.87 | 0.91 | +9.78R | -0.035 / -0.065 / -0.015 | -0.35R | 57% | 112 |
| TP1 | 1.43 | - | +5.70R | -0.041 / -0.054 / -0.009 | -0.41R | 40% | 64 |
| TP2 | 1.05 | - | +8.14R | -0.043 / -0.055 / -0.006 | -0.43R | 37% | 78 |
| TP2-BE75 | 1.01 | - | +8.22R | -0.043 / -0.055 / -0.007 | -0.43R | 37% | 86 |
| P60 | 1.42 | - | +5.72R | -0.040 / -0.051 / -0.009 | -0.40R | 39% | 64 |

Rule choice (highest LEARN R a trade): **20R** (-0.032R); every structure is below zero
before costs in LEARN and CONFIRM, and the best ones are statistically tied (differences < 0.01R, t < 1).

## One-minute resolution (tick check, 9 months of Exness ticks in 2021-22, 585 trades)

| Structure | win rate M1 bars | win rate ticks | R a trade M1 (pessimistic) | M1 (optimistic) | ticks |
|---|---|---|---|---|---|
| 1R | 41.0% | 42.7% | -0.131 | -0.093 | -0.075 |
| 2R | 28.7% | 29.1% | -0.127 | -0.116 | -0.070 |
| 3R | 21.7% | 22.1% | -0.131 | -0.124 | -0.067 |
| 5R | 13.7% | 13.7% | -0.180 | -0.180 | -0.136 |
| 10R | 8.6% | 8.6% | -0.072 | -0.072 | -0.036 |
| 20R | 4.6% | 4.6% | -0.060 | -0.060 | -0.027 |
| TP1 | 11.3% | 11.3% | -0.083 | -0.083 | -0.048 |
| TP2 | 7.1% | 7.1% | -0.153 | -0.153 | -0.121 |
| TP2-BE75 | 7.1% | 7.1% | -0.127 | -0.127 | -0.098 |
| P60 | 11.0% | 11.0% | -0.128 | -0.128 | -0.097 |

Win rates on M1 bars equal the tick truth from 5R up and are 0.3-1.7 points low at 1-3R; the remaining R gap comes
from tick-level fill prices (a limit filled on a tick jump gets a better price than the level), not from ordering.
