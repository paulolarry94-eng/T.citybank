# START HERE — T.citybank status and handover (2026-11-03)

One page to pick the project up later. Details live in `CLAUDE.md` (rules + everything known), the research memory
(`research/truth/memory/`), and the reports linked below.

## 1. How to resume (3 commands)
```bash
bash tools/bootstrap.sh                                   # installs packages, prints the research memory digest
python3 -m unittest $(ls research/truth/tests/test_*.py)  # 175 tests, about 1 minute: should end with OK
python3 research/truth/cyclegoal.py --survivors           # the scoreboard below, recomputed
```
Test any new idea only as a strategy file through the Truth Lab:
`python3 research/truth/run.py research/truth/strategies/<idea>.py` (template: `research/truth/strategies/TEMPLATE.py`).
Data is in the repo (`data/`, M1 bars 2011-2025 for 12 markets; `data/holdout/` Jan-Oct 2026). Rules that never change:
fix settings before results, costs and swaps always included, 2023-25 is looked at once per strategy, plain reports.

## 2. The goal, as a number
Owner's goal: **+2% per cycle of 10 trades, with the drawdown over a 360-trade lifecycle kept inside 3.6%** (2-7% per cycle
as the wider aim; fortnightly payouts). Maths (`research/goal/CYCLE_GOAL_MATH.pdf`, principle P28):
- With fixed risk, +2% per cycle inside 3.6% needs a per-trade **edge quality s = mean R / spread of R of about 0.42**
  (examples: 70% wins at 1:1, 55% at 2:1, 45% at 3:1). Inside 5%: 0.36; inside 8%: 0.28.
- More independent trades per cycle lower the bar: **s x sqrt(independent trades per cycle) about 1.4** (+2%) or 2.8 (+7%).

## 3. Best results (survivors), in cycle units
Risk set so 95% of 360-trade lifecycles stay inside a 3.6% drawdown; 2011-2025 backtests after costs and swaps
(`cyclegoal.py --survivors`).

| Strategy | Trades | Edge quality s | Return per 10-trade cycle at the 3.6% cap | Cycles a year | About % a year at the cap | Gap to s 0.42 |
|---|---|---|---|---|---|---|
| EURUSD daily close-beyond reversal (Tier B) | 453 | 0.125 | +0.23% | 3 | +0.7% | 3.4x |
| Tokyo fix on gotobi days, USDJPY (Tier B) | 1,072 | 0.088 | +0.14% | 7 | +1.0% | 4.8x |
| 11-leg book (Tier B) | 6,100 | 0.062 | +0.09% | 41 | +3.7% (6-7% with the drawdown guard, P27) | 6.8x |
| All 13 together | 7,625 | 0.063 | +0.09% | 51 | about +4.5% | 6.7x |
| 11-leg book, untouched Jan-Oct 2026 (real forward data) | 333 | 0.020 | +0.003% | - | about 0 | 21x |

Other survivors: TimelessCity v2.42 (EA, Sharpe 0.67 with swaps, 1.04 swap-free; S1 EUR weak in 2023-25) and futures trend +
carry (Sharpe 0.50 2011-24, works only on real futures, not CFDs).

## 4. Worst results (what does not work, and why)
| Idea | Tried | Result |
|---|---|---|
| Owner's 4-flip EMA / four-candle price action (v1-v4, no-EMA, best + trend filter) | about 6,200 settings | best of all lost -0.03R to -0.12R a trade on unseen 2023-25; family closed (`research/results/final/FINAL.md`) |
| Month-end FX hedge rebalancing at the 4 pm fix (last push, payer + known direction) | 6 | real in 2011-19 (+0.10R, s 0.12), reversed 2020-22 (s -0.41), flat on unseen 2023-25 (-0.03R); competed away after publication (`research/results/flows/MONTHEND_HEDGE.md`) |
| Owner's body-engulf 4-candle range (50/70% entry, 1R-10R, breakeven, lookback, dojis, safe windows, strict/loose engulf, timeframe layering; M1-H4, 12 markets; 2026-11-08) | 5,184 | every setting lost after costs (best -0.10R a trade); the 4 settings chosen for the 2023-25 look all lost (-0.07 to -0.38R a trade); about 0 before costs; loose engulf no better, layering keeps 1-2% of trades; 1:1 wins 34-47% vs 53-72% needed; 10R hit by 6.6% vs ~9% needed; target hit rates at chance; safe windows +0.05R, still negative; bug audit clean; gold characteristics (learn 2019, 70 conditions) none positive; family closed (`research/results/body4/RESULT.md`, `v2/` to `v5/`, `gold/`) |
| Noise gate on the survivors (trade only when movement is clean; 2026-11-06) | 8 | no better than random filtering (p 0.36), halves trades, reversed on 2026 (`research/results/noisegate/RESULT.md`) |
| Owner's 3:30 EMA retest (incl. 1:1 stop grid) | 64 | -0.16 to -0.22R a trade, edge quality -0.18 to -0.08 (`research/results/owner330/RESULT.md`) |
| Chart-pattern families (ORB, FVG, supply/demand, Quasimodo, SnR, engulfing, ~1,400 liquidity grabs, Leg 34) | ~250,000 | about 0 before costs, negative after (P1, P14) |
| Third-party bots (Gold Hunter grid, Dark Mimas) | replayed | lose on equity; grids hide open losses (P15) |
| Laddered / clever sizing (SEESARE ladders, GREEN/AMBER states) | studies | sizing cannot create an edge (P8, P24-P26) |
Common causes: no raw edge before costs on 5-minute to 1-hour shapes; costs of 0.1-0.2R a trade; best-of-many backtests
not carrying forward (P10, P11).

## 5. Where we are
- **About 100 ideas and 316,000 configurations tested; 6 survivors** (last push 2026-11-03: one more payer flow, rejected), all with edge quality 0.02-0.13. In cycle units the best
  realistic portfolio makes about **+0.1% per 10-trade cycle**, i.e. a few % a year inside a 3.6% drawdown, against the goal
  of +2% per cycle. The 2026 forward check of the book was about flat.
- Built and waiting: TimelessCity EA (compiled by the owner earlier), uncompiled MQL5 for the SEESARE router (`mt5/Seesare/`),
  the Truth Lab with cycle reporting, detectors and chart replays for the owner's patterns.

## 6. What the goal needs (and what to do next)
1. **A stronger edge, not more patterns.** s about 0.42 per trade, or many independent edges at once (the book at s 0.06 would
   need about 530 independent trades per cycle). Shapes on price charts have not delivered; **flows with a payer** have
   (Tokyo fix, P22): hunt forced, scheduled order flows with a known direction (Q10, Q19, Q23) that are hard to front-run
   (small, local, operationally forced). Well-published flows fade: the month-end hedge flow worked 2011-19, then reversed.
2. **Or relax the cycle**: a 2-week cycle needs a fortnight Sharpe of 1.17 for +2% inside 3.6% (we have 0.33: +0.19% per
   2 weeks, ~5% a year); it changes the label, not the money (`research/results/goal/FORTNIGHT_CYCLE.md`). A wider
   drawdown helps more: 8% gives about 11% a year in backtest.
3. **Forward evidence before money**: compile and parity-check the EAs (Q22, needs the owner's OK to run the MT5 installer
   here), 3-6 months of demo with the weekly report, confirm RoboForex/Exness costs and swap-free status (Q1).
4. Housekeeping still open: re-run the intraday studies that used HistData markets before the clock fix (Q26); the 3:30 2026
   summer question (Q25) can be settled by a paper test from mid-March 2027 or its pre-registered 2023-25 look.

## 7. Map of the latest work (2026-11-01 to 03)
`research/results/final/FINAL.md` (owner patterns, final) · `research/results/ema4/` and `research/results/pa4/` (4-flip
versions) · `research/results/owner330/` (3:30 retest) · `research/results/batch01/` (payer-flow batch) ·
`research/results/flows/MONTHEND_HEDGE.md` (last push, month-end hedge flow) ·
`research/results/body4/RESULT.md` and `v5/RESULT.md` (body-engulf range and its 2023-25 look, 2026-11-08) ·
`research/goal/` (cycle maths) · `tools/histdata_clock.py` (data clock fix) · `research/truth/README.md` (lab tools).
