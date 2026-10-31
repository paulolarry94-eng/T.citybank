# Truth Lab report — leg34_gold_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: On gold's 5-minute chart, after a 4-3-2-1 trend structure with engulfing legs above (below) the 10 EMA and a falling (rising) EMA, price returns to the eaten Leg 4 candle within 8 hours and continues the trend far enough for 3-4R targets or a trailing exit to pay after costs.

Fingerprint `06f74d5badf43bd4` · started 2026-10-31 20:21:05 UTC · markets XAUUSD · timeframes M5 · parameters {"k": [3, 4, 5], "engulf": ["perfect", "any"], "window": ["all", "owner"], "buffer": ["fixed", "scaled"], "exit": ["t3", "t4", "t3be", "t4be", "ladder", "ema"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 144 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.186R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
