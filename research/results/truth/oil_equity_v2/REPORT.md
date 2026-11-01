# Truth Lab report — oil_equity_v2

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: A falling oil price this month predicts higher equity index returns next month, a rising one lower returns.

Fingerprint `90e65c160f8d58f3` · started 2026-11-01 07:22:52 UTC · markets US500, NAS100, GER40, UK100, JP225 · timeframes H1 · parameters {"mode": ["long_cash", "long_short"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 2 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.044R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
