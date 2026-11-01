# Truth Lab report — tom_indices_v2

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Month-end and month-start money flows lift equity indexes on the last trading day and the first three.

Fingerprint `6f860d8435d89e40` · started 2026-11-01 07:22:38 UTC · markets US500, NAS100, GER40, UK100, JP225 · timeframes H1 · parameters {"window": ["d-1_d+3"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 1 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.058R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
