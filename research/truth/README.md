# The Truth Lab

One protocol for any trading idea. Write the idea once; the lab strips it down to what is true after
costs, swaps, luck and hindsight. If it survives, you get an EA specification and a trade list for
the MT5 parity check.

## Test an idea
```bash
bash tools/bootstrap.sh                                     # once per fresh container
cp research/truth/strategies/TEMPLATE.py research/truth/strategies/my_idea.py   # fill in NAME, HYPOTHESIS, GRID, signals()
python3 research/truth/run.py research/truth/strategies/my_idea.py --no-look     # everything except the final period
python3 research/truth/run.py research/truth/strategies/my_idea.py               # + the one logged look at 2023-2025
```
Results land in `research/results/truth/<NAME>/`: `REPORT.md` (read this), `summary.json`, `grid.csv.gz`,
`pooled.csv.gz`, `oos_log.json`, and for Tier A/B strategies `EA_SPEC.md` + `parity_trades.csv`.

## What the lab does (identical for every idea)
| Step | What | Why |
|---|---|---|
| 0 | SHA-256 fingerprint of the strategy file | after the final look, changed rules need a new NAME (no tuning on the answer) |
| 1 | look-ahead check: real-time decisions + prefix invariance | catches strategies that peek at future bars or whole-history statistics |
| 2 | grid over TIMEFRAMES x GRID x management, all MARKETS, fills before 2023 | spreads, commission, slippage, swaps, rollover block, one position at a time |
| 3 | development gate (2011–19), neighbours, validation (2020–22), walk-forward | a real edge is broad, stable and survives re-selection |
| 4 | stress (costs x1.5, swaps x2, +1 minute) and deflated Sharpe | survives worse fills; is it luck given how many settings were tried? |
| 5 | one logged look at 2023–25 | the only truly unseen period, used once |
| 6 | Tier A (deploy) / Tier B (forward-test) / Rejected | the criteria in `research/northstar/PREREGISTRATION.md` §5 |
| 7 | low-cost swap-free profile | what a raw-spread, swap-free account would change |
| 8 | portfolio fit vs the 11-leg book | does it add, or duplicate what you already have? |

## Rules that keep it honest
- Decide MARKETS, TIMEFRAMES and GRID before running. Choosing markets after seeing which worked is hindsight.
- Small grids: the deflated Sharpe charges for every setting tried.
- A rejection is a result. Record it, don't rescue it: a new idea gets a new NAME.
- New markets: add data (`tools/dukascopy_m1.py` on a home PC, or `mt5/NorthStarExport.mq5` + `tools/ingest_mt5.py`)
  and a cost line in `costs.json` (estimates are marked; replace them with your broker's numbers).

## From Tier A/B to an EA
1. `EA_SPEC.md` gives the rules and the selected configuration.
2. Copy `mt5/TruthEA.mq5` and implement `Signal()` from the rules. Everything else (closed-bar
   decisions, next-bar entry, stop, target, chandelier trail, time stop, bias, rollover block, governor
   risk, trade log) is built in. **The template is uncompiled source; compile it in MetaEditor.**
3. Strategy Tester on 2023–2025, then
   `python3 tools/parity_check.py research/results/truth/<NAME>/parity_trades.csv <TruthEA log>.csv --market <SYMBOL> --tf-minutes <bar>`.
   Pass = ≥ 95% of trades matched, median R difference ≤ 0.10.
4. Demo with `mt5/NorthStarGovernor.mq5` and the weekly report (`research/northstar/weekly.py`).

## Examples (already run)
- `coin_flip.py`, a control of random entries: **rejected** (one random setting even passed the first gate;
  walk-forward, neighbours and the deflated Sharpe caught it).
- `donchian_trend.py` / `donchian_trend_v2.py`: **rejected as a 4-market rule**. Positive on gold and USDJPY,
  negative on EUR and GBP, which is why TimelessCity runs trend only on gold and yen.

Tests: `python3 -m unittest discover -s research/truth/tests -v`.
