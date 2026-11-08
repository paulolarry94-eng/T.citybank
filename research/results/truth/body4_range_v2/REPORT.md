# Truth Lab report — body4_range_v2

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: The same body-engulf range entries reach a 2R or 1R target often enough to pay costs and swaps (needs roughly 40% wins at 2R and 60% at 1R after costs).

Fingerprint `53bb1d0e2297cc0e` · started 2026-11-08 01:40:01 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M1, M5, M15, M30, H1, H4 · parameters {"target": [2, 1], "entry": [0.5, 0.7], "be": [1, 0], "buffer": [0.0, 0.05, 0.1, 0.2], "lookback": [1, 0]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 384 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.217R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
