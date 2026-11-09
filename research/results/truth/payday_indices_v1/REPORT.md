# Truth Lab report — payday_indices_v1

**Verdict: Rejected**

Hypothesis: Salary money arriving around the 15th lifts equity indexes on the next trading day.

Fingerprint `360f43f984ad4995` · started 2026-11-03 07:54:23 UTC · markets US500, NAS100, GER40, UK100, JP225 · timeframes H1 · parameters {"day": ["payday"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 1 configurations; 100% positive in development 2011–19, 0% positive in development and validation; median +0.014R per trade.
3. Development gate passed by 1 configurations.
   Candidate: `{"tf": "H1", "day": "payday", "tgt": 0.0, "trail": 0.0, "bias": 0}`
   Development 529 trades, E +0.014R, t 1.69 · validation E -0.025R · walk-forward E +0.016R · neighbours all positive: False (median t —)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E -0.009R · deflated Sharpe +0.951 (chance the edge is real after 1 tries).
5. Final look 2023–25 (logged 2026-11-01 08:14:22 UTC): 151 trades, E -0.006R, t -0.45, PF +0.90; per market US500 +0.000, NAS100 -0.010, GER40 -0.047, UK100 -0.003, JP225 +0.019.
6. Criteria: 1_E_pos_dev_val_oos ✘, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✔, 4_neighbours_stable ✘, 5_stress_dev_val_pos ✘, 6_oos_pos_2_markets ✔.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.028, 2020–22 -0.017, 2023–25 +0.008R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book +0.10; Sharpe book +1.21 → book + this +0.84 (2017 on: +1.03 → +0.63).

## Cycle goal (owner: +2% to +7% per 10-trade cycle, 95% of 360-trade lifecycles inside the drawdown cap)
Edge quality s = mean R / spread of R per trade (after costs). Needed: +2% inside 3.6% 0.42, inside 5% 0.35; +7% inside 3.6% 0.81, inside 5% 0.68.

| Period | Trades | Win rate | Edge quality s | Cycle at 3.6% cap | at 5% | at 8% | Gap to +2% at 3.6% |
|---|---|---|---|---|---|---|---|
| 2011-19 | 529 | 55% | 0.073 | +0.04% | +0.05% | +0.09% | x5.7 |
| 2020-22 | 146 | 50% | -0.070 | -0.02% | -0.03% | -0.05% | no edge |
| 2023-25 | 149 | 50% | 0.012 | +0.02% | +0.03% | +0.05% | x35.8 |

## Cycles and lifecycles in actual trade order (risk set so 95% of bootstrapped 360-trade lifecycles stay inside 3.6%)
| Period | Risk per trade | Trades a year | Cycles a year | Months per lifecycle | Positive cycles | Median cycle | Worst cycle | Lifecycles done | Lifecycle return (each) | Worst lifecycle drawdown |
|---|---|---|---|---|---|---|---|---|---|---|
| 2011-19 | 0.317% | 59 | 5.9 | 72.8 | 64% | +0.12% | -1.31% | 1 | +1.2% | 3.57% |
| 2020-22 | 0.117% | 50 | 5.0 | 86.3 | 50% | -0.00% | -0.46% | 0 | - | 0.00% |
| 2023-25 | 0.370% | 51 | 5.1 | 84.7 | 79% | +0.11% | -0.49% | 0 | - | 0.00% |

## Cost ladder (same trades, other prices; swaps unchanged): mean R per trade (t)
| Prices | 2011-19 | 2020-22 | 2023-25 |
|---|---|---|---|
| gross | +0.021 (+2.7) | -0.020 (-0.7) | +0.005 (+0.4) |
| roboforex_prime | +0.019 (+2.0) | -0.029 (-0.8) | +0.005 (+0.3) |
| exness_zero | — (—) | — (—) | — (—) |
| lab_standard | +0.013 (+1.7) | -0.025 (-0.8) | +0.002 (+0.1) |

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
