# Truth Lab report — ath_trend_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Buying a 10-year closing high with a 1-ATR trailing stop earns after costs on our markets.

Fingerprint `05b5d6f3093790c7` · started 2026-11-01 08:10:49 UTC · markets XAUUSD, EURUSD, GBPUSD, USDJPY, US500, NAS100, GER40, UK100, JP225, WTI, XAGUSD · timeframes D1 · parameters {"side": ["long", "both"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 2 configurations; 50% positive in development 2011–19, 50% positive in development and validation; median -0.039R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
