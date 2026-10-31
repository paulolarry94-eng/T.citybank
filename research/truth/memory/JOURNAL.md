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

## 2026-10-31 (later) · active hours for the Dark Mimas bot; what its winners look like
- **Asked:** did we try other timeframes; study the winners and their hours; give the bot active hours; what is special
  about the rare winners of high-frequency bots; keep risk at 1% per trade; only timeless alpha.
- **Done:** timing study learning on 2011–19 and checking on 2020–25 (`research/gridbot/dark_mimas_time.py`); a lab
  strategy with session windows declared before running, 1R = 2×ATR stop, exit at the next arrow, M15/H1/H4, follow or
  fade, 4 markets, Exness Zero costs (`osc_turn_sessions_v1`; new `executors.next_arrow`, 2 new tests, 17 pass).
  Hindsight noted: this family's 2011–25 behaviour had been seen before the lab run.
- **Learned:** P17 (active hours picked from a backtest do not carry forward). Big winners = trend days at session
  opens (known only afterwards); grid losses = trend days. Higher timeframes are less bad (M15 −0.068R, H1 −0.035R,
  H4 −0.025R per trade), consistent with P3, but all negative. At a negative edge the best risk per trade is zero.
- **Decisions:** the oscillator/Dark family is closed. Real progress remains costs (owner's phone check) and breadth (Q4).

## 2026-10-31 (later) · breadth data downloaded (owner on a phone; the .bat could not run)
- **Asked:** the GitHub download "is hitting errors"; how to get the data.
- **Done:** read the cancelled run's logs: Dukascopy throttled GitHub's servers too (every year failed). Switched the source
  to HistData.com (works from the cloud) plus Exness's own tick archive where HistData is wrong or missing; wrote
  `tools/histdata_m1.py`, `tools/exness_m1.py` and `tools/check_m1.py`; removed the failing workflow.
- **Learned (data facts):** HistData GRXEUR from 2020-06-15 to 2023-12-03 is a different index (3,000–4,400), so it is unusable
  there. HistData has no WTI after 2023-12-01. Both gaps were filled from Exness, with seams matching within 0.3%. Time zone verified
  against the 14:30 UTC US cash-open spike.
- **Next:** declare which families to test on US500, GER40, WTI, XAGUSD before any run (Q4).

## 2026-10-31 (evening) · "reason over everything to find gold"
- **Asked:** use everything learned to find the real edge.
- **Done:** fixed in advance, then ran: trend family on US500/GER40/WTI/XAGUSD (64 configurations); RSI(2) on US500/GER40
  (4); the same RSI(2) on 3 new indices NAS100/UK100/JP225 (4; HistData data added and checked); WTI trend alone, a market
  picked after results (hindsight, called out; 64). New executor `exit_when` + test (18 pass). Wrote the synthesis at the top
  of research/CONCLUSION.md.
- **Learned:** commodities and JPY trend, while equity indices and EUR mean-revert (P6). CFD financing eats single-market
  index and commodity trend (P12). The hindsight oil pick failed 2023–25 (P10). Index RSI(2) has a small raw edge that costs
  remove (Q5 answered). No new leg.
- **Decisions:** the gold is the existing book at measured Exness costs. The levers are the swap-free check, live proof,
  2–3% risk after proof, and prop capital (Q7). Pattern and market hunting on CFDs has diminishing returns.
- **Facts vs estimates:** costs for the new markets are the lab's conservative estimates (commissions unknown).

## 2026-10-31 (night) · the owner's 4-leg engulfing SOP ("it's an edge")
- **Asked:** study 12 case-study documents deeply; test all windows, swing sizes 3-5, whole-candle engulfing, stop 3.5 pips
  beyond Leg 4, retest within N candles, breakeven on/off; also gold daily; "train your eyes to see it reliably".
- **Done:** coded the SOP and calibrated the detector on the owner's own cases until it reproduced them: 6 exact matches,
  owner-rejected cases not flagged (`research/sop/parity_cases.py`). Several documents carry the screenshot date, not the trade
  date; the real dates were found by price. Lab additions: real-spread limit fills (`FILL_SPREAD`; before, a buy limit needed the
  whole all-in cost to fill, which misses touch-and-go fills); `executors.bracket` with breakeven; vectorised detector (80x
  faster); 20 tests pass. Ran 756 FX and 72 gold configurations through the lab, then February–October 2026 Exness data
  (untouched) as the final check.
- **Learned:** rejected everywhere (P14 evidence). Before costs it is slightly negative; costs add 0.10–0.14R per trade (small
  stops). Breakeven helps a little in 2011–22, then hurts in 2026 (P4). New P18: case studies select winners.
- **Facts vs estimates:** commission is the high-end public estimate; FXCM (owner's charts) vs Exness prices differ by ~0.1–0.5 pip.

## 2026-10-31 (night, later) · "get the conditions that made it win, then test in and out of sample"
- **Done:** every SOP setup on EUR/GBP M5/M15/M30 2011-2025 plus Feb-Oct 2026 (23,000+ filled), each simulated alone with the
  lab's fills and exits; 19 features known at entry (hour, day, engulfing types, entry %, leg geometry, stop size, cost share,
  volatility, H4 trend, EMA slope). Learned on 2011-19 only: terciles and categories (56 conditions), then the best pair
  (109 conditions tried), kept only if positive in both halves. Method committed before running.
- **Learned:** 0 of 56 conditions positive even in 2011-19. The best pair (stop >12 pips, costs <12% of R) lost -0.045R in the
  years it was picked from; later -0.08R, +0.12R (2023-25, 257 trades), -0.32R (Feb-Oct 2026). All setups lose -0.15 to
  -0.18R in every period at a 28% win rate. Nothing known at entry separates the winners: P18 evidence. No lab run (the rule
  failed its own keep criterion).
- **Decisions:** the SOP family is closed. The detector stays as a journaling tool if the owner wants it.

## 2026-10-31 (night, last) · "they're not setups, just probability: how do we increase our probability?"
- **Done:** measured on the book's own trades how costs, breadth and time change the share of profitable fortnights, months,
  quarters and years (`research/probability/odds.py`).
- **Learned:** P19. Costs: fortnights 54% -> 59%, years 87% -> 100% (lab -> Exness swap-free). Breadth: one leg 26% of fortnights,
  the book 54-59%. Time: ~250-430 trades for a 90% chance of being up. About 4 fortnights in 10 lose even in the best case.
- **Decisions:** payouts should come from a buffer above the high-water mark, not every fortnight (to discuss with the owner).
