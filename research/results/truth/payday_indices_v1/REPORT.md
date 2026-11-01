# Truth Lab report — payday_indices_v1

**Verdict: Rejected**

Hypothesis: Salary money arriving around the 15th lifts equity indexes on the next trading day.

Fingerprint `360f43f984ad4995` · started 2026-11-01 08:14:08 UTC · markets US500, NAS100, GER40, UK100, JP225 · timeframes H1 · parameters {"day": ["payday"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 1 configurations; 100% positive in development 2011–19, 0% positive in development and validation; median +0.016R per trade.
3. Development gate passed by 1 configurations.
   Candidate: `{"tf": "H1", "day": "payday", "tgt": 0.0, "trail": 0.0, "bias": 0}`
   Development 529 trades, E +0.016R, t 2.11 · validation E -0.010R · walk-forward E +0.008R · neighbours all positive: False (median t —)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E -0.004R · deflated Sharpe +0.980 (chance the edge is real after 1 tries).
5. Final look 2023–25 (logged 2026-11-01 08:14:22 UTC): 151 trades, E -0.006R, t -0.45, PF +0.90; per market US500 +0.000, NAS100 -0.010, GER40 -0.047, UK100 -0.003, JP225 +0.019.
6. Criteria: 1_E_pos_dev_val_oos ✘, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✔, 4_neighbours_stable ✘, 5_stress_dev_val_pos ✘, 6_oos_pos_2_markets ✔.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.030, 2020–22 -0.002, 2023–25 -0.000R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book +0.08; Sharpe book +1.21 → book + this +0.89 (2017 on: +1.03 → +0.70).

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
