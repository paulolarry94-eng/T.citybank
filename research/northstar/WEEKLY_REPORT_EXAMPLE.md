# North Star weekly report — week ending 2025-12-26 (EXAMPLE from 2025 backtest trades — not live data)

Tags: **FACT** = observed in the logs · **ESTIMATE** = statistical, with uncertainty · **RULE** = action that follows from the pre-registered monitoring rules (R1–R5).

## 1. Account equity and balance
- FACT: balance 10,593.06, equity 10,593.06 (start of week equity 10,562.36).
## 2. Realised and unrealised P&L
- FACT: realised this week +30.70 from 5 closed trades; unrealised now +0.00.
## 3. Return for the week and since inception
- FACT: week +0.29%; since inception +5.93% (2025-01-01 → 2025-12-26).
- ESTIMATE: backtest weekly range at 1% base risk — 5%: -1.26%, median: +0.07%, 95%: +1.89%. This week is inside the 5–95% range (R4: information only).
## 4. Peak-to-trough drawdown
- FACT: current drawdown 0.33%; worst since inception 9.95%.
## 5. Open positions and total risk
- FACT: 4 open position(s); open risk 0.00% of equity (cap 10%).
  - XAU_Donchian20_H4_turtle XAUUSD long since 2025-12-11 18:00, risk 22.28
  - GBPJPY_Donchian20_H4_trail GBPJPY long since 2025-12-18 14:00, risk 26.10
  - XAU_EMA20-50_H4 XAUUSD long since 2025-11-25 02:00, risk 35.71
  - EURGBP_Bollinger_D1_k1.5 EURGBP long since 2025-12-25 02:00, risk 59.60
## 6. Trades by strategy
| strategy | week trades | week R | live trades | live mean R | backtest mean R | current losing streak | backtest 99% streak |
|---|---|---|---|---|---|---|---|
| EUR_EuroHours_short_TueThu | 2 | +0.28 | 153 | +0.058 | +0.047 | 0 | 7 |
| XAU_S1_reversion_H1M30M20 | 0 | +0.00 | 8 | -0.004 | +0.261 | 2 | 4 |
| JPY_VolBreakout_D1_k0.7 | 3 | +0.94 | 90 | -0.078 | +0.070 | 2 | 7 |
| XAU_Donchian20_H4_turtle | 0 | +0.00 | 39 | +0.378 | +0.075 | 0 | 10 |
| JPY_S2_Donchian20_H4_long | 0 | +0.00 | 3 | -0.123 | +0.283 | 1 | 8 |
| XAU_EMA20-50_H4 | 0 | +0.00 | 5 | +3.549 | +0.334 | 0 | 7 |
| GBP_WeeklySweep_FollowThrough | 0 | +0.00 | 6 | -0.063 | +0.309 | 0 | 4 |
| JPY_Donchian55_D1_trail | 0 | +0.00 | 5 | -0.054 | +0.186 | 0 | 5 |
| JPY_RSI2_D1_lo5 | 0 | +0.00 | 6 | +0.371 | +0.104 | 0 | 4 |
| GBPJPY_Donchian20_H4_trail | 0 | +0.00 | 38 | -0.315 | +0.082 | 1 | 7 |
| EURGBP_Bollinger_D1_k1.5 | 0 | +0.00 | 30 | -0.177 | +0.002 | 0 | 6 |
## 7. Expectancy and profit factor (with sample-size caveats)
- ESTIMATE: live expectancy +0.048R per trade, 95% interval [-0.103, +0.199] from 383 trades; profit factor 1.13.
- ESTIMATE: at this spread of results, about 3,831 trades are needed before the sign of the expectancy is known with 95% confidence — not reached yet; do not judge the system on this sample.
## 8. Spread, slippage and execution quality
- FACT: median entry spread nan points; median slippage +0.0 points; swap +0.00; commission +0.00.
- FACT: median slippage of the last 20 fills +0.0000R (limit 0.0130R).
- RULE R3: within limits.
## 9. Live/demo against backtest ranges
- ESTIMATE: backtest trades per active week 5%–95%: 5–11; this week 5 (FACT).
- ESTIMATE: backtest win rate 47%, mean +0.076R; live win rate 47% (FACT, 383 trades).
## 10. Portfolio state
- FACT: governor state at week end: **GREEN**.
## 11. Data, execution and risk-limit breaches
- FACT: none logged.
## 12. Recommended action (rules R1–R5)
- RULE R1: GREEN — continue unchanged.
- RULE R2: GBPJPY_Donchian20_H4_trail under review (38 live trades, t vs backtest -2.46, losing streak 1 vs 99% 7). Operator decision required; no automatic change.
