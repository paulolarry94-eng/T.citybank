# Truth Lab report — sweep5_pivot_v2

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: After a pivot is swept, a two-step engulfing reversal traps breakout traders; a 60% pull-back limit with the stop beyond the four candles reaches the next pivots (TP1, TP2) often enough to pay, taking 60% at TP1.

Fingerprint `85c358bed1b91dc8` · started 2026-11-12 09:38:51 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M1, M5, M15, M30, H1 · parameters {"sweep": ["now", "recent"], "stop": ["range", "wide"], "life": [24, 96], "exit": ["partial", "tp1", "tp2"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 120 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.221R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
