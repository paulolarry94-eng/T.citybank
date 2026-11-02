# Truth Lab report — eurusd_close_beyond_reversal_v1

**Verdict: Tier B: forward-test candidate**

Hypothesis: A daily close beyond the prior day's range is an exhaustion move; a stop entry back through the bar's far extreme catches the snap-back, and banking the first profitable New York close harvests it.

Fingerprint `0fe044ee85982c53` · started 2026-11-02 02:00:56 UTC · markets EURUSD · timeframes D1 · parameters {"stop_pips": [150, 250, 350]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 3 configurations; 100% positive in development 2011–19, 100% positive in development and validation; median +0.032R per trade.
3. Development gate passed by 2 configurations.
   Candidate: `{"tf": "D1", "stop_pips": 250, "tgt": 0.0, "trail": 0.0, "bias": 0}`
   Development 252 trades, E +0.040R, t 1.77 · validation E +0.030R · walk-forward E +0.104R · neighbours all positive: True (median t +1.26)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E +0.016R · deflated Sharpe +0.907 (chance the edge is real after 3 tries).
5. Final look 2023–25 (logged 2026-10-31 15:45:34 UTC): 112 trades, E +0.012R, t +0.38, PF +1.14; per market EURUSD +0.012.
6. Criteria: 1_E_pos_dev_val_oos ✔, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✔, 4_neighbours_stable ✔, 5_stress_dev_val_pos ✔, 6_oos_pos_2_markets ✘.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.055, 2020–22 +0.046, 2023–25 +0.030R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book +0.13; Sharpe book +1.21 → book + this +1.23 (2017 on: +1.03 → +0.90).

## Cycle goal (owner: +2% to +7% per 10-trade cycle, 95% of 360-trade lifecycles inside the drawdown cap)
Edge quality s = mean R / spread of R per trade (after costs). Needed: +2% inside 3.6% 0.42, inside 5% 0.35; +7% inside 3.6% 0.81, inside 5% 0.68.

| Period | Trades | Win rate | Edge quality s | Cycle at 3.6% cap | at 5% | at 8% | Gap to +2% at 3.6% |
|---|---|---|---|---|---|---|---|
| 2011-19 | 252 | 88% | 0.111 | +0.21% | +0.29% | +0.47% | x3.8 |
| 2020-22 | 89 | 91% | 0.091 | +0.09% | +0.13% | +0.20% | x4.6 |
| 2023-25 | 112 | 85% | 0.035 | +0.02% | +0.03% | +0.05% | x11.9 |

## Cost ladder (same trades, other prices; swaps unchanged): mean R per trade (t)
| Prices | 2011-19 | 2020-22 | 2023-25 |
|---|---|---|---|
| gross | +0.056 (+2.5) | +0.046 (+1.3) | +0.028 (+0.9) |
| roboforex_prime | +0.054 (+2.4) | +0.044 (+1.2) | +0.025 (+0.8) |
| exness_zero | +0.052 (+2.3) | +0.042 (+1.2) | +0.024 (+0.8) |
| lab_standard | +0.050 (+2.2) | +0.040 (+1.1) | +0.022 (+0.7) |

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
