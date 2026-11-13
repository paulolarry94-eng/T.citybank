# Architecture: what is where, and where new work goes

The project is a research lab with one rule: nothing is believed until a protocol has stripped it down to what is true after
costs, swaps, luck and hindsight. The layers below run from raw data up to the MT5 code and the memory that records every result.

```
data/                          1-minute bars, 12 markets, 2011-2025 (+ holdout/ Jan-Oct 2026)
  |  research/engine.py        loaders, resampling, the TimelessCity twin
  |  research/northstar/core.py  execution core: fills, spread, commission, slippage, swaps, one trade book
  v
research/truth/                THE TRUTH LAB: protocol.py (one protocol for any idea), run.py, costs*.json, executors.py,
  |                            controls.py, cyclegoal.py, memory.py (+ memory/), tests/
  v
research/truth/strategies/     ONE FILE PER IDEA (49 files + TEMPLATE.py); a strategy file may import a pattern engine
research/<family>/             pattern engines for ideas with their own order logic: reference simulator + numba twin + tests
  v
research/results/<study>/      the evidence: reports, JSON, charts (71 folders); research/trades/ holds trade lists (.npy)
research/goal, portfolio, champion, hunt, seesare, multiasset     portfolio, sizing, report and cap studies
  v
mt5/  tools/                   MQL5 EAs (TimelessCity compiled by the owner, the rest uncompiled), data tools, parity check
```

## The layers

| Layer | Where | What it is |
|---|---|---|
| Data | `data/{SYM}_M1_bid_{YEAR}.npz`, `data/holdout/` | 180 files (12 markets x 15 years; keys `ts` in ms, `o`, `h`, `l`, `c`) plus `holdout/` with Jan-Oct 2026 for six markets. Sources and seams: `docs/DATA_AND_SOURCES.md` |
| Loaders and engines | `research/engine.py`, `research/northstar/core.py` | `engine.load_m1`, `engine.resample`; the execution core with the fill law, costs and financing. more than 50 files import `engine` |
| The Truth Lab | `research/truth/protocol.py`, `run.py`, `executors.py`, `controls.py`, `cyclegoal.py`, `cycles_league.py` | look-ahead check, grid, development gate (2011-19), validation (2020-22), walk-forward, stress, deflated Sharpe, one logged look (2023-25), tiers, swap-free profile, portfolio fit, cycle goal, cost ladder |
| Costs | `research/truth/costs.json`, `costs_exness_zero.json`, `costs_roboforex_prime.json` | all-in round-trip cost and swap per market; the four research markets measured, others estimates (labelled) |
| Strategies | `research/truth/strategies/*.py` | one file per idea: NAME, HYPOTHESIS, FAMILY, MARKETS, TIMEFRAMES, GRID, `signals()` |
| Pattern engines | `research/body4/`, `ema4/`, `owner330/`, `sweep4/`, `sweep5/`, `sweep6/`, `pa4/`, `four/`, `sop/`, `fvg/`, `msnr/`, `orb/`, `liquidity_grab/` | detector + reference simulator (the specification) + numba twin + trade-for-trade parity tests, one folder per owner pattern family |
| Portfolio and reports | `research/goal/` (timeless mix, cycle maths), `research/portfolio/` (build, sizing, report data), `research/champion/`, `research/northstar/risk.py`, `research/hunt/`, `research/seesare/`, `research/multiasset/` | how the survivors combine, risk and drawdown envelopes, payouts, futures trend + carry |
| Evidence | `research/results/<study>/`, `research/trades/` | every report and every trade list cited by the memory |
| Memory | `research/truth/memory/` | `ledger.jsonl` (every idea), `PRINCIPLES.md`, `OPEN_QUESTIONS.md`, `JOURNAL.md`, `LESSONS.md` (generated) |
| Deployment | `mt5/` | `TimelessCity.mq5` + presets (compiled by the owner), `TruthEA.mq5` template, `NorthStarGovernor.mq5`, `NorthStarExport.mq5`, `Seesare/` router (all uncompiled source) |
| Tools | `tools/` | `lab.py` (front door), `bootstrap.sh`, data downloaders and checks, `parity_check.py`, SEESARE twins |
| Report page | `research/results/portfolio/report/` | CSV data, the page source `index.html`, a single-file offline copy |

## Where new work goes

| You want to | Do this |
|---|---|
| Test an idea | `python3 tools/lab.py new <name> ...` (`docs/TEST_A_STRATEGY.md`). Results go to `research/results/truth/<NAME>/`, the ledger is updated by the lab |
| Test an idea with its own order logic | new folder `research/<family>/` with `PREREGISTRATION.md` (committed before any result), reference simulator, numba twin, `research/truth/tests/test_<family>.py` for parity, study scripts that write to `research/results/<family>/`; the strategy file in `research/truth/strategies/` calls them. Model: `research/sweep5/` |
| Add a market | data files in `data/`, a line in `research/truth/costs.json` (mark estimates), `python3 tools/check_m1.py SYM 2011 2025` |
| Add a data source | a downloader in `tools/`, a row in `docs/DATA_AND_SOURCES.md` |
| Build a portfolio of survivors | follow `research/portfolio/build.py`: weights and risk set on 2011-22 only, later periods reported untouched |
| Record anything | the lab appends to the ledger itself; studies run outside the lab need `memory.record(..., source=...)`; then JOURNAL, PRINCIPLES (with evidence), OPEN_QUESTIONS, `memory.py --render`, `tools/lab.py catalogue` |

## Frozen evidence: do not move or rename
The ledger, principles, journal and open questions cite paths under `research/` (results, trades, strategies, engines), and the
tests import them. They are the evidence trail. If something must move, change every citation and re-run the tests in the same
commit. Prefer adding to the layers above over reorganising them.

## Older modules at the top of `research/`
Early scripts written before the lab. They are kept because later code still imports them or because they are the evidence
for early results.
| Imported by newer code (library) | Imported by nothing (historic runners, evidence) |
|---|---|
| `engine.py` (53 importers), `gold_lab.py` (14), `gold_search.py` (9), `portfolio.py` (7), `liquidity.py` (5), `pareto.py` (5), `config.py` (3), `multi_book.py` (2), `funnel.py`, `liquidity2.py`, `payout.py`, `strategies2.py` (1 each) | `gold_book.py`, `liquidity_search.py`, `liquidity2_search.py`, `market_search.py`, `search.py`, `search2.py`, `run_120.py`, `run_final.py`, `run_pareto.py` |

`research/*.md` (`FINAL_REPORT.md`, `CONCLUSION.md`, `REPORT.md`, `FUNNEL.md`) are the early summaries; `START_HERE.md` is current.
`recovered/edge_room/` is a partial rebuild of an earlier project from a session transcript (source material, not a working build).

## Tests
`python3 -m unittest discover -s research/truth/tests` runs the whole suite (lab, pattern engines and their parity, SEESARE twins,
the front door). A pattern engine is only trusted once its fast version matches its plain-Python reference trade for trade.

## Dependencies
Python 3.11, numpy, pandas, numba, holidays, plus matplotlib (charts) and reportlab (PDF) for the report scripts. Exact versions
that the tests passed on: `requirements-frozen.txt`.
