# Truth Lab report — eurusd_close_beyond_reversal_v1

**Verdict: Tier B: forward-test candidate**

Hypothesis: A daily close beyond the prior day's range is an exhaustion move; a stop entry back through the bar's far extreme catches the snap-back, and banking the first profitable New York close harvests it.

Fingerprint `0fe044ee85982c53` · started 2026-10-31 15:45:12 UTC · markets EURUSD · timeframes D1 · parameters {"stop_pips": [150, 250, 350]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 3 configurations; 100% positive in development 2011–19, 100% positive in development and validation; median +0.032R per trade.
3. Development gate passed by 2 configurations.
   Candidate: `{"tf": "D1", "stop_pips": 250, "tgt": 0.0, "trail": 0.0, "bias": 0}`
   Development 252 trades, E +0.040R, t 1.77 · validation E +0.030R · walk-forward E +0.104R · neighbours all positive: True (median t +1.26)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E +0.016R · deflated Sharpe +0.907 (chance the edge is real after 3 tries).
5. Final look 2023–25 (logged 2026-10-31 15:45:34 UTC): 112 trades, E +0.012R, t +0.38, PF +1.14; per market EURUSD +0.012.
6. Criteria: 1_E_pos_dev_val_oos ✔, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✔, 4_neighbours_stable ✔, 5_stress_dev_val_pos ✔, 6_oos_pos_2_markets ✘.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.055, 2020–22 +0.046, 2023–25 +0.030R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book +0.11; Sharpe book +1.00 → book + this +1.08 (2017 on: +0.84 → +0.76).

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
