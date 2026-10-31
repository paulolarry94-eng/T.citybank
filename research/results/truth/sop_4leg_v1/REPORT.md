# Truth Lab report — sop_4leg_v1

**Verdict: Rejected**

Hypothesis: After a clean two-swing trend structure with engulfing rejections at both swing extremes and an aligned EMA, price returns to the origin engulfing zone (Leg 4) and continues the trend from there.

Fingerprint `c9d4e687a7ae5fb8` · started 2026-10-31 19:05:13 UTC · markets EURUSD, GBPUSD · timeframes M5, M15, M30 · parameters {"k": [3, 4, 5], "engulf": ["perfect", "any"], "window": ["owner", "asia", "london", "overlap", "ny", "london_ny", "all"], "valid": [5, 10, 20], "be": [0, 1]} · management {"tgt": [2.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 756 configurations; 11% positive in development 2011–19, 5% positive in development and validation; median -0.149R per trade.
3. Development gate passed by 2 configurations.
   Candidate: `{"tf": "M15", "k": 3, "engulf": "perfect", "window": "overlap", "valid": 10, "be": 1, "tgt": 2.0, "trail": 0.0, "bias": 0}`
   Development 240 trades, E +0.084R, t 1.03 · validation E -0.240R · walk-forward E -0.084R · neighbours all positive: False (median t +0.24)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E -0.106R · deflated Sharpe +0.001 (chance the edge is real after 756 tries).
5. Final look 2023–25 (logged 2026-10-31 19:08:34 UTC): 97 trades, E -0.109R, t -0.89, PF +0.81; per market EURUSD -0.027, GBPUSD -0.203.
6. Criteria: 1_E_pos_dev_val_oos ✘, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✘, 4_neighbours_stable ✘, 5_stress_dev_val_pos ✘, 6_oos_pos_2_markets ✘.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.135, 2020–22 -0.190, 2023–25 -0.049R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book -0.01; Sharpe book +1.00 → book + this +0.52 (2017 on: +0.84 → +0.12).

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
