# Truth Lab report — oil_equity_v1

**Verdict: Rejected: look-ahead (signals change when future bars are removed)**

Hypothesis: A falling oil price this month predicts higher equity index returns next month, a rising one lower returns.

Fingerprint `7ff5e30af80e844d` · started 2026-11-01 07:20:43 UTC · markets US500, NAS100, GER40, UK100, JP225 · timeframes H1 · parameters {"mode": ["long_cash", "long_short"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **FAIL**.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
