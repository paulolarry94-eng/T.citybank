# LESSONS — generated from ledger.jsonl (do not edit; run `python3 research/truth/memory.py --render`)

50 ideas tested, about 303,117 configurations; 6 survivors. Principles: `PRINCIPLES.md` · queue: `OPEN_QUESTIONS.md` · sessions: `JOURNAL.md`.

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
| intraday | 15 | 1 | 182,543 |
| breadth | 9 | 0 | 611 |
| engulfing | 9 | 0 | 3,836 |
| owner-idea | 9 | 0 | 1,636 |
| trend | 9 | 4 | 102,565 |
| structure | 8 | 0 | 1,634 |
| retest | 7 | 0 | 10,308 |
| reversal | 7 | 1 | 105,844 |
| session | 7 | 0 | 183,863 |
| breakout | 6 | 0 | 119,346 |
| index | 6 | 0 | 72 |
| daily | 5 | 1 | 86 |
| ema | 5 | 0 | 996 |
| gold | 5 | 0 | 363 |
| limit-entry | 5 | 0 | 996 |
| seasonal | 5 | 2 | 17 |
| smc | 5 | 0 | 14,988 |
| calendar | 4 | 1 | 6 |
| flow | 4 | 1 | 6 |
| mean-reversion | 4 | 0 | 11 |
| third-party-ea | 4 | 0 | 304 |
| awesome-list | 3 | 0 | 0 |
| book | 3 | 1 | 9 |
| filter-mining | 3 | 0 | 244 |
| grid | 3 | 0 | 196 |
| liquidity | 3 | 0 | 1,376 |
| oscillator | 3 | 0 | 288 |
| portfolio | 3 | 3 | 16 |
| reversion | 3 | 3 | 16 |
| sweep | 3 | 0 | 1,376 |
| averaging | 2 | 0 | 160 |
| bailout-exit | 2 | 1 | 6 |
| carry | 2 | 1 | 2 |
| costs | 2 | 0 | 8 |
| dip-buying | 2 | 0 | 8 |
| energy | 2 | 0 | 128 |
| eurusd | 2 | 1 | 147 |
| fix | 2 | 1 | 6 |
| fvg | 2 | 0 | 9,312 |
| pattern | 2 | 0 | 4,896 |
| risk | 2 | 0 | 60 |
| rsi2 | 2 | 0 | 8 |
| short-vol | 2 | 0 | 17 |
| sizing | 2 | 0 | 60 |
| stop-entry | 2 | 1 | 6 |
| time-filter | 2 | 0 | 144 |
| trailing | 2 | 0 | 156 |
| usdjpy | 2 | 1 | 6 |
| winner-anatomy | 2 | 0 | 135 |
| breakeven | 1 | 0 | 102,260 |
| control | 1 | 0 | 48 |
| cross-asset | 1 | 0 | 0 |
| cross-sectional | 1 | 0 | 1 |
| diversified | 1 | 1 | 1 |
| exness | 1 | 0 | 5 |
| factor | 1 | 0 | 1 |
| forward-test | 1 | 1 | 1 |
| futures | 1 | 1 | 1 |
| gbpusd | 1 | 0 | 144 |
| hindsight-market-choice | 1 | 0 | 64 |
| ict | 1 | 0 | 780 |
| macro | 1 | 0 | 0 |
| metals | 1 | 0 | 64 |
| momentum | 1 | 0 | 1 |
| monthly | 1 | 0 | 0 |
| oil | 1 | 0 | 0 |
| options-expiry | 1 | 0 | 0 |
| out-of-sample | 1 | 1 | 1 |
| pairs | 1 | 0 | 1 |
| payouts | 1 | 0 | 3 |
| probability | 1 | 0 | 3 |
| prop | 1 | 0 | 20 |
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
| turn-of-month | 1 | 0 | 0 |
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
