# Data and sources

Everything the research stands on, where it came from, what is known about its quality, and how to extend it.
Terms of use for the sources are **not verified** (see the last section).

## The price data (`data/`, `data/holdout/`)
1-minute bid bars in `{SYM}_M1_bid_{YEAR}.npz` (keys: `ts` in milliseconds UTC, `o`, `h`, `l`, `c`, and `v` where present). Weekends and
gaps between sessions have no bars, as in MT5. Spreads and commission are not in the bars; they are charged by the cost files.

| Markets | Source | Period | Notes |
|---|---|---|---|
| XAUUSD, EURUSD, GBPUSD, USDJPY | Dukascopy 1-minute bid candles (uploaded by the owner; `research/northstar/PREREGISTRATION.md` section 1) | 2011-2025 | gold starts in May 2011 and has a gap 2018-06-19 to 2018-12-31 (trades spanning it are discarded; `research/REPORT.md`); EURUSD 2023-25 has Dukascopy/Exness seams (OPEN_QUESTIONS Q4) |
| US500, NAS100, UK100, JP225, XAGUSD, EURGBP | HistData.com free 1-minute bars (`tools/histdata_m1.py`) | 2011-2025 | HistData stamps were one hour late in daylight-saving periods; corrected in place (P29, `tools/histdata_clock.py`, `research/results/data/histdata_clock.json`) |
| GER40 | HistData to 2020-01-29, then Exness DE30 Zero ticks | 2011-2025 | HistData's index differs from 2020-06-15 to 2023-12-03, so it was replaced; seams match within 0.3% |
| WTI | HistData to 2023-12-01, then Exness USOIL Zero ticks | 2011-2025 | no monthly roll-gap pattern; the April 2020 negative-oil episode is in the data |
| 2026 (`data/holdout/`): XAUUSD, EURUSD, GBPUSD, USDJPY | Exness Zero-account ticks (ticks.ex2archive.com), bid | 2026-01-01 to **2026-10-30** | a second feed from HistData is in `data/holdout/histdata/` for the same four |
| 2026: EURGBP, GER40 | HistData month by month (`tools/histdata_months.py`) | EURGBP to 2026-10-30; GER40 to **2026-11-06** | |
| Futures (trend + carry only) | pysystemtrade's public futures data, cloned at run time (`bash tools/bootstrap.sh --with-futures-data`) | 2000 on | **not stored in this repo** |

Coverage and sanity: `python3 tools/check_m1.py US500,GER40,WTI,XAGUSD 2011 2025` (start years, gaps, price ranges).

## Costs and swaps
| What | Where | Status |
|---|---|---|
| Exness Zero spreads | `research/exness/exness_costs.py` -> `research/results/exness/zero_spreads.json`, report `research/exness/EXNESS_COSTS.md` | **measured** from Exness's public tick archive (8 markets x 6 sample months): spread about 0 on the Zero account |
| Exness commission | `research/truth/costs_exness_zero.json` | **estimated** at the high end of published rates |
| RoboForex Prime | `research/truth/costs_roboforex_prime.json` | **published** figures (EURUSD 0.55 pip all-in with slippage); the owner plans this broker |
| Lab default costs and swaps | `research/truth/costs.json` | the four research markets measured (20-40% above ECN levels), the rest conservative estimates, marked as such |
| Other brokers (Tickmill, Pepperstone, eToro) | `research/results/sweep4/LOOK.json` | the owner's pasted figures, **unverified** |
| Swap-free status of the owner's account | OPEN_QUESTIONS Q1 | **unconfirmed**; every result is reported with swaps and swap-free side by side |
| US news days | `research/truth/calendars/us_news_days.json` | assembled in-session from public schedules; verify before relying on it |

The real numbers will come from the account itself: compile and run `mt5/NorthStarExport.mq5` (uncompiled source), then
`tools/ingest_mt5.py` (brokers' specs, spreads, swaps, bars, calendar).

## What has been looked at (important for any new test)
The development window is 2011-2019, validation 2020-2022, the final holdout 2023-2025. Every window up to **2026-10-30** has
been used by at least one study: 2023-25 by the final looks of many strategies (`oos_log.json` in each strategy folder), Jan-Oct
2026 by the champion check, the v7 look, the pivot-sweep looks and the 3:30 EMA check. **Only data after 2026-10-30 (GER40 after
2026-11-06) has never been seen.** Treat it as the one clean out-of-sample window, and decide what to test on it before looking
(`docs/RESUME_AFTER_4_MONTHS.md`).

## Extending the data
```bash
python3 tools/exness_m1.py EURUSD 2026 2026          # Exness ticks -> M1 bars; check where it writes, the 2026 files here live in data/holdout/
python3 tools/histdata_months.py EURGBP 2026 11 12   # HistData, a year in progress, month range -> data/holdout/
python3 tools/check_m1.py EURGBP,GER40 2026 2026     # coverage and sanity before any test uses it
```
Not rehearsed after the freeze: run on one market first and compare a few bars against the broker's own chart. HistData names its
pairs differently from our symbols (see the tools). A new market also needs a line in `research/truth/costs.json`.
The Dukascopy downloader (`tools/dukascopy_m1.py`, `tools/get_four_markets.bat`) works from a home PC; Dukascopy throttles cloud
and GitHub addresses.

## Terms of use: not verified
The repo holds derived 1-minute bars of data from HistData.com, Dukascopy and Exness's public tick archive (about 700 MB). This
project did not read or verify their terms for storing or sharing those files. Check them before sharing the repo or the data files
with anyone, and see `docs/IP_REGISTER.md`.
