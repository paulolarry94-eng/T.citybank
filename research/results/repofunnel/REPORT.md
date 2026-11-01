# Repo funnel: 132 public strategies through our tests (2026-11-01)

**Outcome: nothing new to trade on Exness CFDs.** Of 132 strategies in the three collections the owner named, 84 could be
tested (68 on our 11 CFDs, 16 on futures data), 3 had been tested earlier, and 45 cannot be tested with our data.
None of the 68 CFD strategies survives. On futures, five pass the pre-registered gate; only time-series momentum has
strong evidence, and it is the trend family we already hold as a futures-only survivor.

| Source | Strategies | Tested here | Configurations | Passed the gate | Survivors |
|---|---:|---:|---:|---:|---:|
| trustdan (Turtle/Seykota Pine scripts) | 48 | 48 on CFDs | 48 | 0 | 0 |
| sofus-nl (swing setups) | 23 | 18 on CFDs (5 need volume or company data) | 36 | 0 | 0 |
| awesome-systematic-trading | 61 | 2 on CFDs, 16 on futures (3 done earlier, 40 not testable) | 3 CFD + 16 futures | 1 CFD (payday, then failed) + 5 futures | 5 futures-only candidates (1 strong) |
| **Total** | **132** | **84** | **103** | | **0 for CFDs** |

What the numbers say, in plain words:

1. **Their headline winners lose on our markets.** trustdan's champion Alt10 ("76% success" on US stocks) loses
   0.62R per trade 2011–19 after costs and swaps; their #2, Alt45, loses 0.62R. All 48 variants are negative in
   development pooled over the 11 markets; the best is still -0.24R. sofus's setups (claimed profit factors 1.7–4.5 on
   stocks) are all negative too; the least bad is RSI(2) reversion at -0.02R.
2. **Swaps decide trend on CFDs.** With our swap estimates every trend rule loses; swap-free and at half our costs the
   Turtle core makes +0.20R per trade 2011–19 and the 10-year-high trend (awesome list) makes +0.25R with 10 of 11
   markets positive and +0.12R in 2020–22. As pre-registered, the verdict uses costs with swaps, so these are not
   survivors; the swap-free view is reported, not used. It strengthens the case to settle Q1 (is the account swap-free?)
   and Q17 (our index swaps are charged in points and overstate early years).
3. **Published calendar effects faded.** Payday (hold the S&P 500 over the 16th) passed 2011–19 (+0.016R per trade,
   t 2.1) and then lost in 2020–22, under stress and in its one 2023–25 look (151 trades, -0.006R). Commodity momentum
   and term structure made 17-18% a year in 2000–09 and lost money after 2010 (P11).
4. **Two futures "winners" were a data artifact, now fixed.** In the first futures run, country-index pairs (Sharpe +1.4
   in every period) and the WTI–Brent spread (Sharpe +2 to +3) looked excellent. Both vanish when the trade is placed one
   day after the signal (markets close at different hours, and holidays leave stale prices). v2 trades one day later for
   all 16 strategies. New principle P23.
5. **Futures candidates.** Time-series momentum (Sharpe 1.1 / 0.6 / 1.0 in the three periods, t 3.9, deflated Sharpe
   0.88): real, but it is our existing futures trend family. Commodity skewness (0.3 / 0.7 / 0.9, t 2.2, deflated
   0.28) is the one new idea with every period positive. FX carry, asset-class momentum and paired switching pass a
   weak gate with t 0.4–2.3 and deflated Sharpe 0.01–0.33: not distinguishable from luck after 16 tries. All need a
   futures account; none runs on 11 CFDs (skewness needs about 28 commodities).

How it was done: `research/repofunnel/PREREG.md` (committed before any result), `INVENTORY.csv` (every strategy and its
class), a daily engine that replays the Pine logic on our M1 data (`d1.py`, `trustdan.py`, `sofus.py`,
`awesome_cfd.py`; 11 tests incl. a no-peeking check on truncated data), the Truth Lab unchanged for the CFD files
(`research/results/truth/funnel_trustdan_v1`, `funnel_sofus_v1`, `ath_trend_v1`, `payday_indices_v1`), and
`futures_funnel.py` for the cross-asset rules. Costs: lab all-in costs with overnight swaps; "swap-free" = half costs,
no swap (reported separately). R = 1% of equity per unit of risk. Periods: 2011–19 development (two eras), 2020–22
validation, 2023–25 one logged look (futures: 2000–09, 2010–19, 2020–22, 2023-01 to 2024-03). Gate: >= 200 trades,
both eras positive, >= 9 of 11 markets positive.

Caveats: trustdan and sofus were written for US stocks; our translation keeps the rules but not the asset class.
Five sofus patterns are mechanical approximations of discretionary charts. Two sofus setups never trigger on our daily
data (RSI back to 40–50 while still above a rising EMA21; the strict cup and handle). Index swaps are lab estimates in
points (Q17). Futures returns exclude interest on cash; the futures data end 2024-03-28. For F1, F4, F5, F10, F11 and
F13 the 2023–24 period had been seen in the v1 run (disclosed in PREREG section E2).

## Results

Columns: R per trade after costs and swaps unless marked swap-free; "Markets +" = markets with a positive 2011–19 result.

### trustdan (48 configurations)

| Rule | Trades 2011–19 | R/trade 2011–19 | t | 2011–15 | 2016–19 | R/trade 2020–22 | Markets + (of 11) | Swap-free 2011–19 | Swap-free 2020–22 | Swap-free markets + |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| alt8 | 543 | -0.28 | -1.1 | +0.07 | -0.60 | -0.41 | 5 | +0.19 | -0.19 | 6 |
| alt17 | 202 | -0.44 | -1.2 | +0.08 | -1.03 | -0.62 | 4 | +0.27 | -0.36 | 5 |
| alt6 | 77 | -2.36 | -1.2 | -2.38 | -1.90 | -2.45 | 1 | +2.54 | -1.58 | 3 |
| alt5 | 452 | -0.33 | -1.4 | -0.08 | -0.58 | -0.26 | 6 | +0.27 | +0.01 | 6 |
| alt14 | 488 | -0.24 | -1.5 | -0.08 | -0.40 | -0.30 | 3 | +0.11 | -0.11 | 5 |
| alt18 | 490 | -0.47 | -1.5 | -0.15 | -0.77 | -0.36 | 5 | +0.34 | -0.03 | 6 |
| core (Turtle 55/10) | 490 | -0.38 | -1.8 | -0.14 | -0.61 | -0.32 | 5 | +0.20 | -0.05 | 6 |
| alt13 | 490 | -0.36 | -1.9 | -0.11 | -0.61 | -0.19 | 6 | +0.19 | +0.03 | 6 |
| alt11 | 490 | -0.31 | -2.1 | -0.17 | -0.44 | -0.14 | 4 | +0.13 | +0.06 | 6 |
| alt27 | 507 | -0.44 | -2.1 | -0.14 | -0.75 | -0.49 | 5 | +0.31 | -0.22 | 8 |
| alt41 | 464 | -0.21 | -2.2 | -0.10 | -0.31 | -0.14 | 2 | -0.00 | -0.05 | 6 |
| alt2 | 125 | -0.68 | -2.2 | -0.70 | -0.66 | -0.14 | 2 | -0.28 | +0.12 | 3 |
| alt16 | 4 | -1.64 | -2.2 | -0.34 | -2.07 | -1.71 | 0 | -1.53 | -1.66 | 0 |
| alt33 | 474 | -0.36 | -2.3 | -0.16 | -0.56 | -0.29 | 3 | +0.21 | -0.07 | 8 |
| alt12 | 494 | -0.63 | -2.4 | -0.36 | -0.89 | -0.36 | 3 | +0.12 | -0.01 | 6 |
| alt22 | 636 | -0.25 | -2.5 | -0.20 | -0.31 | +0.06 | 4 | +0.07 | +0.20 | 7 |
| alt15 | 488 | -0.67 | -2.5 | -0.48 | -0.85 | -0.02 | 3 | +0.25 | +0.43 | 6 |
| alt4 | 195 | -1.82 | -2.5 | -0.82 | -2.86 | +0.15 | 3 | +0.34 | +1.37 | 4 |
| alt28 | 280 | -0.62 | -2.7 | -0.29 | -0.96 | -0.78 | 5 | -0.13 | -0.56 | 5 |
| alt44 | 283 | -0.61 | -2.7 | -0.27 | -0.96 | -0.77 | 4 | -0.13 | -0.55 | 5 |
| alt19 | 596 | -0.57 | -2.9 | -0.35 | -0.77 | -0.15 | 3 | +0.06 | +0.18 | 5 |
| alt9 | 509 | -0.47 | -2.9 | -0.36 | -0.57 | -0.27 | 4 | +0.07 | -0.01 | 5 |
| alt29 | 460 | -0.45 | -3.1 | -0.35 | -0.56 | -0.35 | 3 | +0.12 | -0.15 | 7 |
| alt7 | 439 | -0.70 | -3.1 | -0.52 | -0.88 | -0.69 | 3 | +0.13 | -0.39 | 7 |
| alt32 | 486 | -0.52 | -3.1 | -0.38 | -0.65 | -0.37 | 2 | +0.10 | -0.13 | 8 |
| alt39 | 432 | -0.62 | -3.2 | -0.45 | -0.79 | -0.45 | 3 | +0.09 | -0.18 | 7 |
| alt45 | 432 | -0.62 | -3.2 | -0.45 | -0.79 | -0.45 | 3 | +0.09 | -0.18 | 7 |
| alt25 | 486 | -0.54 | -3.3 | -0.40 | -0.69 | -0.40 | 2 | +0.08 | -0.15 | 8 |
| alt47 | 432 | -0.68 | -3.3 | -0.51 | -0.84 | -0.58 | 3 | +0.10 | -0.29 | 7 |
| alt36 | 436 | -0.62 | -3.3 | -0.48 | -0.77 | -0.43 | 3 | +0.10 | -0.17 | 7 |
| alt10 | 439 | -0.62 | -3.3 | -0.46 | -0.78 | -0.46 | 2 | +0.09 | -0.20 | 8 |
| alt30 | 432 | -0.64 | -3.3 | -0.48 | -0.79 | -0.44 | 3 | +0.10 | -0.17 | 6 |
| alt24 | 433 | -0.61 | -3.3 | -0.44 | -0.79 | -0.44 | 2 | +0.09 | -0.18 | 8 |
| alt37 | 489 | -0.56 | -3.4 | -0.42 | -0.69 | -0.40 | 2 | +0.05 | -0.16 | 6 |
| alt21 | 436 | -0.65 | -3.4 | -0.50 | -0.80 | -0.46 | 3 | +0.07 | -0.19 | 7 |
| alt34 | 448 | -0.41 | -3.5 | -0.26 | -0.55 | -0.17 | 2 | +0.05 | +0.01 | 7 |
| alt38 | 452 | -0.40 | -3.5 | -0.26 | -0.54 | -0.16 | 3 | +0.05 | +0.02 | 6 |
| alt35 | 492 | -0.37 | -3.5 | -0.30 | -0.45 | -0.15 | 2 | +0.04 | +0.02 | 6 |
| alt40 | 495 | -0.37 | -3.5 | -0.30 | -0.43 | -0.14 | 2 | +0.03 | +0.02 | 6 |
| alt46 | 434 | -0.66 | -3.5 | -0.51 | -0.82 | -0.48 | 2 | +0.10 | -0.21 | 8 |
| alt26 | 448 | -0.42 | -3.5 | -0.27 | -0.56 | -0.18 | 2 | +0.05 | -0.00 | 7 |
| alt31 | 452 | -0.41 | -3.6 | -0.27 | -0.55 | -0.17 | 3 | +0.04 | +0.01 | 6 |
| alt43 | 432 | -0.69 | -3.6 | -0.53 | -0.84 | -0.44 | 2 | +0.06 | -0.16 | 7 |
| alt23 | 665 | -0.50 | -3.6 | -0.33 | -0.68 | -0.13 | 2 | +0.01 | +0.06 | 6 |
| alt42 | 478 | -0.75 | -3.8 | -0.72 | -0.77 | +0.01 | 4 | -0.01 | +0.36 | 5 |
| alt1 | 856 | -0.55 | -4.0 | -0.45 | -0.65 | -0.27 | 2 | -0.07 | -0.02 | 5 |
| alt20 | 1437 | -0.04 | -4.5 | -0.04 | -0.04 | +0.00 | 1 | -0.01 | +0.02 | 3 |
| alt3 | 421 | -1.91 | -4.9 | -1.44 | -2.42 | -0.05 | 2 | -0.34 | +1.04 | 4 |

### sofus (36 configurations)

| Setup, side | Trades 2011–19 | R/trade 2011–19 | t | 2011–15 | 2016–19 | R/trade 2020–22 | Markets + (of 11) | Swap-free 2011–19 | Swap-free 2020–22 | Swap-free markets + |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| s01_vcp both | 28 | -0.11 | -0.5 | -0.22 | -0.01 | -0.42 | 4 | +0.10 | -0.31 | 5 |
| s01_vcp long | 25 | -0.19 | -0.8 | -0.38 | +0.03 | -0.38 | 3 | +0.04 | -0.26 | 4 |
| s02_cup_handle both | 0 | — | — | — | — | — | 0 | — | — | 0 |
| s02_cup_handle long | 0 | — | — | — | — | — | 0 | — | — | 0 |
| s03_ema_cross both | 119 | -0.02 | -0.1 | -0.00 | -0.03 | -0.08 | 5 | +0.14 | -0.00 | 7 |
| s03_ema_cross long | 80 | -0.05 | -0.3 | +0.21 | -0.31 | -0.49 | 6 | +0.15 | -0.41 | 6 |
| s04_rsi_pullback both | 0 | — | — | — | — | — | 0 | — | — | 0 |
| s04_rsi_pullback long | 0 | — | — | — | — | — | 0 | — | — | 0 |
| s07_stage2 both | 169 | -0.46 | -5.9 | -0.45 | -0.48 | +0.17 | 2 | -0.11 | +0.38 | 3 |
| s07_stage2 long | 99 | -0.51 | -5.0 | -0.60 | -0.42 | +0.36 | 2 | -0.04 | +0.60 | 5 |
| s08_bull_flag both | 90 | -0.65 | -4.2 | -0.50 | -0.78 | +0.63 | 2 | -0.36 | +0.83 | 3 |
| s08_bull_flag long | 58 | -0.68 | -3.5 | -0.57 | -0.77 | +1.06 | 2 | -0.33 | +1.32 | 3 |
| s10_triple_rsi_div both | 30 | +0.00 | +0.0 | +0.28 | -0.21 | -0.09 | 4 | +0.09 | -0.05 | 5 |
| s10_triple_rsi_div long | 14 | -0.66 | -7.4 | -0.56 | -0.69 | +0.83 | 0 | -0.58 | +0.90 | 1 |
| s11_qullamaggie both | 15 | -0.24 | -0.8 | -0.03 | -0.38 | -1.04 | 3 | +0.01 | -0.99 | 4 |
| s11_qullamaggie long | 12 | -0.49 | -1.8 | -0.13 | -0.67 | -1.04 | 1 | -0.18 | -0.99 | 2 |
| s12_multi_period both | 553 | -0.18 | -3.8 | -0.26 | -0.09 | -0.09 | 2 | +0.00 | +0.00 | 6 |
| s12_multi_period long | 372 | -0.22 | -3.8 | -0.33 | -0.08 | -0.15 | 5 | +0.01 | -0.05 | 7 |
| s13_ma_stack both | 639 | -0.30 | -4.4 | -0.29 | -0.31 | -0.03 | 3 | -0.02 | +0.13 | 5 |
| s13_ma_stack long | 389 | -0.38 | -4.9 | -0.44 | -0.32 | +0.00 | 3 | -0.01 | +0.19 | 6 |
| s14_adx_trend both | 472 | -0.22 | -3.9 | -0.22 | -0.23 | +0.03 | 2 | -0.09 | +0.10 | 3 |
| s14_adx_trend long | 221 | -0.27 | -3.2 | -0.45 | -0.08 | +0.24 | 2 | -0.09 | +0.34 | 4 |
| s16_trend_template both | 269 | -0.24 | -2.3 | -0.25 | -0.23 | +0.02 | 3 | -0.03 | +0.12 | 4 |
| s16_trend_template long | 193 | -0.29 | -2.4 | -0.38 | -0.16 | -0.13 | 4 | -0.03 | -0.03 | 5 |
| s18_roc_breakout both | 1215 | -0.19 | -1.9 | -0.08 | -0.31 | +0.12 | 2 | +0.05 | +0.24 | 5 |
| s18_roc_breakout long | 682 | -0.37 | -4.7 | -0.37 | -0.37 | +0.26 | 3 | -0.04 | +0.41 | 6 |
| s19_hhv_breakout both | 656 | -0.28 | -2.6 | -0.21 | -0.35 | -0.23 | 5 | +0.13 | -0.07 | 8 |
| s19_hhv_breakout long | 383 | -0.33 | -2.4 | -0.40 | -0.27 | -0.09 | 3 | +0.23 | +0.12 | 6 |
| s20_frog_pan both | 396 | -0.24 | -4.3 | -0.25 | -0.23 | -0.12 | 2 | -0.06 | -0.03 | 4 |
| s20_frog_pan long | 283 | -0.27 | -4.1 | -0.32 | -0.22 | -0.16 | 3 | -0.05 | -0.06 | 5 |
| s21_proximity_pullback both | 1100 | -0.20 | -4.1 | -0.26 | -0.13 | -0.13 | 1 | -0.05 | -0.06 | 4 |
| s21_proximity_pullback long | 687 | -0.27 | -5.4 | -0.34 | -0.17 | -0.14 | 2 | -0.09 | -0.06 | 5 |
| s22_rsi2_reversion both | 1064 | -0.04 | -2.0 | -0.04 | -0.04 | -0.02 | 5 | +0.01 | +0.00 | 6 |
| s22_rsi2_reversion long | 630 | -0.02 | -0.8 | +0.00 | -0.05 | -0.03 | 5 | +0.03 | -0.01 | 6 |
| s23_trend_pullback both | 1769 | -0.19 | -4.8 | -0.26 | -0.12 | -0.07 | 1 | -0.04 | +0.01 | 5 |
| s23_trend_pullback long | 1019 | -0.22 | -4.2 | -0.34 | -0.11 | -0.01 | 3 | -0.04 | +0.09 | 3 |

### awesome-list strategies on our CFDs (3 configurations)

| Strategy | Trades 2011–19 | R/trade 2011–19 | t | 2011–15 | 2016–19 | R/trade 2020–22 | Markets + (of 11) | Swap-free 2011–19 | Swap-free 2020–22 | Swap-free markets + |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all-time-high trend both | 318 | +0.01 | +0.1 | -0.03 | +0.08 | +0.03 | 7 | +0.25 | +0.12 | 10 |
| all-time-high trend long | 258 | -0.08 | -1.1 | -0.15 | +0.02 | +0.10 | 3 | +0.20 | +0.20 | 6 |
| payday (5 index CFDs) | 529 | +0.02 | +2.1 | +0.02 | +0.01 | -0.01 | 5 | +0.03 | -0.00 | 5 |

### Futures (16 strategies, v2 with a one-day execution lag)

| # | Strategy | Judged on | Sharpe 2000–09 | Sharpe 2010–19 | Sharpe 2020–22 | t 2000–19 | Deflated Sharpe | Cost bp/yr | 2023-01..2024-03 | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| F1 | Time-series momentum | return | +1.12 | +0.61 | +0.98 | +3.9 | 0.88 | 11 | +0.10%/month (seen in v1) | **Candidate (futures only)** |
| F2 | Commodity momentum | return | +0.65 | -0.35 | -0.45 | +1.1 | 0.05 | 111 | — | Rejected (gate) |
| F3 | Commodity term structure | return | +1.00 | -0.26 | -0.22 | +1.9 | 0.21 | 190 | — | Rejected (gate) |
| F4 | Commodity skewness | return | +0.32 | +0.67 | +0.88 | +2.1 | 0.28 | 82 | +0.46%/month (seen in v1) | **Candidate (futures only)** |
| F5 | Commodity return asymmetry | return | +0.16 | +0.40 | +0.27 | +1.2 | 0.06 | 95 | -1.32%/month (seen in v1) | Rejected: negative final look |
| F6 | Currency momentum | return | +0.43 | -0.01 | +0.93 | +1.0 | 0.05 | 12 | — | Rejected (gate) |
| F7 | FX carry | return | +0.70 | +0.02 | +1.07 | +1.8 | 0.17 | 25 | +1.37%/month | **Candidate (futures only)** |
| F8 | Dollar carry | return | +0.61 | -0.02 | -0.10 | +1.4 | 0.10 | 7 | — | Rejected (gate) |
| F9 | Short-term reversal (simplified) | return | -0.08 | -0.55 | +0.82 | -1.3 | 0.00 | 224 | — | Rejected (gate) |
| F10 | Paired switching (vs 50/50) | excess over buy-and-hold | +0.10 | +0.09 | +0.58 | +0.4 | 0.01 | 5 | +1.02%/month (seen in v1) | **Candidate (futures only)** |
| F11 | Country index pairs | return | +0.38 | -0.35 | -1.37 | +0.4 | 0.01 | 118 | — | Rejected (gate) |
| F12 | Country betting-against-beta | return | +0.26 | +0.56 | -0.38 | +1.8 | 0.17 | 26 | — | Rejected (gate) |
| F13 | WTI-Brent spread | return | -0.62 | -0.55 | +0.03 | -2.5 | 0.00 | 240 | — | Rejected (gate) |
| F14 | January barometer (vs buy-and-hold) | excess over buy-and-hold | -0.06 | -0.72 | -0.23 | -1.1 | 0.00 | 1 | — | Rejected (gate) |
| F15 | Asset-class trend (vs equal weight) | excess over buy-and-hold | +0.28 | -0.17 | +0.60 | +0.5 | 0.01 | 11 | — | Rejected (gate) |
| F16 | Asset-class momentum (vs equal weight) | excess over buy-and-hold | +0.69 | +0.28 | +0.01 | +2.3 | 0.33 | 5 | +0.11%/month | **Candidate (futures only)** |


### Not testable with our data (45)

- Need single-stock cross-sections or company accounts (33 awesome-list strategies: value, quality, accruals, earnings,
  buybacks, R&D, ROA, short interest, small caps, low volatility, stock momentum/reversal/pairs, 52-week-high, ESG,
  filings, mutual funds, soccer clubs, 12-month cycle, residual momentum, F-score; sofus residual momentum).
- Need real traded volume (sofus VWAP reclaim, anchored VWAP, volume-weighted trend) or earnings dates (sofus power
  earnings gap).
- Need option prices (dispersion, volatility risk premium, synthetic lending rates), proprietary or macro series
  (sentiment index, PPP, CAPE, earnings yield, factor library, style indices), crypto data (bitcoin intraday, crypto
  rebalancing), or longer history than we have (US sector futures start 2011–2014).

Already tested earlier (3): turn of the month, option-expiry week, oil predicts equities — all rejected 2026-11-01.

## What to take from it

- A public repo's ranking is a ranking of backtests on other assets with no costs, no swaps and no holdout. On our
  markets with all three, the order changes and the sign flips (trustdan's best are among our worst).
- The trend family keeps telling the same story: it lives or dies on financing. The cheapest next step is still the
  owner's swap-free confirmation (Q1) and charging index financing as a rate (Q17); then one pre-registered re-test of
  the 10-year-high trend under a new name (Q18).
- Futures remain the only route where cross-asset momentum and carry earn; that route needs a futures broker (Q6).
