# Truth Lab report — body4_range_v5

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: A small-timeframe body-engulf range that agrees with the same setup on a bigger timeframe (strict or loose engulfing), traded in safe hours, reaches 2R-10R often enough to pay its costs.

Fingerprint `5d47dad91b5f7e86` · started 2026-11-08 02:47:07 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M1, M5, M15, M30, H1, H4 · parameters {"engulf": ["body", "loose"], "layer": ["none", "on"], "target": [2, 3, 5, 10], "be": [1, 0], "buffer": [0.0, 0.2], "lookback": [1, 0]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 768 configurations; 7% positive in development 2011–19, 3% positive in development and validation; median -0.137R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
