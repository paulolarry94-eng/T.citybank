# Truth Lab report — ecb_fix_eurusd_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Orders benchmarked to the ECB 14:10 CET concertation push EURUSD one way into the fix (continuation) and the push fades after it (reversal), by more than RoboForex Prime's round-trip cost.

Fingerprint `b96393341bd595f7` · started 2026-11-01 19:33:47 UTC · markets EURUSD · timeframes M5 · parameters {"trade": ["into", "after"], "days": ["all", "month_end"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 4 configurations; 25% positive in development 2011–19, 0% positive in development and validation; median -0.012R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
