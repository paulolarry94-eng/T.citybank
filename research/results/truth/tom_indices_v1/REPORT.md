# Truth Lab report — tom_indices_v1

**Verdict: Rejected: look-ahead (signals change when future bars are removed)**

Hypothesis: Month-end and month-start money flows lift equity indexes on the last trading day and the first three.

Fingerprint `297782478c82b85a` · started 2026-11-01 07:20:38 UTC · markets US500, NAS100, GER40, UK100, JP225 · timeframes H1 · parameters {"window": ["d-1_d+3"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **FAIL**.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
