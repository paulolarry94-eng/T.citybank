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

### P2 Resting limit / retest entries suffer adverse selection
They fill when price runs against you and miss the trades that work. QM: retest worse than market entry in
97% of paired settings (−0.081R); supply/demand −0.035 to −0.084R; FVG midpoint depth worse in 96%.
Evidence: North Star ablation. Confidence: high.

### P3 Higher timeframes beat lower ones
Costs per unit of risk shrink and noise falls. FVG M5→H1 +0.15R in every paired setting; QM M15→H1 +0.05R.
Evidence: North Star ablation. Confidence: high.

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

### P12 CFD financing kills high-notional strategies
Trend + carry needs about 4x notional; CFD markups make it Sharpe 0.06 versus 0.50 on futures. Bonds are
impossible as CFDs. Evidence: multiasset study. Confidence: high.
More evidence (2026-10-31): single-market trend trades on index and commodity CFDs pay 0.06–0.33R financing per trade
(US500 0.33R, GER40 0.26R, silver 0.12R, oil 0.06R at the lab's estimates), more than the raw edge on indices and silver.

### P13 Short volatility hides ruin
VIX carry: good years, then −97%. Evidence: multiasset study. Confidence: high.

### P14 Chart-pattern concepts have no edge on these markets after costs
ICT/SMC (FVG, liquidity grabs, structure shifts), Quasimodo, supply/demand, Malaysian SnR, engulfing, ORB:
all rejected, about 250,000 configurations. Evidence: ledger. Confidence: high (for XAU/EUR/GBP/JPY, 2011–2025).
More evidence (2026-10-31): the owner's 4-leg engulfing SOP (calibrated on their own case studies): 2 of 756 FX settings
pass the gate and then fail; 0 of 72 on gold H4/D1; February–October 2026, untouched: −0.09 to −0.35R per trade.

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

### P17 Active hours picked from a backtest do not carry forward
Choosing a strategy's best trading hours on past data mostly selects luck. Dark Mimas family: best 6 hours picked on
2011–19 made +1.11 pips per trade before costs, then −0.13 in 2020–25 (0 of 18 positive after costs). Grid best hours:
+2.76 → +0.18 pips per basket. The lab test with session windows declared in advance (osc_turn_sessions_v1:
6 windows × 3 timeframes × 3 oscillators × follow/fade, 4 markets) gave 0 of 108 passing, and every window lost about the
same (−0.04 to −0.05R). The big winners of high-frequency bots are trend days that start near the London or New York
open, and a trend day is known only after it ends. A time filter must survive a learn-then-check split before anyone
trusts it. Evidence: research/gridbot/DARK_MIMAS_REPORT.md, research/results/truth/osc_turn_sessions_v1/. Confidence: medium-high.

### P18 Case studies select winners; only a coded scan of every setup shows the hit rate
The owner's 4-leg SOP documents showed mostly wins. Coded so that it reproduces the owner's own cases (same legs, entry and
stop on 6 of 12), the rules find about 4,600 setups on EURUSD M30 alone in 2011–2025; 4 of the 5 reproduced cases won,
but only 21–34% of all setups win, below the ~37% the 2R target needs after costs. Before trusting any discretionary
pattern, code it, check it against the trader's examples, then test every occurrence. Evidence: research/sop/SOP_REPORT.md.
Confidence: medium-high.
More evidence (2026-10-31): looking for "the conditions that made it win" across 23,000 setups and 19 features known at entry,
none of 56 single conditions was profitable even in the learning years (2011-19); the best 2-condition rule lost there too.
When nothing separates winners in-sample, the wins are noise around a negative mean. Evidence: research/results/sop/winning_conditions.json.

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
