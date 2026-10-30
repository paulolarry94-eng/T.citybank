# Four strategies and a central risk manager

Trend continuation, failed breakout reversal, volatility contraction → expansion, volatility
expansion follow-through; every exit question (breakeven distance, reward:risk, trailing) tested
as a controlled experiment; one central risk manager over everything.

Protocol: 24 entry variants x 3 timeframes (H1/H4/D1) x 4 markets x 360 exits = **102,240 runs**,
1-minute fills, all-in costs. Selection on 2011–2019, confirmation on 2020–2022, one locked test on
2023–2025 (rules committed in `8d8128a` before that test; every look logged in
`results/orb_oos_log.json`). The fast engine matches a slow literal re-implementation on 642
trades (stops, targets, breakeven, chandelier trail): 0 mismatches.

## 1. The four families (`signals.py`)

| family | rule (signal on a closed bar, entry next bar) |
|---|---|
| TC trend continuation | EMA20/50 pullback then resume, or Donchian 20/55 breakout, only with the trend (EMA50 vs EMA200) |
| FB failed breakout reversal | N-bar (20/55) high/low broken by a wick that closes back inside, or broken by a close and closed back inside within 3 bars; with or without a trend filter |
| VC contraction → expansion | Bollinger width in the lowest 10/20% of 120 bars (or an NR7 bar), then the first close outside the 10-bar box within 5 bars |
| VE expansion follow-through | a bar of 1.5/2/2.5 x ATR range closing in its top (bottom) quarter → follow it |

## 2. Exits: what breakeven, targets and trailing do (`analyze.py`, `mgmt_oos.py`, `exit_sharpe.py`)

**Across all 102k runs** (change vs the same entries with no target, no BE, no trail):
- Fixed targets reduce R per trade in every family; 1R the most (−0.04 to −0.06R, worse in 2020–22), 5R the least.
- Breakeven at 0.5R hurts or is inconsistent; at 1.5–2R it is roughly neutral (±0.01R).
- A tight chandelier (2 ATR) hurts (−0.02 to −0.04R); 4 ATR is neutral.

**On the three locked entries, all markets pooled** (R per trade, 2011–19 / 2020–22 / 2023–25):

| exit | trend continuation | contraction → expansion | expansion follow-through |
|---|---|---|---|
| plain (100-bar time exit) | +0.09 / +0.07 / −0.01 | +0.10 / −0.07 / −0.05 | +0.10 / +0.39 / +0.04 |
| breakeven 0.5R | +0.14 / +0.07 / −0.09 | +0.17 / +0.06 / −0.08 | +0.22 / +0.31 / −0.07 |
| breakeven 1R | +0.17 / −0.02 / −0.08 | +0.23 / +0.00 / −0.05 | +0.27 / +0.21 / +0.03 |
| breakeven 2R | +0.14 / +0.01 / +0.01 | +0.18 / −0.02 / −0.08 | +0.23 / +0.18 / +0.02 |
| target 1R | +0.01 / +0.04 / +0.01 | +0.01 / +0.05 / +0.03 | +0.08 / +0.13 / +0.03 |
| target 3R | +0.01 / +0.19 / +0.15 | −0.03 / +0.03 / +0.18 | +0.11 / +0.22 / +0.23 |
| chandelier 4 ATR | +0.12 / +0.22 / +0.13 | +0.17 / +0.07 / +0.08 | +0.20 / +0.39 / +0.10 |

- **Breakeven is a backtest mirage:** it lifts 2011–19 results a lot and hurts in 2023–25 at 0.5–1R. At 2R it is harmless and adds nothing.
- **Small targets (1–1.5R) choke the edge.** 3R or more is fine.
- **Per trade, a loose trail (chandelier 4 ATR) is the most consistent exit,** better than plain in every period for all three.

**But per-trade R is the wrong yardstick for a portfolio.** Long holds keep many legs open at
once, and they lose together. Judged by the monthly Sharpe of each strategy across the four
markets, exits that cap the trade (a target plus a trail) win, the plain time exit is worst, and
breakeven-only exits collapse in 2023–25 (negative Sharpe for trend continuation and contraction).
Rebuilding the four with the 4-ATR trail raised R per trade but cut the risk-managed return at
equal drawdown from 22% to 8% a year. Choosing exits by the best *worst-era* Sharpe on 2011–2022
alone selects exactly the locked exits below, so they stay.

## 3. Universal rules, locked, and the final test (`universal.py`, `lock.py`, `final.py`)

One configuration per family for all four markets (development pooled across markets; both
development eras positive; at least 3 of 4 markets positive; highest pooled development t):

| family | locked rule (all H4, stop 1.5 x ATR) | 2011–19 | 2020–22 | **2023–25** |
|---|---|---|---|---|
| VE expansion | bar >= 2.5 x ATR, close in top/bottom quarter, with trend; target 2R, BE 0.5R, chandelier 2 | +0.146 (t 3.7) | +0.237 (t 3.2) | **+0.047** (t 0.7) |
| VC contraction | BB width in lowest 20%, 10-bar box breakout with trend; target 5R, BE 0.5R, chandelier 2 | +0.094 (t 2.4) | +0.115 (t 1.7) | **+0.054** (t 0.9) |
| TC trend | Donchian 55 breakout with trend; target 5R, BE 0.5R | +0.114 (t 2.3) | +0.201 (t 2.3) | **−0.016** (t −0.2) |
| FB failed breakout | 55-bar wick failure, no filter; BE 1R | +0.144 (t 2.6) | **−0.125** (t −1.8) | +0.071 (t 0.8) |

Failed breakout reversal fails validation (0 of 4 markets positive in 2020–22), consistent with the
ORB, liquidity-sweep, Turtle Soup and Malaysian SnR studies. It is excluded; its small 2023–25
gain does not reverse a failed validation. All three survivors weakened out of sample (normal cost
of selection). By market, gold and USDJPY stayed positive in every period for trend continuation
and expansion; EURUSD and GBPUSD faded in 2023–25.

## 4. Central risk manager (`risk_manager.py`)

For every new trade: risk = min(base x leg weight x brake, 4%), refused if total open risk would pass
30% or that market's open risk would pass 12%.
- Leg weight: inverse monthly volatility of the leg, measured on 2011–2019 only.
- Drawdown brake: risk x1 at the equity peak, falling linearly to x0.3 at a 25% drawdown.
- Strategy throttle (halve a leg after 20 net-losing trades): tested, cuts drawdown 2–4 points but
  costs as much return, so not used.

Equal-risk comparison (base solved so the median drawdown of reshuffled 15-year histories = 25%):

| set | median CAGR | 1-in-20 CAGR | 1-in-20 DD | real CAGR | real max DD | real 2023–25 per year |
|---|---|---|---|---|---|---|
| the four strategies alone (12 legs) | 22% | 9% | 32% | 22% | 25% | −1% |
| current 11-leg book | 52% | 32% | 31% | 41% | 25% | +19% |
| **book + the four (23 legs)** | **56%** | 30% | 31% | **53%** | **22%** | **+15%** |

Real yearly returns, book + four, no withdrawals: 2011 −1%, 2012 +98%, 2013 +128%, 2014 +264%,
2015 −3%, 2016 +94%, 2017 −14%, 2018 +32%, 2019 +76%, 2020 +69%, 2021 +13%, 2022 +225%, 2023 +12%,
2024 +4%, 2025 +29%.

**Fortnightly payouts** (salary mode; base risk 3.42% per unit weight):

| pay / fortnight | paid / year | on time: real / typical / 1-in-20 | trading DD: real / typical / 1-in-20 |
|---|---|---|---|
| 1.00% | 26% | 94% / 99% / 78% | 21% / 25% / 31% |
| 1.25% | 32% | 94% / 98% / 71% | 21% / 25% / 31% |
| **1.50%** | **37%** | 94% / 94% / 67% | 21% / 25% / 31% |
| 1.75% | 41% | 94% / 90% / 58% | 21% / 25% / 31% |
| 2.00% | 45% | 88% / 85% / 51% | 21% / 25% / 31% |

Edge-decay stress at 1.50%: −0.02R per trade → on time 84% typical / 45% 1-in-20, DD 1-in-20 35%;
−0.05R → 53% / 16%, DD 1-in-20 44%.

## 5. Verdict

- Timeless alpha exists here in **volatility expansion follow-through** (the most stable rule:
  every neighbour positive, 4 of 4 markets in development and validation), with trend continuation
  and contraction→expansion as weaker partners; all three are concentrated in gold and USDJPY.
- **Failed breakout reversal has no edge** in any form tested across this whole project.
- **Breakeven does not create edge.** Targets of 1–1.5R hurt. A loose trail helps per trade, but the
  portfolio prefers exits that cap holding time.
- The four strategies are not a system on their own (22% a year at a 25% drawdown, flat in
  2023–25). Folded into the existing book under one central risk manager they raise the real
  2011–2025 return from 41% to 53% a year while lowering the worst drawdown from 25% to 22%.
