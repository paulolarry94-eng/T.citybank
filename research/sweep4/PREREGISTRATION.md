# Pivot-sweep body-engulf range (owner, 2026-11-12) — pre-registration
Written and committed before any result of this study. Strategy file: `research/truth/strategies/sweep4_pivot_v1.py`.

## Owner's rule (words of 2026-11-12)
"build an indicator just like pivot points high low on trading view ... no lookback anymore ... keep 60 body of 2nd and
4th candle but they must appear immediately after a sweep of a pivot point ... range still from 4th candle low or high to
highest high or low amongst the four candles ... you enter at 60% of the range ... experiment which stop style works best
... layer the pivot points for structural stops or plain 3-15R ... find the best timeframe ... cycle centric ... 10 trades
high win rate".

## Rules (SELL; BUY is the mirror)
1. Pivots (`research/sweep4/pivots.py`): TradingView Pivot Points High Low, left = right = N bars (owner's chart: 10).
   A pivot high is known only when its N-th right bar has closed. It is live until the first later bar trades above it:
   that bar SWEEPS it.
2. Pattern: candle 1 bullish, candle 2 bearish and its body engulfs candle 1's body; candle 3 bullish, candle 4 bearish
   and its body engulfs candle 3's body (strict body engulf, as in v1-v7). Candles 2 and 4 each >= 60% body. No lookback,
   no midpoint rule.
3. Sweep, "immediately after": `c12` = candle 1 or candle 2 is the bar that sweeps a live pivot high (primary reading);
   `near` = the bar before candle 1 or any of the four candles sweeps one (wider reading).
4. Range: from candle 4's low to the highest high of the four candles. Sell limit at 60% of the range up from candle 4's
   low (lo + 0.6 x range). Opposite pending orders: the wider range wins (as v1-v7). One trade at a time per market.
5. Stops: `range` = the range high; `buf20` = range high + 20% of the range; `trail` = the range high, then trailed to each
   newly confirmed pivot high between the stop and the price.
6. Targets: fixed 3R, 5R, 8R, 10R, 15R; structural `p1` = the nearest live pivot low on the target side at least 3R away
   (at most 15R), `p2` = the next pivot low beyond it (no such pivot = no trade).
7. Positions closed Friday 20:30 UTC; costs RoboForex Prime where published (else the lab's estimate) + swaps.

## Grid (fixed now)
12 markets (XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, EURGBP, WTI, US500, NAS100, GER40, UK100, JP225) x 6 timeframes
(M1, M5, M15, M30, H1, H4) x pivot N {10, 5} x sweep {c12, near} x stop {range, buf20, trail} x target {3, 5, 8, 10, 15,
p1, p2} = 504 configurations a market, 6,048 market cells.

## How it is judged (cycle-centric)
- The Truth Lab verdict (development 2011-19, validation 2020-22; 2023-25 look only if development passes).
- Study (`research/sweep4/study.py`), per configuration pooled over markets, per timeframe, and per market x timeframe:
  trades, win rate, R a trade, edge quality s = mean / sd, and 10-trade cycles (consecutive trades in time order): share
  of cycles positive, mean R per cycle, share of cycles reaching +2% at 0.5% risk a trade (= +4R per 10 trades).
  At Prime costs and at zero cost (price move alone).
- Control: the same 60%-body four-candle patterns with NO sweep anywhere near (`none`). The sweep matters only if
  `c12` / `near` beat `none` on the same timeframe and target.
- "Best combination in the land": the 10 market x timeframe x configuration cells with the best 2011-19 edge quality
  among cells with >= 60 trades, then their 2020-22 result unchanged. With 6,048 cells the best 2011-19 cells are expected
  to look good by luck alone; only 2020-22 counts.
- 2023-25: seen before for the body-engulf family (v5 look) but never with this rule; looked at once, only for a
  configuration that passes 2011-22. Jan-Oct 2026: seen by v7's look (different rule); same condition.

## Disclosed before the study
- While checking that the two engines agree (2026-11-12), trade counts and mean R were printed for gold Jan-Jun 2019 on
  M1, M5 and M15 for 4 settings (e.g. M1 `c12` positive on 8-14 trades, M5 `c12` negative on 3-4 trades). Seen; too few
  trades to steer anything; the grid above was not changed because of them.
- Priors: v1-v7 of the body-engulf range and ~1,400 liquidity-grab variants (sweeps of PDH/PDL, weekly levels, swing
  points, SFP, sweep + MSS) were all rejected after costs; all about zero before costs. What differs here: the pivot
  sweep and the four candles are required together, with a 60% entry and structural targets.
