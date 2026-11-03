# Four-candle price action, no EMA, A+ only — result (2026-11-03)

**Verdict: rejected.** 0 of 540 configurations made money in 2011-19 (12 markets, M5-H4, all hours, RoboForex Prime costs,
close daily, news days skipped). The owner's new entry (limit at the 4th candle's high for sells / low for buys, stop beyond
the highest of the four) is the worst of the three entries on every timeframe. Pre-registered before results
(`research/pa4/PREREGISTRATION.md`); 2023-25 not opened.

## Entries compared on the same setups (median R per trade over the stop/buffer/exit settings)
| Timeframe | Close of the 4th, 2011-19 | 50% of the 4th | **4th candle high/low (new)** | 2020-22: close / 50% / new | Trades 2011-19 (close / 50% / new) |
|---|---|---|---|---|---|
| M5 | -0.153 | -0.198 | **-0.225** | -0.122 / -0.181 / -0.194 | 37,277 / 22,558 / 7,137 |
| M15 | -0.112 | -0.142 | **-0.181** | -0.075 / -0.088 / -0.158 | 15,084 / 9,782 / 3,772 |
| M30 | -0.110 | -0.128 | **-0.118** | -0.075 / -0.133 / -0.207 | 8,400 / 5,660 / 2,300 |
| H1 | -0.086 | -0.106 | **-0.122** | -0.035 / -0.055 / -0.138 | 4,586 / 3,077 / 1,365 |
| H4 | -0.034 | -0.104 | **-0.179** | -0.021 / -0.049 / -0.078 | 1,390 / 785 / 364 |

- The deeper the limit, the worse: price that comes back to the 4th candle's high is mostly price that keeps going against
  the trade (P2). Only about 1 setup in 5 fills there, and those fills are the bad ones.
- Best of all 540 (H4, close entry, 4th-candle stop, 1x ATR trailing): -0.014R in 2011-19, -0.022R in 2020-22.
- Control: the same four alternating candles WITHOUT the 2nd and 4th closing beyond the previous candle's range do as well
  (difference -0.005R in 2011-19, +0.005R in 2020-22). The full-engulfing closes carry no information.
- Where/when (learn 2011-19, check 2020-22): 138 cells with enough trades, best t below 3 in every one, 0 pass.
Reports: `research/results/truth/pa4_engulf_v1/` (REPORT, CYCLES_LEAGUE, controls.json), `research/results/pa4/WHERE_WHEN.md`, `where_when.json`.
