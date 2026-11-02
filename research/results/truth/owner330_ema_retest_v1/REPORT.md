# Truth Lab report — owner330_ema_retest_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: When the 30-minute candle at the New York open crosses its 10 EMA, the first M5 EMA cross back inside that candle's range, traded on the break of the M5 candle with a fixed R target, pays more than costs.

Fingerprint `7a93770f72720192` · started 2026-11-02 12:32:32 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M5 · parameters {"anchor": ["wat1530", "ny0930"], "entry": ["A", "B3", "B6", "B12"], "target": [2, 3, 4], "be": [0, 1]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 48 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.201R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
