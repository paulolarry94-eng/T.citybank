# Phase 2: what separates winners from losers (frictionless, M1, 12 markets)

Superset: every four-candle setup (bodies >= 40%, with or without a sweep): 238,132 trades in 2011-15 (LEARN),
209,579 in 2016-19 (CONFIRM), 190,030 in 2020-22 (VALIDATE), each simulated alone with no costs.
Outcome: R a trade with the Phase 1 payout (20R). Overall: -0.076 / -0.095 / -0.046R a trade. A condition counts only if it holds in 2011-15 (t >= 3) AND 2016-19 (t >= 2).
Tests: 137 single conditions + 1,005 pairs; expected false passes by luck: 0.035.

## Outcome
- **No condition and no pair makes money in both 2011-15 and 2016-19** (0 of 1,142).
- **Winners and losers look the same.** For every feature the difference between winners' and losers' averages is under
  0.1 standard deviations (Kolmogorov-Smirnov distance under 0.04). There is no trait the winners have and the losers lack.
- A few conditions consistently LOSE LESS: a sweep present (vs none), 12-16 UTC (vs 16-21 UTC), not Monday, no sweep on the
  target side, candle bodies under 100%. None turns positive.

## Your questions

### Which candle swept the pivot (the latest sweep before candle 4 closed)
Candles since the sweep = this category (candle 4 = 0, candle 1 = 3, 'before 1' = 4, ...).

| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| candle 4 | 197 / 214 | +0.521 / +0.191 / +0.159 | 7.6% | +0.139 / -0.075 / -0.090 | no |
| candle 3 | 680 / 735 | +0.098 / -0.265 / -0.262 | 5.7% | -0.116 / -0.108 / -0.154 | no |
| candle 2 | 868 / 849 | +0.129 / +0.003 / +0.279 | 5.5% | -0.025 / +0.001 / +0.028 | no |
| candle 1 | 5,811 / 5,189 | +0.026 / -0.015 / +0.112 | 5.5% | -0.044 / -0.065 / -0.054 | no |
| candle before 1 | 5,234 / 4,514 | +0.038 / -0.087 / +0.045 | 5.4% | -0.082 / -0.060 / -0.050 | no |
| 2-4 before candle 1 | 15,148 / 13,106 | -0.039 / -0.022 / +0.030 | 5.0% | -0.063 / -0.081 / -0.048 | no |
| 5-10 before candle 1 | 25,876 / 22,725 | -0.050 / -0.057 / -0.001 | 4.9% | -0.066 / -0.094 / -0.045 | no |
| none | 184,318 / 162,247 | -0.091 / -0.109 / -0.067 | 4.7% | -0.126 / -0.113 / -0.082 | loses more (both periods) |

### Sweep depth beyond the pivot, FX pairs, in pips


| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| 0-1 pip | 17,288 / 15,718 | -0.047 / -0.019 / +0.014 | 5.0% | - | no |
| 1-2 pips | 4,270 / 3,433 | -0.079 / -0.017 / +0.043 | 4.9% | - | no |
| 2-3 pips | 1,727 / 1,208 | -0.091 / -0.277 / -0.171 | 4.8% | - | no |
| 3-5 pips | 1,275 / 768 | -0.066 / -0.118 / +0.085 | 4.7% | - | no |
| 5-10 pips | 513 / 350 | +0.212 / +0.139 / -0.106 | 6.8% | - | no |
| 10+ pips | 81 / 59 | +0.858 / -0.224 / +2.336 | 9.9% | - | no |
| no sweep | 83,755 / 72,149 | -0.104 / -0.116 / -0.078 | 4.6% | - | no |

### Sweep depth in ATR units (all markets)


| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| Q1 <= 0.173 | 10,763 / 10,684 | +0.042 / -0.032 / +0.040 | 5.4% | -0.045 / -0.055 / -0.046 | no |
| Q2 0.173-0.325 | 10,763 / 9,617 | -0.084 / -0.012 / +0.002 | 4.9% | -0.101 / -0.074 / -0.024 | no |
| Q3 0.325-0.523 | 10,758 / 9,285 | +0.001 / -0.018 / +0.023 | 5.3% | -0.044 / -0.098 / -0.072 | no |
| Q4 0.523-0.858 | 10,767 / 9,199 | -0.038 / -0.057 / +0.031 | 4.9% | -0.065 / -0.083 / -0.049 | no |
| Q5 > 0.858 | 10,763 / 8,547 | -0.038 / -0.125 / +0.037 | 5.0% | -0.063 / -0.107 / -0.053 | no |
| n/a | 184,318 / 162,247 | -0.091 / -0.109 / -0.067 | 4.7% | -0.126 / -0.113 / -0.082 | loses more (both periods) |

### Smaller body of candles 2 and 4 (your 40% / 50% / 60% question)


| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| 40-50% | 34,264 / 33,752 | -0.017 / -0.070 / -0.081 | 5.0% | -0.104 / -0.102 / -0.069 | no |
| 50-60% | 56,220 / 49,905 | -0.100 / -0.100 / -0.007 | 4.6% | -0.123 / -0.118 / -0.077 | no |
| 60-70% | 49,837 / 44,237 | -0.074 / -0.071 / -0.053 | 4.8% | -0.102 / -0.099 / -0.074 | no |
| 70%+ | 97,811 / 81,685 | -0.083 / -0.114 / -0.047 | 4.7% | -0.114 / -0.103 / -0.075 | no |

### Stop versus the sweep extreme ('a range from the sweep')


| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| stop inside the sweep wick | 25,603 / 21,867 | -0.052 / -0.068 / +0.028 | 4.9% | -0.086 / -0.089 / -0.065 | no |
| stop at the sweep extreme | 8,778 / 7,777 | +0.008 / -0.082 / +0.145 | 5.3% | -0.057 / -0.068 / -0.040 | no |
| stop beyond the sweep extreme | 19,433 / 17,688 | +0.000 / -0.005 / -0.015 | 5.3% | -0.037 / -0.080 / -0.034 | no |
| no sweep | 184,318 / 162,247 | -0.091 / -0.109 / -0.067 | 4.7% | -0.126 / -0.113 / -0.082 | loses more (both periods) |

### Pull-back from the sweep extreme to candle 4's close (ATR units)


| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| Q1 <= 1.05 | 10,763 / 9,900 | -0.031 / +0.007 / +0.042 | 5.0% | -0.069 / -0.079 / -0.031 | no |
| Q2 1.05-1.72 | 10,763 / 9,918 | +0.034 / -0.089 / +0.035 | 5.3% | -0.035 / -0.086 / -0.054 | no |
| Q3 1.72-2.33 | 10,684 / 9,333 | -0.002 / -0.041 / -0.029 | 5.2% | -0.065 / -0.086 / -0.061 | no |
| Q4 2.33-3.2 | 10,841 / 9,352 | -0.012 / -0.059 / +0.062 | 5.1% | -0.072 / -0.074 / -0.032 | no |
| Q5 > 3.2 | 10,763 / 8,829 | -0.107 / -0.053 / +0.023 | 4.8% | -0.077 / -0.087 / -0.070 | no |
| n/a | 184,318 / 162,247 | -0.091 / -0.109 / -0.067 | 4.7% | -0.126 / -0.113 / -0.082 | loses more (both periods) |

### Sweep candle closed back inside the pivot


| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| yes | 22,184 / 20,741 | -0.015 / -0.000 / +0.020 | 5.2% | -0.047 / -0.062 / -0.056 | no |
| no | 31,630 / 26,591 | -0.029 / -0.083 / +0.033 | 5.0% | -0.076 / -0.098 / -0.040 | no |
| no sweep | 184,318 / 162,247 | -0.091 / -0.109 / -0.067 | 4.7% | -0.126 / -0.113 / -0.082 | loses more (both periods) |

### Pivots swept


| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| 1 | 33,335 / 29,613 | -0.028 / -0.076 / +0.013 | 5.1% | -0.075 / -0.087 / -0.048 | no |
| 2 | 11,913 / 10,671 | -0.013 / +0.005 / +0.053 | 5.1% | -0.042 / -0.083 / -0.044 | no |
| 3+ | 8,566 / 7,048 | -0.023 / -0.003 / +0.050 | 5.1% | -0.050 / -0.062 / -0.058 | no |
| none | 184,318 / 162,247 | -0.091 / -0.109 / -0.067 | 4.7% | -0.126 / -0.113 / -0.082 | loses more (both periods) |

### Engulfing type


| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| both strict | 73,704 / 74,399 | -0.086 / -0.089 / -0.056 | 4.7% | -0.106 / -0.106 / -0.081 | no |
| one strict | 107,553 / 91,031 | -0.058 / -0.103 / -0.050 | 4.9% | -0.114 / -0.106 / -0.071 | no |
| both loose | 56,875 / 44,149 | -0.096 / -0.085 / -0.023 | 4.7% | -0.115 / -0.104 / -0.070 | no |

### Hour candle 4 closes (UTC)


| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| 00-07 Asia | 59,313 / 56,740 | -0.089 / -0.109 / -0.022 | 4.3% | -0.137 / -0.119 / -0.087 | no |
| 07-12 London | 63,000 / 53,648 | -0.041 / -0.055 / -0.009 | 4.6% | -0.107 / -0.098 / -0.060 | no |
| 12-16 overlap | 54,442 / 45,569 | -0.007 / -0.042 / -0.045 | 5.2% | -0.090 / -0.088 / -0.062 | loses less (both periods) |
| 16-21 New York | 52,932 / 45,020 | -0.168 / -0.174 / -0.117 | 5.1% | -0.105 / -0.105 / -0.068 | loses more (both periods) |
| 21-24 late | 8,445 / 8,602 | -0.103 / -0.109 / -0.102 | 4.5% | -0.155 / -0.169 / -0.127 | no |

### Weekday


| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| Mon | 46,449 / 41,293 | -0.139 / -0.152 / -0.016 | 4.1% | -0.123 / -0.123 / -0.061 | loses more (both periods) |
| Tue | 47,816 / 41,287 | -0.055 / -0.013 / -0.056 | 4.5% | -0.103 / -0.095 / -0.073 | no |
| Wed | 47,791 / 42,289 | -0.080 / -0.119 / -0.076 | 4.4% | -0.118 / -0.103 / -0.084 | no |
| Thu | 48,477 / 42,748 | -0.047 / -0.081 / -0.034 | 4.6% | -0.103 / -0.108 / -0.078 | no |
| Fri | 46,172 / 40,439 | -0.062 / -0.110 / -0.051 | 6.3% | -0.112 / -0.093 / -0.075 | no |

### Minutes until the limit filled


| Condition | trades 2011-15 / 2016-19 | 20R: R a trade 2011-15 / 2016-19 / 2020-22 | win rate 2011-15 | 3R: R a trade (3 periods) | consistent? |
|---|---|---|---|---|---|
| Q1 <= 1 | 45,873 / 42,566 | -0.071 / -0.138 / -0.033 | 4.7% | -0.111 / -0.127 / -0.071 | no |
| Q2 1-2 | 36,271 / 32,111 | -0.091 / -0.107 / +0.012 | 4.6% | -0.129 / -0.118 / -0.067 | no |
| Q3 2-5 | 55,788 / 49,257 | -0.070 / -0.104 / -0.067 | 4.8% | -0.130 / -0.109 / -0.094 | no |
| Q4 5-13 | 50,789 / 42,731 | -0.096 / -0.058 / -0.064 | 4.7% | -0.110 / -0.100 / -0.079 | no |
| Q5 > 13 | 49,411 / 42,914 | -0.055 / -0.068 / -0.062 | 5.0% | -0.083 / -0.077 / -0.055 | no |

## Winners vs losers (2011-15; 2016-19 in brackets)

| Feature | winners' average | losers' average | standardized difference | KS distance |
|---|---|---|---|---|
| vol_regime | 1.12 | 1.07 | +0.094 (+0.081) | 0.040 (0.034) |
| range_atr | 2.11 | 2.06 | +0.061 (+0.068) | 0.024 (0.034) |
| risk_atr | 0.844 | 0.824 | +0.061 (+0.068) | 0.024 (0.034) |
| depth_R | 0.783 | 0.83 | -0.050 (-0.049) | 0.036 (0.031) |
| room2 | 11.3 | 11.8 | -0.045 (-0.030) | 0.027 (0.021) |
| mom60 | 0.831 | 1.07 | -0.041 (-0.026) | 0.024 (0.015) |
| room1 | 6.66 | 6.86 | -0.032 (-0.020) | 0.017 (0.011) |
| fill_delay | 8.53 | 8.19 | +0.028 (+0.025) | 0.012 (0.021) |
| body4 | 0.768 | 0.772 | -0.025 (-0.017) | 0.026 (0.022) |
| depth_atr | 0.545 | 0.556 | -0.024 (-0.031) | 0.022 (0.021) |
| daypos | 0.48 | 0.485 | -0.017 (-0.007) | 0.012 (0.009) |
| pullback_atr | 2.09 | 2.11 | -0.013 (+0.003) | 0.015 (0.014) |
| c4pos | 0.0733 | 0.0721 | +0.013 (+0.023) | 0.019 (0.026) |
| mom1440 | 0.0189 | 0.013 | +0.011 (+0.016) | 0.009 (0.009) |
| ratio2 | 2.02 | 1.99 | +0.005 (+0.003) | 0.014 (0.024) |
| body2 | 0.773 | 0.774 | -0.005 (-0.019) | 0.019 (0.018) |
| ratio4 | 1.98 | 1.96 | +0.005 (-0.006) | 0.015 (0.019) |
| pivot_age | 380 | 357 | +0.003 (+0.015) | 0.016 (0.014) |

## Why the losers lose (stopped trades, 20R payout)

| | 2011-15 | 2016-19 | 2020-22 |
|---|---|---|---|
| immediate failure (best < 0.3R) | 52% | 52% | 50% |
| middle (0.3-1R) | 11% | 11% | 11% |
| reversal (reached >= 1R first) | 37% | 37% | 39% |
| wick stop (stop exceeded by < 0.2R, then +1R within an hour) | 6% | 6% | 5% |
| breakout (ran >= 3R past the stop first) | 68% | 68% | 69% |
| reached TP1 later the same day | 80% | 81% | 81% |
| reached TP2 later the same day | 71% | 72% | 72% |

Most losers are not stop hunts: half never move 0.3R in favour, and two thirds keep going 3R or more past the stop (the
sweep was the start of a real move). Only 5-6% are wick stops that a slightly bigger stop would have saved. That most later
reach TP1 anyway (after running far past the stop) is what a random walk does, not a sign the stop is too tight.

## The scanner rule built from these results (greedy, 2011-15, checked on 2016-19)

- add `hour (UTC, candle 4 close) = 12-16 overlap`: 2011-15 -0.007R (+0.069, t 4.22), 2016-19 -0.042R, 2020-22 -0.045R
- add `weekday != Mon`: 2011-15 +0.024R (+0.031, t 3.52), 2016-19 -0.039R, 2020-22 -0.036R
- payout re-chosen on 2011-15: 20R (+0.024 / -0.039 / -0.036R). Keeping the sweep requirement too: +0.103 / -0.027 / -0.019R (information only).

Positive only in the years it was chosen on: the signature of fitting noise.
