# Truth Lab report — osc_turn_sessions_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Turns of a smooth oscillator start intraday swings; trading them only in the session when that market moves (follow) or ranges (fade) keeps the trades whose follow-through pays for costs.

Fingerprint `c1289545b1ca7bd6` · started 2026-10-31 17:24:47 UTC · markets XAUUSD, EURUSD, GBPUSD, USDJPY · timeframes M15, H1, H4 · parameters {"osc": ["R1", "R2", "R3"], "window": ["all", "asia", "london", "overlap", "ny", "london_ny"], "mode": ["follow", "fade"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 108 configurations; 2% positive in development 2011–19, 0% positive in development and validation; median -0.044R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
