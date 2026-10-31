# JOURNAL — one entry per session (newest last)

Format: date · what the owner asked · what was done · what was learned (with evidence) · decisions · next.
Facts and estimates are labelled; nothing is recorded as learned without evidence.

## 2026-10-27 → 2026-10-31 · founding sessions (North Star, scanner, multi-asset, liquidity, Truth Lab)
- **Asked:** find strategies and risk systems for a 60–120% a year goal; validate rigorously (North Star
  brief); test ICT/SMC, liquidity grabs and a daily best-setup scanner; search GitHub repos (pysystemtrade,
  vectorbt, qlib, nautilus); build a container that tests any idea and builds an EA if worthy; give it memory.
- **Done:** about 300,000 configurations across 25+ studies; the North Star pre-registered protocol;
  financing and rollover modelling; a risk-manager comparison; futures trend+carry; the Kelly/Monte Carlo
  frontier; a TimelessCity re-score; the Truth Lab (`research/truth/`), TruthEA template, parity checker,
  Exness export script, Dukascopy downloader; this memory.
- **Learned:** P1–P14 in PRINCIPLES.md. Survivors: TimelessCity v2.42, the 11-leg book (Tier B), futures
  trend+carry. Everything pattern-based was rejected on these four markets.
- **Decisions:** stop pattern hunting; the next truth comes from real costs (Q1), EA parity (Q2) and demo (Q3).
- **Facts vs estimates:** the Exness sensitivity (book Sharpe 1.64) is an ESTIMATE until Q1 is answered.
- **Next:** Q1 → Q2 → Q3; breadth (Q4) when data arrives.

## 2026-10-31 (later) · prop-firm (FTMO) approach
- **Asked:** how to build a bot that survives and is consistent on an FTMO-style prop account.
- **Done:** checked current FTMO rules (public summaries, not the official page: +10% / +5% targets, 5% daily and
  10% max loss of the initial balance, 4 trading days, no time limit reported for 2026); replayed TimelessCity and the
  11-leg book from every month start 2011-2024 under those rules (`research/prop/ftmo_sim.py`).
- **Learned (study, P&L at exit; optimistic and pessimistic bounds):** the book is the better prop engine (many small
  uncorrelated trades): both phases passed in 33% (1% risk) to 40-54% (1.5% risk) of windows; +10% takes ~6-8 months;
  funded payouts ~6-8% of the account a year at 80%. At 1.5% risk, phase 1 failure rises to 4-28%. TimelessCity passes less often.
- **Decisions:** none yet. Open question Q7 added (per-phase risk, near-barrier brake, structural daily-loss guard).
- **Facts vs estimates:** FTMO rules are from third-party summaries; costs are our research costs, not FTMO's.

## 2026-10-31 (later) · third-party EA review: Gold Hunter V9
- **Asked:** is there anything in Gold Hunter V9 (.ex5 + .set) that helps the goal; look from another perspective.
- **Done:** .ex5 is compiled and protected (no readable logic); reconstructed the standard hedged grid from the .set
  (0.01 lots, multiplier 1.0, step 1020 pips, basket TP 420 pips, 99 orders per side, no stop); replayed on XAUUSD
  M1 2011–2025 under two pip readings, with costs + swaps and a low-cost swap-free profile; capped variants; account
  replays from 168 month starts at $1k–$50k per 0.01 lot (`research/gridbot/gold_hunter_sim.py`).
- **Learned:** P15 (judge bots by equity, not balance). The grid harvests small range moves but carries an unbounded
  trend tail; no edge once the tail is capped. Confirms P13 (short-volatility shape) and P10 (short windows mislead).
- **Decisions:** not usable for the goal; the replay method is the template for auditing future third-party EAs.
- **Facts vs estimates:** the EA's exact code is unknown; results are for the standard reading of its settings.

## 2026-10-31 (later) · owner's EUR/USD daily reversal (no indicators)
- **Asked:** test the spec exactly: red close below the prior low → buy stop at its high (next session only); green
  close above the prior high → sell stop at its low; flat only; 4-pip costs; exit when in profit 16:45–16:55 New York,
  else a 250-pip stop.
- **Done:** priors showed 5/5 reversal ideas rejected (told the owner why this differs). Extended the Truth Lab with
  stop-order entries, a custom-exit executor (New York bailout) and per-strategy costs, with 3 new tests (15 pass).
  Ran the spec (stop 150/250/350 pips declared) and a 4-market breadth check declared before running.
- **Learned:** Tier B on EUR/USD: +0.040 / +0.030 / +0.012R per trade (dev / val / 2023–25), deflated Sharpe 0.91 (3 tries),
  88% winners, Sharpe 0.49 falling to 0.23, +0.9% a year at 1% risk. 4-market rule fails (EUR-specific): adds to P6. New P16.
- **Decisions:** watch-list (Q8); not a goal-mover. Real Exness costs (Q1) remain the priority.
- **Facts vs estimates:** the 2023–25 look is logged once (fingerprint 0fe044ee8598); P&L is booked at exit.

## 2026-10-31 (later) · where to get data for 4 more markets
- **Asked:** where to download data for 4 more markets.
- **Done:** declared the markets before any data: US500, GER40, WTI, XAGUSD (Q4). Tested Dukascopy from the
  cloud again: most requests still throttled (HTTP 429), so the download runs on the owner's PC. The downloader's decoding was
  checked on one real day each for US500 (2,061.6) and XAGUSD (37.03) and on synthetic files. Added several
  symbols, `--four`, longer back-off on 429, a Windows double-click file (`tools/get_four_markets.bat`) and
  `tools/DATA_HOWTO.md`; the CSV importer now maps Dukascopy index and oil names.
- **Learned:** nothing about edges (no results).
- **Next:** owner downloads and uploads → declare families → Truth Lab runs per market with Exness costs.

## 2026-10-31 (later) · Exness Zero costs and Dark Mimas
- **Asked:** find Exness costs from any source using a realistic sample; research the "Dark" EAs (owner downloaded
  Dark Mimas: manual + 4 .set files) and learn from them.
- **Done:** found Exness's public tick archive (ticks.ex2archive.com, Zero-account feeds 2020–2026); measured Zero
  spreads on a sample fixed before measuring (6 months × 8 markets); collected commission figures (they conflict) and
  built realistic and low-commission profiles; re-scored the 11-leg book. Researched the vendor (MQL5 pages, two live
  signals). Reconstructed both Dark Mimas settings (classic stop-and-reverse; 5-pip averaging grid) with 3 oscillator
  versions and replayed EUR/GBP M5/M15/H1 2011–25 (144 runs). Breadth-data download moved to GitHub Actions (owner on
  a phone).
- **Learned:** Zero spreads ≈ 0 (cost = commission + slippage). Book Sharpe 1.15 with swaps, 1.51 swap-free
  (2023–25 0.75 / 1.06): P5 and P1 updated. Dark Mimas: rejected, 0 of 108 tradable configurations profitable; grid
  wins 96–98% of baskets yet loses; vendor signals show 51–53% equity drawdowns (P15, P16 strengthened).
- **Decisions:** Exness Zero profile added as an extra cost profile (lab standard unchanged). Owner's 2-minute
  phone check (swap values, commission) is now the cheapest high-value action.
- **Facts vs estimates:** spreads are MEASURED (Exness ticks); commission is an ESTIMATE (high end of public figures);
  slippage is assumed; book numbers are backtests before the expected live haircut (P11).
