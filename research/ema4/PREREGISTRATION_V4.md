# Owner's 4-flip EMA pattern — v4 pre-registration (2026-11-03, before any v4 result)

v4 = v3 (`PREREGISTRATION_V3.md`: full engulfing, each break from the other side of the EMA) + the owner's correction
"the breakouts too should be obvious ... the breakout one sell is not obvious that the body began above the EMA, please make
sure you find exactly my strategy".
**Rule added:** each of the four candles must OPEN at least `clear` x ATR(14) on one side of the 10 EMA and CLOSE at least
`clear` x ATR(14) on the other. "Obvious" is not a number the owner gave, so three levels are tested: 0.05 / 0.1 / 0.2 ATR
(0.1 ATR is about 0.3 pip on EURUSD M5). Calibration from the owner's approved charts (stated before results): the faintest
candle is 0.08 ATR on 20 Oct 2026 (0.25 pip; on the owner's TradingView feed that close is also barely above the line), 0.16
ATR on the EURUSD 20 Aug 2014 template; the 27 Oct 2026 chart's 3rd candle sits on the line (about 0.01 ATR) and fails every
level. Effect (EURUSD M5 2011-22, A+ / B+): v3 273 / 1,793; clear 0.05 169 / 966; 0.1 106 / 485; 0.2 38 / 97.
Grid: M5 M15 M30 H1 H4 x entry 2 x stop 3 x buffer 2 (0, 0.5 ATR) x exit 7 x grade 2 x clear 3 = **2,520 configurations**,
12 markets. Same reports as v2/v3 (lab, cycle league, control, where/when, profile). Examples at clear 0.1:
`research/results/ema4/v4_examples/`. v3 is run as well (clear 0) for comparison; v2 and v3 results were seen before this rule.
