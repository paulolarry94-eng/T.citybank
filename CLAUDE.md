# T.citybank — project memory for Claude

Owner goal: a systematic MT5 portfolio (Exness Zero account) with fortnightly payouts; aspiration 60–120% a
year. The job is to find out what is TRUE, not what looks impressive in a backtest.

## How to test anything: the Truth Lab
```bash
bash tools/bootstrap.sh
python3 research/truth/run.py research/truth/strategies/<idea>.py [--no-look]
```
Write new ideas as strategy files (`research/truth/strategies/TEMPLATE.py`). Do not write ad-hoc backtests
for new ideas; the lab's protocol is the standard (`research/truth/README.md`).

## Non-negotiable rules
1. Never claim code compiled, tests passed or an edge was verified unless it actually happened here.
   MQL5 cannot be compiled in this container: say "uncompiled source".
2. Fix markets, timeframes and parameter grids before seeing results. Choosing markets or settings after
   seeing results is hindsight, and it must be called out if done.
3. 2023–2025 is the final holdout: one logged look per strategy fingerprint. After a look, changed rules
   require a new strategy NAME.
4. Every result includes costs (spread + commission + slippage) and overnight swaps; report a
   low-cost swap-free profile separately, never instead.
5. Report rejections plainly, and say how many configurations were tried (deflated Sharpe).
6. Plain language for the owner: outcome first, numbers in tables, no hype.

## What is known (2026-10-31, details in `research/CONCLUSION.md`)
- Survivors: **TimelessCity v2.42** (`mt5/TimelessCity.mq5` + presets: gold dip reversion S1, USDJPY trend S2,
  gold trend S3); the **11-leg book** (`research/results/book_v3.json`, Tier B forward-test candidate);
  **futures trend + carry** (works only on real futures, not CFDs).
- Rejected after costs on XAUUSD/EURUSD/GBPUSD/USDJPY: ORB, FVG, supply/demand, Quasimodo, Malaysian SnR,
  engulfing, about 1,400 liquidity-grab variants, an intraday best-setup scanner, short volatility, pairs,
  cross-sectional momentum, broad mean reversion, GREEN/AMBER sizing states.
- Biggest levers: real costs and swaps (Exness Zero swap-free could add +0.3 to +0.6 Sharpe; unverified),
  and breadth (more markets for the proven families).

## Map
- `data/` M1 bid bars 2011–2025 for XAUUSD, EURUSD, GBPUSD, USDJPY (`{SYM}_M1_bid_{YEAR}.npz`).
- `research/engine.py`, `research/gold_lab.py`: loaders and early engines.
- `research/northstar/`: execution core (`core.py`), pattern modules, pre-registration, risk manager, weekly
  report; the lab builds on it.
- `research/truth/`: the Truth Lab. `research/results/truth/<NAME>/` holds its reports.
- `research/multiasset/`: trend+carry on pysystemtrade futures data; Kelly/Monte Carlo frontier; PROJECT.md.
- `mt5/`: TimelessCity.mq5 + presets, NorthStarGovernor.mq5 + NorthStarRisk.mqh, TruthEA.mq5 template,
  NorthStarExport.mq5 (exports broker specs, M1 bars with spread, and the economic calendar). All MQL5 except
  TimelessCity is uncompiled.
- `tools/`: `dukascopy_m1.py` (Dukascopy throttles cloud IPs: run it on a home PC), `ingest_mt5.py`,
  `parity_check.py`, `bootstrap.sh`.

## Next steps (gated)
Exness export → re-score at real costs → compile TimelessCity and parity-check it → 3–6 months demo with the
weekly report → code the remaining book legs → breadth on new markets → live small, scale only if live matches.
