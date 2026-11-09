# The most timeless mix of the survivors (owner, 2026-11-09)
Pre-registration, written and committed before any number of this study.

Owner: "run the final check and config mix ... without my instruction find the most timeless mix ... put it all together,
get something closest to what can make sense".

## Universe
The 13 survivors as loaded by `research/seesare/daily_queue_study.py` (the 11-leg book and the two lab survivors
tokyo_fix_gotobi_v1 and eurusd_close_beyond_reversal_v1), Exness Zero costs + swaps (swap-free reported separately), each
leg with its existing weight (book: inverse volatility fixed on 2011-19; lab legs: the same formula). No new strategies, no
re-optimised weights.

## "Timeless" (fixed now, uses only data before 2023)
A leg is timeless if its R per trade after costs and swaps is above 0 in EACH of three eras: 2011-2014, 2015-2018,
2019-2022 (by entry time), with at least 10 trades in each era. The timeless mix = the timeless legs with their weights.

## How it is judged
- Periods: 2011-22 (where the rule was chosen; in-sample), 2023-25 (seen before by the book's look, but not by this rule),
  January-October 2026 (the book legs' trades were seen in the champion check; the Tokyo fix and the EURUSD reversal are run
  on 2026 data here for the first time, with their lab settings unchanged).
- Two-week cycles: 14-day blocks from Monday 2011-01-03, a trade counts in the fortnight it closes (as in
  research/goal/fortnight_cycle.py). Risk per trade for a 3.6% and an 8% lifecycle cap (36 fortnights, 95% of bootstrapped
  lifecycles) is set on 2011-22 only, then applied unchanged to 2023-25 and 2026.
- Compared side by side with the same method: the timeless mix, all 13 survivors, the 11-leg book.
- Decision rule: the timeless mix is the recommendation if its fortnight Sharpe over 2023-25 + Jan-Oct 2026 is at least that
  of all 13 survivors; otherwise all 13 survivors are.
