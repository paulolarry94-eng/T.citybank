# PRINCIPLES — what the evidence has taught (the project's learned pathways)

A principle enters only with evidence (a Truth Lab verdict or a reproducible study in this repo). Each has a
confidence: **high** (several independent studies agree), **medium** (one solid study), **prior** (reasoned,
not yet tested here). When new evidence contradicts a principle, edit it, keep the old text under
"History", and record the change in JOURNAL.md. Never delete a principle silently.

### P1 Costs decide intraday trading
Raw edge of intraday setups on XAU/EUR/GBP/JPY is about +0.01–0.02R per trade; all-in costs are about 0.07R.
Evidence: scanner (61,787 setups: gross +0.015R, costs 0.076R), ORB study, liquidity studies. Confidence: high.

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

### P5 Overnight swaps matter for multi-day trades
Gold trend 2011–18 +0.13R → +0.01R with a constant swap; four strategies 2023–25 +0.036 → +0.005R; the book
+0.063 → +0.044R. A swap-free account changes the picture (book Sharpe 1.00 → 1.64 with low costs).
Evidence: North Star rescore, TimelessCity rescore. Confidence: high (size of the Exness effect unverified).

### P6 Trend persistence is market-specific
Gold and USDJPY trend; EURUSD and GBPUSD don't (Donchian lab: gold +0.14–0.21R, JPY +0.15–0.28R, EUR/GBP
negative; TimelessCity's EUR trend leg S4 rejected). Declare markets before testing; picking them afterwards
is hindsight. Confidence: high.

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

### P11 Expect live results 30–50% weaker than heavily searched backtests
Selection bias from wide searches. Evidence: industry and statistics; not yet measured live here.
Confidence: prior (to be measured on demo).

### P12 CFD financing kills high-notional strategies
Trend + carry needs about 4x notional; CFD markups make it Sharpe 0.06 versus 0.50 on futures. Bonds are
impossible as CFDs. Evidence: multiasset study. Confidence: high.

### P13 Short volatility hides ruin
VIX carry: good years, then −97%. Evidence: multiasset study. Confidence: high.

### P14 Chart-pattern concepts have no edge on these markets after costs
ICT/SMC (FVG, liquidity grabs, structure shifts), Quasimodo, supply/demand, Malaysian SnR, engulfing, ORB:
all rejected, about 250,000 configurations. Evidence: ledger. Confidence: high (for XAU/EUR/GBP/JPY, 2011–2025).

### P15 Judge any bot by equity, not balance: realised P&L hides open risk
Averaging grids bank many small wins while a losing basket grows. Gold Hunter V9's settings, replayed 2011–2025:
realised profit positive, net −$155k to −$196k per 0.01 lot once open losses count; it showed a realised profit after
3 months in 95–100% of start dates, then wiped out 19–74% of accounts within 3 years. With the tail capped by a stop,
all 12 versions lose (no edge underneath). Evidence: research/gridbot/. Confidence: high (for grid/averaging bots on gold).
