# Final result: the owner's EMA / four-candle patterns (2026-11-02 to 2026-11-03)

**Outcome: no version of the pattern has an edge after costs, and the best one fails on data it had never seen.** The best of
about 6,200 settings, with an added H4 50-EMA trend filter, lost 0.03R a trade in 2023-25 (86 trades, t -0.4) and lost again
in Jan-Oct 2026 (6 trades). Without the filter it lost 0.12R a trade in 2023-25. Verdict by the pre-registered rule: FAILS.

## The final test (pre-registered in `research/final/PREREGISTRATION.md` before it ran; one logged look at 2023-25)
Best variant (chosen with hindsight from 2011-22): 4th candle closes beyond the 3rd candle's open (A+ and B+), H4, entry at the
4th candle's close, stop beyond the 4th candle + 0.25 ATR, 2R target, closed daily, RoboForex Prime costs, 12 markets.
Confluence added: trade only with the H4 50-EMA trend (sell below it, buy above it).

| | 2011-19 | 2020-22 | **2023-25 (unseen)** | Jan-Oct 2026 (5 markets) |
|---|---|---|---|---|
| Without the filter | +0.106R, 282 trades, t 1.85 | +0.056R, 115, t 0.7 | **-0.122R, 117, t -1.66** | -0.30R, 7 trades |
| With the trend filter | +0.116R, 198, t 1.79 | +0.069R, 84, t 0.7 | **-0.033R, 86, t -0.40** | -0.42R, 6 trades |
The filter helped (10 of 12 markets positive in 2011-19 instead of 7; less loss in 2023-25), but it cannot add an edge the
pattern does not have. Details by market and year: `final_look.json`; lab report: `research/results/truth/ema4_final_v1/`.

## Everything tested in this family
| Test | Settings | Result | Report |
|---|---|---|---|
| 3:30 EMA retest (v1, v2 1:1 with stop grid) | 48 + 16 | rejected; 2026 summer lead unproven | `research/results/owner330/RESULT.md` |
| 4-flip EMA v1 (4th beyond the 3rd open) | 640 | rejected; only H4 thin positive | `research/results/ema4/RESULT.md` |
| 4-flip v2-v4 (full engulfing, real breaks, obvious breaks; stops, trailing) | 5,040 | rejected; engulfing grade adds nothing | `research/results/ema4/RESULT_V2_V4.md` |
| Four candles, no EMA, A+ only; entry at the 4th candle high | 540 | rejected; 4th-candle-high entry worst | `research/results/pa4/RESULT.md` |
| Best variant + H4 50-EMA trend filter, unseen 2023-25 and 2026 | 2 | FAILS | this file |

## What was built and stays useful
- Detector with every rule the owner taught (`research/ema4/scanner.py`), replay of the owner's charts, chart printers,
  random audit charts, 2026 second data feed (`data/holdout/histdata/`).
- Lab tools: cycle-centric selection (`SELECT_BY = "s"`), trades scored in time order (cycles, lifecycles), cycle league
  (`research/truth/cycles_league.py`), controls pooled across markets and keyed by timeframe (`research/truth/controls.py`),
  where/when learn-then-check (`research/ema4/where_when.py`).
- Data fix: HistData's clock (P29). 164 tests pass.
