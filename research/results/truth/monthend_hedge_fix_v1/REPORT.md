# Truth Lab report — monthend_hedge_fix_v1

**Verdict: Rejected**

Hypothesis: Month-end currency-hedge rebalancing at the London 4 pm fix moves the dollar against the month's relative US-vs-foreign equity performance, by more than RoboForex Prime's cost.

Fingerprint `92ff62b6b5bdc552` · started 2026-11-03 08:55:08 UTC · markets EURUSD, GBPUSD, USDJPY · timeframes M5 · parameters {"entry": ["1200", "1400", "1500"], "filter": ["all", "strong"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 6 configurations; 100% positive in development 2011–19, 17% positive in development and validation; median +0.114R per trade.
3. Development gate passed by 2 configurations.
   Candidate: `{"tf": "M5", "entry": "1400", "filter": "all", "tgt": 0.0, "trail": 0.0, "bias": 0}`
   Development 315 trades, E +0.096R, t 2.07 · validation E -0.319R · walk-forward E -0.183R · neighbours all positive: True (median t +1.87)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E -0.014R · deflated Sharpe +0.857 (chance the edge is real after 6 tries).
5. Final look 2023–25 (logged 2026-11-03 08:56:13 UTC): 106 trades, E -0.032R, t -0.52, PF +0.88; per market EURUSD +0.101, GBPUSD +0.034, USDJPY -0.242.
6. Criteria: 1_E_pos_dev_val_oos ✘, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✘, 4_neighbours_stable ✔, 5_stress_dev_val_pos ✘, 6_oos_pos_2_markets ✔.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.106, 2020–22 -0.310, 2023–25 -0.023R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book +0.01; Sharpe book +1.21 → book + this +0.82 (2017 on: +1.03 → +0.46).

## Cycle goal (owner: +2% to +7% per 10-trade cycle, 95% of 360-trade lifecycles inside the drawdown cap)
Edge quality s = mean R / spread of R per trade (after costs). Needed: +2% inside 3.6% 0.42, inside 5% 0.35; +7% inside 3.6% 0.81, inside 5% 0.68.

| Period | Trades | Win rate | Edge quality s | Cycle at 3.6% cap | at 5% | at 8% | Gap to +2% at 3.6% |
|---|---|---|---|---|---|---|---|
| 2011-19 | 315 | 53% | 0.117 | +0.21% | +0.29% | +0.47% | x3.6 |
| 2020-22 | 103 | 34% | -0.408 | -0.08% | -0.11% | -0.18% | no edge |
| 2023-25 | 106 | 46% | -0.050 | -0.03% | -0.04% | -0.06% | no edge |

## Cycles and lifecycles in actual trade order (risk set so 95% of bootstrapped 360-trade lifecycles stay inside 3.6%)
| Period | Risk per trade | Trades a year | Cycles a year | Months per lifecycle | Positive cycles | Median cycle | Worst cycle | Lifecycles done | Lifecycle return (each) | Worst lifecycle drawdown |
|---|---|---|---|---|---|---|---|---|---|---|
| 2011-19 | 0.214% | 36 | 3.6 | 121.2 | 61% | +0.21% | -1.21% | 0 | - | 0.00% |
| 2020-22 | 0.024% | 35 | 3.5 | 122.2 | 20% | -0.07% | -0.16% | 0 | - | 0.00% |
| 2023-25 | 0.125% | 36 | 3.6 | 118.8 | 30% | -0.01% | -0.43% | 0 | - | 0.00% |

## Cost ladder (same trades, other prices; swaps unchanged): mean R per trade (t)
| Prices | 2011-19 | 2020-22 | 2023-25 |
|---|---|---|---|
| gross | +0.115 (+2.5) | -0.300 (-3.9) | -0.014 (-0.2) |
| roboforex_prime | +0.096 (+2.1) | -0.319 (-4.2) | -0.032 (-0.5) |
| exness_zero | +0.084 (+1.8) | -0.330 (-4.3) | -0.042 (-0.7) |
| lab_standard | +0.074 (+1.6) | -0.342 (-4.4) | -0.053 (-0.9) |

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
