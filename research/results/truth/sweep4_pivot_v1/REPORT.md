# Truth Lab report — sweep4_pivot_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: Right after a pivot level is swept, a strong two-step body-engulf reversal marks trapped breakout traders; a 60% pull-back entry with the stop beyond the sweep reaches 3R-15R or the next pivot often enough to pay.

Fingerprint `8009640f77b78315` · started 2026-11-12 07:26:35 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M1, M5, M15, M30, H1, H4 · parameters {"piv": [10, 5], "sweep": ["c12", "near"], "stop": ["range", "buf20", "trail"], "target": [3, 5, 8, 10, 15, "p1", "p2"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 504 configurations; 24% positive in development 2011–19, 3% positive in development and validation; median -0.154R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
