# Truth Lab report — sop_4leg_gold_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: After a clean two-swing trend structure with engulfing rejections at both swing extremes and an aligned EMA, price returns to the origin engulfing zone (Leg 4) and continues the trend from there. On gold's higher timeframes (owner's daily example).

Fingerprint `e2b3f1f32416bee5` · started 2026-10-31 19:08:38 UTC · markets XAUUSD · timeframes H4, D1 · parameters {"k": [3, 4, 5], "engulf": ["perfect", "any"], "window": ["all"], "valid": [10, 20, 50], "be": [0, 1]} · management {"tgt": [2.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 72 configurations; 35% positive in development 2011–19, 19% positive in development and validation; median -0.073R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
