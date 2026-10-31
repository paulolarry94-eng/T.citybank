# Truth Lab report — wti_trend_v1

**Verdict: Rejected**

Hypothesis: Oil trends (inventory cycles, OPEC decisions and hedging flows diffuse slowly). Chosen after breadth_trend_v1 (hindsight); only 2023-25 is clean.

Fingerprint `e77413114dabc308` · started 2026-10-31 18:17:34 UTC · markets WTI · timeframes H4, D1 · parameters {"n": [20, 55], "atr_stop": [2.0, 3.0]} · management {"tgt": [0.0, 3.0], "trail": [3.0, 0.0], "bias": [0, 1]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 64 configurations; 80% positive in development 2011–19, 56% positive in development and validation; median +0.076R per trade.
3. Development gate passed by 13 configurations.
   Candidate: `{"tf": "H4", "n": 55, "atr_stop": 2.0, "tgt": 3.0, "trail": 0.0, "bias": 0}`
   Development 267 trades, E +0.160R, t 1.44 · validation E -0.168R · walk-forward E -0.006R · neighbours all positive: True (median t +0.54)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E +0.028R · deflated Sharpe +0.005 (chance the edge is real after 64 tries).
5. Final look 2023–25 (logged 2026-10-31 18:17:44 UTC): 99 trades, E -0.183R, t -1.11, PF +0.77; per market WTI -0.183.
6. Criteria: 1_E_pos_dev_val_oos ✘, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✘, 4_neighbours_stable ✘, 5_stress_dev_val_pos ✔, 6_oos_pos_2_markets ✘.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.227, 2020–22 -0.123, 2023–25 -0.130R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book -0.00; Sharpe book +1.00 → book + this +0.69 (2017 on: +0.84 → +0.30).

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
