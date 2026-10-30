# Project North Star — plan and status (multi-strategy phase)

Goal (owner): the highest sustainable growth with regular fortnightly payouts; aspiration 60–120% a year.
Project manager's job: find every independent source of return, combine them, size them on the
growth/drawdown frontier, and ship an EA. The only rule kept is the one that makes results real:
nothing is counted that only works in hindsight.

## 1. The arithmetic of the goal (Kelly)
Log growth at portfolio volatility σ with Sharpe S ≈ S·σ − σ²/2; yearly return = e^growth − 1. Full Kelly
(σ = S) maximises it. *(Corrected 2026-10-30: an earlier version of this table showed log growth as if it
were the yearly return, which overstated the Sharpe the goal needs.)*

| True Sharpe | Yearly return at 25% vol | at 40% vol | at 60% vol | Full Kelly (theoretical max) |
|---|---|---|---|---|
| 0.74 (our −1 s.e.) | 17% | 24% | 30% | 32% at 74% vol |
| **1.08 (our best estimate)** | **27%** | **42%** | **60%** | 79% at 108% vol |
| 1.42 (our +1 s.e.) | 38% | 63% | 96% | 174% at 142% vol |

Sharpe needed: **60% a year → 1.7 at 30% vol, 1.5 at 35%, 1.4 at 40%. 120% a year → 2.0 at 45% vol,
2.2 at 40%.** Fat-tailed simulation, 3-year paths (`what it takes`, §6):

| Sharpe / vol | Median yearly return | Bad decile | Median max DD | 1-in-20 DD |
|---|---|---|---|---|
| 1.08 / 25% (today) | 27% | 6% | 26% | 43% |
| 1.5 / 30% | 50% | 20% | 26% | 42% |
| 2.0 / 35% | 90% | 47% | 27% | 42% |
| 2.0 / 40% | 105% | 52% | 30% | 47% |

The project's lever is **breadth**: more independent edges raise the Sharpe; leverage doesn't.

## 2. Evidence so far: daily returns, costs included (`combine.py`, `mr_breadth.py`, `carver.py`)

| Source | Sharpe 2011–2024Q1 | Notes |
|---|---|---|
| 11-leg book (costs + financing) | **1.01** | 2011–16 1.23, 2017–20 0.62, 2021–24 1.08 |
| Trend + carry, 47 futures markets (no bonds-only/VIX), Carver defaults, nothing fitted | **0.50** | 2000–2024Q1 0.96 with bonds; 2000–09 1.21, 2010–18 1.00, 2019–24 0.35 |
| Same as CFDs (broker financing markups) | 0.06 | 4x notional x markup destroys it; bonds impossible as CFDs |
| Cross-sectional momentum (12-1, within class) | 0.00 | rejected |
| Pairs stat-arb (10 linked pairs) | −0.20 | rejected |
| RSI(2) / Bollinger mean reversion on 56 markets | 0.01 / −1.2 | stock indices only +0.41 (watch-list) |
| Short volatility (VIX carry) | — | −97% drawdown; rejected |
| Portfolio volatility overlay | no gain | Sharpe 1.08 → 1.06–1.07, deeper drawdown |

Correlation of the book with trend+carry: **−0.02**. Best combination: book 57% / trend+carry futures
43% (inverse-vol weights fitted on 2011–16 only): Sharpe **1.08** (2011–16 1.28, after 0.91).

## 3. Frontier for book + trend/carry futures (3-year paths, quarter-block bootstrap, 1,000 paths)

| Vol target | Historical CAGR / max DD | Median 3-yr CAGR | 10% worst CAGR | Median max DD | 1-in-20 DD | P(DD > 50%) | P(CAGR > 60%) |
|---|---|---|---|---|---|---|---|
| 15% | 16% / 15% | 15% | 5% | 15% | 24% | 0% | 0% |
| 20% | 22% / 20% | 21% | 5% | 20% | 31% | 0% | 1% |
| **25%** | **27% / 25%** | **26%** | **6%** | **24%** | **37%** | **0.4%** | 6% |
| 30% | 32% / 30% | 32% | 7% | 29% | 41% | 1% | 17% |
| 40% | 42% / 38% | 40% | 4% | 37% | 55% | 10% | 29% |
| 60% | 60% / 54% | 56% | 4% | 51% | 71% | 53% | 47% |

Drawdowns are understated: book P&L is booked at trade exit (no intratrade marking).
**Recommended operating point today: 20–25% vol (about quarter Kelly).** Expected about 20–27% a year with
about 20–25% typical drawdowns. 60% a year is a 1-in-6 three-year outcome at 30% vol, not a plan.
Note: this daily-return frontier supersedes earlier trade-based figures (e.g. Hunt 2's "53% CAGR at
22% DD"), which had no financing and a lower drawdown measurement.

## 4. Repositories surveyed
- **robcarver17/pysystemtrade**: used. Its public data (252 futures, daily, to 2024-03, carry and
  spread costs) gave the trend+carry source; the framework (EWMAC + carry + vol targeting + IDM) is
  implemented in `carver.py`.
- **philipperemy/FX-1-Minute-Data** (and forks): code only now; the data moved to Google Drive
  (blocked here). It was intended for M1 breadth on 66 pairs + indices + commodities.
- **vectorbt**: installable from PyPI here; a faster vectorised engine but no new edge. Our numba
  engines already run a 30k-config grid in 3 minutes.
- **microsoft/qlib**: an ML alpha platform for stocks (cross-sectional equity factors). Needs stock
  universes and data; doesn't fit MT5 FX/CFD trading. Skipped.
- **nautilus_trader**: production event-driven engine with live adapters (Interactive Brokers,
  Binance, Databento, …), no MT5. Relevant only if execution moves to futures via IBKR.
- **Market making**: needs exchange access, queue priority and rebates; a retail MT5 account pays
  the spread rather than earning it. Not available.
- **Option selling**: no options on retail MT5. The closest proxy (short VIX futures) had a −97%
  drawdown.

## 5. Next phases (decision gates)
1. **Unblock data (owner action).** Allow `datafeed.dukascopy.com` in this environment's network
   settings. That gives M1 data for about 30 more markets (crosses, indices, oil, silver,
   2011–2025), so the book's proven families can run across them. This is the main route to a
   higher Sharpe.
2. **Breadth run.** Book families x new markets through the same timeless funnel. Gate: new legs
   positive in every era and out-of-sample, correlation < 0.3 with existing legs.
3. **Execution route for trend+carry.** It only works on real futures: an MT5 futures broker (CME
   micro contracts) or IBKR. On CFDs it's worthless (Sharpe 0.06). Decision needed from the owner.
4. **Size at 20–25% vol** with the RED circuit breaker; fortnightly salary payouts from realised
   profit only.
5. **Demo 6 months**, weekly report (`../northstar/weekly.py`), then small live.

## 6. What it takes to reach and pass the goal
Portfolio Sharpe ≈ leg Sharpe x √(N / (1 + (N−1)·ρ)), with N independent legs at average correlation ρ.
Today: 11 legs averaging about Sharpe 0.3 each, near-zero correlation → 1.0; with trend+carry 1.08.

| Goal | Portfolio Sharpe | Legs needed (Sharpe 0.3 each, ρ ≈ 0) | (Sharpe 0.5 each, ρ 0.02) |
|---|---|---|---|
| 60% a year, ~30% DD | 1.5 | ~25 | ~11 |
| 120% a year, ~30% DD | 2.0 | ~45 | ~24 |
| 200%+ a year | 2.9 | not reachable with 0.3 legs | ~100 |

Correlation is the hidden ceiling: at ρ = 0.02, 0.3-Sharpe legs can never pass 2.1 however many
there are. Uncorrelated markets (indices, energy, crypto, metals) matter more than more USD pairs.

Shopping list (owner):
1. M1 bid data 2011–2025 (ask too if possible) for: AUDUSD, NZDUSD, USDCAD, USDCHF, EURJPY, GBPJPY,
   EURGBP, AUDJPY, CADJPY, CHFJPY, EURAUD, EURCHF, GBPAUD, AUDNZD, XAGUSD, XPTUSD, WTI, Brent, natural
   gas, US500, NAS100, US30, GER40, UK100, JP225, BTCUSD, ETHUSD. Free tick data for the FX pairs and
   silver already exists for 2007–2018 in the `FX-Data` GitHub organisation (EURUSD to 2022); 2019–2025
   and every index, energy and crypto market still need fetching. Easiest: allow
   `datafeed.dukascopy.com` here. Otherwise run dukascopy-node on your PC
   (`npx dukascopy-node -i audusd -from 2019-01-01 -to 2020-01-01 -t m1 -p bid -f csv`, one file per
   year) and push the CSVs to a GitHub repo; `tools/ingest_m1.py` reads that naming directly.
2. The MT5 broker's real costs: symbol specs (spread by hour, commission, swap long/short) for
   every symbol above.
3. A futures route (an MT5 futures broker with CME micros, or IBKR) for trend+carry.
4. Optional new edge types: economic-calendar history with timestamps, CFTC COT weekly positioning,
   central-bank rate history.
