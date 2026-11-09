# OPEN QUESTIONS — the queue (highest value first)

Move a question to "Answered" with a link to its evidence once it is resolved. New ideas from the owner go
here first, with FAMILY tags, so priors can be checked before testing.

### Q1 What are the real Exness Zero costs and is the account swap-free?
PARTLY ANSWERED (2026-10-31, `research/exness/EXNESS_COSTS.md`): Zero spreads measured from Exness's own tick archive
are about 0 on XAU/EUR/GBP/JPY, so cost = commission + slippage. With high-end published commission the book re-scores
to Sharpe 1.36 with swaps and 1.74 swap-free (corrected 2026-10-31 from 1.15 / 1.51, Sunday-exit bug; profile:
`research/truth/costs_exness_zero.json`). Still open, owner
check on a phone (2 minutes): (a) MT5 app → symbol Specification → Swap long/short = 0? (swap-free status, worth
+0.38 Sharpe); (b) commission shown in History after a 0.01-lot EURUSD and XAUUSD round trip.

Owner's MT5 Specification (2026-11-01, symbol assumed US500): contract size 1, margin 0.25% (1:400), swap long -142.4
points and short 0 per night (Friday x3), trade sessions Sun 22:00-24:00, Mon-Thu 00:00-21:00 and 22:00-24:00, Fri to 20:55.
Commission is not shown in the Specification: it appears in History after a trade (open/close 0.03 lot on demo).

Broker change (owner, 2026-11-01): the owner now plans RoboForex Prime (raw spread from 0, commission, leverage 1:300).
This does not answer Q1 (Q1 is the Exness account). RoboForex facts from its own pages: Prime commission "10 / mio" (read as
10 USD per million USD per side, about 1 USD per lot per side; reviews agree); average Prime spreads EURUSD 0.1, USDJPY 0.2 pip;
published Prime swaps EURUSD long -0.98 / short +0.19, USDJPY long +0.38 / short -2.1 pips per night. Swap-free is NOT settled:
the Prime account page still lists "Swap-Free account: No", while RoboForex's March 2026 release says new accounts are
swap-free on currencies and metals with no extra charge (one review says triple-swap days carry a tripled fee). Cost profile:
research/truth/costs_roboforex_prime.json (published figures, not measured). Owner check, 2 minutes: on the Prime account,
MT5 symbol Specification -> Swap long/short = 0? and the commission shown in History after a 0.01-lot EURUSD round trip.

### Q2 Does the TimelessCity EA trade like the research?
Compile v2.42, Strategy Tester 2023–2025 (real ticks), compare with
`research/results/northstar/parity/timelesscity/*.csv` using `tools/parity_check.py`.

### Q3 How much weaker is live than the backtest? (tests P11)
Measure on 3–6 months of demo with `research/northstar/weekly.py`.
FIRST EVIDENCE (2026-10-31, untouched data, not live fills): the 11-leg book on January–October 2026 Exness Zero prices made
+0.022R per trade vs +0.078R backtested, −1.36% at 1% risk (+0.78% swap-free), at or below 4% of backtest 10-month stretches;
13% / 23% if the live edge is 30% / 50% weaker. Consistent with P11, too short to tell a smaller edge from none (~430 trades
needed). Dashboard: https://claude.ai/artifact/BohhgY8e3XiUhstZdVSTVg; data `research/results/champion/`. Keep scoring it
month by month with `research/champion/regen_2026.py` as new Exness months arrive (no rule or weight changes).

### Q4 Breadth: do the book's families work on new markets?
Needs M1 data for ~27 markets (`tools/dukascopy_m1.py --all 2011 2025` on a home PC; Dukascopy throttles
cloud IPs). Pre-register markets and families before running through the Truth Lab.
**Declared 2026-10-31, before any data was seen: US500, GER40, WTI, XAGUSD** (owner asked for 4 markets).
Reasons: stocks (US500; also allows Q5), European stocks in London hours (GER40), energy (WTI), and the
direct test of whether the gold families transfer (XAGUSD). GER40 and US500 move together, and so do silver and
gold, so these add less independence than four unrelated markets would. Not chosen: BTCUSD (Dukascopy history
starts later than 2011) and natural gas (high costs). Families must be declared before the first run. To check
when the data arrives: start years (Dukascopy returned "not found" for WTI on 2011-06-07), oil contract-roll
price jumps, and costs and swaps from the Exness export (Q1). How-to: `tools/DATA_HOWTO.md`.
Data source changed (2026-10-31, before any test): Dukascopy throttled the cloud and GitHub Actions, so the four markets
come from HistData.com (`tools/histdata_m1.py`, bid M1, EST→UTC). Markets unchanged.
DATA READY (2026-10-31), checked with `tools/check_m1.py`: US500 2011–25 HistData; GER40 HistData 2011 → 2020-01-29, then
Exness DE30 Zero (HistData's GRXEUR is a different index from 2020-06-15 to 2023-12-03, so it was replaced); WTI HistData 2011
→ 2023-12-01, then Exness USOIL Zero; XAGUSD HistData 2011–25 (2025 surge to ~$64–84 confirmed against Exness). Seams
match within 0.3%. No monthly roll-gap pattern in WTI; the April 2020 negative-oil episode is in the data. Next: declare the
families (book families: trend, dip reversion) before the first run; costs for these markets are still estimates.
CLOCK FIX (2026-11-02): HistData's stamps were one hour late in daylight-saving periods (New York rules 2011-2018, UK rules
from 2019), although documented as EST without daylight saving. All HistData files (EURGBP, XAGUSD, US500, NAS100, UK100,
JP225, GER40 to 2020-01-29, WTI to 2023-12-01) corrected in place; tools/histdata_m1.py converts correctly for new downloads.
Evidence and method: tools/histdata_clock.py, research/results/data/histdata_clock.json, P29. Intraday studies before the fix
are listed for a re-run in Q26.

### Q5 Equity-index RSI(2) mean reversion (watch-list) — TESTED 2026-10-31, see Answered
+0.41 Sharpe on stock indices in the daily futures data (`research/multiasset/mr_breadth.py`). Needs index
data and a pre-registered Truth Lab run.

### Q6 Futures route for trend + carry
Works only on real futures (P12). Owner decision: an MT5 futures broker (CME micros) or IBKR.
Update (2026-11-01, repo funnel v2): on the same futures data, time-series momentum passes every period (Sharpe 1.12 / 0.61 /
0.98, t 3.9, deflated Sharpe 0.88) and commodity skewness is the one new candidate with every period positive (0.32 / 0.67 /
0.88, t 2.2, deflated Sharpe 0.28 after 16 tries). FX carry, asset-class momentum and paired switching pass only weakly.
A futures account would carry trend + carry (+ skewness to test as a sleeve). research/results/repofunnel/REPORT.md.

### Q7 Prop accounts (FTMO-style): which per-phase risk and which guard maximise pass x payout?
Replay (`research/prop/ftmo_sim.py`) says the book passes both phases in 33-54% of 12-month windows at 1-1.5% risk
but slowly (median 6-8 months for +10%). To test: a near-barrier risk brake (rational in prop accounts because
-10% ends the account, unlike P8's personal-account finding), phase-specific risk, an open-risk cap that makes a
5% daily breach structurally impossible, and FTMO's real costs/swaps on a Swing account. FAMILY: prop, risk, sizing.

### Q8 EUR/USD daily close-beyond reversal (owner's spec): worth a small forward test?
Tier B (`research/results/truth/eurusd_close_beyond_reversal_v1/REPORT.md`): +0.04R per trade, Sharpe 0.49 and falling
(0.59 → 0.48 → 0.23), +0.9% a year at 1% risk; weakens the book after 2017 (0.84 → 0.76). Watch-list only unless real
Exness costs (Q1) or a 2026 forward test show it stronger. FAMILY: reversal, daily, stop-entry, eurusd.

### Q9 Are inverse-volatility leg weights right for the book?
Raised by the 2026 test: the weights (inverse monthly volatility, 2011–19) put the most risk on legs that trade rarely
(JPY RSI2 1.00, GBP weekly sweep 0.93, gold S1 0.63), and those lost in 2026 while the busy, low-weight legs won; equal
weights would have done better in 2026. Choosing weights from 2026 is hindsight, so 2026 cannot decide this. Test only on
2011–22 with a walk-forward (weights fitted on past years, applied to the next), then one look at 2023–25, comparing:
inverse-vol (current), equal risk, and inverse-vol capped by trade count. FAMILY: portfolio, weighting, sizing, book.

### Q10 Flow-driven calendar edges with a known payer (declare rules before loading data)
TESTED 2026-11-01 from the awesome-systematic-trading list (owner's choice): turn of the month and option-expiry week in 5
indexes (no effect beyond drift; tom_indices_v2 / opex_week_indices_v2 rejected) and oil -> equity (rejected on CFDs and on
futures: gone since 2011). `research/results/flows/calendar_study.json`, `oil_equity_futures.json`.
PARTLY ANSWERED (2026-11-01): Tokyo fix on gotobi days, USDJPY buy 23:00 -> 00:55 UTC = Tier B (`research/results/truth/tokyo_fix_gotobi_v1/REPORT.md`, `research/results/flows/`). Open: turn of month and pre-FOMC in US500/GER40,
Japanese fiscal year-end. Follow-ups for the Tokyo fix: (a) the 23:00 UTC spread in winter (Jan 2024 4.8 pips): an
execution rule (enter when spread <= 0.5 pip, within 15 minutes) needs its own name and test; (b) add it to the book's
forward test as leg 12; (c) the after-fix short (00:55 -> 02:00) was strong in 2020-25 but failed the 2011-19 gate: watch only.
Candidates, each with someone who must trade regardless of price: USDJPY "Gotobi" days (Japanese importers buy dollars at
the Tokyo fix on the 5th/10th/15th...; documented in research, untested here); turn of the month in US500/GER40 (salary and
pension flows); the pre-FOMC drift in US500 (documented, weaker after 2015); Japanese fiscal year-end JPY flows (March).
Priors: London 4 pm fix reversal real but only half a cost; month-end 1.4-1.9 costs but 12 trades a year (Hunt 2). Data:
USDJPY, US500, GER40 M1 in data/. FAMILY: calendar, flow, fix, seasonal.

Update 2026-11-03 (last push): month-end FX hedge rebalancing at the 4 pm fix (direction from US vs foreign month-to-date equity
returns) TESTED: real in 2011-19, reversed in 2020-22, flat in 2023-25; rejected (research/results/flows/MONTHEND_HEDGE.md).

### Q11 Gold's cost is now the lowest it has ever been relative to its movement
Commission is fixed in dollars per ounce while gold doubled: a 5-minute stop's cost fell from 10-17% of R (2011-22) to 6%
(2025) (`research/results/sop/leg34_diag.json`). Hypotheses that died on costs could be re-scored at today's relative cost,
but only declared ones (e.g. a documented Asia-up / New-York-down intraday drift), never hours mined from results (P17).
FAMILY: costs, gold, session, seasonal.

### Q12 Portfolio volatility targeting for the book (risk physics, not a new signal)
Scale the whole book's risk by the inverse of its recent realised volatility (20-60 days), fitted walk-forward, against
fixed 1%. Prior: P8 (GREEN/AMBER states did not help); this is a different mechanism (continuous scaling, documented as
"volatility-managed portfolios", mixed out of sample). FAMILY: sizing, volatility, portfolio, book.

### Q13 A bet-size rule that grows with live evidence (fractional Kelly under uncertainty)
At a live Sharpe of 0.8 the book's growth-optimal risk is ~10% per trade; 1% is a tenth of it. Sized for the backtest
Sharpe (1.36) when the truth is 0.8, half-Kelly becomes 0.85 Kelly: a 39% chance of a 50% drawdown in the ideal model.
Define in advance how risk rises (1% -> 2% -> 3%) as live per-trade evidence accumulates (~1,000 trades for t = 2 at
+0.078R). FAMILY: sizing, kelly, live.

### Q14 Positioning data as a signal (CFTC Commitments of Traders, weekly, public)
Speculator positioning extremes in gold, JPY and EUR futures as a trend filter or a contrarian signal; first check that the
data can be downloaded from the cloud. Evidence elsewhere is mixed; untested here. FAMILY: positioning, sentiment, weekly.

### Q15 A 5-minute hunter must hunt flows with a payer, not shapes (owner's 5-min focus, 2026-11-01)
Shapes at M5 are about zero before costs on 11 markets (P21, P1). Candidates where someone must trade at a set time:
the Tokyo fix (USDJPY, 00:55 UTC; ties to Q10), the London 4 pm fix (known small), the US cash close auction (US500/NAS100
last 10-15 minutes), the first minutes after scheduled data (CPI, NFP) using the exported economic calendar. Also check
first: the lab's index/oil/silver costs are estimates (US500 0.6 pt) while Exness Zero spreads measured ~0.003 pt; the
index commission is unknown (owner: MT5 Specification). FAMILY: intraday, flow, fix, auction, news, m5.

### Q16 An ML "gatekeeper" (meta-labeling) only on legs that already have an edge
From advice the owner shared (2026-11-01): a model that blocks or sizes trades from market-state features. It can help a
strategy with a real edge and overfits one without (P21: the 133-condition winner study failed; on gold Leg 34 blocking the
lowest-25% volatility moved the win rate 21.6% -> 21.9% and stayed at -0.17R). Test only on the book's legs and the Tokyo fix,
with purged walk-forward (fit on past years, apply to the next), few features, decided before results. The same advice's
spread guard is Q10 follow-up (a); correlation-aware sizing is Q9/Q12; "ghost stops" are rejected without a hard backup stop.
The three MQL5 GitHub repositories it named were not found by web search (kinorand/MQL5-ML-Framework,
w-m/mql5-matrix-examples, shmuma/mql5-risk-management). FAMILY: ml, meta-labeling, filter, sizing.

### Q17 Index financing in the lab is fixed in points; make it a rate (percent of price) before testing multi-day index holds
costs.json charges e.g. NAS100 3.0 points a night whatever the price (about 5%/yr at 20,000, over 40%/yr at 2011's 2,500),
so early years are overcharged. Exness's real US500 swap is -142.4 points long / 0 short (owner's MT5 spec, ~7.6%/yr at
~6,800). Did not change today's verdicts (each idea failed before financing too), but would bias any future multi-day index
test. FAMILY: costs, financing, index, methods.
Update (2026-11-01): now the gating item for trend on CFDs (repo funnel: Turtle core -0.38R with swaps vs +0.20R swap-free).

### Q18 Re-test the 10-year-high trend once financing is settled (Q1 swap-free status, Q17 index financing as a rate)
ath_trend_v1 (awesome list) failed with the lab's swaps (+0.006R/trade, 7 of 11 markets) but swap-free at half costs made
+0.25R in 2011-19 (+0.20 and +0.34 in the two eras), +0.12R in 2020-22 and 10 of 11 markets positive. That swap-free view was
seen AFTER the run, so it is a hunch, not a result: a re-test needs a new name, the owner's confirmed swap terms (or rate-based
index financing) fixed in advance, and a single configuration. Its 2023-25 look has not been taken. FAMILY: trend,
all-time-high, financing, breadth.

### Q19 Owner's 24-flow "payer matrix" (2026-11-01): which rows are real, testable payer flows?
Owner pasted an AI-written list of 24 "structural payer flows" for a 20-30-leg bot. Triage against our data (11 markets M1
2011-2025) and memory, before any test:
- Test first (payer known, data in hand): WM/R 4 pm London fix at month-end with the direction from the month's US-vs-rest
  equity returns (EURUSD, GBPUSD, USDJPY; Hunt 2 already saw the month-end fix move at 1.4-1.9x our research costs, 12 a
  year per pair: disclose); the last 30 minutes into the US cash close (leveraged-ETF and dealer rebalancing; US500, NAS100;
  folds in MOC and ETF NAV rows); month-end and quarter-end pension rebalancing CONDITIONAL on the month's equity move
  (US500, NAS100, GER40, UK100; the unconditional turn of month already failed).
- Later, weaker or thinner: ECB 14:15 CET reference rate (EURUSD); FOMC days and NFP Fridays (~70-100 events 2011-19, need
  exact dates); commodity option-expiry pinning (WTI, gold; needs an expiry calendar); triple-witching intraday; Treasury
  settlement days; Sunday-open gap (a shape, low prior). Owner-side additions from Claude: gold London PM auction, oil index roll.
- Not payer flows / not directional: TOCOM close for FX, market-on-open gaps without imbalance data, VIX roll (ETPs roll
  daily), London/NY overlap (liquidity, not direction), ETF NAV arbitrage, "retail margin liquidation hour".
- No data or too rare: option-gamma strikes (open interest), crypto funding (no crypto prices), Golden Week (HK50/AUD
  missing), dividend repatriation (15 observations per month), Lunar New Year (CNH/HKD), central-bank intervention
  (unscheduled, ~4 events in 15 years). Already tested: CTA trend breaks = trend following (P6).
Expect 2-4 survivors from the ~11 testable rows. Only verified legs go into the EA's time/event router. FAMILY: calendar,
flow, fix, intraday, owner-idea, payer.
Tested 2026-11-01: ECB 14:10 CET reference rate on EURUSD at RoboForex Prime costs (ecb_fix_eurusd_v1, 4 configurations):
REJECTED at the development gate; gross edge about zero in both shapes (into the fix -0.16 / -0.64 pip, fade after it +0.40 /
+0.14 pip, 2011-19 / 2020-22), so a cheaper account cannot rescue it (research/results/truth/ecb_fix_eurusd_v1/,
research/results/q19/ecb_fix_costs.json). Fix rows so far: Tokyo (known payer and direction) Tier B; London 4 pm x2 and ECB
(no known direction) rejected. Remaining rows need a direction from somewhere (month's equity returns for month-end
rebalancing, US close imbalance) or data we lack.
Update 2026-11-02: month-end rebalancing (conditional on the month's move) and the US close flow were tested in Batch 01
(Q23): both rejected.

### Q20 SEESARE P26 router (owner directive 2026-11-01): which constraint is the goal, and how does the ladder trade at $1,000?
Owner directive: run the payer flows through an MQL5 "time and event router" sized by SEESARE P26 (16-level hierarchy,
0.144% ... 0.0003% of a fixed $1,000 virtual State Value), one event a day, 360-event lifecycle, RoboForex ECN, copy trading,
HMAC-chained Telegram attestation. Blueprint: mt5/SEESARE_ROUTER_BLUEPRINT.md. Facts computed from the SEESARE formulas:
(1) at $1,000 only L0-L1 are tradeable on EURUSD at 0.01 lot (lower boundary <= 13.7 / 9.0 pips), gold at none, so after one
Negative Outcome the ladder deadlocks unless SHADOW (paper) resolutions drive it; (2) with time-expiry exits counted as
Positive Outcomes, (Negative, small Positive x2) x 120 breaks the ~3.6% envelope (16.2% drawdown at +0.01R wins); counted as
MANUAL resolutions (SEESARE 7.1) the same path costs 0.25%. CORRECTED 2026-11-01 (Phase 1 build): that was incomplete; losing
time exits that never move the ladder lose 29.55% (360 x -0.6R) and a 3.5:1 stop followed by two 1:1 target hits loses 14.96%;
only a pre-trade check (drawdown + all-in risk <= $36) holds the envelope (3.53% / 3.60%), now coded in
mt5/Seesare (CSeesareCycleLedger::AllowsRealRisk; evidence research/truth/tests/test_seesare_phase1.py, P24); (3) L0 caps returns near +1.7% a year at +0.05R/event and +3.4% at
+0.10R, so the envelope and the 60-120% goal exclude each other; (4) the multiplier formula (^2.5) and SEESARE's own table
(about ^2) disagree below 3.5:1; (5) a license-keyed HMAC chain cannot be verified by the public. Open decisions for the owner:
shadow vs bigger state vs cent account; envelope vs return target; formula vs table; RoboForex cost measurement; legal opinion
before followers (SEESARE classifies itself as non-executing software). FAMILY: risk, sizing, seesare, architecture, mt5, owner-idea.
Status 2026-11-01: owner chose SHADOW-driven ladder, time exits = MANUAL, exponent 2.0, keyless chain, dual-service outbox.
Phase 1 delivered as uncompiled MQL5 (clock, timing matrix, spread gate, cycle ledger, outbox; mt5/Seesare/README.md) with a
Python twin and 32 tests. Open: owner compiles and runs SeesarePhase1SelfTest.mq5 on the RoboForex terminal; owner decides the
time-exit policy (mandate keeps the envelope only via the guard and stops real trading after ~43 bleeding events; counting
losing time exits NEGATIVE keeps all 360 real at 0.19%); envelope vs return target; RoboForex costs and server scheme.

Phase 2 (2026-11-01): owner hardcoded "losing time exits count as negative" (now enforced by the ledger and declared in the
genesis line); flow modules coded (uncompiled): Tokyo fix (CANDIDATE, PAPER/LIVE), London 4 pm fix owner's rule (REJECTED in the
lab: wmr_fix_reversion_v1, 0/4 configs; documented post-fix timing wmr_fix_postfade_v1 also rejected), US close imbalance
(UNTESTED: no data). Router EA runs PAPER and SEESARE SHADOW only, sends no orders. Facts: no flow has a verified 5:1-10:1
payoff; the Tokyo fix pays about 1:1, so SEESARE sizes it at 8.8% of a level and at $1,000 it is SHADOW only (one 0.01 lot at the
0.3% stop risks $3.07 vs a $0.12 plan; even the 1.5x cap gives $2.05). Open: owner compiles and runs both self-tests; owner
decides between SHADOW-only SEESARE at $1,000, a larger virtual baseline, or a cent account.

Phase 3 (2026-11-01, owner chose a RoboForex ProCent cent account): built (uncompiled) the cent-account sizer (Exposure.mqh:
account money per USD, USD 1 / USC 100; plan -> cent lots rounded down; lowest real level), Telegram outbox formatter
(Telegram.mqh + Outbox.mqh format 2: plain text with [Cycle X/36, Step Y/10] and broker deal tickets, then the record, SHA-256
checksum) and a read-only deal reader (DealReader.mqh). Twin tools/seesare_outbox.py, 22 tests. Facts: the cent account makes the
Tokyo fix REAL only at L0-L3 (ratio 1.04) or L0-L9 (3.5), not at all 16 levels; ProCent USDJPY spread 1.9 pips (official
page), no index CFDs on ProCent (US close module cannot run there); cycle study (P25): with the hardcoded rule the ladder sinks to
L15 by event 13, 6 real trades in 15 years, 0 cycles; +2% per cycle needs +1.46R per event at L0 vs about +0.05R measured.
Open: owner compiles and runs the three self-tests on the RoboForex terminal (the Phase 3 one prints the real minimum lot and
level table); owner decides whether a time exit with a gain may climb the ladder (changes P25's mechanism; would need a new
lifecycle rule and its own study); minimum lot on ProCent (0.01 per most reviews, 0.1 per one) measured on the terminal.

Phase 4 (2026-11-01): owner chose "time-exit ascension": a time exit with a net gain is POSITIVE (climbs), a net loss NEGATIVE,
exactly 0 MANUAL; hardcoded (time_policy=GAIN_POSITIVE_LOSS_NEGATIVE), twin and vectors updated; router input InpLadder (16
level %, declared in genesis). Study (pre-registered): the ladder still sinks (P26): the Tokyo fix wins 52.6% of mornings, the
ladder needs about 75% to stay near the top. Real trades in 15 years: 15 (default ladder), 22 (owner-scaled x2.44), 191
(owner-scaled + declared 4:1, which the flow does not have); best cycles +0.021% mean, median -0.003%. The ascension rule makes
the guard, not the ladder, the only drawdown limit again (16.2% ladder-only on the pump path, P24). Open: owner decides between
(a) fixed small size for the Tokyo fix outside the ladder (P8), (b) changing SEESARE's step sizes (a SEESARE redesign, needs its
own study), (c) waiting for a flow with a verified high win rate; owner compiles and runs the self-tests.

Universe under the cap (2026-11-01, P27): combining the survivors and choosing the sizing rule gives about 6-7%/yr in backtest
at a 3.6% lifecycle cap (book + guard or book + drawdown-keyed ladder); 2026 untouched -0.6% to -2.3%; SEESARE's outcome ladder
about 0. Open: owner decides whether to replace the outcome ladder in CycleLedger.mqh with the drawdown-keyed 16-level ladder
(risk = 0.3 x room left x leg weight), and whether 6-7%/yr backtest (weaker live, P11) at this cap is worth running.
Per lifecycle (360 real trades, reset): about +6% per lifecycle for the book (drawdown ladder: 13 of 13 completed in
2011-22, none stopped); the owner's +2% per 10-trade cycle would be +72% per lifecycle.
Phase 5 (2026-11-01): owner adopted the drawdown-keyed ladder; built into CycleLedger.mqh (format 2) and the twin, uncompiled.
Tokyo weight 0.57 by default, 1.00 the cap ("maximised" was mixed, 2.00 worse). Open: the 11 book legs are not router modules
(only the Tokyo fix can trade: one lifecycle about 5 years); concurrent positions need the plan recorded at entry; the ECB
reference-rate flow is untested (Q19); owner compiles and runs the three self-tests.
Daily queue (2026-11-01): one trade a day from the 13 validated strategies cannot reach a median 1-3% per 10-trade cycle at
3.6-5% drawdown: every-day version +0.0-0.05% per cycle; top-3 legs +0.6% per cycle but a cycle takes ~5.5 months
(research/results/seesare/daily_queue_study.json). Reaching 1% per daily cycle at this cap needs about +0.6R per trade, about
8 times the book's +0.078R. Open: owner decides the goal unit (per cycle vs per year) and whether to forward-test the book.
Cycle math (2026-11-02, P28, research/results/seesare/cycle_math_study.json): +2% per 10-trade cycle inside 3.6% (95% of
lifecycles) needs a per-trade Sharpe of about 0.42 (0.36 at 5%, 0.32 at 6%, 0.28 at 8%); ours is 0.06-0.13. The book at a 5%
cap makes about +0.12% per cycle. Open: owner chooses between the target (needs an edge we do not have) and the cap.
### Q25 Owner's 3:30 EMA retest (2026-11-02): rejected for 2011-22; is the 2026 summer result a new regime?
Rules from the owner's 20 charts and answers, coded and checked (9 of 10 of the owner's example days match): M30 candle at
the anchor opens one side of the 10 EMA and closes the other; the first fresh M5 EMA cross touching its range is the
reference; stop entry at its far side (or pullback B3/B6/B12, or 50% of a displaced candle); 2R/3R/4R, breakeven on/off;
out at 16:00 New York; NFP/CPI/FOMC days skipped. Lab: REJECTED, 0 of 48 configurations positive in 2011-19 or 2020-22 on 12
markets; before costs about 0 (research/results/owner330/RESULT.md). Open: Jan-Oct 2026 was positive for the owner's 15:30
WAT anchor (both data feeds), entirely in US summer time when 15:30 WAT = 10:30 New York (+0.23R / +0.42R, t 1.1 / 1.8),
the timing that was worst in 2011-22 (-0.27R, every year negative). The owner chose the timing in 2026 (selection). Ways to
settle it: (a) paper forward test of the exact scanner from mid-March 2027 (US summer; from Nov 2026 to mid-March 15:30 WAT is
the 9:30 New York candle again), about 12 trades a month on 5 markets, ~40 trades to tell 2026-like from history-like; (b) the
one 2023-25 look, pre-registered in research/owner330/PREREGISTRATION.md ("Proposed look"), waits for the owner's word. Even
at the 2026 level, edge quality 0.13-0.23 is below the 0.42 the +2%-per-cycle goal needs. FAMILY: session, ema, retest,
intraday, ny-open, owner-idea.
v2 (owner's correction after the audit charts, 2026-11-02): reference may touch the range through its pullback; stop at the
candle or pullback extreme + 0-0.5 ATR; 1:1. REJECTED: 0 of 16; win rate 40-46% vs 56-59% needed (2011-19), negative in
2020-22 and in 2026 on both feeds. research/results/owner330/RESULT.md (v2 section).

### Q33 Architecture for a hands-off system: Wealth Game or SEESARE cap with higher alpha? (owner, 2026-11-08)
FAMILY: architecture, sizing, seesare, payout, owner-idea. Proposal (awaiting the owner's decision; blueprint decision 2):
the 3.6% cap governs; the Wealth Game survives only as the payout rule (when a lifecycle ends in profit, withdraw half the
profit and start the next lifecycle and its 3.6% from the new base). Layers: verified edges (Truth Lab, then SHADOW on live
data) -> allocation (small risk, so one gap fits inside the cap: 0.25% x 14R = 3.5%) -> pre-trade cap check (P24) -> payout
ratchet -> drift check (a module whose live R per trade falls below its backtest band goes back to SHADOW by itself) ->
plumbing (VPS that reaches Telegram, restart recovery, heartbeat). Inside a fixed cap, return grows with the square of edge
quality (fortnight study: 3.6x short in Sharpe = about 10x short in return), so ~60% a year inside 3.6% needs about 3.5x
the best mix's edge quality and ~120% about 5x (estimates). Not built: payout ratchet and drift check (twin first).

### Q31 RoboForex VPS + copy trading + affiliate "cycle" (owner, 2026-11-08): what does it need?
FAMILY: business, copy-trading, affiliate, vps, roboforex, seesare, owner-idea.
Facts from RoboForex's own pages, read 2026-11-08 (terms can change):
- Copy Trading Service (CopyFX renamed at the end of 2025): trader account = any real MT4 account, or MT5 / R StocksTrader
  with the Hedge system; deposit at least $100; performance fee 5-50% of the investor's profit above their high-water mark,
  or no commission; investment period 1, 2 or 4 weeks, fee paid Monday 00:00 server time at the end of the period; no
  cross-platform copying (one trader account per platform).
- Whether a ProCent (cent) account can be a trader account is NOT stated (ask support). The SEESARE router at $1,000 trades
  REAL only on ProCent (Tokyo fix L0-L3, none on a standard account), so a standard account needs about 100x the money.
- Copy Partner Program (Nov 2025): people who bring investors to a trader get a share of that trader's commission, set by
  the trader (example: 50%, 60% above $100 earned). Standard partner program: up to 85% of spreads and 30% of swaps of
  referred clients (fixed payouts per lot).
- Free RoboForex VPS: 1 core, 1 GB RAM, 30 GB HDD, Windows Server 2019; free with equity above $300 (bonuses excluded) and
  at least 3 standard lots a month (CFD volume excluded), otherwise $5 a month; client accounts only. It reaches only
  RoboForex servers and websites, so the SEESARE Telegram relay cannot post from it. MetaQuotes VPS: free until 2026-12-31
  after a $500 MT5 deposit (no DLLs; WebRequest reportedly migrates, untested here).
Still needed: ProCent eligibility; a VPS that can reach Telegram; the counsel opinion before followers (blueprint F6); a
compiled, self-tested router with a forward record (NorthStar report section 8); an edge worth copying (P28: +2% per cycle
needs edge quality ~0.42, ours 0.06-0.13; best fortnight mix +0.19% per 2 weeks, about 5% a year at the 3.6% cap).
Conflict to disclose: affiliate pay grows with followers' trading volume (spreads, swaps), the costs that sink intraday
strategies (P1).

### Q30 Owner's body-engulf 4-candle range (2026-11-07) — TESTED, rejected; CLOSED 2026-11-08 (2023-25 look failed)
FAMILY: engulfing, owner-idea, limit-entry, breakeven, synthetic-index, intraday. Candles 1-4 alternate; the 2nd and 4th
bodies engulf the 1st and 3rd bodies (wicks ignored); range = high-low of the four; limit at the midpoint, stop at the far
end, target 4R, stop to breakeven at +2R. Scanner and 5 random examples (XAUUSD/EURUSD): research/body4/.
Priors: the four-candle family (~6,200 settings) was rejected on FX/gold/indices; limit entries (P2) and breakeven (P4).
New here: Boom 1000 (Deriv synthetic index, RNG-generated with built-in drift and spikes), never tested. Needs: the owner's
Boom 1000 M1/tick export and broker specs (the Deriv data feed could not be reached from here), plus answers on body size,
order expiry, time exit, overlapping patterns, both sides.
Owner's answers (2026-11-07): report results by candle size (tiny candles allowed); cancel if the target is reached
before the fill; no trade starts over the weekend, all close Friday (cutoff 20:30 UTC assumed); price already past the
midpoint -> market, also test skip; newer same-direction setup replaces the pending order, opposite setup: wider range
wins; stop at the range end, test buffers; breakeven at +2R vs none (profit factor); all 12 markets, M1 + M5 first, then
higher timeframes; lookback: >= 3 of 5 candles in the trade's direction, with and without. Reference order engine
`research/body4/body4_orders.py` + 8 rule examples (`research/results/body4/examples2/`) + 3 tests.
Still open: which 5 candles (the owner's own Boom buy chart has 0 of 5 bullish before candle 1); an open trade when a
new setup forms (assumed: kept, setup ignored); Boom 1000 data + broker specs.

Answer (2026-11-08): Boom 1000 dropped by the owner. Owner's corrections applied (skip if candle 4 closes beyond the midpoint;
every same-direction order waits and the first fill removes the others; lookback main; 50% and 70% entries; spread-only
fills, P30). Pre-registered, 192 configurations x 12 markets x M1-H4: REJECTED. Every setting loses after costs (-0.11 to
-0.47R a trade), about 0 before costs; breakeven lowers profit factor; 50% beats 70%; wider stops lose less; lookback no
effect; engulfing loses a little less than the plain shape on M1-M15 only; best market x timeframe picks did not hold.
research/results/body4/RESULT.md. Open only if the owner's discretion (which setups he skips by eye) is logged forward.
v2 (2026-11-08, owner: "try 1:2R and 1:1R"): 384 configurations, REJECTED; 1R wins 34-47% where 53-72% is needed, 2R
25-35% vs 35-48%; best -0.10R a trade. research/results/body4/v2/RESULT.md.
v3 (2026-11-08, owner: dojis count as bullish, 1:2 and 1:10, breakeven at 75%; "check for bugs"): REJECTED, no bug found
(full audit: patterns, entries and exits independently re-checked); 10R hit by 6.6% of trades vs about 9% needed before
costs. research/results/body4/v3/RESULT.md.
v4 (2026-11-08, owner: biggest losers, safe windows, 2R-10R, the RR hit 50% of the time): REJECTED, 3,456 settings. Losses
= no edge in the move + 0.35R costs a trade; biggest losers = overnight index gaps, Brexit, data holes; safe window +0.05R,
still negative; hit rates at chance; half the trades reach only 0.3-0.9R. research/results/body4/v4/RESULT.md.
v5 (2026-11-08, owner: "test both engulf, loosen ones, then test the data in 2023-2025, then try layering timeframes"):
768 settings (strict vs loose engulf x layering on/off), REJECTED. Loose is no better (26%/56% of pairs, 3x the trades);
layering helps a little (+0.03 to +0.06R in 62-75% of pairs) but keeps 1-2% of trades. Owner's 2023-25 look (4 primaries
chosen on 2011-22 first): all negative, -0.07 to -0.38R a trade; 16 of 448 settings positive, median -0.18R. 2023-25 is
used up for this family (5,184 settings in v1-v5); only Jan-Oct 2026 is unseen. research/results/body4/v5/RESULT.md.
Open only as a forward log of the owner's own calls (setups marked before the outcome).
Examples (2026-11-08): 10 v5 trades drawn at random from the 4 look settings, every rule written on the chart
(research/results/body4/v5/examples/). About 2 in 3 loose setups fail the strict rule only because candle 2 or 4
opens inside the previous body by less than one spread (median 0.6-0.75 spread; M5 296,083 and H1 29,497 setups):
tick noise, which is why strict and loose tested the same.
Gold characteristics (2026-11-08, owner: "focus on gold, all the setups in 2019, find the best characteristics";
pre-registered, learn 2019): REJECTED. 20 characteristics, 70 conditions; every group loses after costs, about 0
before; only cost traits matter; the 2019 rule (M30 + loose) lost in 14 years and in 2026.
research/results/body4/gold/RESULT.md.
v6 (2026-11-09, owner's last configuration: candles 2 and 4 at least 60% body, 2-candle lookback, 4R/5R/6R, "best
architecture mix" for two-week cycles): REJECTED (72 lab configurations, 0 pass). 2-candle lookback +0.02R, 60% body
nothing; targets hit below even zero-cost needs; the best mix (3 of 72 cells) lost in 2020-22 and 2023-25. Jan-Oct
2026 kept unseen. research/results/body4/v6/RESULT.md.
v7 (2026-11-09, owner: "lookback candles obey the same 60% threshold ... how realistic is this cost ... curate
strategy, timeframe and account": Prime, M5/M15, 13-17 UTC, 3R-6R): REJECTED (16 lab configurations, 0 pass). Our
Prime costs match the owner's figures (0.06-0.11R a trade on EURUSD); about 9 trades a year; the 2011-19 profit (86
trades) reversed in 2020-22, even at zero cost. research/results/body4/v7/RESULT.md.

### Q29 TradingView "Noise Gate" (The_Peaceful_Lizard, 2022, open source) as the owner uses it (2026-11-06)
FAMILY: filter, noise-gate, owner-idea, tradingview. The script only reshapes a signal (source, moving-average length,
ratio, level; hard/soft knee): values whose size is below `level` are shrunk. It has no buy/sell rule, so the owner's
signal, level and entry/exit must be fixed before a test. Its code could not be fetched here (only the description).

### Q28 Owner's noise gate (2026-11-06) — TESTED, rejected
FAMILY: filter, regime, noise-gate, efficiency-ratio, owner-idea. Gate the survivors by how clean recent movement is.
Answer: no better than random filtering (p 0.36), reversed in 2026 (research/results/noisegate/RESULT.md). If the owner
meant a specific indicator called "noise gate", its exact rules can be tested the same way.

### Q27 Owner's 4-flip EMA pattern (2026-11-02) — TESTED, rejected
CLOSED 2026-11-03: best variant + H4 50-EMA trend filter FAILS on the unseen 2023-25 holdout and 2026
(research/results/final/FINAL.md).
Four consecutive candles crossing the 10 EMA in turn; B+ when the 4th closes beyond the 3rd open, A+ when the 2nd also closed
beyond the 1st open; entry 50% of the 4th or at its close; stop and target grids; close daily. 640 configurations, 12
markets, M5-H4: 0 pass; where/when 0 of 180 cells (research/results/ema4/RESULT.md). Only lead: H4 (+0.11 to +0.14R in
2011-19 on 106-282 trades, about 0 in 2020-22); a held-longer H4/D1 version would be a new, hindsight-flagged test.
v2-v4 (2026-11-03, owner's corrections: full engulfing, breaks from the other side, obvious breaks; 3 stops, trailing and
EMA exits; 5,040 settings): all rejected; the engulfing grade has no selection value (research/results/ema4/RESULT_V2_V4.md).
No-EMA price-action version (2026-11-03, A+ only, entries close / 50% / 4th-candle high; 540 settings): rejected, 0 positive in
2011-19; the 4th-candle-high entry is the worst (research/results/pa4/RESULT.md).
FAMILY:
ema, engulfing, chop, multi-timeframe, owner-idea.

### Q26 Re-run the intraday studies that used HistData markets before the clock fix (2026-11-02)
HistData's stamps were one hour late in daylight-saving periods (P29; fixed in the data 2026-11-02). Re-run and compare:
the Leg 34 pocket scan (research/hunter5m/pocket_scan.py; 11 markets x 6 timeframes x 3 sessions), the winner anatomy and
runner profile (research/hunter5m/), the Q21 GER40 opening-range diagnostic (research/results/q21/), and the H1 index
calendar studies (tom_indices_v2, opex_week_indices_v2, oil_equity_v2, payday_indices_v1: multi-day holds, so small effect
expected). Done already: Batch 01 (verdicts unchanged; the US close 2020-22 'positive' slice was an artifact). Daily studies
(breadth trend, index RSI2, funnels, ath_trend) shift only the day boundary by an hour: low priority. FAMILY: data, clock.

### Q24 Sweep-and-Shift Reversal (owner spec, 2026-11-02) — TESTED, rejected
XAUUSD + EURUSD, H1 sweep of the 20-bar extreme by 0.5 ATR, reclaim within 3 bars, M15 structure break, fade to the prior
swing (min 2R), near-miss control. Lab: rejected (research/results/truth/ssr_sweep_shift_v1/REPORT.md, controls.json).
EURUSD alone looked better in all three periods (+0.151 / -0.017 / +0.194R) but choosing it now is hindsight, and Jan-Oct
2026 holds only about 30 such EURUSD trades: too few to decide (an edge of s 0.1 needs about 900 trades to show). Not
pursued unless the owner wants a EURUSD-only forward paper test. FAMILY: liquidity, sweep, mss, smc, reversal, owner-idea.

### Q23 Owner's Batch 01: 13 payer-flow candidates (2026-11-02)
Pre-registered with controls and a stricter batch rule (t >= 3, beats its control, replicates): research/batch01/. Tested 9
(month-end rebalancing) and 11 (leveraged/vol-target flow into the US close): both REJECTED (research/results/batch01/
BATCH01_REPORT.md). Not testable here, by reason: 1, 2, 13 need daily front and second-month futures prices per contract
(pysystemtrade holds one contract plus carry/forward; not tradeable as spreads on MT5); 3 needs VX term structure and ETP
roll sizes (no VIX on Prime); 4 and 12 too few events (owner pre-flagged); 5 needs a dividend payment calendar with sizes;
6 EM FX and coupon calendars; 7 new-issue cash bonds (no bonds on Prime); 8 cross-currency basis; 10 option open interest
by strike. Any of these can be reopened if the owner supplies the data source. FAMILY: calendar, flow, payer, batch01,
owner-idea.
Re-run 2026-11-02 after the HistData clock fix (P29): verdicts unchanged; the one US close slice that was positive in 2020-22
(+0.031R, t 2.1) was a clock artifact (-0.011R on corrected data). BATCH01_REPORT.md, re-run section.

### Q22 Build and verify the MQL5 code here (owner, 2026-11-02): compile, self-tests, Strategy Tester, parity
Checked in the cloud session: Wine 9.0 installs from Ubuntu's archive; MetaQuotes' mt5setup.exe (64-bit) downloads. Running
the installer was blocked by the session's safety check (third-party software), so nothing is compiled yet. Needs: owner's OK
to run the installer under Wine (then MetaEditor command-line compile of every .mq5); for self-tests and the Strategy Tester a
demo login (environment secret) and a network path from MT5 to the broker's servers (unknown through this proxy). Alternatives:
GitHub Actions Windows runner (compile + tester with a demo login as a secret) or the owner's PC / a VPS. Details: section 9 of
research/goal/CYCLE_GOAL_MATH.pdf. FAMILY: tooling, mql5, verification, parity.

### Q21 "Magnetic Distance" momentum bursts with micro-stops and fast scratches (owner paste, 2026-11-01)
Claim: entering at a velocity break of the 15-minute opening range toward a liquidity "magnet" (previous day high/low, session
open), stop under the entry candle, scratch at -0.2R if no follow-through in 3 candles, gives 40% +2R / 25% +0.75R / 25% -0.2R /
10% -1R (+0.83R per trade) and a maximum drawdown of 3.2R with "mathematical certainty". Checked (arithmetic only, no data): the
split is assumed, not measured; on its own numbers 360 trades exceed 3.2R in 31% and 3.6R in 16% of simulations (worst 8.5R);
round-trip costs at 3-10 pip stops are 0.1-0.3R per trade and raise P(> 3.6R) to 36-92%. Priors all rejected: ORB (2023-25 -0.12
to -0.16R), daily sweeps of PDH/PDL (raw -0.02 to +0.06R), London best-setup scanner (raw +0.015R vs cost 0.076R), ~1,400
liquidity variants, breakeven/scratch exits (P4), intraday costs (P1). Our cap is 3.6% of the account, not 3.6R. Testable with
tick volume (M1 'v' field) in the lab if the owner wants; expected outcome from priors: rejection.
Diagnostics (2026-11-01, owner parked Q21): (1) sessions: no session reaches zero after costs. ORB canonical by session
(2011-19 after / before costs): London -0.068 / +0.056R, New York 08:00 (in the London-NY overlap) -0.123 / -0.003, New York
09:30 -0.110 / -0.002, Tokyo -0.142 / -0.004 (research/orb/ORB_REPORT.md); 396-cell pocket scan 2023-25 median after / before
costs: Asia -0.183 / -0.031, London -0.158 / -0.009, New York -0.151 / -0.014R; 2 of 396 cells positive in both 2011-19 and
2020-22, both negative in 2023-25. The failure is uniform: raw edge about zero everywhere, costs make it negative.
(2) tick-volume surge: predicts slightly more movement in both directions, not direction (research/results/q21/
velocity_diagnostic.json; USDJPY rank correlation with follow-through +0.001 / -0.008; top quintile below the cost). In the ORB
study the activity filter was neutral in development and negative in validation (USDJPY only: the only market with tick
volume every year).
FAMILY: breakout, orb, liquidity, momentum, intraday, scratch, micro-stop, owner-idea.

## Answered
- **Q32 (2026-11-08), owner's Wealth Game (25% risk on 1:4 trades, withdraw half at each 4x, 12 levels):** the account shrinks at 25% risk unless
  1:4 trades win more than 29.3%; at our measured hit rates (12-18% at 4R) 80-94% of runs end below the $100 start;
  for a +0.05R edge the best risk is about 1% a trade. Evidence: research/results/goal/WEALTH_GAME.md. FAMILY: sizing, risk,
  compounding, kelly, owner-idea.
- **Q4 (partly, 2026-10-31):** the book's trend family does not transfer to US500, GER40, WTI or XAGUSD (0 of 64; oil alone
  failed 2023–25). Evidence: research/results/truth/breadth_trend_v1/, wti_trend_v1/. Still open: JPY crosses and metals
  on a swap-free account.
- **Q5 (2026-10-31):** RSI(2) dip-buying is positive on US500 and GER40 in every period (2023–25 +0.09R, PF 1.67, 83 trades) but
  not significant, negative under stress, and about zero after costs on NAS100, UK100 and JP225. Rejected at the lab's costs;
  the raw edge (+0.02 to +0.09R) is real but small. Revisit only with measured index commissions on a swap-free account.
  Evidence: research/results/truth/index_rsi2_v1/, index_rsi2_breadth_v1/.
