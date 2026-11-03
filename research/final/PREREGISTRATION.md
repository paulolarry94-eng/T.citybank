# Final task: the best 4-flip variant + one confluence indicator — pre-registration (2026-11-03, before the final test)

Owner: "Out of all the positive variants, use the best and add another indicator that'll go very well with it to have an
additional confluence as the last task before you wrap up ... and give final result".

## Choice (made AFTER seeing 2011-22 results: hindsight, stated plainly)
Ranked every setting of ema4_flip_v1-v4 and pa4_engulf_v1 (about 6,200) with >= 200 trades and positive in both 2011-19 and
2020-22 by t over 2011-22. Best: **ema4_flip_v1, H4, entry at the 4th candle's close, stop 4th candle + 0.25 ATR, 2R, A+ and
B+**: 2011-19 +0.106R (282 trades, t 1.85), 2020-22 +0.056R (115, t 0.71), 2011-22 +0.092R (t 1.96), 7 of 12 markets
positive; its neighbours (3R, 0.1 ATR buffer) are also positive. Being the best of ~6,200, its 2011-22 numbers are inflated.

## Confluence indicator (one, fixed now)
**Trend filter: H4 50-period EMA.** Sell only if the 4th candle closes below the H4 50 EMA; buy only if above. Reason: the
pattern is a fight around the fast 10 EMA; the lab's evidence is that continuation beats reversal (P7) and trend
persistence is real on some markets (P6), so the fight is taken only when it resolves with the slower trend.

## Test (`research/truth/strategies/ema4_final_v1.py`, trend 0 = without, 1 = with the filter; `research/final/final_test.py`)
1. Truth Lab run (gate, stress, cycle goal); it looks at 2023-25 itself only if a configuration passes its gate.
2. If it does not, ONE logged look at 2023-25 for both configurations, made by `final_test.py`, written to
   `research/results/final/final_look.json` with the fingerprint (allowed: one look per fingerprint), plus Jan-Oct 2026 on
   the five markets with 2026 data (Exness ticks; EURGBP HistData).
Decision rule for the filtered version (fixed now): **WORKS (forward-test candidate)** if 2023-25 mean R > 0 with t >= 2 AND
Jan-Oct 2026 mean R > 0; **NOT PROVEN** if 2023-25 > 0 with t < 2; **FAILS** if 2023-25 <= 0. Costs: RoboForex Prime
published; closed daily, so no swaps; news days skipped.
