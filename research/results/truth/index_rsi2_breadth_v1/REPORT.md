# Truth Lab report — index_rsi2_breadth_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Short-term sell-offs in equity indices overshoot (liquidity demand from forced and impatient sellers) and revert within days; buying them in an uptrend earns that liquidity premium plus the equity drift.

Fingerprint `cee44b5be5eb8807` · started 2026-10-31 18:25:05 UTC · markets NAS100, UK100, JP225 · timeframes D1 · parameters {"lo": [5, 10], "trend": [100, 200]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 4 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.026R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
