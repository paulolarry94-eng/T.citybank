# Truth Lab report — ema4_final_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Four consecutive candles crossing the 10 EMA in turn, with the 4th closing beyond the 3rd candle's open (B+), or also the 2nd beyond the 1st (A+), predict a move in the 4th candle's direction larger than costs.

Fingerprint `eef782f192ecf2a6` · started 2026-11-03 01:07:26 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes H4 · parameters {"entry": ["close"], "stop": ["c4"], "buffer": [0.25], "target": [2], "grade": ["AB"], "trend": [0, 1]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 2 configurations; 100% positive in development 2011–19, 100% positive in development and validation; median +0.111R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
