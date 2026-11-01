# EA specification — tokyo_fix_gotobi_v1 (Tier B: forward-test candidate)

Hypothesis: Japanese importers' dollar buying at the 09:55 JST Tokyo fix on gotobi days lifts USDJPY into the fix (and it eases after), by more than the round-trip cost.

Signal rules: Tokyo fix on "Gotobi" days, USDJPY (Q10/Q15: a flow with a payer). Rules fixed 2026-11-01 BEFORE any result.

Why it might pay: Japanese importers buy dollars at the Tokyo fixing (09:55 JST = 00:55 UTC; Japan has no daylight
saving) and settle most on gotobi days: the 5th, 10th, 15th, 20th, 25th and the last day of the month, moved to the previous
Tokyo business day when it falls on a weekend, a Japanese holiday or the bank year-end (31 Dec - 3 Jan). Published research
reports the dollar rising into the fix on those days and easing after it. Nothing here was taken from our own data.
Trades (market orders at the open of the minute named, exits at the open of the minute named):
  pre2300   buy 23:00 UTC (08:00 JST) on the evening before a gotobi fix, sell 00:55 UTC (the fix);
  pre0000   buy 00:00 UTC (09:00 JST, Tokyo open), sell 00:55 UTC;
  post0055  sell 00:55 UTC (after the fix), buy back 02:00 UTC.
  Protective stop 0.3% of price (a catastrophe stop, rarely touched in an hour or two; R = 0.3% of price). No overnight
  swap (no 22:00 UTC rollover inside the trade).
Grid: trade [pre2300, pre0000, post0055] = 3 configurations, gotobi days only (other days are the control, reported by
  research/flows/tokyo_fix_study.py, not traded).
Costs: Exness Zero realistic USDJPY (1.35 pips round trip: commission is charged in dollars, so it costs more in yen).
Priors: no earlier idea shares the calendar/fix/flow tags; Hunt 2 found the London 4 pm fix reversal real but worth half a
  cost, and month-end flows 1.4-1.9 costs but only 12 trades a year.


Configuration: `{"tf": "M5", "trade": "pre2300", "tgt": 0.0, "trail": 0.0, "bias": 0}` on USDJPY.
Management: target 0.0R (0 = none), chandelier trail 0.0 x ATR (0 = none), time stop 50 bars, H4 EMA50 bias filter off; market entry at the next bar's open after the signal bar closes; no entries 20:30–23:00 UTC; one position per market.
Build: copy mt5/TruthEA.mq5, implement Signal() from the rules above, set the inputs to this configuration.
Parity: run the Strategy Tester (real ticks) and compare its trade log with results/truth/tokyo_fix_gotobi_v1/parity_trades.csv using tools/parity_check.py; pass = >= 95% of trades matched (entry within one bar, same side) and R within 0.1.
Then: demo per research/northstar/NORTHSTAR_REPORT.md §7, sized by the portfolio governor.
