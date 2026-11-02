# Truth Lab report — ema4_flip_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Four consecutive candles crossing the 10 EMA in turn, with the 4th closing beyond the 3rd candle's open (B+), or also the 2nd beyond the 1st (A+), predict a move in the 4th candle's direction larger than costs.

Fingerprint `d039fe0124357572` · started 2026-11-02 23:50:30 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M5, M15, M30, H1, H4 · parameters {"entry": ["mid50", "close"], "stop": ["c4", "all4"], "buffer": [0.0, 0.1, 0.25, 0.5], "target": [1, 2, 3, 4], "grade": ["A", "AB"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 640 configurations; 15% positive in development 2011–19, 5% positive in development and validation; median -0.093R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
