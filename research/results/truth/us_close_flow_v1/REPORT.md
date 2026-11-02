# Truth Lab report — us_close_flow_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Leveraged and vol-target funds rebalance into the US cash close in the direction of the day's move, so the last 15-30 minutes continue big moves by more than RoboForex Prime's cost.

Fingerprint `1495b4bfca9e8c33` · started 2026-11-02 08:55:10 UTC · markets US500, NAS100 · timeframes M5 · parameters {"anchor": ["prev_close", "open"], "entry": ["15:30", "15:45"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 4 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.040R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
