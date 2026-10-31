# Truth Lab report — index_rsi2_v1

**Verdict: Rejected**

Hypothesis: Short-term sell-offs in equity indices overshoot (liquidity demand from forced and impatient sellers) and revert within days; buying them in an uptrend earns that liquidity premium plus the equity drift.

Fingerprint `b964c8b77620e052` · started 2026-10-31 18:16:35 UTC · markets US500, GER40 · timeframes D1 · parameters {"lo": [5, 10], "trend": [100, 200]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 4 configurations; 100% positive in development 2011–19, 100% positive in development and validation; median +0.031R per trade.
3. Development gate passed by 1 configurations.
   Candidate: `{"tf": "D1", "lo": 10, "trend": 200, "tgt": 0.0, "trail": 0.0, "bias": 0}`
   Development 206 trades, E +0.040R, t 1.26 · validation E +0.026R · walk-forward E —R · neighbours all positive: True (median t +1.39)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E -0.005R · deflated Sharpe +0.555 (chance the edge is real after 4 tries).
5. Final look 2023–25 (logged 2026-10-31 18:16:42 UTC): 83 trades, E +0.094R, t +1.87, PF +1.67; per market US500 +0.126, GER40 +0.057.
6. Criteria: 1_E_pos_dev_val_oos ✔, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✘, 4_neighbours_stable ✔, 5_stress_dev_val_pos ✘, 6_oos_pos_2_markets ✔.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.090, 2020–22 +0.044, 2023–25 +0.113R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book +0.03; Sharpe book +1.00 → book + this +0.78 (2017 on: +0.84 → +0.66).

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
