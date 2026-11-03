# Last push: month-end FX hedge rebalancing at the London 4 pm fix — pre-registration (2026-11-03, before any result)

Owner: "you can look for flows that have a payer (someone forced to trade at a known time) rather than candle shapes ...
run final test before you wrap up everything, this our last push".

Choice: of the payer flows testable with our data and not yet tested, this one has a payer (hedgers who must resize currency
hedges at the month-end WM/Reuters 4 pm London fix) AND a direction known before the trade (month-to-date US vs foreign equity
performance), the missing piece in the rejected London-fix fades (P22). Published evidence: Melvin & Prins (2015). Nothing
was taken from our data to choose it.

Rules and grid: `research/truth/strategies/monthend_hedge_fix_v1.py` (6 configurations: entry 12:00 / 14:00 / 15:00 London x
filter all / |diff| >= 2%; EURUSD vs GER40, GBPUSD vs UK100, USDJPY vs JP225 against US500; exit at 16:00 London; stop 0.3%;
RoboForex Prime costs). Truth Lab protocol unchanged (one 2023-25 look only if a configuration passes the gate). Control:
the same rule on the 10th business day of the month. Cycle view: a month-end flow gives about 12 trades a year per market
(36 a year on three markets = 3.6 cycles a year), so even a real edge adds only a few cycles a year.
