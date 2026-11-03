# Owner's 4-flip EMA pattern — v2 pre-registration (2026-11-03, before any v2 result)

v1 (`ema4_flip_v1`, rejected 2026-11-02, results seen) -> the owner changed ONE rule and asked for more stops, a trailing
stop and better settings: "instead of the validation being 4th candle close below the open of 3rd let it be the low, so it's
a full engulfing candle. Same for A+ ... adding some stops above 4th candle ... same timeframes and markets ... arrange the
conditions with the best rewards, try a trailing stop, use your intelligence to find better settings to maximize rewards."
Owner's chart marks (EURUSD 20 Aug 2014): the 1st and 3rd candles' highs (engulf levels for a buy) and the 3rd candle's
and the pattern's lows (stop levels).

## Rules (`research/truth/strategies/ema4_flip_v2.py`; tests `test_ema4.py` 7, `test_ema4_v2.py` 3, `test_ema4_strategy.py` 4)
- Pattern as v1 (four consecutive candles crossing the 10 EMA in turn, a doji does not count) with FULL engulfing:
  B+ = the 4th closes below the 3rd candle's LOW (sell) / above its HIGH (buy); A+ = also the 2nd beyond the 1st's low/high.
- Entry: 50% of the 4th candle (limit, 3 candles) or the 4th candle's close. One position per market; a new pattern deletes
  the pending order; news days skipped; stop >= 3 x cost; out at the daily close (20:30 UTC).
- Stop: 4th candle (`c4`), 3rd and 4th candles (`c34`), all four (`all4`); + 0 / 0.25 / 0.5 ATR(14).
- Exit: 1R / 2R / 3R / 4R target; ATR trailing stop 1x or 2x (no target); EMA exit (no target; out when a candle closes back
  across the 10 EMA against the trade).
- Grid: M5 M15 M30 H1 H4 x entry 2 x stop 3 x buffer 3 x exit 7 x grade 2 = **1,260 configurations**, 12 markets, all hours.

## Tests (same protocol as v1)
Truth Lab (gate, validation 2020-22, walk-forward, stress, deflated Sharpe over 1,260; one 2023-25 look only if a
configuration passes), cycle league (all 1,260 ranked by edge quality), control (same trades on four-flips WITHOUT the full
engulfing), where/when learn-then-check (`where_when.py ema4_flip_v2`: best of 252 settings per market x timeframe x session
on 2011-19, must hold in 2020-22 with t >= 2), descriptive profile (`profile.py ema4_flip_v2`).

## Not clean, said plainly
The owner changed the rule after seeing v1's results; v2 is a pre-registered test of the new rule, not a blind first look.
1,260 configurations plus 180 cells is a large search: the best numbers will be inflated by the choice; the 2020-22 check,
the gate and the deflated Sharpe are the guards. Priors: v1 and every earlier idea of this family rejected (P1, P2, P3, P14).
