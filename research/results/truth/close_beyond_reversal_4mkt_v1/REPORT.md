# Truth Lab report — close_beyond_reversal_4mkt_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Same as eurusd_close_beyond_reversal_v1: an exhaustion close beyond the prior range snaps back.

Fingerprint `367894baf44b3f7c` · started 2026-10-31 15:45:47 UTC · markets XAUUSD, EURUSD, GBPUSD, USDJPY · timeframes D1 · parameters {"stop_pct": [1.35, 2.25, 3.15]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 3 configurations; 100% positive in development 2011–19, 100% positive in development and validation; median +0.009R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
