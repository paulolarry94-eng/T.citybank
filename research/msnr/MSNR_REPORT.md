# Gold 6–8 pm Nigeria time, Malaysian SnR, engulfing and failed engulfing

## 1. Buying gold 18:00–20:00 Nigeria time (WAT = UTC+1, no daylight saving) — `gold_wat.py`

Buy at 17:00 UTC, sell at 19:00 UTC, every weekday, all-in cost $0.45.

| window | trades | before costs | after costs | 2011–18 t | 2019–25 t | years positive |
|---|---|---|---|---|---|---|
| 18:00–20:00 WAT | 3,544 | +0.01 cost (zero drift) | −$0.44 | −4.5 | −3.2 | 0 / 15 |

No neighbouring window (17–20, 18–21, 18:30–20, 18–22), neither US clock season, and no single
weekday has a positive drift. **No edge.**

## 2. Malaysian SnR, engulfing, failed engulfing — `msnr_lab.py`, `grid.py`

There is no official rulebook; community definitions were taken from the sources listed at the
end and the main disagreements (pivot depth, what counts as a touch) were tested side by side.

- **A-level** (resistance): bullish candle followed by a bearish candle, level = the bullish
  close, which must be the highest close of bars j−k..j+k (pivot depth k = 1, 3). **V-level**: mirror.
- **Fresh** until the first wick touches it; only that first touch is traded. Expiry 300 bars.
- **Storyline**: last closed daily bar above (buy only) or below (sell only) its EMA50.
- Modes: limit order at the fresh level (stop beyond the formation wick); engulfing
  confirmation after the touch; **failed engulfing** (the engulfing bar's extreme is closed
  beyond within 3 bars: trade the break, stop beyond the engulfing bar's other side); RBS/SBR
  (broken level flips role, buy/sell the first retest); engulfing and failed engulfing with no
  level (baseline). Targets 1/2/3R, time stop 50 bars, one position at a time.
- Levels and entries on the same timeframe (M15, M30, H1, H4) or higher-timeframe levels with
  lower-timeframe entries (M15<H1, H1<H4, M15<H4, H1<D1, H4<D1). For gold, every configuration was
  also run restricted to entries 18:00–20:00 WAT (the confluence test).
- Same 1-minute fill rules and costs as all other studies.

**2,202 configurations. 8.5% are positive; median −0.125R per trade.** Average result in
2019–2025 by mode: limit −0.12R, engulfing −0.11R, failed engulfing −0.11R, RBS/SBR −0.15R, engulfing
with no level −0.11R, failed engulfing with no level −0.09R. Fresh levels add a little information
to an engulfing signal (gold H1: −0.05R at a level vs −0.09R anywhere) but never enough to pay
costs. The 18:00–20:00 WAT restriction does not help.

**Selection test:** picking the best configurations on 2011–2018 alone does not work:
the top 10 by in-sample Sharpe earned −0.01R on average in 2019–2025, the top 100 −0.07R.

## 3. The one surviving cluster (watch-list, not traded yet)

Gold, M15 entries at fresh H1 levels (pivot depth 3), **failed engulfing in the direction of the
daily storyline**: price reaches a fresh H1 resistance, a bearish engulfing forms, then within
3 bars a candle closes above that engulfing's high → buy at the next open (stop below the
engulfing bar, target 3R). Mirror for sells at support in a down storyline.

| | trades/yr | R per trade | 2011–18 | 2019–25 | eras 11–15 / 16–18 / 19–25 | t | longs / shorts |
|---|---|---|---|---|---|---|---|
| gold, 3R | 11.2 | +0.40 | +0.49 | +0.33 | +0.51 / +0.47 / +0.33 | 2.76 | +0.16 / +0.83 |
| USDJPY, same rule | 13.8 | +0.24 | +0.33 | +0.13 | +0.49 / +0.08 / +0.13 | 1.95 | +0.35 / +0.05 |

For it: pivot depth 3, 4 and 5 all work (+0.40 to +0.56R); every target from 1R to 5R is positive;
USDJPY agrees. Against it: M30 entries on the same levels are flat (+0.05R), H4 levels do not
work, EURUSD and GBPUSD lose (−0.23R / −0.25R), and with 2,202 configurations tried a t of 2.8 is
below the multiple-testing bar (about 4.1). Gold 2024 was −0.86R.

Added to the 11-leg book (if real): monthly Sharpe 1.52 → 1.75 (2019–25: 1.35 → 1.52).
**Recommendation: forward-test it (paper or minimum size) for 6–12 months; add it to the book only
if it keeps near its tested expectancy.**

## 4. Is 60–120% one configuration away? — `../hunt/frontier.py`, `../hunt/growth60.py`

The expanded 11-leg book with the drawdown brake (600 reshuffled 15-year histories per row):

| typical DD | open-risk cap | per-trade cap | median CAGR | 1-in-20 CAGR | 1-in-20 DD | worst DD |
|---|---|---|---|---|---|---|
| 25% | 30% | 4% | 51% | 32% | 31% | 35% |
| **30%** | **40%** | **6%** | **64%** | **38%** | **36%** | **42%** |
| 35% | 40% | 6% | 77% | 45% | 42% | 48% |
| 40% | 50% | 8% | 93% | 53% | 48% | 54% |
| 45% | 60% | 10% | 109% | 61% | 53% | 60% |

60% a year is reachable at roughly 30% typical drawdowns. 120% needs about 45% typical drawdowns
and a 60% worst case. The book's edge (Sharpe ~1.5) fixes this trade-off; only a better edge moves it.

**Growth 60 with fortnightly payouts** (salary mode, as in Hunt 2):

| pay per fortnight | paid per year | on time: real / typical / 1-in-20 | trading DD: typical / 1-in-20 |
|---|---|---|---|
| 1.00% | 26% | 94% / 99% / 87% | 30% / 36% |
| 1.25% | 32% | 94% / 98% / 83% | 30% / 36% |
| **1.50%** | **38%** | 94% / 97% / 78% | 30% / 36% |
| 1.75% | 43% | 94% / 94% / 71% | 30% / 36% |
| 2.00% | 47% | 94% / 90% / 64% | 30% / 36% |

Edge-decay stress at 1.50%: −0.02R per trade → on time 88% typical / 56% 1-in-20, DD 1-in-20 40%;
−0.05R per trade → 55% / 22%, DD 1-in-20 48%.

## Sources consulted for the Malaysian SnR definitions

- [Malaysian SnR by DanielM (TradingView, open source)](https://in.tradingview.com/script/yqRdpnSH-Malaysian-SnR-by-DanielM)
- [Malaysian SnR Storyline (TradingView)](https://kr.tradingview.com/script/zHJLrkfS-Malaysian-SnR-Storyline)
- [Malaysian SnR open-source script (TradingView)](https://my.tradingview.com/script/iWgxW7bW)
- [Advanced MSNR Strategy notes (Knowt)](https://knowt.com/note/14ba7f25-848c-4200-8672-0d191f1dbd13/Advanced-MSNR-Strategy)
- [Malaysian SnR concept (LuxAlgo)](https://www.luxalgo.com/library/concept/malaysian-snr.md)
- [SnR Key Level by RWBTradeLab (MQL5; failed-engulfing idea)](https://www.mql5.com/ko/market/product/185329)
- [Malaysia SNR Levels and Storyline (MQL5)](https://www.mql5.com/ru/market/product/122784)

(The LuxAlgo and TradingView pages could not be opened from this session's network; their
search summaries were used.)
