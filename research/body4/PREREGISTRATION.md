# Body-engulf 4-candle range (owner, Q30) — pre-registration (2026-11-08, written before any backtest result)

Boom 1000 is out of scope (owner, 2026-11-08). Rules: the owner's charts of 2026-11-07 and the corrections of 2026-11-08,
coded in `research/body4/body4_orders.py` (the specification, plain Python) and run by the identical fast engine
`research/body4/body4_fast.py` (tests: `research/truth/tests/test_body4.py`, incl. trade-for-trade parity on 2019 gold).
Lab strategy file: `research/truth/strategies/body4_range_v1.py`.

## Rules (main version in bold)
- Pattern: 4 alternating candles; the 2nd and 4th BODIES engulf the 1st and 3rd bodies (wicks ignored; dojis are neither).
  Range = high-low of the four candles, wicks included.
- Lookback: **at least 3 of the 5 candles before candle 1 go the trade's way** (dojis count for neither); also tested off.
- Intent: **candle 4 must close on the trade's side of the midpoint, else skip** (owner: "shows no intent").
- Entry: limit at **50% (midpoint)** or at a 70% pull-back (buy: high - 0.7 x range; sell: low + 0.7 x range).
  Skipped if price is already through the level when the order would be placed.
- Stop at the range end + buffer **0** / 5 / 10 / 20% of the range; target 4R; breakeven at +2R **on** / off.
- Orders: every valid same-direction setup waits; the first to fill removes the others (owner: "when the setup forms
  higher and is triggered, the lower one is removed"). An opposite setup replaces the waiting orders only if its range is
  wider than every one of them. An order is cancelled when price reaches its target before it fills. While a trade is
  open, new setups are ignored (assumption, not contradicted by the owner).
- Week: no setups Friday 20:30 UTC - Sunday 23:00 UTC (= Monday 00:00 Lagos); everything closes Friday 20:30 UTC.
  No fills in the daily rollover 20:30-23:00 UTC. Overnight holds Monday-Thursday pay the lab's swap.
- Costs (RoboForex Prime published): spread decides whether a price is reached (bid data; ask = bid + spread),
  commission per trade, slippage on stop and market exits only. XAGUSD and UK100 (not on Prime): the lab's all-in
  estimate split 50/25/25. Setups whose 1R is not bigger than the round-trip cost cannot be traded (skipped).
- Unclear minutes (M1 data cannot order events inside a minute): stop before target; a fill and a stop in the same
  minute count as a stop; a target and a fill in the same minute cancel the order. Counted and reported.

## Search (fixed)
12 markets (XAUUSD XAGUSD EURUSD GBPUSD USDJPY EURGBP WTI US500 NAS100 GER40 UK100 JP225) x timeframes M1 M5 (stage 1,
the owner's first ask) and M15 M30 H1 H4 (stage 2) x entry 2 x breakeven 2 x buffer 4 x lookback 2 = **192
configurations**. The Truth Lab protocol decides: development 2011-19 gate (>= 200 trades, both eras > 0, >= 75% of
markets > 0), selection by edge quality s, validation 2020-22, walk-forward, stress (costs x1.5, swaps x2, +1 minute),
deflated Sharpe for all 192, ONE logged look at 2023-25 only for a gate-passing selection, then Jan-Oct 2026.

## Reported, never used to select
- Paired comparisons over every market x timeframe x other settings, 2011-19 and 2020-22 separately: breakeven on vs
  off (profit factor and R per trade: the owner's question), 50% vs 70% entry, the four buffers, lookback on vs off.
- Owner's "volume" objective: total R per year and profit factor next to edge quality for every configuration.
- Candle size (owner: "find out if bigger candles were better"): average body of candles 1-4 / ATR(14) at candle 4,
  terciles fixed per market x timeframe on 2011-19 setups (no outcomes used); R per tercile.
- Best market x timeframe (owner: "best markets ... if M5 works on one market we stay there"): learn-then-check. For each
  market x timeframe the best configuration on 2011-19 (by s, at least 100 trades), scored on 2020-22. A pick counts only
  if it holds on 2020-22; choosing it from 2011-19 alone would be hindsight.
- Control (`controls.py`): the same order logic on the same four alternating candles WITHOUT the engulfing.
- Swap-free profile next to (never instead of) the result with swaps.
