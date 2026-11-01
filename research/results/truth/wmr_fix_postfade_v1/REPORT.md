# Truth Lab report — wmr_fix_postfade_v1

**Verdict: Rejected**

Hypothesis: The push into the 16:00 London fix reverses once the fix orders are filled: fading it from 16:00 to 17:00 London earns more than the round-trip cost.

Fingerprint `51e801113a200227` · started 2026-11-01 13:34:33 UTC · markets EURUSD, GBPUSD · timeframes M5 · parameters {"stop": ["catastrophe", "structure"], "days": ["all", "month_end"]} · management {"tgt": [5.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 4 configurations; 50% positive in development 2011–19, 25% positive in development and validation; median +0.021R per trade.
3. Development gate passed by 1 configurations.
   Candidate: `{"tf": "M5", "stop": "catastrophe", "days": "month_end", "tgt": 5.0, "trail": 0.0, "bias": 0}`
   Development 215 trades, E +0.046R, t 1.23 · validation E +0.091R · walk-forward E -0.037R · neighbours all positive: False (median t -0.10)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E +0.043R · deflated Sharpe +0.701 (chance the edge is real after 4 tries).
5. Final look 2023–25 (logged 2026-11-01 13:34:49 UTC): 72 trades, E +0.018R, t +0.50, PF +1.15; per market EURUSD +0.042, GBPUSD -0.007.
6. Criteria: 1_E_pos_dev_val_oos ✔, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✘, 4_neighbours_stable ✘, 5_stress_dev_val_pos ✔, 6_oos_pos_2_markets ✘.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.058, 2020–22 +0.104, 2023–25 +0.031R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book +0.18; Sharpe book +1.21 → book + this +1.18 (2017 on: +1.03 → +1.01).

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
