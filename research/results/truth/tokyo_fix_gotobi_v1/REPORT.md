# Truth Lab report — tokyo_fix_gotobi_v1

**Verdict: Tier B: forward-test candidate**

Hypothesis: Japanese importers' dollar buying at the 09:55 JST Tokyo fix on gotobi days lifts USDJPY into the fix (and it eases after), by more than the round-trip cost.

Fingerprint `84a2551837367f73` · started 2026-11-01 06:47:33 UTC · markets USDJPY · timeframes M5 · parameters {"trade": ["pre2300", "pre0000", "post0055"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 3 configurations; 100% positive in development 2011–19, 100% positive in development and validation; median +0.019R per trade.
3. Development gate passed by 1 configurations.
   Candidate: `{"tf": "M5", "trade": "pre2300", "tgt": 0.0, "trail": 0.0, "bias": 0}`
   Development 644 trades, E +0.041R, t 1.88 · validation E +0.064R · walk-forward E +0.016R · neighbours all positive: True (median t +1.23)
4. Stress 2011–22 (costs x1.5, swaps x2, +1 min): E +0.025R · deflated Sharpe +0.969 (chance the edge is real after 3 tries).
5. Final look 2023–25 (logged 2026-11-01 06:47:44 UTC): 214 trades, E +0.052R, t +1.45, PF +1.28; per market USDJPY +0.052.
6. Criteria: 1_E_pos_dev_val_oos ✔, 2_oos_PF110_t2_n100 ✘, 3_walk_forward_E_pos ✔, 4_neighbours_stable ✔, 5_stress_dev_val_pos ✔, 6_oos_pos_2_markets ✘.
7. Low-cost swap-free profile (costs x0.5, no swap): 2011–19 +0.063, 2020–22 +0.083, 2023–25 +0.067R per trade.
8. Portfolio fit: monthly correlation with the 11-leg book +0.03; Sharpe book +1.21 → book + this +1.38 (2017 on: +1.03 → +1.39).

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
