# LESSONS — generated from ledger.jsonl (do not edit; run `python3 research/truth/memory.py --render`)

23 ideas tested, about 301,020 configurations; 3 survivors. Principles: `PRINCIPLES.md` · queue: `OPEN_QUESTIONS.md` · sessions: `JOURNAL.md`.

## Survivors
| Idea | Family | Verdict | Key numbers | Evidence |
|---|---|---|---|---|
| Hunt 2 / 11-leg book | portfolio, trend, reversion, seasonal | Survivor: Tier B forward-test candidate | Sharpe 1.00 after costs+swaps (1.64 low-cost swap-free); 2023-25 +0.044R/trade, PF 1.12 | research/hunt/HUNT2_REPORT.md; research/northstar/NORTHSTAR_REPORT.md |
| Futures trend + carry (pysystemtrade data, Carver defaults) | trend, carry, futures, diversified | Survivor (futures only) | Sharpe 0.96 since 2000, 0.50 2011-24; as CFDs 0.06 | research/multiasset/PROJECT.md |
| TimelessCity v2.42 re-score (S1 gold/EUR, S2 USDJPY, S3 gold) | trend, reversion, portfolio | Survivor: deployed EA (demo gate pending) | Sharpe 0.67 with swaps, 1.04 low-cost swap-free; S1 EUR -0.06R 2023-25 (watch) | research/northstar/TIMELESSCITY_RESCORE.md |

## Family priors (how earlier ideas with this tag ended)
| Tag | Ideas | Survived | Configurations |
|---|---|---|---|
| trend | 6 | 3 | 102,436 |
| reversal | 5 | 0 | 105,838 |
| smc | 5 | 0 | 14,988 |
| breakout | 4 | 0 | 119,218 |
| session | 4 | 0 | 183,323 |
| liquidity | 3 | 0 | 1,376 |
| sweep | 3 | 0 | 1,376 |
| carry | 2 | 1 | 2 |
| fvg | 2 | 0 | 9,312 |
| intraday | 2 | 0 | 180,685 |
| mean-reversion | 2 | 0 | 3 |
| pattern | 2 | 0 | 4,896 |
| portfolio | 2 | 2 | 15 |
| retest | 2 | 0 | 9,312 |
| reversion | 2 | 2 | 15 |
| risk | 2 | 0 | 60 |
| sizing | 2 | 0 | 60 |
| breadth | 1 | 0 | 2 |
| breakeven | 1 | 0 | 102,260 |
| control | 1 | 0 | 48 |
| cross-sectional | 1 | 0 | 1 |
| diversified | 1 | 1 | 1 |
| engulfing | 1 | 0 | 2,202 |
| factor | 1 | 0 | 1 |
| futures | 1 | 1 | 1 |
| ict | 1 | 0 | 780 |
| momentum | 1 | 0 | 1 |
| pairs | 1 | 0 | 1 |
| prop | 1 | 0 | 20 |
| quasimodo | 1 | 0 | 3,456 |
| random | 1 | 0 | 48 |
| ranking | 1 | 0 | 61,787 |
| scanner | 1 | 0 | 61,787 |
| seasonal | 1 | 1 | 11 |
| short-vol | 1 | 0 | 1 |
| stat-arb | 1 | 0 | 1 |
| supply-demand | 1 | 0 | 1,440 |
| support-resistance | 1 | 0 | 2,202 |
| volatility | 1 | 0 | 102,260 |

## Every idea tested (newest first)
| Date | Idea | Family | Configs | Verdict | Key numbers |
|---|---|---|---|---|---|
| 2026-10-31 | TimelessCity v2.42 re-score (S1 gold/EUR, S2 USDJPY, S3 gold) | trend, reversion, portfolio | 4 | Survivor: deployed EA (demo gate pending) | Sharpe 0.67 with swaps, 1.04 low-cost swap-free; S1 EUR -0.06R 2023-25 (watch) |
| 2026-10-31 | Liquidity grabs at swing points (SFP, equal highs, sweep+MSS, NY-sweeps-London) | liquidity, sweep, smc, ict, reversal | 780 | Rejected | best (sweep+MSS H1) 2023-25 -0.185R; ~1,400 liquidity variants tested in total |
| 2026-10-31 | donchian_trend_v1 | trend, breakout | 96 | Rejected: no configuration passed the development gate | 50-bar time stop; gold/JPY positive, EUR/GBP negative |
| 2026-10-31 | donchian_trend_v2_room_to_run | trend, breakout | 64 | Rejected: no configuration passed the development gate | 4-market rule fails: gold +0.14-0.21R, JPY +0.15-0.28R, EUR/GBP negative |
| 2026-10-31 | coin_flip_control_v1 | control, random | 48 | Rejected | control: 1 random setting passed the first gate, caught by walk-forward/neighbours/DSR |
| 2026-10-31 | FTMO-style prop challenge replay (TimelessCity, 11-leg book) | prop, risk, sizing | 20 | Study: informative (no new edge) | book at 1-1.5% risk/trade: phase 1 passed in 52-72% of 12-month windows (median ~26-34 weeks), both phases 33-54%; funded payouts ~6-8% of account/yr; TimelessCity lower (17-33% both phases) |
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
| 2026-10-28 | Hunt 2 / 11-leg book | portfolio, trend, reversion, seasonal | 11 | Survivor: Tier B forward-test candidate | Sharpe 1.00 after costs+swaps (1.64 low-cost swap-free); 2023-25 +0.044R/trade, PF 1.12 |
| 2026-10-28 | Gold WAT session + Malaysian SnR | support-resistance, engulfing, reversal, session | 2202 | Rejected | no robust edge |
| 2026-10-28 | Four strategies (trend continuation, failed breakout, vol contraction/expansion) | trend, reversal, volatility, breakeven | 102260 | Rejected (as a set) | with swaps 2023-25 +0.005R/trade; failed-breakout reversal fails everywhere; breakeven is a backtest mirage |
| 2026-10-27 | ORB 50 study | breakout, intraday, session | 118898 | Rejected | all 4 finalists negative 2023-25 (-0.12 to -0.16R) |
