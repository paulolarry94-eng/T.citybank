# EA specification — eurusd_close_beyond_reversal_v1 (Tier B: forward-test candidate)

Hypothesis: A daily close beyond the prior day's range is an exhaustion move; a stop entry back through the bar's far extreme catches the snap-back, and banking the first profitable New York close harvests it.

Signal rules: Owner's spec (2026-10-31): no-indicator daily reversal on EUR/USD.
Long: a RED daily candle whose close is below the previous day's low -> buy stop at that candle's high, valid for the
next session only. Short: a GREEN candle whose close is above the previous day's high -> sell stop at its low, next
session only. Only when flat. Exit: in profit between 16:45 and 16:55 New York time -> close; otherwise a fixed stop
(250 pips in the spec; 150 and 350 are the declared neighbours). Costs: 4 pips round trip per the spec ($40 per lot).

Configuration: `{"tf": "D1", "stop_pips": 250, "tgt": 0.0, "trail": 0.0, "bias": 0}` on EURUSD.
Management: target 0.0R (0 = none), chandelier trail 0.0 x ATR (0 = none), time stop 50 bars, H4 EMA50 bias filter off; market entry at the next bar's open after the signal bar closes; no entries 20:30–23:00 UTC; one position per market.
Build: copy mt5/TruthEA.mq5, implement Signal() from the rules above, set the inputs to this configuration.
Parity: run the Strategy Tester (real ticks) and compare its trade log with results/truth/eurusd_close_beyond_reversal_v1/parity_trades.csv using tools/parity_check.py; pass = >= 95% of trades matched (entry within one bar, same side) and R within 0.1.
Then: demo per research/northstar/NORTHSTAR_REPORT.md §7, sized by the portfolio governor.
