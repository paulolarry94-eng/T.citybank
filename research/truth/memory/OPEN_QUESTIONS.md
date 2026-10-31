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
**Declared 2026-10-31, before any data was seen: US500, GER40, WTI, XAGUSD** (owner asked for 4 markets).
Reasons: stocks (US500; also allows Q5), European stocks in London hours (GER40), energy (WTI), and the
direct test of whether the gold families transfer (XAGUSD). GER40 and US500 move together, and so do silver and
gold, so these add less independence than four unrelated markets would. Not chosen: BTCUSD (Dukascopy history
starts later than 2011) and natural gas (high costs). Families must be declared before the first run. To check
when the data arrives: start years (Dukascopy returned "not found" for WTI on 2011-06-07), oil contract-roll
price jumps, and costs and swaps from the Exness export (Q1). How-to: `tools/DATA_HOWTO.md`.

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

### Q8 EUR/USD daily close-beyond reversal (owner's spec): worth a small forward test?
Tier B (`research/results/truth/eurusd_close_beyond_reversal_v1/REPORT.md`): +0.04R per trade, Sharpe 0.49 and falling
(0.59 → 0.48 → 0.23), +0.9% a year at 1% risk; weakens the book after 2017 (0.84 → 0.76). Watch-list only unless real
Exness costs (Q1) or a 2026 forward test show it stronger. FAMILY: reversal, daily, stop-entry, eurusd.

## Answered
(none yet)
