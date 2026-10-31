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

### Q5 Equity-index RSI(2) mean reversion (watch-list) — TESTED 2026-10-31, see Answered
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

### Q9 Are inverse-volatility leg weights right for the book?
Raised by the 2026 test: the weights (inverse monthly volatility, 2011–19) put the most risk on legs that trade rarely
(JPY RSI2 1.00, GBP weekly sweep 0.93, gold S1 0.63), and those lost in 2026 while the busy, low-weight legs won; equal
weights would have done better in 2026. Choosing weights from 2026 is hindsight, so 2026 cannot decide this. Test only on
2011–22 with a walk-forward (weights fitted on past years, applied to the next), then one look at 2023–25, comparing:
inverse-vol (current), equal risk, and inverse-vol capped by trade count. FAMILY: portfolio, weighting, sizing, book.

### Q10 Flow-driven calendar edges with a known payer (declare rules before loading data)
Candidates, each with someone who must trade regardless of price: USDJPY "Gotobi" days (Japanese importers buy dollars at
the Tokyo fix on the 5th/10th/15th...; documented in research, untested here); turn of the month in US500/GER40 (salary and
pension flows); the pre-FOMC drift in US500 (documented, weaker after 2015); Japanese fiscal year-end JPY flows (March).
Priors: London 4 pm fix reversal real but only half a cost; month-end 1.4-1.9 costs but 12 trades a year (Hunt 2). Data:
USDJPY, US500, GER40 M1 in data/. FAMILY: calendar, flow, fix, seasonal.

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

## Answered
- **Q4 (partly, 2026-10-31):** the book's trend family does not transfer to US500, GER40, WTI or XAGUSD (0 of 64; oil alone
  failed 2023–25). Evidence: research/results/truth/breadth_trend_v1/, wti_trend_v1/. Still open: JPY crosses and metals
  on a swap-free account.
- **Q5 (2026-10-31):** RSI(2) dip-buying is positive on US500 and GER40 in every period (2023–25 +0.09R, PF 1.67, 83 trades) but
  not significant, negative under stress, and about zero after costs on NAS100, UK100 and JP225. Rejected at the lab's costs;
  the raw edge (+0.02 to +0.09R) is real but small. Revisit only with measured index commissions on a swap-free account.
  Evidence: research/results/truth/index_rsi2_v1/, index_rsi2_breadth_v1/.
