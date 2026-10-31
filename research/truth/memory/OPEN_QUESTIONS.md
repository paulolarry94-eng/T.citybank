# OPEN QUESTIONS — the queue (highest value first)

Move a question to "Answered" with a link to its evidence once it is resolved. New ideas from the owner go
here first, with FAMILY tags, so priors can be checked before testing.

### Q1 What are the real Exness Zero costs and is the account swap-free?
Blocks everything that depends on costs (could move the book from Sharpe 1.00 to 1.64). Owner action: run
`mt5/NorthStarExport.mq5`, push the folder, report the commission per lot. Then:
`python3 tools/ingest_mt5.py <folder>`, replace estimates in `research/truth/costs.json`, re-score.

### Q2 Does the TimelessCity EA trade like the research?
Compile v2.42, Strategy Tester 2023–2025 (real ticks), compare with
`research/results/northstar/parity/timelesscity/*.csv` using `tools/parity_check.py`.

### Q3 How much weaker is live than the backtest? (tests P11)
Measure on 3–6 months of demo with `research/northstar/weekly.py`.

### Q4 Breadth: do the book's families work on new markets?
Needs M1 data for ~27 markets (`tools/dukascopy_m1.py --all 2011 2025` on a home PC; Dukascopy throttles
cloud IPs). Pre-register markets and families before running through the Truth Lab.

### Q5 Equity-index RSI(2) mean reversion (watch-list)
+0.41 Sharpe on stock indices in the daily futures data (`research/multiasset/mr_breadth.py`). Needs index
data and a pre-registered Truth Lab run.

### Q6 Futures route for trend + carry
Works only on real futures (P12). Owner decision: an MT5 futures broker (CME micros) or IBKR.

### Q7 Prop accounts (FTMO-style): which per-phase risk and which guard maximise pass x payout?
Replay (`research/prop/ftmo_sim.py`) says the book passes both phases in 33-54% of 12-month windows at 1-1.5% risk
but slowly (median 6-8 months for +10%). To test: a near-barrier risk brake (rational in prop accounts because
-10% ends the account, unlike P8's personal-account finding), phase-specific risk, an open-risk cap that makes a
5% daily breach structurally impossible, and FTMO's real costs/swaps on a Swing account. FAMILY: prop, risk, sizing.

## Answered
(none yet)
