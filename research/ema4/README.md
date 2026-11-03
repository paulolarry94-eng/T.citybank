# Owner's 4-flip EMA pattern — understanding, tools and open questions (2026-11-02, before any backtest)

> **Status 2026-11-03: family closed, all versions rejected.** Final result: `research/results/final/FINAL.md`.
> Versions: v1 (`ema4_flip_v1`, 4th beyond the 3rd open) · v2 full engulfing (`PREREGISTRATION_V2.md`) · v3 breaks from the
> other side (`PREREGISTRATION_V3.md`) · v4 obvious breaks (`PREREGISTRATION_V4.md`) · no-EMA price action
> (`research/pa4/`) · best variant + trend filter (`research/final/`). Results: `research/results/ema4/RESULT.md`,
> `RESULT_V2_V4.md`, `research/results/pa4/RESULT.md`.

## The rule as understood (the owner's words: "4 interactions with the 10 EMA", "THIS IS THE ONLY PATTERN")
One timeframe (M5), one pattern. SELL (BUY is the mirror): four consecutive candles whose bodies cross the 10 EMA in turn:
1 out above (bullish, opens at/below the line, closes at/above it), 2 back in below (bearish), 3 out above, 4 back in below.
- **B+**: the 4th closes below the 3rd candle's open. **A+**: also the 2nd closed below the 1st candle's open.
- Only the 2nd engulfing, or none: rejected. Overlapping windows count (a sell on 1-4 and a buy on 2-5 can both exist).
- Trade: entry at 50% of the 4th candle (wick to wick), stop beyond the 4th candle; targets 1R-4R, find the best.

## Tools
- `scanner.py`: the detector (EMA = TradingView ema(close,10), the line drawn on each candle; options for line tolerance,
  minimum body and engulfing margin, all off by default). Tests: `research/truth/tests/test_ema4.py` (6).
- `replay.py`: the owner's six charts, found in our EURUSD data by matching their closes (best match 0.1-0.2 pip; next best
  day 3-17 pips off): 20, 22, 26 Oct (chart 4) and 27 Oct 2026 (charts 1 and 2/3). Output `research/results/ema4/replay.json`.
- `charts.py`: draws every pattern numbered 1-4 with entry and stop (`research/results/ema4/charts/`).

## Replay: 5 of 7 calls match
| Chart | Owner | Scanner (our feed) | Why |
|---|---|---|---|
| 1 (27 Oct 16:40) | B+ sell, won | no pattern | the 3rd candle (16:50) is a doji 0.02 pip under the EMA in our feed; a 0.2-pip bullish body in the owner's |
| 2/3 (27 Oct 06:35) | rejected sell | B+ sell | the 4th closes 0.3 pip below the 3rd open in our feed, 0.1 pip above in the owner's |
| 4 (26 Oct 15:35) | rejected buy | rejected (only the 2nd engulfed) | match |
| 5 (22 Oct) | rejected buy and sell | both rejected: in each, only the 2nd candle engulfed | match |
| 6 (20 Oct) | B+ sell (failed), A+ buy (won) | B+ sell, A+ buy | match; but the A+ buy's 50% entry was never revisited |
Both misses are sub-pip feed differences; no tolerance or margin setting fixes both (a margin that fixes chart 2 breaks chart 6).
The bot will decide on its own broker's candles, so such borderline cases will always differ from TradingView.

## Facts that shape the test (counts and stop sizes only, EURUSD 2011-22; no results looked at)
- About 0.31 A+ and 0.62 B+ patterns a day on EURUSD, spread over all 24 hours.
- Stop distance (50% entry to the 4th candle's extreme): median 2.1-2.35 pips; 1.5 pips in Asian hours, about 3 pips in
  London/New York. RoboForex Prime's 0.55-pip round trip is 0.23-0.26R a trade (0.35R in Asian hours).
- Priors: every earlier idea of this family (owner's 4-leg engulfing SOP, Leg 34, the 3:30 retest; M5 EMA/engulfing with limit
  entries) was rejected, mostly because before-cost results were about zero and costs took 0.1-0.2R (P1, P2, P14).

## Open questions for the owner (the test runs once these are settled; proposed defaults in brackets)
See the session message of 2026-11-02; answers are recorded in PREREGISTRATION.md before the first backtest.
