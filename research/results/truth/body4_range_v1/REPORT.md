# Truth Lab report — body4_range_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Four alternating candles whose 2nd and 4th bodies engulf the 1st and 3rd mark a range whose midpoint (or 70% pull-back) is a good place to join the 4th candle's direction for a 4R move, after costs and swaps.

Fingerprint `9ae0e7fecfab060d` · started 2026-11-08 01:25:23 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M1, M5, M15, M30, H1, H4 · parameters {"entry": [0.5, 0.7], "be": [1, 0], "buffer": [0.0, 0.05, 0.1, 0.2], "lookback": [1, 0]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 192 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.198R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
