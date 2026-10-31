# Truth Lab report — breadth_trend_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Trend persistence (slow information diffusion, hedging and momentum flows) exists in equity indices, oil and silver as it does in gold and USDJPY; futures evidence (research/multiasset) says indices and energy trend.

Fingerprint `94312d81b003db7d` · started 2026-10-31 18:16:25 UTC · markets US500, GER40, WTI, XAGUSD · timeframes H4, D1 · parameters {"n": [20, 55], "atr_stop": [2.0, 3.0]} · management {"tgt": [0.0, 3.0], "trail": [3.0, 0.0], "bias": [0, 1]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 64 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.121R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
