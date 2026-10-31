# Truth Lab report — coin_flip_control_v1

**Verdict: Rejected**

Hypothesis: None — random direction at random bars. Exists to prove the lab rejects noise.

Fingerprint `e5c9e121982edd30` · started 2026-10-31 12:39:49 UTC · markets XAUUSD, EURUSD, GBPUSD, USDJPY · timeframes H1, H4 · parameters {"every": [20, 40]} · management {"tgt": [2.0, 3.0, 0.0], "trail": [0.0, 3.0], "bias": [0, 1]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 48 configurations; 19% positive in development 2011–19, 6% positive in development and validation; median -0.060R per trade.
3. Development gate passed by 1 configurations.
   Candidate: `{"tf": "H4", "every": 40, "tgt": 0.0, "trail": 3.0, "bias": 1}`
   Development 405 trades, E +0.083R, t 1.12 · validation E +0.042R · walk-forward E -0.000R · neighbours all positive: False (median t +0.17)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E +0.017R · deflated Sharpe +0.238 (chance the edge is real after 48 tries).
5. Final look 2023–25 (logged 2026-10-31 12:20:28 UTC): 147 trades, E +0.026R, t +0.24, PF +1.06; per market XAUUSD +0.500, EURUSD -0.210, GBPUSD -0.011, USDJPY -0.225.
6. Criteria: 1_E_pos_dev_val_oos ✔, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✘, 4_neighbours_stable ✘, 5_stress_dev_val_pos ✔, 6_oos_pos_2_markets ✘.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.127, 2020–22 +0.086, 2023–25 +0.061R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book +0.07; Sharpe book +1.00 → book + this +0.91 (2017 on: +0.84 → +0.84).

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
