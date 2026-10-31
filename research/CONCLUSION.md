# Conclusion of the research phase (2026-10-31)

## What the evidence says
- **Tested:** about 300,000 configurations and candidate trades, 2011–2025, after spreads, commission,
  slippage and overnight swaps. Every concept had rules fixed before its results, and every final
  check used data the selection never saw. Concepts covered: opening range breakout (ORB), FVG,
  supply/demand, Quasimodo, Malaysian SnR, engulfing, liquidity grabs (about 1,400 variants), an
  intraday best-setup scanner, short volatility, pairs, cross-market momentum, mean reversion.
- **No edge on these markets after costs:** popular discretionary pattern concepts (ICT/SMC, ORB,
  intraday sweeps). Their raw edge before costs is about +0.01 to +0.02R per trade; costs are about
  0.07R.
- **What works:** a small set of systematic edges with a reason to exist.
  - **TimelessCity v2.42** (already coded): gold dip-reversion S1, USDJPY trend S2, gold trend S3.
  - **The 11-leg book**: TimelessCity's ideas plus the EUR London-morning short, a JPY volatility
    breakout, JPY RSI(2), JPY 55-day Donchian, a filtered gold EMA cross, GBP weekly follow-through
    and two crosses.
  - **Futures trend + carry**: works only on real futures, not CFDs.
- **What it's worth (backtest, P&L booked at exit):**

| System | Costs and swaps | Sharpe | Per year | Max drawdown |
|---|---|---|---|---|
| TimelessCity at deployed risk | full swaps | 0.67 | 15% | 30% |
| TimelessCity at deployed risk | low cost, swap-free | 1.04 | 27% | 25% |
| 11-leg book at 25% vol | as assumed | 1.00 | about 27% | about 26% |
| 11-leg book at 25% vol | low cost, swap-free | 1.64 | 46% | 26% |
| 11-leg book at 35% vol | low cost, swap-free | 1.64 | 67% | 35% |
| Same, with live 30% weaker than backtest | low cost, swap-free | about 1.15 | 29–41% | 32–42% |

- **The two biggest levers:** costs and swaps (Exness Zero may be worth +0.3 to +0.6 Sharpe), and
  breadth (more independent legs on more markets).
- **What doesn't help:** more pattern hunting; GREEN/AMBER risk states (plain fixed-fractional sizing
  was better); leverage beyond about a third of Kelly.
- **The goal:** 60% a year is possible only with favourable real costs, live results close to the
  backtest, and acceptance of 35–45% drawdowns. 120% a year every year isn't achievable safely.

## What to do (in order, each step gated)
1. **Real costs (this week).** Run `mt5/NorthStarExport.mq5` on the Exness terminal and note the Zero
   commission per lot. Re-score everything at the real costs.
2. **Parity (1–2 weeks).** Compile TimelessCity v2.42 (presets checked), run the Strategy Tester on
   2023–2025 and compare with `results/northstar/parity/timelesscity/*.csv`. Fix differences before
   anything else.
3. **Demo (3–6 months).** TimelessCity exactly as in its Deployment Guide, with the weekly report
   (`northstar/weekly.py`). Gate: live R per trade inside the backtest band, legs not drawing down
   together, costs as measured.
4. **Code the book's remaining legs** in MQL5, simplest and highest-weight first. Parity-test each
   and add it to the demo.
5. **Breadth.** Run `tools/dukascopy_m1.py --all 2011 2025` on a home PC, push the data, and run the
   book's families across about 27 more markets. Keep only uncorrelated survivors. Target: Sharpe 1.5.
6. **Live, small, then scale.** Start at about 20–25% vol (about a quarter of Kelly). Raise toward
   35% only after 6–12 months of live results matching the backtest. Pay out a fixed share of
   realised profit each fortnight.
7. **Optional:** a futures account (CME micros) for trend + carry.

## What to stop
Searching for new chart patterns. Adding risk machinery that doesn't improve results. Trusting any
backtest, including these, over a live record.
