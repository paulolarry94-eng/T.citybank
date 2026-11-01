# Truth Lab report — wmr_fix_reversion_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Hedge and rebalancing orders worked into the 16:00 London fix push EURUSD and GBPUSD one way; fading that push from 15:55 to 16:05 London earns more than the round-trip cost.

Fingerprint `962ff324765b0fc6` · started 2026-11-01 13:34:08 UTC · markets EURUSD, GBPUSD · timeframes M5 · parameters {"stop": ["catastrophe", "structure"], "days": ["all", "month_end"]} · management {"tgt": [5.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 4 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.064R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
