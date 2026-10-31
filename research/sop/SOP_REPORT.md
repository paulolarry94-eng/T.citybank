# The owner's 4-leg engulfing SOP — verdict (2026-10-31)

**Rejected.** Coded from the 12 case-study documents and the owner's answers, the detector finds the owner's own setups
(same legs, entry and stop on 6 cases). Tested on every setup it finds in 2011–2025, and on February–October 2026
(untouched by anything), the method loses money: about −0.1 to −0.35R per trade (R = the amount risked), and it is
slightly negative even before costs.

## How the rules were coded and checked (`research/sop/parity_cases.py`)
| Case | Owner | Coded rules |
|---|---|---|
| EU#3 (29 Oct 2025, M30 sell) | win | same legs, entry 1.1664, stop 1.16721, 70%; win |
| GU#1 (29 Jan 2026, M30 buy) | loss | same entry 1.37631 and stop; loss |
| Document 1 (30 Jan, M5 sell) | rejected for time | same legs, entry 1.18832 (owner 1.18829); would have won |
| Document 2 (29 Jan, M5 sell) | hesitated | same legs, both slow engulfings, filled at the owner's 14:30; win |
| #6 (15 Jan, M5 buy) | win | same legs, entry 1.15989 (owner 1.15987), stop 1.15897 (1.15896), filled 17:06 (owner 17:05); win |
| #10 (23 Jan, M15 buy; doc dated 29 Jan) | win | same entry 1.17325 (1.17328) and stop 1.1725 (1.17247); the retest came during the 3-candle swing confirmation |
| EU#4, #8 | rejected | not flagged |
| EU#1, #7 | win, loss | same legs, different entry % |
| EU#2, #9 | wins | missed |
Several documents carry the screenshot date, not the trade date; the real dates were found by price level.

## Results (Exness Zero costs: measured spread + commission + slippage; limit fills at the real spread)
| | 2011–19 | 2020–22 | 2023–25 | Feb–Oct 2026 |
|---|---|---|---|---|
| Owner's setup, M5 | −0.18R | −0.14R | — | −0.09R (376 trades, 30% win) |
| Owner's setup, M15 | −0.14R | −0.19R | — | −0.35R (126 trades, 21% win) |
| Owner's setup, M30 | −0.14R | −0.12R | — | +0.02R (82 trades, 34% win) |
| Best of 756 (M15, overlap, perfect, retest 10, breakeven) | +0.08R | −0.24R | −0.11R (97 trades) | −0.24R (18 trades) |
Owner's setup = swing 3, perfect or slow engulfing, owner's window, retest within 10 candles. Before costs it is
−0.02 to −0.05R per trade; costs add 0.10–0.14R because the stops are small. With a 2R target and these costs, a win
rate of about 37% is needed; the full population wins 21–34%.

## The owner's questions (756 configurations per market, 2011–2022)
| Question | Answer |
|---|---|
| Best trading window | all negative; New York 16–20 UTC least bad (−0.04R) with few trades; owner window −0.15R |
| Swing 3, 4 or 5 candles | no difference (−0.15R each) |
| Perfect vs slow engulfing | perfect a little better in 2011–19, worse in 2020–22 |
| Retest within 5, 10 or 20 candles | no difference |
| Breakeven at 1:1 | +0.01 to +0.02R in ~70% of paired settings 2011–22, but worse in Feb–Oct 2026 |
| Timeframe | M30 least bad, M5 worst |
| Gold H4 / daily | 0 of 72 pass; daily setups are rare (none in Feb–Oct 2026) |
Deflated Sharpe of the best FX setting after 756 tries: 0.001.

## Why the case studies looked so good
The detector finds about 4,600 of these setups on EURUSD M30 alone in 2011–2025. The documents show 12, chosen after
the fact and mostly winners. Of the owner's cases the code reproduces, 4 of 5 won; of all setups, 21–34% win. A
journal that records every setup the rules produce, not the memorable ones, is the only way to see the real hit rate.
Case #7's loss: EUR/USD jumped 5–6 pips a minute at 15:00 UTC (10:00 New York, US data time); the 7-pip stop was hit
within minutes of the fill.

Evidence: `research/results/truth/sop_4leg_v1/`, `sop_4leg_gold_v1/`, `research/results/sop/` (parity, holdout).
