# LESSONS — generated from ledger.jsonl (do not edit; run `python3 research/truth/memory.py --render`)

67 ideas tested, about 303,382 configurations; 6 survivors. Principles: `PRINCIPLES.md` · queue: `OPEN_QUESTIONS.md` · sessions: `JOURNAL.md`.

## Survivors
| Idea | Family | Verdict | Key numbers | Evidence |
|---|---|---|---|---|
| Futures trend + carry (pysystemtrade data, Carver defaults) | trend, carry, futures, diversified | Survivor (futures only) | Sharpe 0.96 since 2000, 0.50 2011-24; as CFDs 0.06 | research/multiasset/PROJECT.md |
| TimelessCity v2.42 re-score (S1 gold/EUR, S2 USDJPY, S3 gold) | trend, reversion, portfolio | Survivor: deployed EA (demo gate pending) | Sharpe 0.67 with swaps, 1.04 low-cost swap-free; S1 EUR -0.06R 2023-25 (watch) | research/northstar/TIMELESSCITY_RESCORE.md |
| eurusd_close_beyond_reversal_v1 | reversal, daily, stop-entry, eurusd, bailout-exit | Tier B: forward-test candidate |  | research/results/truth/eurusd_close_beyond_reversal_v1/REPORT.md |
| Champion (11-leg book) untouched test, Jan-Oct 2026 + professional tearsheet | book, out-of-sample, forward-test, portfolio, trend, reversion | Survivor, weakened: 2026 below backtest, within a 30-50% live haircut | Legs regenerated with original code on Exness Zero 2026 ticks (entry parity 100% on 10 legs, 96% on XAU EMA). Jan-Oct 2026 at 1% risk: -1.36% with swaps (+0.78% swap-free), max DD 5.3%, 333 trades, +0.022R/trade vs +0.078R backtest (z -0.81, p 0.21; weighted p 0.07). At or below 4.1% of backtest 10-month stretches (median +8.2%); 13% if live edge 30% weaker, 23% if 50%. Backtest 2011-25 (corrected): Sharpe 1.36, 10.7%/yr, max DD 9.7%, 14/15 years; swap-free 1.74; stress (costs x1.5, swaps x2) 0.76. 2026 losses came from high-weight, rarely trading legs (S1 gold, JPY RSI2, JPY Donchian55) and GBPJPY; VBO and gold Donchian20 won. | research/champion/{regen_2026,tearsheet,dashboard_data}.py; research/results/champion/; dashboard https://claude.ai/artifact/BohhgY8e3XiUhstZdVSTVg |
| Hunt 2 / 11-leg book | portfolio, trend, reversion, seasonal | Survivor: Tier B forward-test candidate | Sharpe 1.00 after costs+swaps (1.64 low-cost swap-free); 2023-25 +0.044R/trade, PF 1.12. CORRECTED 2026-10-31 (Sunday-exit bug, P20): Sharpe 1.24 after research costs+swaps 2011-24Q1 (1.03 after 2016); Exness Zero 1.36 with swaps, 1.74 swap-free 2011-25; untouched Jan-Oct 2026 -1.36% | research/hunt/HUNT2_REPORT.md; research/northstar/NORTHSTAR_REPORT.md |
| tokyo_fix_gotobi_v1 | calendar, flow, fix, intraday, usdjpy, seasonal | Tier B: forward-test candidate |  | research/results/truth/tokyo_fix_gotobi_v1/REPORT.md |

## Family priors (how earlier ideas with this tag ended)
| Tag | Ideas | Survived | Configurations |
|---|---|---|---|
| intraday | 17 | 1 | 182,551 |
| awesome-list | 13 | 0 | 147 |
| index | 13 | 0 | 98 |
| owner-idea | 13 | 0 | 1,666 |
| breadth | 12 | 0 | 697 |
| calendar | 12 | 1 | 139 |
| flow | 12 | 1 | 42 |
| trend | 12 | 4 | 102,718 |
| breakout | 9 | 0 | 119,432 |
| engulfing | 9 | 0 | 3,836 |
| reversal | 9 | 1 | 105,852 |
| seasonal | 9 | 2 | 23 |
| daily | 8 | 1 | 172 |
| structure | 8 | 0 | 1,634 |
| repo-funnel | 7 | 0 | 222 |
| retest | 7 | 0 | 10,308 |
| session | 7 | 0 | 183,863 |
| fix | 6 | 1 | 36 |
| ema | 5 | 0 | 996 |
| futures | 5 | 1 | 138 |
| gold | 5 | 0 | 363 |
| limit-entry | 5 | 0 | 996 |
| mean-reversion | 5 | 0 | 47 |
| smc | 5 | 0 | 14,988 |
| eurusd | 4 | 1 | 155 |
| monthly | 4 | 0 | 20 |
| oil | 4 | 0 | 7 |
| risk | 4 | 0 | 70 |
| sizing | 4 | 0 | 70 |
| third-party-ea | 4 | 0 | 304 |
| usdjpy | 4 | 1 | 28 |
| book | 3 | 1 | 9 |
| carry | 3 | 1 | 18 |
| cross-asset | 3 | 0 | 4 |
| filter-mining | 3 | 0 | 244 |
| gbpusd | 3 | 0 | 152 |
| grid | 3 | 0 | 196 |
| liquidity | 3 | 0 | 1,376 |
| macro | 3 | 0 | 4 |
| momentum | 3 | 0 | 53 |
| options-expiry | 3 | 0 | 4 |
| oscillator | 3 | 0 | 288 |
| pattern | 3 | 0 | 4,932 |
| portfolio | 3 | 3 | 16 |
| reversion | 3 | 3 | 16 |
| seesare | 3 | 0 | 26 |
| sweep | 3 | 0 | 1,376 |
| turn-of-month | 3 | 0 | 4 |
| averaging | 2 | 0 | 160 |
| bailout-exit | 2 | 1 | 6 |
| costs | 2 | 0 | 8 |
| cross-sectional | 2 | 0 | 17 |
| dip-buying | 2 | 0 | 8 |
| energy | 2 | 0 | 128 |
| fvg | 2 | 0 | 9,312 |
| rsi2 | 2 | 0 | 8 |
| short-vol | 2 | 0 | 17 |
| sofus | 2 | 0 | 139 |
| stop-entry | 2 | 1 | 6 |
| swing | 2 | 0 | 139 |
| time-filter | 2 | 0 | 144 |
| trailing | 2 | 0 | 156 |
| trustdan | 2 | 0 | 151 |
| winner-anatomy | 2 | 0 | 135 |
| all-time-high | 1 | 0 | 2 |
| breakeven | 1 | 0 | 102,260 |
| cent-account | 1 | 0 | 6 |
| commodities | 1 | 0 | 16 |
| control | 1 | 0 | 48 |
| diversified | 1 | 1 | 1 |
| donchian | 1 | 0 | 48 |
| drawdown-cap | 1 | 0 | 4 |
| exness | 1 | 0 | 5 |
| factor | 1 | 0 | 1 |
| forward-test | 1 | 1 | 1 |
| fx | 1 | 0 | 16 |
| hindsight-market-choice | 1 | 0 | 64 |
| ict | 1 | 0 | 780 |
| look-ahead | 1 | 0 | 16 |
| metals | 1 | 0 | 64 |
| methods | 1 | 0 | 16 |
| out-of-sample | 1 | 1 | 1 |
| pairs | 1 | 0 | 1 |
| payday | 1 | 0 | 1 |
| payoff | 1 | 0 | 16 |
| payouts | 1 | 0 | 3 |
| probability | 1 | 0 | 3 |
| prop | 1 | 0 | 20 |
| pullback | 1 | 0 | 36 |
| pyramiding | 1 | 0 | 48 |
| quasimodo | 1 | 0 | 3,456 |
| random | 1 | 0 | 48 |
| ranking | 1 | 0 | 61,787 |
| scalping | 1 | 0 | 144 |
| scanner | 1 | 0 | 61,787 |
| stat-arb | 1 | 0 | 1 |
| supply-demand | 1 | 0 | 1,440 |
| support-resistance | 1 | 0 | 2,202 |
| swap-free | 1 | 0 | 5 |
| timeframe-scan | 1 | 0 | 396 |
| volatility | 1 | 0 | 102,260 |

## Every idea tested (newest first)
| Date | Idea | Family | Configs | Verdict | Key numbers |
|---|---|---|---|---|---|
| 2026-11-01 | 5-min hunter step 1: Leg 34 winner anatomy, 11 markets (learn gold 2011-19) | engulfing, structure, intraday, filter-mining, winner-anatomy, owner-idea, gold, breadth | 133 | Rejected: winners' attributes do not select winners | ~194,000 filled Leg 34 setups on M5, 11 markets, each simulated alone. Before costs about zero on every market (ladder -0.07 to +0.04R; silver/oil/indices costs are lab estimates). Gold 2011-19: 43% reach +1R, 13% +5R, 6% +10R, 1.5% +20R. Top 10% runners look like all trades (lifts 0.86-1.15); top 1% lean to quiet volatility, a quiet day, a strong 4h push, small structure. Best 2-condition rule (cost_R low & EMA slope mid, 133 conditions) failed its own halves (-0.04 / +0.04R), then -0.08R gold 2020-22, -0.06R 2023-25, -0.10R pooled other markets (9 of 10 negative), -0.02R Jan-Sep 2026. |
| 2026-11-01 | 5-min hunter step 2: top-1% runner-profile score (declared before out-of-sample) | intraday, filter-mining, winner-anatomy, owner-idea, gold, breadth | 2 | Rejected: worse than taking every setup | Score = quiet volatility, quiet day, strong 4h push, small structure, deep Leg 2 (cut points gold 2011-19); trade score>=3. Ladder exit: gold 2011-19 -0.20R (all setups -0.15), 2020-22 -0.13, 2023-25 -0.12, other 10 markets -0.35 (all -0.31), Jan-Sep 2026 -0.14R. The profile concentrates runners and losers alike. |
| 2026-11-01 | Hunter step 3: Leg 34 pocket scan, 11 markets x 6 timeframes x 3 sessions x 2 exits | engulfing, structure, intraday, session, timeframe-scan, owner-idea, breadth | 396 | Rejected: no pocket survives | 396 cells (M5, M10, M15, M30, M45, H1; Asia/London/New York; t3 and ladder), selection on 2011-22 only. 1 cell passed discovery (GBPUSD H1 London t3, t 2.13; ~9 expected by luck) and lost in 2020-22 (-0.37R); 0 confirmed; no cell positive in 2011-19, 2020-22 and 2023-25. Before costs only 33% of cells positive in 2011-19 (medians -0.01 to -0.05R by timeframe); persistence before costs 34% vs 32% = luck. Higher timeframes cut the cost share (median after costs -0.27R M5 -> -0.20R H1) but the raw edge does not improve. Sessions alike (-0.23R). Past hint (sop_4leg_v1 EUR/GBP M30 16-20 UTC) negative on all 9 other markets (-0.04 to -0.51R). |
| 2026-11-01 | tokyo_fix_gotobi_v1 | calendar, flow, fix, intraday, usdjpy, seasonal | 3 | Tier B: forward-test candidate | dev_E +0.041, val_E +0.064, final_E +0.052, final_n +214.000, final_PF +1.283, dsr +0.969, share_dev_positive +1.000 |
| 2026-11-01 | Tokyo fix (Gotobi) study: USDJPY moves into/after the 00:55 UTC fix, gotobi vs other days | calendar, flow, fix, intraday, usdjpy, seasonal | 3 | Study: informative (supports tokyo_fix_gotobi_v1) | Buy 23:00 -> 00:55 UTC on gotobi days: dollar +2.7 pips (2011-19, t 4.0, 646 days), +3.9 (2020-22), +3.6 (2023-25), +5.3 (Jan-Sep 2026, 54 days) vs other days +0.3/+1.3/+1.1/-0.6; after 1.35-pip cost +1.4/+2.6/+2.3/+3.9 pips. Oct 2026 -8.5 (6 days). After-fix short 00:55->02:00: -1.5/-3.9/-4.8 pips on gotobi days, flat in 2026. Exness Zero spread at 23:00 UTC ~0 in 6 of 8 sampled months, 0.65 pip (Mar 2021) and 4.8 pips (Jan 2024): about +0.7 pip average, winter months riskier. |
| 2026-11-01 | tom_indices_v1 | calendar, flow, seasonal, index, turn-of-month, awesome-list | — | Rejected: look-ahead (signals change when future bars are removed) |  |
| 2026-11-01 | opex_week_indices_v1 | calendar, flow, seasonal, index, options-expiry, awesome-list | — | Rejected: look-ahead (signals change when future bars are removed) |  |
| 2026-11-01 | oil_equity_v1 | macro, cross-asset, oil, index, monthly, awesome-list | — | Rejected: look-ahead (signals change when future bars are removed) |  |
| 2026-11-01 | tom_indices_v2 | calendar, flow, seasonal, index, turn-of-month, awesome-list | 1 | Rejected: no configuration passed the development gate | share_dev_positive +0.000 |
| 2026-11-01 | opex_week_indices_v2 | calendar, flow, seasonal, index, options-expiry, awesome-list | 1 | Rejected: no configuration passed the development gate | share_dev_positive +0.000 |
| 2026-11-01 | oil_equity_v2 | macro, cross-asset, oil, index, monthly, awesome-list | 2 | Rejected: no configuration passed the development gate | share_dev_positive +0.000 |
| 2026-11-01 | Calendar study: turn of month, option-expiry week, oil->equity in 5 indexes (drift-controlled) | calendar, flow, seasonal, index, turn-of-month, options-expiry, oil, awesome-list | 3 | Rejected: no effect beyond drift (TOM, OPEX); oil weak and inconsistent | Window-day minus other-day daily return, 2011-19 / 2020-22 / 2023-25: TOM -9.6 to +0.2 bp (4/5 indexes negative), then positive, then negative; OPEX week flips sign (US500 +2.5 bp, -28 bp t -2.1, -1.9 bp). Oil: next month after oil fell minus rose +96 bp (5/5 positive), -13 bp (1/5), +142 bp (4/5), t <= 1.7 everywhere. |
| 2026-11-01 | Oil predicts equity returns on real futures (pysystemtrade, 6 index futures, 1990-2024) | macro, cross-asset, oil, index, monthly, futures, awesome-list | 2 | Rejected: the effect faded after publication | Basket of SP500, NASDAQ, DAX, FTSE100 (+NIKKEI, EUROSTX from 2011): next month after oil fell minus rose +1.15%/month in 2000-2010 (t 1.15, fresh years), -0.03% in 2011-2024 (t -0.05); long/short Sharpe 0.35 then -0.09; long/cash Sharpe 0.49 vs buy-and-hold 0.88 in 2011-2024. Paper published 2008. |
| 2026-11-01 | ath_trend_v1 | trend, breakout, all-time-high, daily, breadth, repo-funnel, awesome-list | 2 | Rejected: no configuration passed the development gate | 10-year closing high + 1xATR10 trail. With swaps: both sides +0.006R/trade 2011-19 (2011-15 -0.03R), 7 of 11 markets; fails. Swap-free at half costs: +0.25R (2011-15 +0.20, 2016-19 +0.34), 2020-22 +0.12R, 10 of 11 markets positive -> the trend family hinges on financing (Q1, Q17, Q18). |
| 2026-11-01 | payday_indices_v1 | calendar, flow, seasonal, index, payday, repo-funnel, awesome-list | 1 | Rejected | Payday (day after the 15th) on 5 index CFDs: 2011-19 +0.016R/trade (R = 5% of price, t 2.1, swap-free +0.030 t 3.9), 2020-22 -0.010R, stress negative, 2023-25 151 trades -0.006R (t -0.45): faded (P11). |
| 2026-11-01 | Repo funnel futures v2: 16 awesome-list cross-asset strategies (pysystemtrade futures, one-day execution lag) | momentum, carry, cross-sectional, futures, monthly, commodities, fx, index, repo-funnel, awesome-list | 16 | Rejected except time-series momentum (confirms the futures trend family) and four weak futures-only passes | Pre-registered gate (Sharpe > 0 in 2000-09, 2010-19, 2020-22) passed by: time-series momentum (1.12/0.61/0.98, t 3.9, deflated Sharpe 0.88, 2023-24Q1 +0.10%/month), commodity skewness (0.32/0.67/0.88, t 2.2, DSR 0.28, +0.46%/month), FX carry (0.70/0.02/1.07, t 1.8, DSR 0.17, +1.37%/month), asset-class momentum vs equal weight (0.69/0.28/0.01, t 2.3, DSR 0.33) and paired switching vs 50/50 (t 0.4, DSR 0.01). Failed: commodity momentum and term structure (+17-18%/yr in 2000-09, negative after), currency momentum, dollar carry, short-term reversal (simplified), country pairs, country BAB (+16%/+30%/yr then -24%/yr 2020-22), WTI-Brent, January barometer, asset-class trend; return asymmetry passed the gate but lost in 2023-24. Futures only (needs ~28 commodities / FX futures). |
| 2026-11-01 | Repo funnel futures v1 (same-day execution) | futures, methods, look-ahead, repo-funnel, awesome-list | 16 | Invalid: look-ahead through markets closing at different hours (and stale holiday prices) | Country-index pairs looked like Sharpe +1.4 in every period and WTI-Brent +2 to +3; placing the trade one day after the signal turns them into -0.35/-1.37 and -0.6/0, while monthly strategies barely change. Superseded by v2 (P23). v1 logged the 2023-24 look for F1, F4, F5, F10, F11, F13. |
| 2026-11-01 | Repo funnel: 132 strategies from trustdan, sofus-nl and awesome-systematic-trading | repo-funnel, trustdan, sofus, awesome-list, trend, swing, calendar, futures | 103 | Rejected for CFDs (0 of 68 testable strategies survive); futures: time-series momentum only (already held as a futures-only family) | Inventory: 84 testable (68 on our 11 CFDs, 16 on futures), 3 tested earlier, 45 need data we lack (stock cross-sections, company accounts, real volume, options, macro series). CFD configurations: 48 trustdan + 36 sofus + 2 ATH trend + 1 payday = 87; futures 16. Lesson: public repo rankings are backtests on other assets without costs, swaps or holdout; on our markets the order changes and signs flip. Trend lives or dies on financing. |
| 2026-11-01 | funnel_trustdan_v1 | trend, breakout, donchian, pyramiding, daily, breadth, repo-funnel, trustdan | 48 | Rejected: no configuration passed the development gate | All 48 trustdan Turtle/Seykota variants negative in 2011-19 pooled over 11 CFDs after costs and swaps (least bad -0.04R: alt20, whose source bug closes each trade the next day; then alt41 -0.21R; core -0.38R; their champion Alt10 -0.62R); <= 6 of 11 markets positive. Swap-free at half costs the core makes +0.20R (val -0.05R) and no rule has both eras positive; breadth max 8 of 11. Their stock-backtest ranking does not carry over. |
| 2026-11-01 | funnel_sofus_v1 | swing, breakout, pullback, momentum, pattern, mean-reversion, daily, breadth, repo-funnel, sofus | 36 | Rejected: no configuration passed the development gate | 18 price-only translations x long/both: all negative 2011-19 except s10 triple RSI divergence both (+0.003R on 30 trades); least bad of the rest EMA 9/21 cross and RSI(2) reversion, about -0.02R. Patterns (VCP, cup and handle, bull flag, Qullamaggie, divergence) rare and negative; RSI pullback (s04) and strict cup and handle never trigger on daily CFD data. |
| 2026-11-01 | seesare_ladder_envelope_v1 | risk, sizing, seesare, drawdown-cap, owner-idea | 4 | Rejected as a guarantee: ladder rules alone allow 29.55% (time exits at -0.6R, manual) and 14.96% (stop at 3.5:1 then two 1:1 wins); a pre-trade check (drawdown + all-in risk <= $36) holds 3.53% / 3.60%. With losing time exits counted NEGATIVE: 0.19%. | dd_mandate_no_guard_pct +29.550, dd_mandate_guard_pct +3.530, real_events_mandate_guard +43.000, dd_loss_negative_guard_pct +0.190, dd_low_ratio_no_guard_pct +14.960, dd_low_ratio_guard_pct +3.600 |
| 2026-11-01 | wmr_fix_reversion_v1 | calendar, flow, fix, intraday, eurusd, gbpusd, reversal, owner-idea | 4 | Rejected: no configuration passed the development gate | share_dev_positive +0.000 |
| 2026-11-01 | wmr_fix_postfade_v1 | calendar, flow, fix, intraday, eurusd, gbpusd, reversal | 4 | Rejected | dev_E +0.046, val_E +0.091, final_E +0.018, final_n +72.000, final_PF +1.151, dsr +0.701, share_dev_positive +0.500 |
| 2026-11-01 | Tokyo fix payoff shape and declared-bracket study | calendar, flow, fix, usdjpy, payoff, seesare, owner-idea | 16 | Rejected: payoff ratio about 1:1 (avg win 11.3/14.8/18.4 pips vs avg loss 11.0/11.4/20.1 in 2011-19/2020-22/2023-25); a 7:1 target is reached on 0.1-3.3% of mornings for stops of 5-20 pips. Declaring a high ratio only raises SEESARE size; it does not add convexity. Descriptive (all years at once): not a strategy selection. |  |
| 2026-11-01 | SEESARE cycle-block study on a cent account (Tokyo fix through the real ledger rules) | seesare, sizing, risk, cent-account, usdjpy, flow, fix, owner-idea | 6 | Rejected as stated: the box holds (max drawdown 0.005-0.016%) only because real trading almost stops. With losing time exits NEGATIVE (hardcoded) and no target, the ladder can only descend: L15 from event 13, 98.8% of 1,071 events there, 6 REAL trades in 15 years (-$0.04), 0 cycles closed. Target at 1.04: same 6 REAL. Time exits MANUAL: 25 REAL, 2 cycles (+0.003%, +0.116%). The cent account makes the Tokyo fix REAL only at L0-L3 (ratio 1.04), L0-L9 at 3.5. +2% per cycle needs +1.46R per event at L0 (mult 1.0); the Tokyo fix earns about +0.05R. | events +1071.000, real_A +6.000, real_C +25.000, cycles_A +0.000, cycles_C +2.000, share_L15_A +0.988, share_L15_B +0.887, share_L15_C +0.950, first_L15_A +13.000, cycle_mean_pct_C +0.060, max_dd_pct_C +0.015, spread_pips +1.900, stress_spread_pips +2.850, lowest_real_level_ratio_1_04 +3.000, lowest_real_level_ratio_3_5 +9.000 |
| 2026-10-31 | TimelessCity v2.42 re-score (S1 gold/EUR, S2 USDJPY, S3 gold) | trend, reversion, portfolio | 4 | Survivor: deployed EA (demo gate pending) | Sharpe 0.67 with swaps, 1.04 low-cost swap-free; S1 EUR -0.06R 2023-25 (watch) |
| 2026-10-31 | Liquidity grabs at swing points (SFP, equal highs, sweep+MSS, NY-sweeps-London) | liquidity, sweep, smc, ict, reversal | 780 | Rejected | best (sweep+MSS H1) 2023-25 -0.185R; ~1,400 liquidity variants tested in total |
| 2026-10-31 | donchian_trend_v1 | trend, breakout | 96 | Rejected: no configuration passed the development gate | 50-bar time stop; gold/JPY positive, EUR/GBP negative |
| 2026-10-31 | donchian_trend_v2_room_to_run | trend, breakout | 64 | Rejected: no configuration passed the development gate | 4-market rule fails: gold +0.14-0.21R, JPY +0.15-0.28R, EUR/GBP negative |
| 2026-10-31 | coin_flip_control_v1 | control, random | 48 | Rejected | control: 1 random setting passed the first gate, caught by walk-forward/neighbours/DSR |
| 2026-10-31 | FTMO-style prop challenge replay (TimelessCity, 11-leg book) | prop, risk, sizing | 20 | Study: informative (no new edge) | book at 1-1.5% risk/trade: phase 1 passed in 52-72% of 12-month windows (median ~26-34 weeks), both phases 33-54%; funded payouts ~6-8% of account/yr; TimelessCity lower (17-33% both phases) |
| 2026-10-31 | Gold Hunter V9 (third-party grid EA, owner's .set) | grid, averaging, short-vol, third-party-ea | 16 | Rejected | hedged constant-lot grid, no stop: realised P&L positive but net -$155k to -$196k per 0.01 lot 2011-25 (pip $0.01); all 12 bounded (capped + stop) versions lose; looks profitable at 3 months in 95-100% of starts, then 19-74% of accounts blown within 3 years |
| 2026-10-31 | eurusd_close_beyond_reversal_v1 | reversal, daily, stop-entry, eurusd, bailout-exit | 3 | Tier B: forward-test candidate | dev_E +0.040, val_E +0.030, final_E +0.012, final_n +112.000, final_PF +1.137, dsr +0.907, share_dev_positive +1.000 |
| 2026-10-31 | close_beyond_reversal_4mkt_v1 | reversal, daily, stop-entry, bailout-exit, breadth | 3 | Rejected: no configuration passed the development gate | share_dev_positive +1.000 |
| 2026-10-31 | Dark Mimas (Marco Solito, free MQL5 EA; owner's classic and grid .set files) | oscillator, scalping, intraday, grid, averaging, third-party-ea, eurusd, gbpusd | 144 | Rejected | classic (stop-and-reverse on oscillator turns): loses before costs in 18/18 (-0.17 to -0.65 pips/trade), -1.2 to -1.9 pips at Exness Zero costs; grid set: 96-98% of baskets win but 0/36 tradable configs profitable at Exness Zero costs (-$1.6k to -$12.8k per 0.01 lot 2011-25). Vendor's live signals: equity DD 51-53% vs balance DD 8-25% (losses held open). |
| 2026-10-31 | osc_turn_sessions_v1 | oscillator, intraday, session, time-filter, third-party-ea | 108 | Rejected: no configuration passed the development gate | share_dev_positive +0.019 |
| 2026-10-31 | Dark Mimas timing study (winner hours; learn 2011-19, check 2020-25) | oscillator, intraday, session, time-filter, third-party-ea, grid | 36 | Study: informative (no new edge) | Best 6 hours picked on 2011-19: +1.11 pips/trade gross -> -0.13 in 2020-25; 0/18 positive after Exness costs. Grid best 8 hours +2.76 -> +0.18 pips/basket (below one order's cost). Big winners = trend days (1.5-2.3x normal range) starting at London/NY opens, known only afterwards; grid stop-outs = trend days (1.3-1.5x range). |
| 2026-10-31 | breadth_trend_v1 | trend, breakout, breadth, index, energy, metals | 64 | Rejected: no configuration passed the development gate | share_dev_positive +0.000 |
| 2026-10-31 | index_rsi2_v1 | mean-reversion, dip-buying, rsi2, index, daily, breadth | 4 | Rejected | dev_E +0.040, val_E +0.026, final_E +0.094, final_n +83.000, final_PF +1.668, dsr +0.555, share_dev_positive +1.000 |
| 2026-10-31 | wti_trend_v1 | trend, breakout, energy, hindsight-market-choice | 64 | Rejected | dev_E +0.160, val_E -0.168, final_E -0.183, final_n +99.000, final_PF +0.774, dsr +0.005, share_dev_positive +0.797 |
| 2026-10-31 | index_rsi2_breadth_v1 | mean-reversion, dip-buying, rsi2, index, daily, breadth | 4 | Rejected: no configuration passed the development gate | share_dev_positive +0.000 |
| 2026-10-31 | sop_4leg_v1 | engulfing, structure, retest, limit-entry, intraday, ema, owner-idea | 756 | Rejected | dev_E +0.084, val_E -0.240, final_E -0.109, final_n +97.000, final_PF +0.806, dsr +0.001, share_dev_positive +0.114 |
| 2026-10-31 | sop_4leg_gold_v1 | engulfing, structure, retest, limit-entry, ema, owner-idea, gold, daily | 72 | Rejected: no configuration passed the development gate | share_dev_positive +0.347 |
| 2026-10-31 | Owner's 4-leg engulfing SOP: case-study parity + Feb-Oct 2026 holdout | engulfing, structure, retest, limit-entry, intraday, ema, owner-idea | 12 | Rejected | Detector reproduces 6 of the owner's 12 cases exactly; on all setups 2011-25 the owner's setup loses 0.12-0.20R/trade (before costs -0.02 to -0.05R); Feb-Oct 2026 (untouched): M5 -0.09R (376 trades), M15 -0.35R, M30 +0.02R (82); breakeven worse in 2026. Case studies select winners: 4 of 5 reproduced cases won vs 21-34% of all setups. |
| 2026-10-31 | SOP winning-conditions study (learn 2011-19, check later) | engulfing, structure, owner-idea, filter-mining, intraday | 109 | Rejected: no winning condition exists | 23,000 filled setups (EUR/GBP M5-M30) with 19 features known at entry: 0 of 56 single conditions positive even in 2011-19; best 2-condition rule (stop >12 pips, costs <12% of R) -0.045R in 2011-19 (both halves negative), -0.08R 2020-22, +0.12R 2023-25 (257 trades), -0.32R Feb-Oct 2026. All setups: -0.15 to -0.18R in every period, 28% win. |
| 2026-10-31 | Exness Zero costs (measured spreads) and book re-score | costs, exness, swap-free, book | 5 | Study: informative | Zero spreads measured from Exness's own tick archive: ~0 on XAU/EUR/GBP/JPY/US500 (cost = commission + slippage). Book Sharpe 1.00 -> 1.15 with swaps, 1.51 swap-free (2023-25: 0.75 / 1.06) at high-end commission ($3.50/side FX, $5.50 gold). Commission and swap-free status unconfirmed. CORRECTED 2026-10-31 (Sunday-exit bug, see journal): 1.36 with swaps, 1.74 swap-free (2023-25: 0.95 / 1.27); lab costs 1.20. |
| 2026-10-31 | Probability ladder: what raises the odds of a profitable fortnight/month/year (11-leg book) | probability, breadth, costs, payouts, book | 3 | Study: informative | CORRECTED 2026-10-31 (Sunday-exit bug): book positive fortnights 55% (lab costs) -> 57% (Exness Zero + swaps) -> 61% (swap-free); months 62/67/69%; years 87/93/100%. One leg alone: 27-28% of fortnights, 58-68% of years. Per trade +0.069/+0.078/+0.103R (sd 1.26R): 90% chance of being up needs ~544/428/253 trades (~7-16 months of the book). |
| 2026-10-31 | Champion (11-leg book) untouched test, Jan-Oct 2026 + professional tearsheet | book, out-of-sample, forward-test, portfolio, trend, reversion | 1 | Survivor, weakened: 2026 below backtest, within a 30-50% live haircut | Legs regenerated with original code on Exness Zero 2026 ticks (entry parity 100% on 10 legs, 96% on XAU EMA). Jan-Oct 2026 at 1% risk: -1.36% with swaps (+0.78% swap-free), max DD 5.3%, 333 trades, +0.022R/trade vs +0.078R backtest (z -0.81, p 0.21; weighted p 0.07). At or below 4.1% of backtest 10-month stretches (median +8.2%); 13% if live edge 30% weaker, 23% if 50%. Backtest 2011-25 (corrected): Sharpe 1.36, 10.7%/yr, max DD 9.7%, 14/15 years; swap-free 1.74; stress (costs x1.5, swaps x2) 0.76. 2026 losses came from high-weight, rarely trading legs (S1 gold, JPY RSI2, JPY Donchian55) and GBPJPY; VBO and gold Donchian20 won. |
| 2026-10-31 | leg34_gold_v1 | engulfing, structure, retest, limit-entry, intraday, ema, owner-idea, gold, trailing | 144 | Rejected: no configuration passed the development gate | share_dev_positive +0.000 |
| 2026-10-31 | Leg 34 gold M5: 2026 check, cost/excursion and EMA-slope diagnostics | engulfing, structure, retest, limit-entry, intraday, ema, owner-idea, gold, trailing | 12 | Rejected (confirms the lab) | Owner's settings (swing 3, any engulfing, all hours), 6 exits x 2 buffers: 2011-19 -0.14 to -0.17R, 2020-22 -0.08 to -0.12, 2023-25 -0.02 to -0.10, untouched Jan-Sep 2026 -0.06 to -0.20R (700-870 trades); Oct 2026 (owner's screenshot month) -0.18 to +0.11R (~100 trades). Before costs +0.00 to +0.02R; costs 10-17% of R (median stop $1-1.60). 48% of trades reach +1R, 23% +3R. EMA slope thirds -0.14/-0.16/-0.13R. Detector matched 2 of 3 dated owner trades (30 Oct 2026); entry 30% of the eaten candle. |
| 2026-10-30 | North Star supply/demand (RBR/DBD/DBR/RBD) | supply-demand, smc, pattern | 1440 | Rejected | no setting passes the gate; every side negative |
| 2026-10-30 | North Star FVG models A-D | smc, fvg, retest | 1440 | Rejected | 0% of settings positive in 2011-19 |
| 2026-10-30 | North Star Quasimodo (+FVG) | quasimodo, pattern, smc | 3456 | Rejected | best H1 +0.13R dev; neighbours negative; deflated Sharpe 0.011 |
| 2026-10-30 | Portfolio risk states GREEN/AMBER/RED | risk, sizing | 40 | Rejected | plain fixed fractional at lower risk dominates at equal tail risk |
| 2026-10-30 | Daily London best-setup scanner | intraday, scanner, ranking, session | 61787 | Rejected | raw edge +0.015R vs costs 0.076R; still negative at 30% of costs |
| 2026-10-30 | Futures trend + carry (pysystemtrade data, Carver defaults) | trend, carry, futures, diversified | 1 | Survivor (futures only) | Sharpe 0.96 since 2000, 0.50 2011-24; as CFDs 0.06 |
| 2026-10-30 | Cross-sectional momentum (12-1, within class) | momentum, cross-sectional, factor | 1 | Rejected | Sharpe 0.00 |
| 2026-10-30 | Pairs stat-arb (10 linked pairs) | stat-arb, pairs, mean-reversion | 1 | Rejected | Sharpe -0.20 |
| 2026-10-30 | RSI(2) / Bollinger mean reversion on 56 markets | mean-reversion, breadth | 2 | Rejected (equity-index RSI2 on watch) | Sharpe 0.01 / -1.2; equity indices +0.41 |
| 2026-10-30 | Short volatility (VIX carry) | short-vol, carry | 1 | Rejected | -97% drawdown |
| 2026-10-29 | FVG study | smc, fvg, retest | 7872 | Rejected | info is in the displacement, not the gap |
| 2026-10-29 | Daily liquidity sweeps (Asian, PDH/PDL, PWH/PWL) | liquidity, sweep, reversal, session | 436 | Rejected | zero-cost edge -0.02 to +0.06R; one survivor (GBP weekly follow-through, now a book leg) |
| 2026-10-29 | Daily structure round 2 (candle sweeps, Turtle Soup, NR4/NR7) | liquidity, sweep, reversal, breakout | 160 | Rejected | none positive in all eras |
| 2026-10-28 | Gold WAT session + Malaysian SnR | support-resistance, engulfing, reversal, session | 2202 | Rejected | no robust edge |
| 2026-10-28 | Four strategies (trend continuation, failed breakout, vol contraction/expansion) | trend, reversal, volatility, breakeven | 102260 | Rejected (as a set) | with swaps 2023-25 +0.005R/trade; failed-breakout reversal fails everywhere; breakeven is a backtest mirage |
| 2026-10-28 | Hunt 2 / 11-leg book | portfolio, trend, reversion, seasonal | 11 | Survivor: Tier B forward-test candidate | Sharpe 1.00 after costs+swaps (1.64 low-cost swap-free); 2023-25 +0.044R/trade, PF 1.12. CORRECTED 2026-10-31 (Sunday-exit bug, P20): Sharpe 1.24 after research costs+swaps 2011-24Q1 (1.03 after 2016); Exness Zero 1.36 with swaps, 1.74 swap-free 2011-25; untouched Jan-Oct 2026 -1.36% |
| 2026-10-27 | ORB 50 study | breakout, intraday, session | 118898 | Rejected | all 4 finalists negative 2023-25 (-0.12 to -0.16R) |
