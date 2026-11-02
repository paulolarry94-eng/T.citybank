# Truth Lab report — monthend_rebalance_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Fixed-weight funds rebalance against the month's equity move in the last days of the month, so index CFDs reverse the month-to-date move into month-end by more than costs and swaps.

Fingerprint `5d4589f42bcd472a` · started 2026-11-02 12:41:08 UTC · markets US500, NAS100, GER40, UK100 · timeframes M30 · parameters {"n_before": [3, 1], "filter": ["all", "strong"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 4 configurations; 50% positive in development 2011–19, 0% positive in development and validation; median -0.001R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
