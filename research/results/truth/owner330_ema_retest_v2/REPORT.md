# Truth Lab report — owner330_ema_retest_v2

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: With the owner's corrected reference (pullback touches the anchor range) and a stop beyond the candle or pullback extreme plus an ATR buffer, the 3:30 EMA retest traded at 1:1 wins often enough to beat costs.

Fingerprint `766089e7d88288da` · started 2026-11-02 22:44:59 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M5 · parameters {"anchor": ["wat1530", "ny0930"], "stop": ["candle", "swing"], "buffer": [0.0, 0.1, 0.25, 0.5]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 16 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.131R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
