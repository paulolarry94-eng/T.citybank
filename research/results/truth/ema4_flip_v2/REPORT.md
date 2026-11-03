# Truth Lab report — ema4_flip_v2

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Four consecutive candles crossing the 10 EMA in turn, with the 4th FULLY engulfing the 3rd (close beyond its low/high; A+ also the 2nd beyond the 1st), predict a move in the 4th candle's direction larger than costs.

Fingerprint `7b8ee330ba5080de` · started 2026-11-03 00:15:04 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M5, M15, M30, H1, H4 · parameters {"entry": ["mid50", "close"], "stop": ["c4", "c34", "all4"], "buffer": [0.0, 0.25, 0.5], "exit": ["1R", "2R", "3R", "4R", "trail1", "trail2", "ema"], "grade": ["A", "AB"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 1260 configurations; 9% positive in development 2011–19, 2% positive in development and validation; median -0.114R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
