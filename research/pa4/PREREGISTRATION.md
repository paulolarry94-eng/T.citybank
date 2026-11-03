# Four-candle price action, no EMA, A+ only — pre-registration (2026-11-03, before any result)

Owner: "Take out ema and B+ and just search for that price action, compare that A+ with same setup but entry at 4th candle
high SL at the highest of the 4". Strategy `research/truth/strategies/pa4_engulf_v1.py`, detector `research/ema4/scanner.py`
`detect_pa`, test `test_ema4.py::test_price_action_a_plus_without_ema`, examples `research/results/pa4/examples/`.

- Pattern (sell; buy mirrored): four consecutive candles: 1 bullish; 2 bearish closing below candle 1's LOW; 3 bullish;
  4 bearish closing below candle 3's LOW. No EMA, no B+. (Candle 3 may be small: no size rule was given.)
- Entries compared: **x4** = sell limit at the 4th candle's HIGH (buy: its LOW), the owner's new entry; **mid50** = limit at
  50% of the 4th; **close** = market at the 4th's close. Limits live 3 candles; a new pattern deletes the pending order.
- Stops: **all4** = beyond the highest high of the four (owner); **c4** = beyond the 4th candle; + 0 / 0.25 / 0.5 ATR(14).
  (x4 with c4 and no buffer has zero risk; x4 with all4 and no buffer has zero risk whenever the 4th has the highest high;
  such trades are skipped by the 3 x cost minimum.)
- Exits: 1R-4R or ATR trailing stop 1x / 2x; out at the daily close (20:30 UTC). News days skipped. RoboForex Prime costs.
- Grid: M5 M15 M30 H1 H4 x 3 entries x 2 stops x 3 buffers x 6 exits = **540 configurations**, 12 markets, all hours.
- Reports: Truth Lab (one 2023-25 look only if a configuration passes), cycle league, control = four alternating candles
  WITHOUT both closes beyond, where/when (learn 2011-19, check 2020-22), and the entry comparison (x4 vs mid50 vs close on
  the same setups).
- Priors: the EMA versions (v1-v4, 5,680 settings) were rejected and the engulfing grade had no selection value; engulfing
  patterns were rejected before (P14). Expectation: rejection.
