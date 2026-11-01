# PRINCIPLES — what the evidence has taught (the project's learned pathways)

A principle enters only with evidence (a Truth Lab verdict or a reproducible study in this repo). Each has a
confidence: **high** (several independent studies agree), **medium** (one solid study), **prior** (reasoned,
not yet tested here). When new evidence contradicts a principle, edit it, keep the old text under
"History", and record the change in JOURNAL.md. Never delete a principle silently.

### P1 Costs decide intraday trading
Raw edge of intraday setups on XAU/EUR/GBP/JPY is about +0.01–0.02R per trade; all-in costs are about 0.07R.
Evidence: scanner (61,787 setups: gross +0.015R, costs 0.076R), ORB study, liquidity studies. Confidence: high.
More evidence (2026-10-31): Exness Zero spreads measured at about 0 (the cost is commission + slippage, about 1 pip on FX);
the Dark Mimas oscillator scalper still loses 1.2–1.9 pips per trade there, and loses before costs too.
Evidence (2026-10-31, Leg 34 on gold M5, 144 configs): before costs +0.00 to +0.02R per trade; Exness Zero costs are 10-17% of a
$1-1.60 five-minute stop (6% in 2025), so every version loses -0.11 to -0.13R. research/results/sop/leg34_diag.json.
Evidence (2026-11-01, 5-min hunter): Leg 34 on M5 across 11 markets is about zero before costs on every market (-0.07 to
+0.04R) and negative after costs on all of them. research/results/hunter5m/winner_anatomy.json.

### P2 Resting limit / retest entries suffer adverse selection
They fill when price runs against you and miss the trades that work. QM: retest worse than market entry in
97% of paired settings (−0.081R); supply/demand −0.035 to −0.084R; FVG midpoint depth worse in 96%.
Evidence: North Star ablation. Confidence: high.

### P3 Higher timeframes beat lower ones
Costs per unit of risk shrink and noise falls. FVG M5→H1 +0.15R in every paired setting; QM M15→H1 +0.05R.
Evidence: North Star ablation. Confidence: high.
Evidence (2026-11-01, Leg 34 pocket scan, 11 markets): moving from M5 to H1 cuts the cost share (median -0.27R -> -0.20R
after costs) but does not create a raw edge (before costs -0.01 to -0.05R at every timeframe). Higher timeframes help only
an idea that already has an edge.

### P4 Breakeven stops are a backtest mirage
They add no out-of-sample edge; small targets hurt. Evidence: four-strategy study (mgmt_oos, exit_eras).
Confidence: medium-high.

More evidence (2026-10-31): owner's SOP: breakeven at 1:1 added +0.01 to +0.02R in 2011–22, then cost money in
February–October 2026 (M30 +0.02R → −0.16R). It is not an edge.

### P5 Overnight swaps matter for multi-day trades
Gold trend 2011–18 +0.13R → +0.01R with a constant swap; four strategies 2023–25 +0.036 → +0.005R; the book
+0.063 → +0.044R. A swap-free account changes the picture (book Sharpe 1.00 → 1.64 with low costs).
Evidence: North Star rescore, TimelessCity rescore. Confidence: high (size of the Exness effect unverified).
Update (2026-10-31, corrected the same night): with MEASURED Exness Zero spreads and high-end published commission, the
book is Sharpe 1.36 with swaps and 1.74 swap-free (2023–25: 0.95 / 1.27); January–October 2026 (untouched) −1.36% with swaps
vs +0.78% swap-free. Swap-free status is the single largest cost lever left (+0.38 Sharpe).
Evidence: research/exness/EXNESS_COSTS.md, research/results/champion/. Commission and swap-free status still unconfirmed.
History: first written as 1.15 / 1.51 (2023–25: 0.75 / 1.06); those daily series dropped trades closing at the Sunday open
(bug fixed 2026-10-31, see JOURNAL). The earlier "1.00 → 1.64" figures came from the same kind of series and are understated too.
Evidence (2026-11-01, repo funnel): trustdan's Turtle core on our 11 CFDs makes -0.38R per trade 2011-19 with the lab's swaps
and +0.20R swap-free at half costs; the 10-year-high trend (awesome list) +0.006R vs +0.25R (10 of 11 markets positive
swap-free, 7 with swaps). Every multi-day trend verdict on CFDs is a verdict on financing. research/results/repofunnel/.

### P6 Trend persistence is market-specific
Gold and USDJPY trend; EURUSD and GBPUSD don't (Donchian lab: gold +0.14–0.21R, JPY +0.15–0.28R, EUR/GBP
negative; TimelessCity's EUR trend leg S4 rejected). Declare markets before testing; picking them afterwards
is hindsight. Confidence: high.
More evidence (2026-10-31): the owner's daily close-beyond reversal is Tier B on EUR/USD (+0.04R per trade) but fails as a
4-market rule (gold negative, GBP flat): EUR/USD mean-reverts at the daily scale, where the others don't.
More evidence (2026-10-31, breadth): before costs, trend at H4–D1 is positive on oil (+0.21R) and silver (+0.11R) but negative
on US500 (−0.05R) and GER40 (−0.04R); equity indices instead revert after short dips (RSI(2) +0.02 to +0.09R raw on 5 indices).
Commodities and JPY trend; equity indices and EUR mean-revert. Evidence: research/results/truth/breadth_trend_v1/,
index_rsi2_v1/, index_rsi2_breadth_v1/.
More evidence (2026-11-01, repo funnel): all 48 trustdan Donchian variants (pyramiding, targets, ADX/RSI filters, SAR,
chandelier, time exits) fail the 9-of-11-markets rule: with swaps at most 6 markets positive, swap-free at most 8. Exits and
filters do not change where trend lives. research/results/truth/funnel_trustdan_v1/.

### P7 After a liquidity grab, continuation beats reversal
About 1,400 sweep/grab variants: fading the grab has no edge; the only survivor is a continuation
(GBP weekly follow-through). Evidence: liquidity studies, LG study. Confidence: medium.

### P8 Simple sizing beats clever risk states
Halving size after a 10% drawdown slows recovery; plain fixed-fractional at lower risk dominates at equal
tail risk. Keep only a hard circuit breaker (RED). Evidence: North Star risk comparison. Confidence: medium-high.

### P9 Breadth of independent edges is the only free lunch
11 legs of about Sharpe 0.3 each with near-zero correlation make Sharpe 1.0. Sharpe ≈ s·√(N/(1+(N−1)ρ)):
correlation sets the ceiling. Evidence: book, multiasset combination. Confidence: high.

### P10 A single gate lets luck through
The coin-flip control passed the development gate and was positive in all three periods; only neighbours,
walk-forward and the deflated Sharpe caught it. Never trust one filter. Evidence: Truth Lab control. Confidence: high.

More evidence (2026-10-31): oil was the only one of four new markets with a positive trend in 2011–22 (+0.14R net). Tested
alone afterwards (hindsight, called out), its 2023–25 look was −0.18R per trade. Picking the winner after the fact found luck.

### P11 Expect live results 30–50% weaker than heavily searched backtests
Selection bias from wide searches. Evidence: industry and statistics. First measurement here (2026-10-31): the 11-leg book
on untouched January–October 2026 Exness data made +0.022R per trade against +0.078R in its 2011–25 backtest (about 70%
weaker per trade, though within noise: z −0.81 on 333 trades), −1.36% at 1% risk vs a typical +8.2% for 10 months.
A stretch that bad has a 4% chance under the full backtest edge, 13% if the edge is 30% weaker, 23% if 50% weaker.
Evidence: research/results/champion/ (dashboard_data.py). Confidence: medium (one short out-of-sample period, no live fills yet).
Evidence (2026-11-01): three published calendar/macro effects from the awesome-systematic-trading list failed on our data:
turn of the month (1987-88 papers) and option-expiry week show no effect beyond drift in 2011-25; oil predicting equities
(2008 paper) was +1.15%/month in 2000-2010 on futures and -0.03% in 2011-2024. Published edges fade; a paper's Sharpe is
an upper bound.
Evidence (2026-11-01, repo funnel): payday (S&P 500 on the day after the 15th) +0.016R/trade 2011-19 (t 2.1), then negative
2020-22 and 2023-25; on futures, commodity momentum and term structure made +17-18%/yr in 2000-09 and lost money after 2010,
country betting-against-beta +16%/+30%/yr then -24%/yr in 2020-22. Public repos rank backtests on other assets with no costs
or holdout: trustdan's champion (Alt10, "76% success" on US stocks) is -0.62R/trade on our markets.

### P12 CFD financing kills high-notional strategies
Trend + carry needs about 4x notional; CFD markups make it Sharpe 0.06 versus 0.50 on futures. Bonds are
impossible as CFDs. Evidence: multiasset study. Confidence: high.
More evidence (2026-10-31): single-market trend trades on index and commodity CFDs pay 0.06–0.33R financing per trade
(US500 0.33R, GER40 0.26R, silver 0.12R, oil 0.06R at the lab's estimates), more than the raw edge on indices and silver.
Evidence (2026-11-01): month-long index CFD holds pay about 0.5%/month in financing at today's rates (the lab's fixed-point
index swaps charge more in early years, up to ~1.2%/month); oil->equity on CFDs turned +0.42%/month before financing into
-0.74% after. Multi-day index ideas belong on futures (Q6).

### P13 Short volatility hides ruin
VIX carry: good years, then −97%. Evidence: multiasset study. Confidence: high.

### P14 Chart-pattern concepts have no edge on these markets after costs
ICT/SMC (FVG, liquidity grabs, structure shifts), Quasimodo, supply/demand, Malaysian SnR, engulfing, ORB:
all rejected, about 250,000 configurations. Evidence: ledger. Confidence: high (for XAU/EUR/GBP/JPY, 2011–2025).
More evidence (2026-10-31): the owner's 4-leg engulfing SOP (calibrated on their own case studies): 2 of 756 FX settings
pass the gate and then fail; 0 of 72 on gold H4/D1; February–October 2026, untouched: −0.09 to −0.35R per trade.
Evidence (2026-10-31): the owner's Leg 34 on gold M5 (3R/4R targets, breakeven, R-ladder and EMA trails): 0 of 144 positive in
2011-19; owner's settings -0.06 to -0.20R per trade on untouched Jan-Sep 2026. research/results/truth/leg34_gold_v1/.
Evidence (2026-11-01, repo funnel): mechanical versions of sofus-nl's VCP, cup and handle, bull flag, Qullamaggie breakout and
triple RSI divergence on 11 CFDs are rare and negative (best: divergence both sides +0.003R on 30 trades in 2011-19);
the strict cup and handle never triggers. research/results/truth/funnel_sofus_v1/.

### P15 Judge any bot by equity, not balance: realised P&L hides open risk
Averaging grids bank many small wins while a losing basket grows. Gold Hunter V9's settings, replayed 2011–2025:
realised profit positive, net −$155k to −$196k per 0.01 lot once open losses count; it showed a realised profit after
3 months in 95–100% of start dates, then wiped out 19–74% of accounts within 3 years. With the tail capped by a stop,
all 12 versions lose (no edge underneath). Evidence: research/gridbot/. Confidence: high (for grid/averaging bots on gold).
More evidence (2026-10-31): Dark Mimas grid set on EUR/GBP 2011–25 wins 96–98% of baskets and loses in all 36 tradable
configurations; the vendor's own live signals show 51–53% equity drawdowns against 8–25% on balance. MQL5 "growth %" is
time-weighted: a $100 start topped up later inflates it; compare money deposited with equity. Confidence: high.

### P16 Win rate is not edge
Exits that bank the first profit behind a wide stop produce 85–90% winners and tiny expectancy. Owner's EUR/USD reversal:
88% winners, +34 pips average win vs −179 average loss, +0.04R per trade, +0.9% a year at 1% risk (4.3% a year at 5%
risk with a 21% drawdown). Gold Hunter: realised wins nearly every month, net loss. Judge by expectancy, return per unit
of drawdown and equity. Evidence: research/results/truth/eurusd_close_beyond_reversal_v1/, research/gridbot/. Confidence: high.
Evidence (2026-10-31, Leg 34 gold M5): 48% of filled trades reach +1R before the stop, 31% +2R, 23% +3R. "It was in profit
before the loss" is the normal path of a no-edge trade, not a sign of edge; breakeven and trailing turn it into many small
losses (before costs +0.004 to +0.014R).

### P17 Active hours picked from a backtest do not carry forward
Choosing a strategy's best trading hours on past data mostly selects luck. Dark Mimas family: best 6 hours picked on
2011–19 made +1.11 pips per trade before costs, then −0.13 in 2020–25 (0 of 18 positive after costs). Grid best hours:
+2.76 → +0.18 pips per basket. The lab test with session windows declared in advance (osc_turn_sessions_v1:
6 windows × 3 timeframes × 3 oscillators × follow/fade, 4 markets) gave 0 of 108 passing, and every window lost about the
same (−0.04 to −0.05R). The big winners of high-frequency bots are trend days that start near the London or New York
open, and a trend day is known only after it ends. A time filter must survive a learn-then-check split before anyone
trusts it. Evidence: research/gridbot/DARK_MIMAS_REPORT.md, research/results/truth/osc_turn_sessions_v1/. Confidence: medium-high.
Evidence (2026-11-01): Leg 34 by session (Asia, London, New York) x 6 timeframes x 11 markets: no session differs
(median -0.23R); the past M30 16-20 UTC pocket (EUR/GBP) lost on all 9 other markets.

### P18 Case studies select winners; only a coded scan of every setup shows the hit rate
The owner's 4-leg SOP documents showed mostly wins. Coded so that it reproduces the owner's own cases (same legs, entry and
stop on 6 of 12), the rules find about 4,600 setups on EURUSD M30 alone in 2011–2025; 4 of the 5 reproduced cases won,
but only 21–34% of all setups win, below the ~37% the 2R target needs after costs. Before trusting any discretionary
pattern, code it, check it against the trader's examples, then test every occurrence. Evidence: research/sop/SOP_REPORT.md.
Confidence: medium-high.
More evidence (2026-10-31): looking for "the conditions that made it win" across 23,000 setups and 19 features known at entry,
none of 56 single conditions was profitable even in the learning years (2011-19); the best 2-condition rule lost there too.
When nothing separates winners in-sample, the wins are noise around a negative mean. Evidence: research/results/sop/winning_conditions.json.
Evidence (2026-10-31, Leg 34 gold M5): the month the owner's screenshots come from (Oct 2026) was mildly positive (+0.03 to
+0.11R, ~100 trades); the nine untouched months before it lost -0.06 to -0.20R (700-870 trades), and so did 2011-2025. The 10 EMA
slope did not separate winners (thirds by steepness: -0.14 / -0.16 / -0.13R).
Evidence (2026-11-01): studying the biggest winners instead of case studies does not help either: rules built from the
attributes of Leg 34's top runners lost out of sample on gold and on 9-10 of 10 other markets (P21).

### P19 Probability of profit = edge per trade x number of independent edges x time, not setup picking
On the 11-leg book's own trades: the share of profitable fortnights rises from 55% (lab costs) to 61% (Exness Zero
swap-free), and of profitable years from 87% to 100% of 2011-25, from costs alone. One leg alone is profitable in 27-28% of
fortnights and 58-68% of years; the eleven together in 55-61% and 87-100%. With +0.08-0.10R per trade and a 1.26R spread,
a 90% chance of being up needs about 250-430 trades (8-13 months of the book). (Corrected 2026-10-31 for the Sunday-exit
bug; first written as 54-59% of fortnights, one leg 26%, 55-66% of years.) Even then 4 fortnights in 10 lose, so
fortnightly payouts must come from a buffer, not from each fortnight. Without positive expectancy no filter raises the
odds (P16, P18). Evidence: research/results/probability/odds.json. Confidence: high (backtest; live will be weaker, P11).

### P20 Every trade must reach the daily P&L: a weekday calendar silently drops Sunday-open exits
Daily series built by re-indexing to business days lost every trade that closed at the Sunday-night FX open. Those exits
are mostly survivors of Friday (stop-outs land on weekdays), so dropping them removed winners: the book's Sharpe read 1.15
instead of 1.36 (Exness + swaps) and 1.01 instead of 1.24 (research costs), and the 2026 test −2.34% instead of −1.36%.
Trade-level R, Truth Lab gates and verdicts were unaffected (the tier is set before the daily series is built). Rule: roll
weekend dates to Monday and check that the daily series sums to the trade list. Evidence: research/truth/tests/test_truth.py
(TestDailySeries), commit 7e194a6. Confidence: high.

### P21 The anatomy of winners cannot be traded when the setup has no raw edge
Of 10,600 gold Leg 34 trades (M5, 2011-19), the top 10% runners look like all the others (no attribute above 1.15x); the
top 1% lean to quiet conditions and a strong 4-hour push, but a filter that keeps those setups keeps more losers too:
-0.20R vs -0.15R for every setup, worse again on 10 other markets and in 2026. The best rule from 133 conditions failed its
own learning halves. Winners are the tail of a noisy distribution, not a separate kind of trade; only a positive mean
before costs can be filtered into a better one. Evidence: research/hunter5m/ (two pre-registered steps). Confidence: high.
Evidence (2026-11-01): the same holds for pockets: of 396 market x timeframe x session cells, cells positive before
costs in 2011-19 were positive in 2020-22 34% of the time, cells negative 32%: no persistence, so no pocket to pick.

### P22 Edges with a payer survive where shapes do not
After ~300,000 configurations of chart shapes rejected after costs, the first new survivor is a flow with a known payer:
Japanese importers buying dollars at the Tokyo fix on gotobi days (USDJPY 23:00 -> 00:55 UTC): positive in every period
2011-19, 2020-22, 2023-25 and Jan-Sep 2026, other days near zero, Tier B, correlation with the book +0.03, book Sharpe
1.21 -> 1.38 in the lab's fit. Look for who must trade, when, and why, before looking at charts. Evidence:
research/results/truth/tokyo_fix_gotobi_v1/, research/results/flows/. Confidence: medium (one flow, one market, small edge
per trade: +1.4 to +3.9 pips after cost).

### P23 A daily backtest across markets must trade one day after the signal
Markets close at different hours (Hang Seng and Nikkei before Europe, Europe before the US) and holidays leave stale prices.
A rule that decides at "today's close" from all markets and earns each market's next close-to-close return is using
information the earlier-closing markets had not priced yet: a look-ahead that no prefix test catches. In the repo funnel's
first futures run, country-index pairs showed Sharpe +1.4 in every period and the WTI-Brent spread +2 to +3; trading one
day later turns them into -0.35/-1.37 and -0.6/0, while monthly strategies barely change. Use a one-day lag (or intraday
fills at a common time) for any multi-market daily or weekly rule. Evidence: research/results/repofunnel/
(futures_funnel_v1_lookahead.json vs futures_funnel_v2.json), PREREG.md section E2. Confidence: high (known mechanism,
reproduced here).

### P24 A drawdown cap needs a pre-trade check, not a sizing ladder
A ladder that shrinks size after losses and grows it after wins (SEESARE P26's 16 levels) bounds each loss, not the sum of
losses: if the outcomes that move the ladder are not the ones that lose money, it never shrinks. Over 360 events, time exits
at -0.6R that count as manual resolutions lose 29.55% at the top level; a 3.5:1 stop followed by two 1:1 target hits climbs
back for free and loses 14.96%. Checking before every real trade that current drawdown + the trade's all-in risk stays
within the cap holds the cap under any sequence (3.53% and 3.60% here); gaps through the stop are the only way past it.
Evidence: research/truth/tests/test_seesare_phase1.py (EnvelopeGuard), tools/seesare_verify.py, mt5/Seesare/README.md.
Confidence: high (arithmetic, reproducible). Related: P8 (sizing states add nothing), P13.
Update 2026-11-01 (Phase 4): under the owner's time-exit ascension rule a stop at L0 followed by two winning time exits
of one cent puts the ladder back at L0 every time: ladder alone 16.2% over 360 events, with the guard 3.60% (121 real,
239 paper); under the Phase 2 rule the same path cost 0.21%. Evidence: research/truth/tests/test_seesare_phase1.py (pump).
Update 2026-11-01 (Phase 5): a ladder keyed to drawdown instead of outcomes IS such a check: with risk <= 0.30 x weight
x room left (weight <= 1), drawdown + risk stays below the cap at every level, and a single loss up to 3.33 times its
plan cannot cross it. Evidence: research/truth/tests/test_seesare_phase1.py (Ladder, EnvelopeGuard), mt5/Seesare/README.md.

### P25 A ladder that climbs only on target hits sinks to its floor when the edge is paid at the time exit
SEESARE moves up one level only on a POSITIVE outcome (a target hit) and down 2-4 levels on a NEGATIVE one. A flow whose
profit arrives at a fixed exit time (the Tokyo fix: buy 23:00, sell 00:55 UTC) has winners that are time exits, which never
climb, while its stops and losing time exits descend. Replayed through the real ledger rules on USDJPY 2011-2025 (1,071 gotobi
mornings, cent account, 1.9-pip spread): the ladder reached L15 at event 13 and stayed there for 98.8% of events; 6 trades in 15
years were large enough to be real, 0 cycles closed. Placing a target at the measured 1:1 ratio did not help (88.7% at L15);
counting time exits as manual only delayed it (L15 from event 54, 2 cycles). The drawdown box held because trading stopped, not
because the flow is good. Before sizing a flow with an outcome ladder, check which outcome pays the flow and whether that
outcome moves the ladder. Evidence: research/seesare/cycle_study.py, research/results/seesare/cycle_study.json.
Confidence: high (mechanism + replay). Related: P24, P8.
Update 2026-11-01 (Phase 4): counting winning time exits as positive (owner's rule) removes this mechanism but not the
sinking: a flow near 50% winners still settles near L13 (P26).

### P26 The SEESARE ladder needs a flow that wins about 3 times in 4 to stay near the top
The ladder climbs one level per positive outcome and falls 2, 3 or 4 per negative one. For independent outcomes with win rate
p, its long-run position (exact Markov arithmetic on the ladder rules) is: p = 0.53 mean level 13.2, 0.4% of the time in
L0-L3; p = 0.65 level 9.9, 12%; p = 0.75 level 4.3, 54%; p = 0.80 level 2.3, 76%. Scaling the level sizes changes how much each
level risks, not where the ladder sits. Replay (owner's time-exit ascension rule, Tokyo fix, cent account, 1.9-pip spread, 52.6%
winning mornings): mean level 13.1-13.5, 15-191 real trades in 15 years depending on the ladder, cycles +0.02% mean at best.
Before sizing a flow with this ladder, check its win rate, not only its edge; a 1:1 flow near 50% belongs on fixed small size
(P8). Evidence: research/seesare/cycle_study_ascension.py, research/results/seesare/cycle_study_ascension.json (Markov table
in the 2026-11-01 journal entry). Confidence: high (arithmetic + replay). Related: P25, P24, P8.

### P27 A 3.6% drawdown cap per lifecycle buys about 6-7% a year from the book, not great alpha
A drawdown cap limits losses; it does not create returns. Return = edge x size x trades, and the cap limits size. With the
11-leg book (Exness Zero + swaps), settings chosen on 2011-22 and one look at 2023-25: fixed risk + the pre-trade guard
(0.75% x leg weight) made +7.2% / +6.8% a year (worst lifecycle 3.6% / 3.5%); a 16-level ladder keyed to drawdown instead of
win/loss streaks (risk = 0.3 x room left) +7.0% / +6.0%, kept trading where the guard froze; plain fixed risk had to be cut to
0.5% to respect the cap and still broke it in 2023-25 (4.7%); SEESARE's outcome ladder earned about 0 (P26). Across
lifecycles an investor still sees 4-6.5% drawdowns. On untouched Jan-Oct 2026 the capped book lost 0.6-2.3%. Adding the Tokyo
fix and the EURUSD reversal helped 2011-22 and hurt 2023-25. Size by the room left under a cap; streak ladders add nothing
(consistent with P8). Evidence: research/seesare/universe_cap_study.py, research/results/seesare/universe_cap_study.json
(48 configurations). Confidence: medium (one universe, few lifecycles per era). Related: P8, P9, P11, P24, P26.
Update 2026-11-01 (per-lifecycle scoring, 360 real trades = one unit, reset): book + drawdown ladder +6.1% mean per
lifecycle (13 completed, 0 stopped, 2011-22), book + guard +6.4% (9 completed, 5 stopped); one lifecycle is about 11
months, so the unit changes the count, not the money. Evidence: research/results/seesare/universe_lifecycle_study.json.
