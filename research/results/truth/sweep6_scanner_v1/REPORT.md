# Truth Lab report — sweep6_scanner_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: The four-candle reversal formed in the London-New York overlap (not Mondays), entered on a 60% pull-back with a 20R target, has enough raw edge to pay costs on some timeframe and market.

Fingerprint `3a65cb8f6f8da8c5` · started 2026-11-12 15:08:54 UTC · markets XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225 · timeframes M1, M5, M15, M30, H1, H4 · parameters {"rule": ["scanner"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 6 configurations; 0% positive in development 2011–19, 0% positive in development and validation; median -0.269R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
