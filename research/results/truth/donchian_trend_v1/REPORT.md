# Truth Lab report — donchian_trend_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Breakouts of an N-bar range persist (trend following: slow information diffusion, hedging flows).

Fingerprint `d2e00c7f54e9b68b` · started 2026-10-31 12:24:42 UTC · markets XAUUSD, EURUSD, GBPUSD, USDJPY · timeframes H4, D1 · parameters {"n": [20, 55], "atr_stop": [2.0, 3.0]} · management {"tgt": [2.0, 3.0, 0.0], "trail": [0.0, 3.0], "bias": [0, 1]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 96 configurations; 4% positive in development 2011–19, 4% positive in development and validation; median -0.038R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
