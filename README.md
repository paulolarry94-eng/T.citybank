# T.citybank

Research lab for a systematic MT5 trading portfolio. Its job is to find out what is true after costs, not what looks good in a
backtest: every idea is written as a strategy file, its settings are fixed before results, and it is tested on 2011-2025 minute
data for 12 markets (plus January-October 2026 for six of them) with spreads, commission, slippage and swaps included.

**Status: frozen on 2026-11-13 for a break of about four months** (tag `freeze-2026-11-13`). Coming back? Start with
`docs/RESUME_AFTER_4_MONTHS.md`. **The repository was public at the freeze**; read `docs/IP_REGISTER.md` section 0.

## Test a strategy
```bash
pip install -r requirements-frozen.txt                      # exact versions the tests passed on (Python 3.11)
python3 -m unittest discover -s research/truth/tests        # 222 tests, under a minute: must end with OK
python3 tools/lab.py priors reversal,intraday               # how earlier ideas like it ended
python3 tools/lab.py new my_idea_v1 --family reversal,intraday --markets XAUUSD,EURUSD --timeframes H1,H4 --hypothesis "Who pays?"
# edit research/truth/strategies/my_idea_v1.py, commit it (the pre-registration), then:
python3 tools/lab.py run my_idea_v1                         # the Truth Lab verdict, without the final look
```
The full routine, with the idea-intake questions and how to read the verdict: `docs/TEST_A_STRATEGY.md`.

## Documents
| Read | For |
|---|---|
| `docs/RESUME_AFTER_4_MONTHS.md` | state at the freeze, how to resume, the yardstick for the months that arrive, decisions waiting |
| `docs/TEST_A_STRATEGY.md` | the routine for testing a new idea |
| `docs/ARCHITECTURE.md` | what is where, and where new work goes |
| `docs/IP_REGISTER.md` | what exists, where it came from, what needs a decision |
| `docs/DATA_AND_SOURCES.md` | data sources and seams, costs, what has been looked at, how to extend |
| `docs/STRATEGY_CATALOGUE.md` | every idea tested (generated from the ledger) |
| `START_HERE.md`, `CLAUDE.md` | one-page status; the rules and everything known (read at the start of every Claude session) |
| `research/results/portfolio/report/report_offline.html` | the portfolio backtest report: one file, opens in any browser |

## What we found
- 133 ideas and about 337,000 configurations tested; 7 survivors or candidates. Chart-pattern ideas have no edge after costs; flows with a payer and
  a few published trend, dip and calendar rules do, but small.
- The recommended candidate is a 13-leg mix (**Timeless 10 + v2**): about +6.7% a year inside a 3.6% drawdown envelope (+15% inside 8%) in
  backtest, every year 2011-25 positive, +0.8% in the ten months of 2026. That is roughly a tenth of the 60-120% aspiration. Nothing is live yet.

## Map
| Folder | What is there |
|---|---|
| `data/` | M1 bid bars 2011-2025 (12 markets) and `holdout/` January-October 2026 |
| `research/truth/` | the Truth Lab: protocol, strategies (one file per idea), costs, tests, memory |
| `research/results/` | every report (one folder per study or strategy) |
| `research/goal/`, `research/portfolio/` | the cycle-goal maths, the timeless mix, the portfolio build and report |
| `research/body4/`, `ema4/`, `sweep4-6/`, ... | engines and detectors for the owner's patterns |
| `mt5/` | MQL5: TimelessCity EA (compiled by the owner), export EA, SEESARE router (uncompiled source) |
| `tools/` | `lab.py` (front door), data download and checks, bootstrap, parity check |
