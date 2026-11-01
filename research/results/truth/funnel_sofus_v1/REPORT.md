# Truth Lab report — funnel_sofus_v1

**Verdict: Rejected: no configuration passed the development gate**

Hypothesis: The sofus-nl swing setups (breakouts, pullbacks, momentum, RSI reversion, patterns) earn after costs on our markets.

Fingerprint `1ba482475d50746a` · started 2026-11-01 08:09:43 UTC · markets XAUUSD, EURUSD, GBPUSD, USDJPY, US500, NAS100, GER40, UK100, JP225, WTI, XAGUSD · timeframes D1 · parameters {"rule": ["s01_vcp", "s02_cup_handle", "s03_ema_cross", "s04_rsi_pullback", "s07_stage2", "s08_bull_flag", "s10_triple_rsi_div", "s11_qullamaggie", "s12_multi_period", "s13_ma_stack", "s14_adx_trend", "s16_trend_template", "s18_roc_breakout", "s19_hhv_breakout", "s20_frog_pan", "s21_proximity_pullback", "s22_rsi2_reversion", "s23_trend_pullback"], "side": ["long", "both"]} · management {"tgt": [0.0], "trail": [0.0], "bias": [0]}

1. Look-ahead check (real-time decisions + prefix invariance): **pass**.
2. Grid: 36 configurations; 3% positive in development 2011–19, 0% positive in development and validation; median -0.243R per trade.
3. Development gate passed by 0 configurations.

Rules: research/northstar/PREREGISTRATION.md (tiers, costs, fills). Raw data: grid.csv.gz, pooled.csv.gz, summary.json, oos_log.json.
