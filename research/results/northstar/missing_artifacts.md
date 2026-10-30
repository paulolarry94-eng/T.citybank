# Missing or incomplete artifacts

| artifact | state | how to recover |
|---|---|---|
| Hour-of-day seasonality scan and window searches (hunt/seasonal_scan.py, windows.py, windows2.py) | printed only, no result file | re-run the scripts (deterministic) |
| Gold 18:00-20:00 WAT test (msnr/gold_wat.py) | printed only | re-run the script |
| MSnR robustness probe (msnr/probe.py) | printed only | re-run the script |
| Euro European-hours variants (hunt/euro_hours.py) | printed only; trades saved for 2 variants | re-run the script |
| Cross-pair trade files (trades/crosses) | 169 of 171 not committed (regenerable) | re-run hunt/crosses.py |
| Per-configuration maximum drawdown for every grid run | never computed (grids log per-year sums only) | recompute per configuration if needed |
| Profit factor for four-strategy and FVG grid runs | wins/losses sums not logged | re-run grid with pos/neg sums |
| Walk-forward results for the four-strategy, FVG and MSnR studies | not run in those studies | run North Star walk-forward on their candidates |
| Per-trade logs of grid configurations | not saved by design (aggregates only); saved for finalists and book legs | re-run a configuration to regenerate |
| P26 / TimelessCity early studies (search.py, search2.py, strategies2.py) | partly summarised in results/*.json; some early outputs recovered from transcript only | see recovered/README.md |
| Financing (swap) costs in all pre-North Star studies | not modelled | North Star re-scores baselines with financing |
