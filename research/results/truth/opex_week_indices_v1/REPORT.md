# Truth Lab report — opex_week_indices_v1

**Verdict: Rejected: look-ahead (signals change when future bars are removed)**

Hypothesis: Option dealers' hedging flows lift equity indexes in the week of the monthly option expiry.

Fingerprint `236c482837588193` · started 2026-11-01 07:20:42 UTC · markets US500, NAS100, GER40, UK100, JP225 · timeframes H1 · parameters {"week": ["opex"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **FAIL**.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
