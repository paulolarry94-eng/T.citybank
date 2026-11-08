# Body-engulf 4-candle range, version 3 — pre-registration (2026-11-08, before any v3 result)

Owner: "a doji counts, the reason I said it was 3 not 2 is because that doji was bullish ... this strategy works, I have
seen it even at 10R ... check for bugs, test it with the doji ... at 1:2 ... 1:10R at breakeven at 75% of the journey ...
give me 10 examples of the most won scenarios and 10 of most loss".

Strategy `research/truth/strategies/body4_range_v3.py` = v2 with three changes:
1. Lookback colours: a doji (open = close) is BULLISH (close >= open, as charts colour it). It counts for a buy's lookback
   and not for a sell's. The owner's image-7 buy (gold M5, 2019-01-02 08:20-08:35) now has 3 of 5 and is valid (tested).
   The four pattern candles still need real bodies (body engulfing).
2. Targets 10R and 2R (reading "1:2 ... 1.10r" as 1:2 and 1:10).
3. Breakeven at 75% of the way to the target (+7.5R for 10R, +1.5R for 2R), on or off.
Everything else as v1/v2. Grid: 6 timeframes x target 2 x entry 2 x breakeven 2 x buffer 4 x lookback 2 = 384
configurations, 12 markets; the Truth Lab decides (one 2023-25 look only for a gate-passing selection).
Before costs a 10R target needs about 1 win in 11 to break even. Trades last longer at 10R, so swaps matter more: the
swap-free profile is reported next to (never instead of) the result with the lab's swaps.

Bug audit (owner: "what in your scan could give negative results, check for bugs"), done on the same data:
- every trade of the main settings re-scored by an independent exit checker (separate code, first-touch search);
- every detected pattern re-checked against the rule from the raw candles (bodies, colours, lookback count);
- buys and sells separately; the most extreme R values listed and explained; before-cost results.
Examples: the 10 biggest winners and the 10 biggest losers of the main settings (50% entry, stop at the range end,
breakeven at 75%, lookback on, 10R), 2011-22 only, at most one per market and day, chosen by R alone.
