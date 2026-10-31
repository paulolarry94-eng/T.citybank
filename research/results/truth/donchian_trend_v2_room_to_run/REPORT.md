# Truth Lab report — donchian_trend_v2_room_to_run

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Breakouts of an N-bar range persist, and trends need room: no target, trail or opposite signal only, long time stop. (v1 with a 50-bar time stop was rejected at the gate.)

Fingerprint `411b3dcd1c11a946` · started 2026-10-31 12:24:50 UTC · markets XAUUSD, EURUSD, GBPUSD, USDJPY · timeframes H4, D1 · parameters {"n": [20, 55], "atr_stop": [2.0, 3.0]} · management {"tgt": [0.0, 3.0], "trail": [3.0, 0.0], "bias": [0, 1]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 64 configurations; 3% positive in development 2011–19, 3% positive in development and validation; median -0.063R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
