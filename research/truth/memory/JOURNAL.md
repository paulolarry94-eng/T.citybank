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

## 2026-10-31 (late night) · "what do the backtest and a professional report say about our champion? the one that quiets the doubt"
- **Asked:** a professional report on the champion (the 11-leg book), with perspective.
- **Done:** regenerated all 11 legs with their original code on 2011–2026 data (2026 = Exness Zero ticks, untouched); entry
  parity with the stored trades 100% on 10 legs, 96% on the gold EMA leg. Scored January–October 2026 with the frozen weights
  (`research/champion/regen_2026.py`), built a tearsheet (`tearsheet.py`) and the report's data (`dashboard_data.py`), and
  published the dashboard https://claude.ai/artifact/BohhgY8e3XiUhstZdVSTVg. Perspective checks fixed before running: share of
  backtest 10-month stretches as bad as 2026 under the full edge and under a 30% / 50% weaker edge; per-trade z-test.
- **Bug found and fixed (P20):** every daily P&L series re-indexed to business days dropped trades that closed at the Sunday-night
  open (228 days, +28% of the backtest's P&L; they are mostly Friday survivors). Fixed in `exness/rescore_book.py`,
  `truth/protocol.py` (portfolio-fit only; tiers and verdicts are set before it), `multiasset/combine.py`,
  `champion/regen_2026.py`; regression test added (21 pass). Re-ran rescore_book (+ risk scaling now reproducible), odds,
  combine, tearsheet. `prop/ftmo_sim.py` was already correct (searchsorted maps Sunday to Monday).
- **Learned (with evidence, `research/results/champion/`):**
  - Backtest 2011–25, Exness + swaps, 1% risk: Sharpe 1.36 (was 1.15), 10.7%/yr, max DD 9.7%, 14/15 years; swap-free 1.74;
    stress (costs ×1.5, swaps ×2) 0.76; 2023–25 0.95.
  - Untouched Jan–Oct 2026: −1.36% with swaps (first measured −2.34% with the bug), +0.78% swap-free, max DD 5.3%, 333 trades,
    +0.022R/trade vs +0.078R (z −0.81, p 0.21; weighted p 0.07). At or below 4.1% of backtest 10-month stretches (median
    +8.2%); 13.3% if the edge is 30% weaker, 22.9% if 50% weaker. P11 gets its first measurement.
  - Losses came from heavily weighted, rarely trading legs (gold S1 −3.98R, JPY Donchian55 −5.54R, JPY RSI2 −2.03R) and GBPJPY
    (−9.58R); the JPY volatility breakout (+12.4R) and gold Donchian20 (+9.79R) won. Raised as Q9; 2026 cannot decide it.
- **Decisions:** no rule or weight changes from 2026 (hindsight). Keep 1% risk; confirm swap-free (Q1); forward-test; judge at
  about 430 trades. Every figure built from a daily series before today is understated; corrected in CLAUDE.md, CONCLUSION.md,
  EXNESS_COSTS.md, P5, P19, Q1, the ledger; `multiasset/PROJECT.md` tables flagged, not regenerated.
- **Facts vs estimates:** commission is the high-end public estimate; swap-free status unconfirmed; 2026 prices are Exness ticks,
  the backtest is other vendors (seam). The two public Sharpe ranges on the dashboard (stocks, CTA index) are recalled, not looked up.
- **Next:** re-score each new 2026/2027 month with `champion/regen_2026.py`; Q9 weighting study on 2011–22 walk-forward only;
  owner's swap-free and commission check.

## 2026-10-31 (last) · the owner's "Leg 34" setup on gold, 5-minute chart
- **Asked:** "the 3-4 strategy is profitable on 5m a lot of times, especially when the 10 EMA slope supports the direction";
  explain it and ask questions. Owner's answers: name = Leg 34; zone = the whole eaten candle; small heads that do not break
  the 10 EMA with an engulfing don't count; limit valid 8 hours; compare 3R and 4R, try trailing; EMA slope read like a
  line chart. Stop buffer on gold and trading hours not answered (both tested two ways, declared before results).
- **Done:** dated the owner's screenshot by price (30 Oct 2026, 01:20 UTC candle); parity: the detector finds the owner's
  tops and reproduces 2 of 3 checkable trades (same fill times), entries at 30% of the eaten candle (the EUR 70% rule
  missed both), one trade missed by ~$1 (owner's entry lower than any rule here). Pre-registered `leg34_gold_v1`
  (144 configs) and the 2026 check before running; new `executors.managed` (fixed 3R/4R, breakeven, R-ladder, EMA trail;
  24 tests pass). Lab: rejected, 0/144 positive in 2011-19 (best -0.12R). Diagnostics `research/sop/leg34_diag.py`.
- **Learned:** no raw edge (+0.00 to +0.02R before costs); costs are 10-17% of the small 5-minute stops. Half the trades
  reach +1R and 23% reach +3R, so "in profit before the loss" is normal (P16). Trailing and breakeven do not help. The EMA
  slope does not sort winners. October 2026 (screenshot month) was mildly positive, Jan-Sep 2026 lost (P18).
- **Decisions:** Leg 34 / the 4-leg SOP family is closed on EUR, GBP and gold at 5-30 min and gold H4/D1. No re-test with
  rules changed after these results (that would need a new name and a reason that is not these results).
- **Facts vs estimates:** commission is the high-end public estimate; owner's prices are OANDA, ours Exness (differ ~$0.1-0.3).

## 2026-10-31 (closing) · "one with an edge exists: what is the miracle, even risk-physics-wise? we are not done"
- **Done:** a synthesis, no new tests. Kelly arithmetic on the book (yearly volatility 7.7% at 1% risk): growth-optimal risk
  per trade is ~10% at a live Sharpe of 0.8 and ~18% at 1.36, so 1% is about a tenth of Kelly. 60-120% a year needs a TRUE
  Sharpe of ~1.2-1.5 at half Kelly (ideal model: 12% chance of a 50% drawdown) or ~1.5 at quarter Kelly. Breadth ceiling:
  book Sharpe ~ leg Sharpe x sqrt(N / (1 + (N-1) x correlation)), capped at leg Sharpe / sqrt(correlation).
- **Decisions:** logged Q10-Q14 (flow calendars with a payer, gold's record-low relative cost, portfolio vol targeting,
  evidence-based bet sizing, CFTC positioning). Nothing promoted to a principle (no new evidence).
- **Facts vs estimates:** the Kelly figures assume normal returns and a known Sharpe; real tails and estimation error make
  the safe fraction smaller.

## 2026-11-01 · "study the 1% of the 1% winners, run them through all markets: build a 5-min hunter"
- **Done:** two pre-registered studies (`research/hunter5m/`). Step 1: every Leg 34 setup on M5 in 11 markets (~194,000 filled,
  each simulated alone, lab fills and exits, Exness costs for 4 markets, lab estimates for 7), 22 features known at entry;
  anatomy of the top 10% / 1% / 0.1% runners on gold 2011-19; rule search (133 conditions); frozen rule tested on gold 2020-25,
  10 other markets and Jan-Sep 2026. Step 2: a "runner profile" score from the top-1% anatomy, declared before its
  out-of-sample numbers.
- **Learned (P21):** before costs Leg 34 is about zero everywhere; top-10% runners look like all trades; top-1% lean to quiet
  conditions and a strong 4-hour push; both rules lose out of sample (step 1: 9 of 10 markets negative; step 2 worse than taking
  every setup, even in-sample). A one-off weekend gap held under the 24-hour time stop cost one 2026 trade -13.7R (real risk).
- **Decisions:** stop mining shapes at M5; logged Q15 (a 5-min hunter must hunt flows with a payer: Tokyo fix, US close
  auction, data releases) and the index-cost check. The 28 MB setups file is regenerable and not committed.
- **Facts vs estimates:** costs for XAGUSD, WTI and the five indices are lab estimates (likely high for indices).

## 2026-11-01 (later) · "check all timeframes, all markets, Asia/London/New York, and the configs tried before"
- **Done:** mined every past Truth Lab grid for configurations positive in 2011-19 and 2020-22 (lead: sop_4leg_v1 EUR/GBP M30
  16-20 UTC, n 17-82). Pre-registered pocket scan (`research/hunter5m/pocket_scan.py`): Leg 34 on 11 markets x M5, M10, M15, M30,
  M45, H1 x Asia/London/New York x 2 exits = 396 cells; selection on 2011-22 only; hint tested on the 9 other markets.
- **Learned:** 1 cell passed discovery (fewer than luck predicts) and failed confirmation; 0 survivors; no cell positive in all
  three periods; before costs the setup is slightly negative at every timeframe and session and positive cells do not persist
  (34% vs 32%). The M30 New-York pocket was luck (negative on 9 of 9 other markets). Evidence added to P3, P17, P21.
- **Owner's US500 spec:** swap long -142.4 points, short 0; margin 0.25%; commission not in the Specification (Q1 note).
- **Decisions:** the 4-leg / Leg 34 family is closed on every market, timeframe and session we hold. Next: flows with a payer
  (Q10/Q15, Tokyo fix first), the book's forward test and sizing (Q12/Q13).

## 2026-11-01 (afternoon) · "what are the results of the 5-min hunter on Japan?" -> the Tokyo fix
- **Asked:** results on Japan. The 5-min Leg 34 hunter on USDJPY and JP225 was already scanned: negative in every
  timeframe x session cell 2011-22 (USDJPY M30 +0.20R in 2026 on 171 trades, but -0.15 to -0.23R in 2011-19).
- **Done:** built the Tokyo-fix flow test (Q10/Q15) with rules from published research, committed before any result:
  `truth/strategies/tokyo_fix_gotobi_v1.py` (3 configs, gotobi days, Japanese holidays via the `holidays` package, now in
  requirements/bootstrap) and the companion pip study `research/flows/tokyo_fix_study.py`; measured Exness Zero spreads at
  the trade minutes (`research/flows/tokyo_fix_spreads.py`).
- **Learned:** Tier B forward-test candidate (buy 23:00 -> sell 00:55 UTC on gotobi days): 2011-19 +0.041R (t 1.88), 2020-22
  +0.064R, 2023-25 +0.052R (t 1.45, PF 1.28, one logged look; the companion study read the same period with the same frozen
  rules), stress +0.025R, deflated Sharpe 0.97, Jan-Sep 2026 +3.9 pips/trade after cost. Correlation with the book +0.03;
  book Sharpe 1.21 -> 1.38 (2017 on 1.03 -> 1.39). New principle P22. Spread at 23:00 UTC usually ~0 but 4.8 pips in Jan 2024.
- **Decisions:** add as a forward-test candidate (leg 12 of the book); test a spread-aware entry under a new name before live.
- **Facts vs estimates:** commission is the high-end estimate; Japanese holidays from the `holidays` package; Oct 2026 had 6 gotobi
  trades (-8.5 pips) — too few to judge.

## 2026-11-01 (evening) · "does all this help?" (owner shared AI-written advice on combined edges, ghost stops, ML, repos)
- **Done:** checked each claim against our evidence; web-searched the three MQL5 GitHub repos it named (not found); one quick
  check on our data: gold Leg 34 2011-19, blocking the lowest-25% volatility moves the win rate 21.6% -> 21.9%, mean R -0.177 ->
  -0.168 after costs, before costs -0.018 vs -0.021 (no edge either way).
- **Verdict:** already doing (3-way time split, real costs and spreads, delay stress, Python before MQL5); useful to test
  (spread guard for the Tokyo fix, correlation-aware sizing Q9/Q12, meta-labeling on legs with an edge = new Q16); wrong or
  risky (60% win rate as the goal (P16), filters that multiply a zero edge (P21), ghost stops without a hard stop, a
  volatility percentile taken over all 15 years = look-ahead).

## 2026-11-01 (night) · "3 ... the best ideas" (test the best ideas from the awesome-systematic-trading list)
- **Done:** read the list's free strategy table (PyPI copy of the README, ~70 strategies); picked those that fit our markets and
  have a payer: turn of the month and option-expiry week (5 index CFDs), oil predicts equities (paper Sharpe 0.31, 0.45, 0.60).
  Skipped: FX/dollar carry (needs rate history; a swap-free account removes carry), bitcoin overnight (no data), stock factors.
  Pre-registered lab strategies; v1 failed the lab's look-ahead check (month-end found from later bars), v2 uses the calendar
  (new names; the companion study had already seen 2011-25, disclosed). Drift-controlled study; futures check of oil 1990-2024.
- **Learned:** all three rejected. TOM and OPEX: no effect beyond drift; negative after costs even before financing (TOM).
  Oil -> equity: +0.42%/month before financing on CFDs (2011-19) but -0.74% after; on futures +1.15%/month in 2000-2010 (t 1.15)
  and nothing since 2011: faded after the 2008 paper (P11 evidence). CFD financing (P12 evidence). New Q17 (index swaps in points).
- **Decisions:** no list strategy added. The flow that works for us (Tokyo fix) came from a payer we identified ourselves.
- **Facts vs estimates:** index costs and swaps are lab estimates; futures returns exclude commissions (tiny monthly).

## 2026-11-01 (late night) · "before we hunt more ... funnel all their strategies" (trustdan, sofus-nl, awesome-systematic-trading)
- **Asked:** treat every strategy in three public collections as a fresh idea and run it through our universe and protocol
  before hunting more payer flows.
- **Done:** inventory of all 132 (`research/repofunnel/INVENTORY.csv`) and pre-registration committed before any result
  (`PREREG.md`); a daily engine that replays Pine/prose rules on M1 data (`d1.py`, `trustdan.py`, `sofus.py`, `awesome_cfd.py`;
  11 tests incl. no-peeking on truncated data); four lab files (48 + 36 + 2 + 1 configurations on 11 CFDs / 5 index CFDs) and a
  futures funnel for 16 cross-asset rules. Fixed a lab bug: the deflated Sharpe crashed for a one-configuration grid (now the
  probabilistic Sharpe with benchmark 0). Report: `research/results/repofunnel/REPORT.md`.
- **Learned:** no CFD survivor (0 of 87 configurations; payday passed 2011-19 then failed 2020-22, stress and its 2023-25 look).
  trustdan's ranking (from US stocks without costs or holdout) inverts on our markets: their Alt10 is -0.62R/trade. Swaps decide
  trend: Turtle core -0.38R with swaps vs +0.20R swap-free; the 10-year-high trend +0.006R vs +0.25R with 10 of 11 markets
  positive (P5 evidence, new Q18). Futures: time-series momentum strong (t 3.9, deflated Sharpe 0.88) = our known futures trend
  family; commodity skewness the one new futures candidate (t 2.2, deflated 0.28); FX carry, asset-class momentum, paired
  switching pass only weakly. The first futures run had a look-ahead through markets closing at different hours: country pairs
  (Sharpe +1.4) and WTI-Brent (+2 to +3) vanished with a one-day lag (new P23; v2 is the version of record, PREREG E2).
- **Decisions:** nothing added to the book. Index financing as a rate (Q17) and the owner's swap-free answer (Q1) now gate any
  further trend work on CFDs; one pre-registered re-test of the 10-year-high trend afterwards (Q18). Futures route (Q6) gains
  commodity skewness as a sleeve to test.
- **Facts vs estimates:** CFD costs and index swaps are lab estimates (index swaps in points overcharge early years, Q17);
  futures costs from pysystemtrade's spread table; futures data end 2024-03-28 and exclude interest on cash; for six futures
  strategies the 2023-24 look was first taken in the flawed v1 run (disclosed). Configurations tried this session: 103.
- **Next:** owner: confirm swap-free status. Then Q17 (rate-based index financing) and Q18; back to payer flows (Q10/Q15).

## 2026-11-01 (late night, 2) · "can we have 20-30 payer flows in a bot? ... which would you choose" + owner's 24-flow list
- **Answered plainly before building:** 20-30 independent payer-flow edges are not available on our 11 markets; breadth math
  is right (s x sqrt(N)) but the limit is independent edges. Realistic bot: 11-leg book + Tokyo fix + 2-4 new flows (~15-20 legs,
  6-9 truly independent); ~12-18%/yr at 1% risk, 60%/yr only with 3-4x the risk and 30-40% drawdowns, 120% unsupported.
  VPS + triple state: yes as a circuit breaker (hard broker stops, restart reconciliation, spread guard, heartbeat), not as a
  sizing booster (P8).
- **Owner's 24-flow list triaged** (new Q19): 4 rows to test now (London month-end fix, last 30 min into the US close,
  conditional month/quarter-end rebalancing), 7 later, 6 not payer flows, 6 no data or too rare, 1 already tested.
- **Decisions:** no MQL5 for untested flows; next test = London 4 pm month-end fix, rules fixed before loading data, on the
  owner's go. Swap-free status (Q1) still open.

## 2026-11-01 (late night, 3) · owner directive: SEESARE P26 x 24-payer-flow router, MQL5 object blueprint
- **Asked:** the object design of an MQL5 master router (time-zone sync, 360-event ledger, $1,000 virtual sizing, HMAC
  Telegram attestation) built on the owner's SEESARE P26 documents (parts 1-2, 177 pages, read in full where relevant).
- **Done:** `mt5/SEESARE_ROUTER_BLUEPRINT.md` (design only; no MQL5 written or compiled). Recomputed the SEESARE numbers.
- **Learned (arithmetic, reproducible from the SEESARE formulas):** planned-risk claims check out (20 losses 0.221%, 100 losses
  0.244%), but at $1,000 most levels are below the 0.01-lot minimum (deadlock after one loss), time-expiry wins can break the
  envelope (16.2%) unless classified as SEESARE manual resolutions (0.25%), the top level caps returns at a few % a year, the
  multiplier formula and table disagree, and the public cannot verify a license-keyed HMAC. Recorded as Q20.
- **Decisions:** time-expiry exits = MANUAL resolutions; Shadow Resolution proposed for infeasible levels; keyless public hash
  chain + SEESARE HMAC; WebRequest in a separate MQL5 service; per-cycle in-sample optimisation (directive Part V) not used.
- **Next:** owner's five decisions (blueprint section 13); then build order step 1 (clock and calendars with test vectors).

## 2026-11-01 (late night, 4) · owner: "deliver the concrete, production-ready code modules for Phase 1"
- **Asked:** MQL5 code for (1) the dynamic clock and timing matrix (server time sync, London/New York/Tokyo windows in UTC,
  DST handoffs, spread-aware entry filter) and (2) the cycle ledger and outbox writer (10-event cycles, keyless SHA-256 chain,
  disk persistence that survives restarts, numbered outbox files for a separate relay service).
- **Done:** `mt5/Seesare/` (uncompiled source): Text, Clock (CSeesareDst, CSeesareClock, CSeesareTimingMatrix), SpreadGate,
  Sha256, StateStore, Outbox, CycleLedger (ladder, cycles, chain, anchors, envelope guard, restart checks), and
  `Scripts/SeesarePhase1SelfTest.mq5` (~290 checks). Python twin and public verifier `tools/seesare_verify.py`; tests
  `research/truth/tests/test_seesare_phase1.py` (32, all pass): DST rules equal the IANA database for every hour 2011-2035 in
  4 venues both ways; tamper, deletion, swap, truncation and ladder/plan forgeries are caught; the MQL5 source carries the
  twin's tables and the self-test's vectors are the twin's (test fails on drift).
- **Learned (verified here):** my earlier claim (time exits = manual holds the envelope, 0.25%) was incomplete: 29.55% and
  14.96% paths exist; a pre-trade drawdown + risk check holds 3.6% under any sequence (P24, ledger entry
  seesare_ladder_envelope_v1). SEESARE's planned deltas at levels 9, 13, 15 sit on exact 4-decimal rounding ties ($0.03135),
  so the ledger rounds multiplier and plan down by a fixed rule to keep MQL5 and Python text identical.
- **Decisions:** time-exit policy is an input, default = owner's mandate (MANUAL), option losing-time-exit = NEGATIVE
  (recommended); shadow events are written to disk (RAM-only would lose the ladder on a VPS restart); cycles count REAL events
  only; tuned ladders are declared in the genesis line and cannot change inside a lifecycle.
- **Facts vs estimates:** nothing compiled; MQL5 file and CryptEncode behaviour taken from the documentation; RoboForex server
  scheme unknown (the self-test measures it; EU vs US DST rules only distinguishable in March and late October).
- **Next:** owner compiles and runs the self-test, sends compiler output and the summary line; owner picks the time-exit
  policy; then Phase 2 (calendar, exposure calculator, gateway, Tokyo fix in SHADOW, relay service).

## 2026-11-01 (late night, 5) · owner: "Phase 2 execution core": hardcode losing time exits = negative, 3 high-convexity flow modules
- **Asked:** (1) hardcode losing time exits as negative; (2) only flows with verified 5:1-10:1 payoffs, multiplier forced up
  (+35-50% at L0); (3) independent legs; MQL5 for Tokyo gotobi fix, US close imbalance (MOC), London 4 pm WMR fix reversion.
- **Corrected premises:** 0.19% was one bleed pattern, not a worst case (the guaranteed planned worst case is the guard's
  3.6%); "un-blowupable" excludes gaps through stops.
- **Tested (Truth Lab, rules fixed and committed before results):** owner's London rule wmr_fix_reversion_v1 (fade 15:30-15:55
  drift, 15:55 -> 16:05, 5:1 or wide stop, all days or month-ends): rejected, 0/4, -0.017R (t -4.7) to -0.12R. Documented timing
  wmr_fix_postfade_v1 (16:00 -> 17:00): rejected; best month-ends +0.046R dev, 2023-25 +0.018R t 0.5. Configurations: 8.
  Prior (Hunt 2) reproduced: fade gross 0.38-0.45 costs on all days, 1.4-1.9 on month-ends (t 1.2-1.6).
- **Studied:** Tokyo fix payoff about 1:1; a 7:1 target is reached on 0.1-3.3% of mornings (ledger entry). US close imbalance
  data does not exist in MT5 or in our data: untested.
- **Built (uncompiled):** ledger enforces the time-exit rule (twin + verifier + vectors, 34 Phase 1 tests); Calendar.mqh
  (JP holidays 2024-35), FlowModule interface, 3 modules with evidence-gated status, Exposure (shadow lot), PaperBook, router EA
  (no order gateway), Phase 2 self-test; twin tools/seesare_flows.py, 14 tests. All 48 twin tests pass.
- **Decisions:** declared ratios come from measured payoffs (Tokyo 1.04), not forced; REJECTED/UNTESTED modules run on paper only;
  no real-order code until the self-tests compile and a module passes its forward test.
- **Next:** owner compiles and runs both self-tests and the router (Tokyo PAPER) on a RoboForex demo; owner chooses SEESARE at
  $1,000 (SHADOW only) vs a larger baseline or a cent account; US close needs an imbalance feed or the momentum-into-the-close
  variant (Q19, needs the lab's 20:30 UTC entry block handled for winter).

## 2026-11-01 (late night, 6) · owner: "Cycle-centric axis": cent account, +2% per cycle, era cycle study, cent sizer + Telegram outbox
- **Asked:** (Part I) a RoboForex ProCent cent account ($1,000 = 100,000 cent units) so all 16 levels place real micro-orders
  inside the 3.6% envelope; multi-leg cycles giving +2% or more per cycle (law of large numbers). (Part II) replay 2011-2025 by
  era, 5-10 cycle sequences, show the drawdown stays in the box. (Code) cent-account position sizer; Telegram outbox formatter
  with the keyless SHA-256 chain, real deal tickets and [Cycle X/36, Step Y/10], written to a folder for the relay.
- **Corrected premises:** a cent account lowers the smallest real trade 100x but not to zero: for the Tokyo fix (0.3% stop,
  about $3.00 per cent lot) levels L0-L3 are real at its measured ratio 1.04 and L0-L9 at 3.5; the rest stay SHADOW. +2% per
  10-event cycle is $2 per event = +1.46R at L0 (multiplier 1.0); the Tokyo fix earns about +0.05R. The law of large numbers makes
  results converge to the edge per trade; it does not make the edge bigger. ProCent has no index CFDs, so the US close module
  cannot run there.
- **Studied (design committed before results, research/seesare/cycle_study.py):** Tokyo fix through the real ledger rules on a
  cent account, 1,071 gotobi mornings, 1.9-pip spread (stress 2.85), 3 variants, 6 runs in all. Hardcoded rule: L15 from event 13,
  98.8% of events at L15, 6 real trades, -$0.04, 0 cycles. Target at 1.04: same 6 real. Time exits MANUAL: 25 real, 2 cycles
  (+0.003%, +0.116%), then L15. Max drawdown 0.005-0.016%: inside the box because real trading stopped (new P25). Descriptive
  study of sizing mechanics on an already-looked strategy; no rule was chosen from it, 2023-25 not used to select anything.
- **Built (uncompiled):** Exposure.mqh cent support (UnitsPerUsd, PlanAtLevel, LowestFeasibleLevel, currency conversion in
  LossPerLot/Size), PaperBook and router pass account units (router refuses unknown currencies), Telegram.mqh (formatter),
  Outbox.mqh format 2 (text + "Record:" line + sum), DealReader.mqh (read-only: deals, net in USD, close reason -> STOP/TARGET/
  TIME/HUMAN/BROKER, closed position -> REAL event), Phase 3 self-test (generated vectors, outbox file byte-exact through its
  checksum, cent end-to-end deals -> ledger -> outbox). Twin tools/seesare_outbox.py; 22 new tests; all 70 twin tests pass.
- **Decisions:** volumes still round down, never up; an unknown account currency stops the router instead of guessing; a
  record the formatter cannot read is refused by the outbox; unknown deal reasons count as BROKER (negative).
- **Facts vs estimates:** ProCent USDJPY spread 1.9 pips and no commission from RoboForex's specifications page; minimum lot
  0.01 per most reviews (one says 0.1); cent lot = 1/100 of a standard lot per reviews; the self-test prints the real values.
  Nothing compiled.
- **Next:** owner compiles and runs the Phase 1-3 self-tests on the RoboForex ProCent terminal and sends the output; owner
  decides whether a time exit with a gain may climb the ladder (P25) before any real lifecycle; relay service not built.

## 2026-11-01 (late night, 7) · owner: "Dynamic time-exit re-calibration": ascension rule, ladder squeezing, outbox
- **Asked:** (1) a time or exhaustion exit with a net gain counts POSITIVE and climbs, a loss stays NEGATIVE, in CycleLedger.mqh
  and the twin; (2) compress the 16 level % to fit a "4:1 structural edge" (+1.40% wins vs -0.35% expirations) so an L0 win
  gives cycle momentum, envelope unbreakable under any outcome distribution; (3) finish the keyless outbox (deal tickets,
  [Cycle X/36 | Step Y/10], plain text to disk); deliver CycleLedger.mqh and SpreadGate.mqh, vectors identical to the twin.
- **Priors:** every earlier SEESARE sizing study was rejected as a guarantee (seesare_ladder_envelope_v1, cycle study); said so.
- **Corrected premises:** no tested flow has a 4:1 payoff (Tokyo fix about 1:1, 52.6% winning mornings after the ProCent spread);
  ladder weights tuned to make a backtest look good would be hindsight, so the scaled ladder was derived from the owner's own
  -0.35% spec, not from data; the 3.6% line is held by the pre-trade guard (planned losses; gaps excepted), not by the ladder.
  Part 3 was already delivered in Phase 3. SpreadGate.mqh needs no change: it works in price points, the same on cent and
  standard accounts, and the time-exit rule lives in the ledger.
- **Built (uncompiled):** CycleLedger.mqh SEESARE_TIME_GAIN_POSITIVE (build policy GAIN_POSITIVE_LOSS_NEGATIVE, genesis-declared,
  earlier-rule lifecycles refused by the build, still verifiable in Python); twin classify by policy name; sample event 8 changed
  to a zero-result time exit to keep the "manual keeps the run" path; vectors regenerated (Phase 1: 204 generated checks, Phase 3:
  87); Phase 2 self-test: 3 rule checks; router input InpLadder. Tests: 74 twin tests pass, incl. the new pump path (16.2% ladder
  only, 3.60% with the guard).
- **Studied (design committed 0e65cc8 before results):** research/seesare/cycle_study_ascension.py, 3 variants x 2 spreads = 6 runs.
  1.9 pips: D default ladder 15 real trades, 1 cycle; E owner-scaled ladder 22 real, 2 cycles; F owner-scaled + declared 4:1 191
  real, 19 cycles, cycle mean +0.021%, median -0.003%, 26% positive, max DD 0.24%. 2.85 pips: F 130 real, cycle mean -0.018%.
  Mean level 13.1-13.9 in all runs; the guard was never needed. Reporting fix after the first run: whole-period R per trade
  was divided by the trade count twice; formula corrected, no rule or input changed, re-run.
- **Learned:** ladder long-run position by win rate (exact Markov arithmetic, independent outcomes): p 0.50 level 13.5 / L0-L3
  0.2%; 0.526 13.2 / 0.4%; 0.60 11.8 / 3.6%; 0.65 9.9 / 12%; 0.70 7.1 / 30%; 0.75 4.3 / 54%; 0.80 2.3 / 76%; 0.85 1.1 / 90% (P26).
  The flow itself: +0.024R per morning at 1.9 pips (t 1.3), -0.005R at 2.85 pips, measured against the 0.3% stop.
- **Facts vs estimates:** nothing compiled; ProCent spread is the published average (real spread at 23:00 UTC unmeasured).
- **Next:** owner decides: fixed small size for the Tokyo fix (P8), a SEESARE step-size redesign (own study), or wait for a
  high-win-rate flow; owner compiles and runs the three self-tests on the RoboForex terminal.

## 2026-11-01 (late night, 8) · owner: "combine the strategy universe, reconfigure the ladder, ~3.6% drawdown, great alpha"
- **Asked:** use every strategy, not one flow; reconfigure ladder rules, figures and level count; drawdown close to 3.6% per
  lifecycle with great alpha ("since drawdown is capped the only way should be up"). Then: "so what's the results like".
- **Corrected premise:** a cap limits losses, it does not create returns; return = edge x size x trades.
- **Priors:** sizing states were rejected before (P8, GREEN/AMBER/RED); every SEESARE ladder study rejected (P24-P26). Said so.
- **Studied (design committed 18aa444 before results):** research/seesare/universe_cap_study.py. Universes: book (U1) and book +
  Tokyo fix + EURUSD reversal (U2). Rules: fixed, fixed + guard, drawdown-keyed 16-level ladder, SEESARE outcome ladder; 6
  settings each; 48 configurations. Lifecycle = 360 signals (about 10 months for U1, 8.5 for U2). Settings chosen on 2011-22
  (run alone), one look 2023-25 (run alone), book's untouched Jan-Oct 2026. A loader bug (wrong time unit for the two lab legs)
  was caught by a smoke test before the design commit.
- **Results (Exness Zero + swaps; dev / 2023-25 / 2026):** U1 guard 0.75%: +7.18 / +6.83%/yr / -2.34% (halted after ~5 months);
  U1 drawdown ladder m 0.3: +7.04 / +5.99 / -1.52%; U1 fixed 0.5%: +5.77 / +3.41 (worst lifecycle 4.71%, cap broken) / -0.60%;
  U1 SEESARE 3%: +0.29 / -0.11 / +2.09%; U2 guard +9.51 / +4.27; U2 ladder +7.75 / +3.30; U2 fixed 0.25% +3.74 / +2.47; U2
  SEESARE about 0. Swap-free adds about 1-1.5%/yr. Across lifecycles drawdowns reach 4.3-6.5%.
- **Learned:** P27.
- **Facts vs estimates:** backtest only; live expected 30-50% weaker (P11); ProCent costs unmeasured (lab costs as proxy).
- **Next:** owner decides on the drawdown-keyed ladder for CycleLedger.mqh and on whether this return is worth running.
