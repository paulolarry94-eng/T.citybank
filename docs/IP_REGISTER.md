# IP register: what exists, where it is, where it came from

An engineering inventory of everything built in this repository, so the owner can see what they hold, what depends on other people's
material, and what needs a decision. **It is not legal advice.** Questions of ownership, licensing and protection are for the owner
and, if they matter commercially, a lawyer. Facts below were checked on 2026-11-13 unless stated.

## 0. Read this first
| Fact | Status | Why it matters |
|---|---|---|
| **The GitHub repository `paulolarry94-eng/T.citybank` is PUBLIC** (read from GitHub on 2026-11-13) | **owner action** | Anyone can read, clone and fork every strategy rule, result, EA source and data file below. Making it private is a setting only the owner can change (GitHub: repository Settings, General, Danger Zone, Change visibility). Whatever was public until then may already have been copied or forked: check the repository's forks and traffic on GitHub. A public repo also makes strategy rules hard to keep as trade secrets |
| No `LICENSE` or copyright notice in the repo | owner decision | Without a licence nobody else is granted permission to reuse it, but nothing in the repo says who the rights holder is. This project does not choose a licence or a rights holder for the owner |
| Authorship of the commits | fact | All commits (284 up to 2026-11-12) are authored `Claude <noreply@anthropic.com>`, written in Claude Code sessions at the owner's direction (each carries a `Claude-Session` link). The owner supplied the concepts, rules, charts and decisions; the code, tests and write-ups were produced by Claude. Who owns AI-assisted work is a legal question this register does not answer |
| Secrets | checked | A local scan of every tracked file for API keys, tokens, private keys and password assignments found none; the files most likely to hold credentials (MQL5 sources, `.set` presets, scripts, `.claude/`) hold only message formatters and field names. The owner's email address is not in any tracked file. GitHub's own secret scanner was not used |
| Third-party data inside the repo | **terms not verified** | about 700 MB of derived 1-minute bars from HistData.com, Dukascopy and Exness's public tick archive. This project did not read their terms for storing or sharing; check before sharing (`docs/DATA_AND_SOURCES.md`) |
| Where the only copy lives | risk | GitHub is the only copy of the repo (about 1.4 GB). Keep an offline mirror (section 6) |

## 1. Trading rules (the edge)
### 1a. The recommended mix, Timeless 10 + v2 (13 legs; `research/results/portfolio/`, `research/results/goal/TIMELESS_MIX.md`)
| Leg | What it does | Where | Origin as recorded in the repo |
|---|---|---|---|
| EUR_EuroHours_short_TueThu | sell EURUSD at 09:00 London, buy back 13:00, Tue-Thu, stop 0.5 ATR | `research/hunt/euro_hours.py` (Hunt 2, step 4) | found in the repo's seasonality scan; window chosen on 2011-18 only |
| tokyo_fix_gotobi_v1 | USDJPY buy 23:00 UTC, sell 00:55 UTC on gotobi days (the Tokyo fix flow) | `research/truth/strategies/tokyo_fix_gotobi_v1.py` | a known calendar flow with a payer, implemented and tested here (Q10, Q15) |
| eurusd_close_beyond_reversal_v1 | after a daily close beyond the prior day's range, a stop entry back through the candle's far end; exit at the first profitable New York close, else a 250-pip stop | `research/truth/strategies/eurusd_close_beyond_reversal_v1.py` | **the owner's specification**, 2026-10-31 (Q8) |
| XAU_S1_reversion_H1M30M20 | gold dip reversion (TimelessCity S1) | `mt5/TimelessCity.mq5`, Python twin `research/engine.py` | the owner's TimelessCity EA: compiled by the owner, written before this repo's history begins (who wrote it is not recorded here) |
| JPY_S2_Donchian20_H4_long | USDJPY Donchian 20 trend, long (TimelessCity S2) | same | TimelessCity EA, as above |
| XAU_Donchian20_H4_turtle | gold Donchian 20 breakout trend, H4 | `research/gold_lab.py`, assembled in `research/multi_book.py` | a published method (Donchian/Turtle); parameters from the repo's research |
| XAU_EMA20-50_H4 | gold EMA 20/50 trend, H4 | same | a published method |
| JPY_RSI2_D1_lo5 | USDJPY RSI(2) dip buying, daily | same | a published method |
| GBPJPY_Donchian20_H4_trail | Donchian 20 with trailing stop on GBPJPY (a cross built from the traded legs) | `research/hunt/crosses.py`, `book_v3.py` | a published method on a synthetic cross |
| GBP_WeeklySweep_FollowThrough | GBPUSD continuation after a sweep of the prior week's high or low | `research/liquidity*.py` | found in the repo's liquidity studies (the only continuation that survived about 1,400 variants) |
| v2_EURGBP_H1, v2_NAS100_H1, v2_GBPUSD_M15 | the owner's pivot-sweep range pattern, three thin legs | `research/sweep5/`, `research/truth/strategies/sweep5_pivot_v2.py` | **the owner's pattern** as read from the owner's charts (2026-11-12); the three cells were picked from 1,440 and are weak |

Trade lists behind the legs: `research/trades/` (and `research/trades/champion_2026/` for the 2026 re-run). Status: a candidate for
forward testing. There is no demo or live record.

### 1b. Other survivors
Futures trend + carry (`research/multiasset/`, Carver's published method; works only on real futures, not CFDs); the 11-leg book
(earlier recommendation, `research/results/book_v3.json`); TimelessCity v2.42 with its four presets (`mt5/*.set`).

### 1c. The owner's concepts that were tested (all rejected unless noted)
First-recorded dates are from the ledger. The full list with verdicts and evidence paths is `docs/STRATEGY_CATALOGUE.md`.
| Concept | First recorded | Recorded result |
|---|---|---|
| 4-leg engulfing SOP; Leg 34 gold M5 | 2026-10-31 | rejected (about 0 before costs) |
| Daily close-beyond reversal on EURUSD | 2026-10-31 | **Tier B candidate** (leg of the mix) |
| SEESARE P26 router, win/loss and drawdown ladders, cent-account design | 2026-11-01 | the ladder alone cannot hold the cap; the pre-trade check can (P24-P27); MQL5 uncompiled |
| 5-minute hunter, Magnetic Distance bursts (Q15, Q21) | 2026-11-01 | no edge found after costs |
| 24-flow "payer matrix" and Batch 01 (Q19, Q23); fix flows | 2026-11-01/02 | Tokyo fix survives; ECB fix, London fix, month-end hedge, US close rejected; 11 of 13 untestable here |
| Sweep-and-shift reversal (Q24) | 2026-11-02 | rejected |
| 3:30 EMA retest (Q25) | 2026-11-02 | rejected |
| 4-flip EMA, four-candle price action (Q27) | 2026-11-02 | rejected (v1 failed the lab's look-ahead check) |
| Noise gate (Q28); TradingView Noise Gate (Q29) | 2026-11-06 | Q28 rejected; Q29 waits for the owner's usage rules |
| Body-engulf 4-candle range, v1-v7 (Q30) | 2026-11-07 | rejected, family closed (2023-25 used up) |
| Wealth Game (25% risk on 1:4 trades) | 2026-11-08 | rejected as sizing |
| Pivot-sweep range v1, v2, deep M1 study (Q34, Q35) | 2026-11-12 | rejected as a rule; three thin legs kept for the mix |
| The goal itself: +2% per 10-trade cycle or per two weeks inside a 3.6% drawdown | 2026-11-02 | maths in `research/goal/CYCLE_GOAL_MATH.pdf` (P28) |

Negative results are part of the asset: 108 of 133 ideas were rejected, each with its pre-registration and evidence.

## 2. Software
| Component | Where | Tests / status |
|---|---|---|
| The Truth Lab (protocol, costs, executors, controls, cycle goal) | `research/truth/` | `research/truth/tests/` (225 tests pass in a clean environment at the freeze) |
| Execution core and engine | `research/northstar/core.py`, `research/engine.py` | covered by the lab tests |
| Pattern engines with reference + numba twins | `research/body4/`, `ema4/`, `owner330/`, `sweep4/`, `sweep5/`, `sweep6/`, `pa4/` | trade-for-trade parity tests |
| Research memory (ledger, principles, journal, open questions) | `research/truth/memory/`, `research/truth/memory.py` | tested |
| Front door: scaffold, checks, catalogue | `tools/lab.py`, `docs/` | tested |
| Portfolio build, sizing, report | `research/portfolio/`, `research/goal/`, `research/results/portfolio/report/` | the report's numbers were checked against its data (1,120 marks) |
| MQL5: TimelessCity EA | `mt5/TimelessCity.mq5` | compiled by the owner; demo gate pending; not compiled or run here |
| MQL5: everything else (`TruthEA`, `NorthStarGovernor`, `NorthStarExport`, `Seesare/`) | `mt5/` | **uncompiled source**; Python twins and self-test vectors exist for SEESARE |
| Data tools and parity check | `tools/` | used in practice; not unit-tested |
| Recovered Edge Room modules | `recovered/edge_room/` | partial rebuild of an earlier project from a session transcript; compiles, never run against the original app (`recovered/README.md`) |

## 3. Data and derived data
`data/` (180 files, 12 markets, 2011-2025) and `data/holdout/` (Jan-Oct 2026) are derived 1-minute bars; sources and seams in
`docs/DATA_AND_SOURCES.md`. `research/results/` (about 225 MB) and `research/trades/` (about 295 MB) are derived results.

## 4. Documents and reports
`START_HERE.md`, `CLAUDE.md`, `research/FINAL_REPORT.md`, `research/CONCLUSION.md`, `research/goal/CYCLE_GOAL_MATH.pdf`,
`research/results/goal/TIMELESS_MIX.md`, `research/results/sweep5/PARETO.md`, the portfolio report
(`research/results/portfolio/report/`; live page https://claude.ai/artifact/QRh9Gy181Wsd2pn7uYgx8K, private to the owner's account), the
earlier champion dashboard (https://claude.ai/artifact/BohhgY8e3XiUhstZdVSTVg), and the memory under `research/truth/memory/`.

## 5. Third-party material (check these before sharing the repo)
| Item | Where | How it is used | Status |
|---|---|---|---|
| HistData.com, Dukascopy, Exness tick archive | `data/`, `data/holdout/`, `research/results/exness/` | derived 1-minute bars and spread statistics | terms for storing or sharing not verified |
| trustdan/trend-following-backtesting-strategies (commit a34b7ba) | `research/repofunnel/trustdan.py` | 48 Pine scripts **translated line by line** into rules | derivative translation; upstream licence not checked; none survived testing |
| sofus-nl/swing-trading-strategies (commit 1b7cf1c) | `research/repofunnel/sofus.py` | 18 setups translated (price-only) | derivative translation; upstream licence not checked; none survived testing |
| awesome-systematic-trading | `research/awesome-systematic-trading_README_snapshot.md`, `research/repofunnel/awesome_cfd.py`, `futures_funnel.py` | a snapshot of its README (third-party text) and implementations of the published ideas it lists | licence not checked; remove the snapshot before sharing if in doubt |
| pysystemtrade futures data (Rob Carver) | not stored; cloned at run time by `bootstrap.sh --with-futures-data` | trend + carry research | upstream licence applies to the clone |
| Gold Hunter V9, Dark Mimas EAs (third-party, compiled) | `research/gridbot/` | **replays built from their published settings**; nothing was decompiled or copied | the reports name the vendors and quote their settings |
| TradingView "Pivot Points High Low" and "Noise Gate" | `research/sweep4/pivots.py`, Q29 | re-implemented from the indicators' behaviour and the owner's charts; the Pine source was not copied | the logic mirrors a third-party indicator |
| Broker figures (RoboForex Prime published; Tickmill, Pepperstone, eToro pasted by the owner) | `research/truth/costs_roboforex_prime.json`, `research/results/sweep4/LOOK.json` | cost assumptions | published or owner-supplied; some unverified |
| Python packages: numpy, pandas, numba, holidays, matplotlib, reportlab | `requirements-frozen.txt` | run-time dependencies | their own open-source licences |
| d3 (v7) | inlined in `research/results/portfolio/report/report_offline.html` | charts in the offline report | ISC licence, notice kept in the file |

## 6. Keeping it
1. **Make the repository private now** if the strategies are meant to stay yours (owner action, see section 0).
2. **Keep an offline mirror** (about 1.4 GB), from any computer with git:
   `git clone --mirror https://github.com/paulolarry94-eng/T.citybank T.citybank.git` and copy it to a drive you control. Restore
   with `git clone T.citybank.git T.citybank`. A mirror holds every branch and tag.
3. **Pick a licence or a notice** only after deciding who the rights holder is and whether anyone else will ever use the code.
4. **Date evidence.** Each entry of `research/truth/memory/JOURNAL.md` opens with the owner's own words and a date, which is the record of
   which concepts came from the owner. The git history (commit times, pre-registration commits such as `9305332`, `7b6add8`, `2111f5f`, `796b079`,
   `76afc11`) and the `freeze-2026-11-13` tag are the record of what existed when. A public repository also shows that the material was
   disclosed from the date it went public.
5. **Rebuild check.** From a fresh clone: `pip install -r requirements-frozen.txt`, then
   `python3 -m unittest discover -s research/truth/tests` must end with OK (verified at the freeze).
