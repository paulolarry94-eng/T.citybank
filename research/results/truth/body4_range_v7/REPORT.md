# Truth Lab report — body4_range_v7

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Curated: a body-engulf range with 60%-body engulfing candles after two 60%-body candles in the trade's direction, on M5/M15 in the London-New York crossover at RoboForex Prime costs, reaches 3R-6R often enough to pay.

Fingerprint `3024ad8f04cac711` · started 2026-11-09 20:25:33 UTC · markets EURUSD, GBPUSD, USDJPY, EURGBP, XAUUSD, US500, NAS100, GER40, WTI, JP225 · timeframes M5, M15 · parameters {"lbbody": [1, 0], "target": [3, 4, 5, 6]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 16 configurations; 25% positive in development 2011–19, 0% positive in development and validation; median -0.121R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
