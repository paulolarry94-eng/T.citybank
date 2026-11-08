# Body-engulf range, version 5: strict vs loose engulfing, timeframe layering, and the owner's 2023-25 look
Pre-registration, 2026-11-08, written before any v5 result.

Owner (after the XAGUSD M5 chart): "test both engulf, loosen ones, then test the data in 2023-2025, then try layering
timeframes: one big with small, both align, then entry in small".

## Strategy `research/truth/strategies/body4_range_v5.py`
- engulf "body" (candles 2 and 4 fully cover the previous body) or "loose" (they only close beyond the previous candle's
  open; a gap at the open is allowed, as in the owner's silver chart).
- layer "none" or "on": a small-timeframe setup trades only if the bigger timeframe had a setup in the same direction whose
  candle 4 closed at most 2 big candles earlier (M1->M15, M5->H1, M15->H4, M30->H4, H1->H4, H4->D1 from 22:00 UTC); the
  big setup passes the same intent and lookback rules; entry, stop and target come from the small setup.
- safe window only (setups 07:00-19:00 UTC, no US news days, flat at 20:30 UTC); entry 50%; buffer 0% or 20%; targets 2R,
  3R, 5R, 10R; breakeven at 75% on/off; lookback on/off (dojis bullish). 768 configurations, 12 markets.
- The grid was narrowed using the v1-v4 DEVELOPMENT results (2011-22 only): 70% entry and the 5%/10% buffers dropped.

## Order of work
1. Truth Lab (gate on 2011-19, validation 2020-22; it logs a 2023-25 look only for a gate-passing selection).
2. Study on 2011-19 and 2020-22 only: loose vs body and layer on vs off (paired), main settings before costs.
3. The owner's 2023-25 look (decided by the owner, 2026-11-08), logged once in
   `research/results/truth/body4_range_v5/oos_log.json` and in the memory:
   - PRIMARY (the answer): for each engulf x layer (4 combinations), the configuration with the highest edge quality on
     2011-22 pooled (12 markets, at least 300 trades). The 4 choices are written to the look file BEFORE any 2023-25 number
     is computed.
   - SECONDARY (description only): 2023-25 for all 768 configurations (median, share positive, best). Picking a setting from
     this list would be hindsight.
   After this look, 2023-25 is used up for the body-engulf family: a later change has only Jan-Oct 2026 left as unseen data.
