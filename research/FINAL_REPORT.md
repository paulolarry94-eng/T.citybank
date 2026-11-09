# T.citybank: final report (2026-11-09)

## The answer
After **124 ideas and about 327,600 tested configurations**, the system that makes the most sense is a **10-leg "timeless"
mix**: the survivor strategies that made money after costs and swaps in every era since 2011. In backtests it makes about
**5-6% a year with the drawdown kept inside 3.6%** (about 11-13% a year inside 8%), and every calendar year 2011-2025 was
positive. On the untouched January-October 2026 data it was **about flat (+0.3%)**. That is a real but small edge: roughly a
tenth of the 60-120% a year the goal asks for. None of the chart patterns tested, including every version of your
body-engulf range, has an edge before costs.

## 1. The system that makes the most sense: the timeless mix
Chosen by a rule fixed before looking (`research/goal/PREREGISTRATION_TIMELESS.md`): a leg qualifies if it was positive in
each of 2011-14, 2015-18 and 2019-22. 10 of the 13 survivors qualify. Results: `research/results/goal/TIMELESS_MIX.md`.

| Leg | Market, timeframe | What it does | Weight |
|---|---|---|---|
| EUR EuroHours | EURUSD, clock | Tue-Thu: sell at 09:00 London time, buy back at 13:00 or stop | 0.33 |
| XAU S1 reversion (TimelessCity S1) | gold, H1/M30/M20, long | buys a strong dip-and-recover pattern, 1R target | 0.63 |
| XAU Donchian20 turtle | gold, H4 | buys/sells a close beyond the 20-bar high/low, turtle exit | 0.21 |
| JPY S2 Donchian20 long (TimelessCity S2) | USDJPY, H4, long | 20-bar breakout above last week's high, trailing stop | 0.37 |
| XAU EMA20-50 | gold, H4 | EMA20/50 cross inside yesterday's range, exit on the opposite cross | 0.34 |
| GBP weekly sweep follow-through | GBPUSD, H1 | after last week's high/low is swept and reclaimed, trades the continuation | 0.93 |
| JPY RSI(2) | USDJPY, D1 | buys deep dips above the 200-day average (sells the mirror), exit at SMA5 | 1.00 |
| GBPJPY Donchian20 | GBPJPY, H4 | 20-bar breakout, trailing stop | 0.25 |
| Tokyo fix on gotobi days | USDJPY, M5 clock | buys 23:00 UTC, sells 00:55 UTC on the Japanese settlement days (a flow with a payer) | 0.57 |
| EURUSD close-beyond reversal | EURUSD, D1 | fades a daily close beyond the prior range, 250-pip stop | 1.00 |
Left out by the rule: JPY volatility breakout, JPY Donchian55, EURGBP Bollinger (each lost in one era).

**How it did** (Exness Zero costs + swaps; risk per trade for each drawdown cap set on 2011-22 only, then kept):
| | 2011-22 | 2023-25 | Jan-Oct 2026 (untouched) |
|---|---|---|---|
| Trades per two weeks | 14.4 | 14.5 | 14.2 |
| Two-week periods that made money | 61% | 54% | 50% |
| 3.6% cap (0.46% risk a trade): % a year (worst drawdown) | +6.0% (4.3%) | +4.7% (3.2%) | +0.3% in 10 months (2.2%) |
| 8% cap (1.0% risk a trade): % a year (worst drawdown) | +13.3% (9.5%) | +10.6% (7.1%) | +0.7% in 10 months (4.9%) |

Every year at the 3.6% cap: 2011 +3.4%, 2012 +5.2, 2013 +7.3, 2014 +7.2, 2015 +5.0, 2016 +10.2, 2017 +4.8, 2018 +3.7,
2019 +7.0, 2020 +2.3, 2021 +5.1, 2022 +10.6, 2023 +3.0, 2024 +4.3, 2025 +7.0, 2026 (Jan-Oct) +0.3.
It beat all 13 survivors together and the 11-leg book on the later data (two-week Sharpe 0.20 vs 0.18 vs 0.14), which is
why the rule picked it. Swap-free, all 13 together are slightly ahead (0.245 vs 0.237).

**Honest limits:** the 2023-25 and 2026 data had been seen before for most legs (not by this rule), the 2026 result is about
zero, and live results usually come in 30-50% weaker than backtests (P11). Expect a few % a year, not more, until a forward
test says otherwise.

## 2. The goal against what we have
| | The goal | The timeless mix |
|---|---|---|
| Per two weeks | +2% inside a 3.6% drawdown | +0.23% (2011-22), +0.18% (2023-25), about 0 (2026) |
| Per year | 60-120% | about 5-6% at 3.6%; 11-13% at 8% (backtest) |
| Two-week Sharpe needed | 1.17 | 0.37 (2011-22), 0.24 (2023-25), 0.03 (2026) |
Inside a fixed drawdown cap, return grows with the square of the edge: reaching 60% a year inside 3.6% would need about 3.5
times the edge quality of anything found here. More risk does not fix that: at 25% risk a trade (the Wealth Game) 80-94% of
accounts end below their start (`research/results/goal/WEALTH_GAME.md`).

## 3. What was tested and failed
| Idea | Settings tried | Result |
|---|---|---|
| Your body-engulf 4-candle range (7 versions + gold study + 2026 check) | 5,342 | loses after costs everywhere, about 0 before; the curated Prime M5/M15 version: 9 trades a year, 4 of 4 lost in 2026 (`research/results/body4/`) |
| Your 4-flip EMA / four-candle price action | about 6,200 | best of all lost on unseen 2023-25 (`research/results/final/FINAL.md`) |
| Your 3:30 EMA retest, Leg 34 (with winner anatomy and pocket scan), 4-leg engulfing SOP | about 1,700 | about 0 before costs, negative after |
| Chart-pattern families (ORB, FVG, supply/demand, Quasimodo, SnR, liquidity grabs) | about 250,000 | about 0 before costs, negative after (P1, P14) |
| Flows with a payer and calendar effects (Tokyo, London 4 pm and ECB fixes, month-end, US close, turn of month, payday) | about 100 | only the Tokyo fix survives; published flows fade (P22) |
| Third-party bots (Gold Hunter grid, Dark Mimas) | replayed | lose on equity (P15) |
| Sizing tricks (SEESARE ladders, risk states, Wealth Game, noise gate) | studies | sizing cannot create an edge (P8, P24-P26) |

## 4. What we need next, in order
1. **Forward proof on a demo account (3-6 months).** TimelessCity (compiled earlier by you) trades the S1 gold leg and close
   relatives of the USDJPY and gold Donchian legs (its exits differ, so check parity); the other legs need EAs: specs exist (`research/northstar/NORTHSTAR_SPEC.md`, `research/results/truth/*/EA_SPEC.md`), the MQL5 is not written
   or compiled yet. Check each EA trade-for-trade against the Python trades (`tools/parity_check.py`), then run all 10 on
   demo with a two-week report.
2. **Real account numbers.** Run `mt5/NorthStarExport.mq5` on the account you will use (spreads, commission, swaps,
   swap-free status) and re-score; swap-free status alone is worth a lot (Q1).
3. **Choose the cap and the payout rule.** 3.6% (about 5% a year) or 8% (about 10-13% a year in backtest); pay out from a
   buffer, because only about half of the two-week periods make money (Q33).
4. **A bigger edge or more capital** for the 60-120% goal: a futures account for trend + carry (the most timeless edge
   found, Sharpe 0.5-0.96, impossible on CFDs), prop-firm capital (Q7), or new payer flows that need data we do not have.
5. **Before taking copy-trading followers:** a legal opinion, and RoboForex's answer on cent accounts (Q31).

## 5. How to keep testing
```bash
bash tools/bootstrap.sh                                      # packages + data check (data is in the repo)
python3 -m unittest discover -s research/truth/tests         # 184 tests, about 30 seconds, must end with OK
python3 research/truth/run.py research/truth/strategies/<idea>.py --no-look   # any new idea, the lab's way
python3 research/goal/timeless_mix.py                        # recompute the mix above
```
The research memory (`research/truth/memory/`: 124 ideas in the ledger, principles P1-P30, open questions, journal) loads at
the start of every session. `START_HERE.md` is the one-page entry point.
