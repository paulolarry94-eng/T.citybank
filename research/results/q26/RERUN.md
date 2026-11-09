# Q26 · Intraday studies re-run after the HistData clock fix (2026-11-03)

**Outcome: no verdict changed and nothing new survives.** Every intraday study that used HistData markets was re-run on
the corrected data, with the same code and the same strategy files (same fingerprints). Numbers moved a little (a typical
cell by about 0.02R a trade), and all of them are still rejected.

Why this was needed: HistData's M1 stamps were one hour late in daylight-saving periods (P29). The data was fixed in commit
e68f660. Affected: EURGBP, XAGUSD, US500, NAS100, UK100, JP225 (all years), GER40 (to 2020-01-29), WTI (to 2023-12-01).

**Control:** XAUUSD, EURUSD, GBPUSD and USDJPY were never HistData. Their numbers came out identical in every study (pocket
scan 0 of 144 cells changed; gold's learned rule and cut points unchanged). So every difference below comes from the data
fix, not from code changes since the studies were first run.

## Old vs new

| Study | Headline | Old (shifted clock) | New (fixed clock) | Verdict |
|---|---|---|---|---|
| Leg 34 pocket scan (396 cells) | cells passing discovery / confirmed / survivors | 1 / 0 / 0 | 1 / 0 / 0 (same GBPUSD H1 London cell, unaffected market) | Rejected, unchanged |
| | cells positive after costs 2011-19 | 15 (3.8%) | 13 (3.3%) | |
| | persistence before costs: positive in 2020-22 if positive / negative in 2011-19 | 34% / 32% | 27% / 33% | still no persistence |
| | median R after costs by session, 2011-19 (Asia / London / NY) | -0.24 / -0.23 / -0.23 | -0.25 / -0.21 / -0.23 | sessions still alike |
| | median R after costs M5 → H1, 2011-19 | -0.27 → -0.20 | -0.30 → -0.20 | |
| | median R before costs by timeframe, 2011-19 | -0.01 to -0.05 | -0.01 to -0.06 | no raw edge at any timeframe |
| | M30 16-20 UTC hint on 9 other markets, 2011-19 (t3) | -0.27 | -0.26 | negative on 9 of 9, unchanged |
| Winner anatomy (learn on gold 2011-19) | best 2-condition rule | cost_R low & EMA slope mid, not kept | identical, not kept | Rejected, unchanged |
| | rule on the other 10 markets, 2011-25 (ladder) | -0.101R (10,345) | -0.101R (10,382) | |
| | rule on JP225 / US500, 2011-25 | +0.19R (92) / -0.05R (634) | +0.10R (92) / -0.08R (649) | |
| Runner profile (score ≥ 3) | other 10 markets 2011-25 (ladder) | -0.345R (36,772) | -0.345R (36,740) | Rejected, unchanged |
| | every setup, same markets | -0.314R | -0.314R | profile still worse than no filter |
| Q21 opening-range tick volume | GER40 2020-25, USDJPY 2011-25 | — | byte-identical | Unchanged (see note) |
| tom_indices_v2 | 2011-19 / 2020-22 R per trade | -0.058 (t -2.86) / -0.037 | -0.053 (t -2.67) / -0.027 | Fails gate, unchanged |
| opex_week_indices_v2 | 2011-19 / 2020-22 | -0.032 (t -1.61) / -0.113 | -0.031 (t -1.57) / -0.126 | Fails gate, unchanged |
| oil_equity_v2 (long/cash) | 2011-19 / 2020-22 | -0.014 / +0.053 | -0.014 / +0.052 | Fails gate, unchanged |
| oil_equity_v2 (long/short) | 2011-19 / 2020-22 | -0.075 (t -3.66) / -0.032 | -0.074 (t -3.55) / -0.032 | |
| payday_indices_v1 | 2011-19 | +0.016 (t 2.11) | +0.014 (t 1.69) | Rejected, unchanged |
| | 2020-22 | -0.010 | -0.025 | |
| | 2023-25 (one logged look, 2026-11-01) | -0.006 (151, t -0.45) | +0.002 (149, t 0.14) | ≈ 0 either way |

R per trade after costs and swaps, at the lab's cost estimates for the index, oil and silver CFDs. Trade counts in brackets.

## Notes

- **Configurations tried:** none new. The same 396 pocket cells, 133 anatomy conditions, 2 runner-profile scores and 5 lab
  configurations as before; nothing was selected again.
- **Holdout:** only `payday_indices_v1` had a logged 2023-25 look. The lab replays that logged look (it does not recompute
  it), so the corrected 2023-25 figure comes from `research/q26/payday_holdout_corrected.py`, for information. Its
  `oos_log.json` is unchanged. The other three lab strategies were run with `--no-look` (they never had a look and still fail
  the gate).
- **Q21 is byte-identical** because it studies GER40 only in 2020-25 (no tick volume before 2020). GER40's HistData part ends
  on 2020-01-29, in winter, when the stamps were already right; USDJPY was never HistData.
- **Silver's "before costs" figure in the anatomy study is not meaningful**: the estimated cost averages 1.3R a trade, so the
  before-costs mean is driven by a few huge outliers (2011-19: +0.85R old, +0.30R new; median -0.03R both times). After costs
  it is -0.80R both times.
- **Not re-run:** daily studies (breadth trend, index RSI(2), repo funnels, `ath_trend_v1`). The fix only moves their day
  boundary by an hour; low priority.
- Batch 01 was re-run on 2026-11-02 (`research/results/batch01/BATCH01_REPORT.md`): verdicts unchanged; the one positive US
  close slice in 2020-22 was a clock artifact.

## Reproduce

```bash
python3 research/hunter5m/winner_anatomy.py
python3 research/hunter5m/runner_profile.py
python3 research/hunter5m/pocket_scan.py
python3 research/q21/velocity_diagnostic.py
python3 research/truth/run.py research/truth/strategies/tom_indices_v2.py --no-look
python3 research/truth/run.py research/truth/strategies/opex_week_indices_v2.py --no-look
python3 research/truth/run.py research/truth/strategies/oil_equity_v2.py --no-look
python3 research/truth/run.py research/truth/strategies/payday_indices_v1.py
python3 research/q26/payday_holdout_corrected.py
python3 research/q26/compare.py        # old results read from git commit 76d7dfe -> rerun_compare.json
```
