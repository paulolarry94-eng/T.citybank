# Truth Lab report — pa4_engulf_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Four alternating candles where the 2nd and the 4th each close beyond the previous candle's full range (no EMA) predict a move in the 4th candle's direction larger than costs.

Fingerprint `ef423560bbf703f1` · started 2026-11-03 00:44:21 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M5, M15, M30, H1, H4 · parameters {"entry": ["x4", "mid50", "close"], "stop": ["all4", "c4"], "buffer": [0.0, 0.25, 0.5], "exit": ["1R", "2R", "3R", "4R", "trail1", "trail2"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 540 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.132R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
