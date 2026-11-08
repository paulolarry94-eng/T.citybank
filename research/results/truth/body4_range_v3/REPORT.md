# Truth Lab report — body4_range_v3

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: With dojis counted as bullish in the lookback, the body-engulf range entries reach a 10R (or 2R) target often enough to pay costs and swaps (10R needs about 1 win in 10 before costs).

Fingerprint `85fc8b16f32a31ae` · started 2026-11-08 01:52:23 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M1, M5, M15, M30, H1, H4 · parameters {"target": [10, 2], "entry": [0.5, 0.7], "be": [1, 0], "buffer": [0.0, 0.05, 0.1, 0.2], "lookback": [1, 0]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 384 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.221R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
