# Pivot-sweep range v2 (owner's chart reading, TP1/TP2 partial) + portfolio Pareto (owner, 2026-11-12)
Written and committed before any v2 result. Strategy file `research/truth/strategies/sweep5_pivot_v2.py` (new NAME: v1 had
a logged look).

## Why v2: the v1 reading differed from the owner's charts (checked on 28-29 Oct 2026 EURUSD M5 in our data)
Our pivots match the owner's TradingView labels to 0-0.7 pip (chart clock = UTC+1). v1 missed the owner's trades because:
(1) it required a STRICT body engulf (the 29 Oct 11:05-11:20 UTC trade opens 0.1 pip past it); (2) 60% bodies (that
candle 4 is 51%); (3) a doji counted for neither colour (28 Oct 23:40-23:55, candle 3 is a doji); (4) the sweep had to be
by candle 1 or 2 (28 Oct: the sweep was 4 candles before candle 1); (5) targets were fixed when candle 4 closed, and the
order was cancelled if price reached that target before the fill (28 Oct: the order waited 2 h 05 min while price fell 24
pips, then filled at 02:05; TP1 1.11333 is a pivot that formed while it waited).
Also found: the owner's 5 Nov trade (17:05-17:20 UTC) was stopped at 17:40 UTC on the owner's own chart before the drop.

## Rules (SELL; BUY is the mirror)
- Pivots: TradingView Pivot Points High Low 10/10 (as v1, `research/sweep4/pivots.py`).
- Candles: candle 1 bullish (a doji counts as bullish), candle 2 bearish and closes below candle 1's open (LOOSE engulf),
  candle 3 bullish (doji = bullish), candle 4 bearish and closes below candle 3's open. Candles 2 and 4 bodies >= 50% of
  their own high-low (owner: "reduce the rule to 50%").
- Sweep of a live pivot high: `now` = by the candle before candle 1, candle 1 or candle 2; `recent` = by any candle from 6
  candles before candle 1 through candle 2.
- Range = candle 4's low to the highest high of the four; sell limit at 60% up (lo + 0.6 x range).
- Order life: the limit waits until filled, or until price trades at the stop level before filling (invalid), or a wider
  opposite setup replaces it, or `life` candles pass; Friday 20:30 UTC cancels. No "target first" cancel.
- At the fill: TP1 = the nearest live pivot low below the entry, TP2 = the next one (pivots known from closed candles at the
  fill time). Fewer than 2 such pivots: no trade.
- Exits (`exit`): `partial` (owner) = 60% closed at TP1, then the stop of the other 40% moves to entry - (spread +
  commission) ("breakeven plus spread"), rest at TP2; `tp1` = all at TP1; `tp2` = all at TP2.
- Stops (`stop`): `range` = the range high; `wide` = range high + 0.5 x range (owner: "could a bigger stop help?").
- One trade at a time per market and timeframe; Friday 20:30 UTC close; RoboForex Prime costs (spread decides fills,
  commission per trade, slippage on stop/time exits) + swaps; the 12 markets.

## Grid (fixed now)
5 timeframes (M1, M5, M15, M30, H1) x sweep {now, recent} x stop {range, wide} x life {24, 96 candles} x exit {partial,
tp1, tp2} = 120 configurations a market, 1,440 market x timeframe x configuration cells.

## Judging (no change from the lab)
- Truth Lab verdict (development 2011-19, validation 2020-22) with `--no-look`.
- Study: per cell trades, win rate, average win / loss in R, expectancy, profit factor, trades a month, by period,
  before and after costs; the loser study (stopped trades: did price later reach TP1/TP2 within one day; how far past
  the stop it went first; would the `wide` stop have survived).
- A cell is a portfolio candidate ("leg") only if positive after costs in each of 2011-14, 2015-18 and 2019-22 with 20+
  trades in each (the timeless rule of PREREGISTRATION_TIMELESS.md). Candidate legs, if any, join the 13 survivors.
- 2023-25 and Jan-Oct 2026 (+ GER40 to 6 Nov): looked at once, only for candidate legs, logged in
  `research/results/sweep5/LOOK.json`. Disclosed: these periods were seen for this family before (v1 look on EURUSD M5).
- Owner's 5 chart trades: replayed where we have data (28-29 Oct, 5 Nov); 11-12 Nov has no data yet.

## Portfolio Pareto (owner: A max timelessness, B balanced, C max return inside a 3.6% envelope)
Universe: the 13 survivors + any v2 legs. Risk per trade per mix is set on 2011-22 for a 3.6% lifecycle envelope (36
fortnights, 95% of bootstrapped lifecycles, as timeless_mix.py); results reported 2011-22, 2023-25, Jan-Oct 2026.
Integrity = share of calendar years 2011-2025 positive. A = the mix with the highest integrity, then the lowest 95%
envelope; B = the best two-week Sharpe among mixes with integrity >= 90%; C = the highest return inside 3.6% among mixes
with integrity >= 90%, and the same mix at 8%, 15% and 25% caps (outside the walls, as the owner allows). Candidate mixes:
timeless 10, all 13, the 11-leg book, and each with the v2 legs added. If 80-120% a year is impossible inside 3.6%, say
so and give the maximum.
