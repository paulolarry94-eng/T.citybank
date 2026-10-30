# North Star — parameter specification (forward-test candidate)

Status: **Tier B forward-test candidate, not deployment-ready.** No configuration met the pre-registered
Tier A criteria (see NORTHSTAR_REPORT.md). Everything below is frozen; any change is a new system and
restarts the forward test.

## 1. Portfolio: the 11-leg book (frozen October 2026, `results/book_v3.json`)

Common rules for every leg (research fill law): signals on CLOSED bars only; market entry at the open of
the next bar (longs pay ask = bid + spread); protective stop placed with the order and never widened;
one position per leg at a time; no breakeven. Times are UTC unless stated. ATR = 14-bar simple average of
true range on the leg's timeframe. H4 bars use broker-clock boundaries (22/02/06/10/14/18 UTC). Weights:
inverse monthly-R volatility on 2011–2019, largest = 1 (risk per trade = base risk x weight).

| # | Leg | Market / TF | Entry | Stop | Exit | Weight | Source |
|---|---|---|---|---|---|---|---|
| 1 | EUR_EuroHours_short_TueThu | EURUSD M1 clock | Tue–Thu: sell at the 09:00 London-time minute open | entry + 0.5 x ATR14 of the last closed UTC day (≥ 3 x cost) | buy back at the 13:00 London-time minute open, or stop | 0.33 | hunt/euro_hours.py `build(k=0.5, days=(1,2,3))` |
| 2 | XAU_S1_reversion_H1M30M20 | XAUUSD H1+M30+M20, long only | S1 "Impulse4" pattern, market entry at breakout close (engine.s1_patterns; TimelessCity MODE_REVERSION + ENTRY_MARKET_BRK, layers H1/M30/M20) | pattern stop | flat 1R target | 0.63 | engine.py `s1_patterns`, config.py P4 |
| 3 | JPY_VolBreakout_D1_k0.7 (filtered) | USDJPY D1 | buy stop at open + 0.7 x previous day range, sell stop at open − 0.7 x range; first touch; keep only if the entry is also beyond the previous UTC day's high (long) / low (short) | back at the day's open (0.7 x range) | that day's close | 0.21 | gold_lab.py `vol_breakout(G,"D1",0.7)` + northstar/regen_filtered.py (exact) |
| 4 | XAU_Donchian20_H4_turtle | XAUUSD H4, both | close above the highest high / below the lowest low of the previous 20 bars | 2.0 x ATR14 | turtle exit: close below the 10-bar low (long) / above the 10-bar high (short) | 0.21 | gold_lab.py `donchian(G,"H4",20,2.0,0,turtle_exit=True)` |
| 5 | JPY_S2_Donchian20_H4_long (filtered) | USDJPY H4, long | close above the 20-bar high; keep only if the entry is above the previous Mon–Fri UTC week's high | 2.0 x ATR14 | chandelier trail: once +1.5R, stop trails 1.5R below the best price | 0.37 | TR_USDJPY_H4_atr2_long + regen_filtered.py (exact) |
| 6 | XAU_EMA20-50_H4 (filtered) | XAUUSD H4, both | EMA20 crosses EMA50; keep only if the entry is inside the previous UTC day's range | 3.0 x ATR14 | the next opposite cross | 0.34 | gold_lab.py `ma_cross(G,"H4",20,50)`; filter reproduces 113/118 stored trades (gap) |
| 7 | GBP_WeeklySweep_FollowThrough | GBPUSD H1 | after the previous week's high (low) is swept and reclaimed within 6 bars, price reaches the opposite weekly level and an H1 bar closes beyond it → trade the continuation (window Mon 00:00–Fri 16:00) | middle of the previous week's range (≥ max(0.15 x day ATR, 3 x cost)) | 2R target or Friday 20:00 | 0.93 | liquidity.py `build(level="weekly", tfm=60, K=6, kind="follow", target=2)` |
| 8 | JPY_Donchian55_D1_trail | USDJPY D1, both | close beyond the 55-day high/low | 2.0 x ATR14 | chandelier trail 1.5R | 0.42 | gold_lab.py `donchian(G,"D1",55,2.0,1.5)` |
| 9 | JPY_RSI2_D1_lo5 | USDJPY D1, both | RSI(2) < 5 and close > SMA200 → long; RSI(2) > 95 and close < SMA200 → short | 2.0 x ATR14 | close crosses SMA5 (max 10 bars) | 1.00 | gold_lab.py `rsi2(G,"D1",5,95)` |
| 10 | GBPJPY_Donchian20_H4_trail | GBPJPY H4, both | close beyond the 20-bar high/low | 2.0 x ATR14 | chandelier trail 1.5R | 0.25 | hunt/crosses.py (research used a synthetic GBPJPY from GBPUSD x USDJPY) |
| 11 | EURGBP_Bollinger_D1_k1.5 | EURGBP D1, both | close below SMA20 − 1.5 sd → long; above SMA20 + 1.5 sd → short | 2.0 x ATR14 | close back at SMA20 (max 20 bars) | 0.56 | gold_lab.py `bollinger(G,"D1",20,1.5)`, hunt/crosses.py |

Research costs (all-in round trip): XAUUSD $0.45, EURUSD 1.5 pips, GBPUSD 1.8 pips, USDJPY 1.2 pips,
GBPJPY 3.0 pips, EURGBP 1.5 pips. Financing per 22:00 UTC rollover held (x3 Wednesday): XAUUSD $0.20/oz,
EUR/GBP 0.6 pip, JPY pairs 0.8 pip (crosses use their quote currency's rate).

Trade lists for parity checks: `results/northstar/parity/<leg>.csv` (2011–2025).

## 2. Risk governor (demo policy FF+RED; PREREGISTRATION.md §6 + amendments 2–3)

| Parameter | Value |
|---|---|
| Sizing | fixed fractional: 1.0% of current equity x leg weight (0.21%–1.0% per trade); never raised after gains |
| Caps (initial-stop risk) | per trade 2%; total open 10%; per instrument 4%; same instrument + direction 3%; net USD direction 6% (gold/EUR/GBP long and USDJPY short = USD-short) |
| Cap breach | the new order is skipped (not resized) |
| RED (circuit breaker) | drawdown ≥ 20% from peak (after acknowledgement re-arms only on a further 5% loss); day loss ≥ 6%; feed stale > 5 min in trading hours; ≥ 3 order rejections in a day; spread > 4x its rolling median at decision; margin level < 300% |
| RED action | no new entries; open positions keep their server stops; a position without a confirmed stop is closed at market after 60 s |
| RED exit | operator acknowledgement (GlobalVariable `NS_ACK` = 1) with live checks passing; resumes at full risk (FF+RED) |
| AMBER | computed and logged only (shadow): drawdown ≥ 10%, day loss ≥ 3%, 5-day loss ≥ 6%, open risk > 8%; set `InpAmberHalvesRisk=true` for the RAG policy (x0.5) |
| Fail-safe | strategy EAs get 0 risk if the governor heartbeat is older than 120 s |
| No entries | 20:30–23:00 UTC (rollover spread) |

## 3. Monitoring (weekly.py rules R1–R5)
R1 state; R2 a strategy is "under review" only with ≥ 30 live trades and t < −2.33 against its backtest
mean, or a losing streak above its backtest 99th percentile (never "broken"); R3 median slippage of the
last 20 fills > 2x assumed (assumed = 25% of the all-in cost ≈ 0.0065R) → AMBER; R4 weekly return outside
the 5–95% band is reported, no action; R5 breaches listed weekly.

Expected ranges at 1% base risk (2011–2022, 200 reshuffled paths): weekly return 5% / median / 95% =
−1.26% / +0.07% / +1.89%; 7.8 trades per week (5–11 in active weeks); win rate 47%; mean +0.076R per
trade; portfolio losing streak 95th percentile 5, longest 12.

## 4. Files
- `mt5/NorthStarRisk.mqh`, `mt5/NorthStarGovernor.mq5` — **source only, not compiled.**
- `mt5/TimelessCity.mq5` (v2.42) implements S1 and Donchian logic used by legs 2, 4 and 5 in earlier
  form; it has **not** been parity-tested against the book's trade lists, and its own header warns that
  its original configuration is negative. The other 8 legs have no MQL5 implementation yet.
