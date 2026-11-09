# Truth Lab report — body4_range_v6

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: A body-engulf range whose engulfing candles are at least 60% body, after two candles in the trade's direction, traded in safe hours, reaches 4R-6R often enough to pay its costs.

Fingerprint `26ffb5c25118a57c` · started 2026-11-09 20:03:29 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M1, M5, M15, M30, H1, H4 · parameters {"body60": [1, 0], "lb2": [1, 0], "target": [4, 5, 6]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 72 configurations; 4% positive in development 2011–19, 0% positive in development and validation; median -0.167R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
