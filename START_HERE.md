# START HERE — T.citybank status and handover (2026-11-09, updated 2026-11-12)

One page to pick the project up later. The full summary for the owner is `research/FINAL_REPORT.md`. Details live in
`CLAUDE.md` (rules + everything known), the research memory (`research/truth/memory/`) and the reports linked below.

## 1. How to resume (4 commands)
```bash
bash tools/bootstrap.sh                                      # installs packages, checks the data files
python3 -m unittest discover -s research/truth/tests         # 207 tests, about 35 seconds: should end with OK
python3 research/truth/memory.py --digest                    # what has been tested, survivors, principles
python3 research/goal/timeless_mix.py                        # the recommended mix (section 3), recomputed
```
Test any new idea only as a strategy file through the Truth Lab:
`python3 research/truth/run.py research/truth/strategies/<idea>.py --no-look` (template: `research/truth/strategies/TEMPLATE.py`).
Data is in the repo (`data/`: M1 bars 2011-2025 for 12 markets; `data/holdout/`: Jan-Oct 2026 for EURUSD, GBPUSD, USDJPY,
EURGBP, XAUUSD). Rules that never change: fix settings before results, costs and swaps always included, a holdout is looked
at once, plain reports.

## 2. The goal, as a number
Owner's goal: **+2% per two-week cycle (or per 10 trades) with the drawdown kept inside 3.6%**, 60-120% a year, fortnightly
payouts. Maths (`research/goal/CYCLE_GOAL_MATH.pdf`, P28): +2% per 10 trades inside 3.6% needs a per-trade edge quality of
about 0.42; per two weeks, a two-week Sharpe of 1.17. Inside a fixed cap, return grows with the square of edge quality.

## 3. The system that makes the most sense: the timeless mix (`research/results/goal/TIMELESS_MIX.md`)
The 10 survivor legs that made money in each of 2011-14, 2015-18 and 2019-22 (rule fixed before looking). Exness Zero costs
+ swaps; risk for each cap set on 2011-22:
| | 2011-22 | 2023-25 | Jan-Oct 2026 (untouched) |
|---|---|---|---|
| 3.6% cap (0.46% risk a trade x leg weight): % a year | +6.0% | +4.7% | +0.3% in 10 months |
| 8% cap (1.0% risk a trade x leg weight): % a year | +13.3% | +10.6% | +0.7% in 10 months |
| Two-week Sharpe (the goal needs 1.17) | 0.37 | 0.24 | 0.03 |
Every year 2011-2025 positive at the 3.6% cap (+2.3% to +10.6%). It beat all 13 survivors and the 11-leg book on 2023-Oct 2026.
Legs: EUR EuroHours, gold S1 reversion, gold Donchian20, USDJPY S2 Donchian, gold EMA20-50, GBP weekly sweep, USDJPY RSI(2),
GBPJPY Donchian20, Tokyo fix (gotobi), EURUSD close-beyond reversal. Not on CFDs but the most timeless edge found: futures
trend + carry (Sharpe 0.96 since 2000, 0.50 2011-24; `research/multiasset/`).

**Update 2026-11-12: Timeless 10 + v2 (13 legs).** Three thin pivot-sweep v2 legs (EURGBP H1, NAS100 H1, GBPUSD M15, RoboForex
Prime costs) joined after a logged look (`research/results/sweep5/PARETO.md`). At 3.6%: +6.66% / +5.38% a year (2011-22 / 2023-25),
+0.80% Jan-Oct 2026, worst drawdown 4.11%, every year 2011-25 positive; at 8%: +15.2% / +12.1% / +1.7%. Full report with cost
profiles, Monte Carlo, account size ($40,800 standard / $408 cent at 3.6%), payouts and examples:
https://claude.ai/artifact/QRh9Gy181Wsd2pn7uYgx8K (data: `research/results/portfolio/`). 2026 is not a clean test for the v2 legs.

## 4. Worst results (what does not work, and why)
| Idea | Tried | Result |
|---|---|---|
| Owner's body-engulf 4-candle range (v1-v7: entries, 1R-10R, breakeven, lookbacks, dojis, safe windows, strict/loose, layering, 60% bodies, two-week mixes, curated Prime M5/M15 13-17 UTC; gold study) | 5,342 | loses after costs everywhere, about 0 before; the 2023-25 look and the 2026 look both lost; Prime costs are realistic (EURUSD 0.06-0.11R a trade) and not the reason (`research/results/body4/`) |
| Owner's pivot-sweep range (v1, v2 chart reading, deep M1 study without costs: exits, 1,142 entry tests, scanner on 12 markets x 6 timeframes) | about 8,700 | wins at chance for every exit before costs; losers are breakouts; negative after costs; no Monte Carlo survivor; 3 thin v2 legs kept for the mix (`research/results/sweep4/`, `sweep5/`, `sweep6/`) |
| Owner's 4-flip EMA / four-candle price action | about 6,200 | best of all lost on unseen 2023-25 (`research/results/final/FINAL.md`) |
| Owner's 3:30 EMA retest, Leg 34, 4-leg SOP | about 1,700 | about 0 before costs, negative after |
| Chart-pattern families (ORB, FVG, supply/demand, Quasimodo, SnR, engulfing, ~1,400 liquidity grabs) | ~250,000 | about 0 before costs, negative after (P1, P14) |
| Payer flows and calendar effects | about 100 | only the Tokyo fix survives; published flows fade (P22) |
| Third-party bots (Gold Hunter grid, Dark Mimas) | replayed | lose on equity; grids hide open losses (P15) |
| Sizing tricks (SEESARE ladders, risk states, noise gate, Wealth Game at 25% risk) | studies | sizing cannot create an edge; 25% risk ruins 80-94% of accounts (P8, P24-P26) |
Common causes: no raw edge before costs on 1-minute to 1-hour shapes; best-of-many backtests not carrying forward (P10, P11).

## 5. Where we are
- **133 ideas, about 329,500 configurations tested; the survivors combine into the timeless mix above**: a real but small
  edge, a few % a year inside 3.6% (about 10% inside 8%), about flat on untouched 2026. That is roughly a tenth of the goal.
- Built: the Truth Lab (pre-registration, look-ahead check, gates, holdout log, cost ladder, cycle reports), M1 engines with
  tests, detectors and chart replays for the owner's patterns, the research memory, TimelessCity (compiled earlier by the
  owner), uncompiled MQL5 for the SEESARE router (`mt5/Seesare/`), the export EA (`mt5/NorthStarExport.mq5`).

## 6. What the goal needs (and what to do next)
1. **Forward proof** of the timeless mix on demo for 3-6 months: write and compile EAs for the legs TimelessCity does not
   cover (specs: `research/northstar/NORTHSTAR_SPEC.md`, `research/results/truth/*/EA_SPEC.md`), parity-check each against
   the Python trades (`tools/parity_check.py`), then a two-week report.
2. **Real account numbers**: run `mt5/NorthStarExport.mq5` on the account to be used (costs, swaps, swap-free status, Q1).
3. **Decide the cap and payouts**: 3.6% (about 5% a year) or 8% (about 10-13%); pay out from a buffer (Q33).
4. **A bigger edge or more capital** for 60-120%: futures trend + carry, prop-firm capital (Q7), payer flows needing data we
   do not have (P22). Copy trading needs a legal opinion first (Q31).

## 7. Map
`research/FINAL_REPORT.md` (final summary) · `research/results/goal/TIMELESS_MIX.md` (the mix) · `research/results/body4/`
(body-engulf range v1-v7, gold study) · `research/results/final/FINAL.md` (four-candle family) · `research/results/goal/`
(cycle maths, two-week cycle, Wealth Game) · `research/champion/` (11-leg book, 2026 forward) · `research/truth/README.md` (lab).
