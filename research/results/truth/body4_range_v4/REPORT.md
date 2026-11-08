# Truth Lab report — body4_range_v4

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Traded only in liquid London/New York hours, away from US news days and flat before the rollover, the body-engulf range reaches some target between 2R and 10R often enough to pay its costs.

Fingerprint `d4a1a6ef20c936aa` · started 2026-11-08 02:22:31 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M1, M5, M15, M30, H1, H4 · parameters {"target": [2, 3, 4, 5, 6, 7, 8, 9, 10], "window": ["safe", "all"], "entry": [0.5, 0.7], "be": [1, 0], "buffer": [0.0, 0.05, 0.1, 0.2], "lookback": [1, 0]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 3456 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.194R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
