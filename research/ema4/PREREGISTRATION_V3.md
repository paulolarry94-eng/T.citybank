# Owner's 4-flip EMA pattern — v3 pre-registration (2026-11-03, before any v3 result)

v3 = v2 (`PREREGISTRATION_V2.md`: full engulfing, 3 stops x 3 buffers, 7 exits, 2 entries, 2 grades, M5-H4, 12 markets,
1,260 configurations) + ONE correction from the owner after the v2 example charts:
"I think you make a mistake with the 1st and 2nd candle… it must be a body break". The data (GBPUSD 10 Sep 2012): the 06:00
"1st candle" opened 0.03 pip above the EMA right after a candle that had already closed 0.31 pip below it, so it was no break.
**Rule added:** each of the four candles must break the EMA from the other side: the previous candle CLOSED on the other side
(a previous close within 0.02 x ATR of the line counts as either side: the owner's EURUSD 20 Aug 2014 example has a 07:15
candle that closed exactly on the line, and the owner takes 07:20 as the 1st candle). The A+/B+ engulfing was already
body-based (the close beyond the low/high; wicks never count) and is unchanged.
Effect on counts (EURUSD M5 2011-22): A+ 381 -> 273, B+ 1,933 -> 1,793. Owner's example charts: unchanged calls.
v2 had been run (0 of 1,260 pass) before this correction; v3 is a pre-registered re-test of the corrected detector, run
with the same grid and the same reports. Code: `research/truth/strategies/ema4_flip_v3.py`; examples `results/ema4/v3_examples/`.
