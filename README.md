# T.citybank

Research lab for a systematic MT5 trading portfolio. Its job is to find out what is true after costs, not what looks good
in a backtest: every idea is written as a strategy file, its settings are fixed before results, and it is tested on
2011-2025 minute data for 12 markets (plus January-October 2026 for five of them) with spreads, commission, slippage and
swaps included.

- **Start here:** `START_HERE.md` (status on one page, how to resume).
- **Final summary:** `research/FINAL_REPORT.md` (the recommended system, the goal against what we have, what to do next).
- **Rules and everything known:** `CLAUDE.md`. Research memory: `research/truth/memory/` (ledger of every idea, principles,
  open questions, journal).

## Test anything
```bash
bash tools/bootstrap.sh                                                   # packages + data check
python3 -m unittest discover -s research/truth/tests                      # 184 tests, about 30 seconds
cp research/truth/strategies/TEMPLATE.py research/truth/strategies/my_idea.py   # write the idea's rules
python3 research/truth/run.py research/truth/strategies/my_idea.py --no-look    # the Truth Lab verdict
python3 research/truth/memory.py --priors <tag>                           # what earlier ideas like it did
```

## Map
| Folder | What is there |
|---|---|
| `data/` | M1 bid bars 2011-2025 (12 markets) and `holdout/` January-October 2026 |
| `research/truth/` | the Truth Lab: protocol, strategies, costs, tests, memory |
| `research/results/` | every report (one folder per study or strategy) |
| `research/goal/` | the cycle-goal maths, the two-week cycle, the timeless mix |
| `research/body4/`, `research/ema4/`, ... | engines and detectors for the owner's patterns |
| `mt5/` | MQL5: TimelessCity EA (compiled by the owner), export EA, SEESARE router (uncompiled source) |
| `tools/` | data download and checks (HistData, Dukascopy, clock fix), bootstrap, parity check |
