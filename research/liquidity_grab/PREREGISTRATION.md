# Liquidity-grab study — pre-registration (2026-10-31, before any result)

Already tested (not repeated): session / day / week LEVEL sweeps — Asian range, previous day high/low,
previous week high/low; reclaim, failed sweep, follow-through, stacked, Turtle Soup, daily/weekly candle
sweeps (596 variants: `../REPORT.md` "Daily liquidity study" and "Daily structure, round two";
scanner families AFD/PDF). One survivor (GBP weekly follow-through) is already a book leg.

New here: liquidity resting at SWING POINTS, where stops cluster.

## Common rules
Data, costs, fills, financing, rollover block, periods and tiers: identical to
`../northstar/PREREGISTRATION.md` (development 2011–19, validation 2020–22, one logged look at 2023–25,
Tier A / B criteria, neighbours, walk-forward, stress, deflated Sharpe). Market entry at the next bar
open after the signal bar closes. Management grid: target {2R, 3R, none} x trail {none, 3 ATR}; time
stop 50 bars; bias filter {off, on} = last closed H4 bar vs its EMA50 in the trade's direction.
Timeframes M30, H1, H4, D1 (D1 = broker day, 22:00 UTC). Stop cap 3 ATR.

Swing point: bar j is a swing high with strength k if its high is the strict maximum of bars j−k..j+k;
it is known at the close of bar j+k. A swing high stays "resting liquidity" until a later bar trades
above it. Lows mirror.

## Modules
- **LG1 Swing-failure sweep (SFP).** A bar trades above one or more resting swing highs, each at least
  `age` bars old, by no more than `depth` x ATR, and CLOSES back below all of them → short. Stop: that
  bar's high + 0.1 ATR. Mirror for longs. Grid: k {3, 5}; age {5, 20}; depth {0.5, 1.0}.
- **LG2 Equal-highs pool.** As LG1, but only when the swept level has another resting swing high within
  `tol` x ATR (equal highs or lows = a liquidity pool). Grid: k {3, 5}; tol {0.1, 0.25}; age 5, depth 1.0.
- **LG3 Sweep then market-structure shift (ICT).** After a bar trades above a resting swing high (age
  ≥ 5), arm: within `win` bars, the first close below the most recent swing low (strength 2) that formed
  before the sweep → short at the next open. Cancelled by a close above the sweep extreme. Stop: sweep
  extreme + 0.1 ATR. Grid: k {3, 5}; win {5, 10}.
- **LG4 New York sweeps London.** M15 bars closing 13:00–16:00 London time: a bar trades above the
  London-morning high (08:00–12:00 London) and closes back below it → short (mirror for the low).
  First per side per day. Stop: day's high so far + 0.05 x daily ATR. Time stop 24 bars (≈ 6 h).
  Management and bias grid only.

## Reporting
Each module's candidate is selected on development data at the North Star costs. For the candidate
only, an "Exness-like" sensitivity (costs x0.5, no swap) is also reported, not used for selection.
