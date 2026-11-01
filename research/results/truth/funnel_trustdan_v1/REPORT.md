# Truth Lab report — funnel_trustdan_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: The trustdan Turtle/Seykota trend variants (Donchian breakouts with pyramiding, targets and filters) earn after costs on our markets.

Fingerprint `3a38f0db76ca3fdf` · started 2026-11-01 08:04:26 UTC · markets XAUUSD, EURUSD, GBPUSD, USDJPY, US500, NAS100, GER40, UK100, JP225, WTI, XAGUSD · timeframes D1 · parameters {"rule": ["core", "alt1", "alt2", "alt3", "alt4", "alt5", "alt6", "alt7", "alt8", "alt9", "alt10", "alt11", "alt12", "alt13", "alt14", "alt15", "alt16", "alt17", "alt18", "alt19", "alt20", "alt21", "alt22", "alt23", "alt24", "alt25", "alt26", "alt27", "alt28", "alt29", "alt30", "alt31", "alt32", "alt33", "alt34", "alt35", "alt36", "alt37", "alt38", "alt39", "alt40", "alt41", "alt42", "alt43", "alt44", "alt45", "alt46", "alt47"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 48 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.548R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
