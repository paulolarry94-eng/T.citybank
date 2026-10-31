# Getting more market data (breadth, OPEN_QUESTIONS Q4)

Declared markets (2026-10-31, before any data): **US500, GER40, WTI, XAGUSD**, 1-minute bid bars 2011–2025.
Dukascopy throttles cloud machines, so the download runs on your own PC.

## Route 1 (recommended): Dukascopy via the repo's downloader (Windows)
1. Install Python from https://www.python.org/downloads/ and tick **"Add python.exe to PATH"** on the first screen.
2. Download this branch as a ZIP (about 300 MB because it includes the existing data):
   https://github.com/paulolarry94-eng/T.citybank/archive/refs/heads/claude/loving-davinci-uzjf3z.zip
   and unzip it.
3. Open the unzipped folder → `tools` → double-click **`get_four_markets.bat`**.
   It installs numpy, then downloads 4 markets × 15 years. It prints one line per year, for example
   `US500 2015: 350000 bars, factor 1000, 01-02 -> 12-31, range 1820-2140`. The time it takes depends on
   Dukascopy. If it stops or says "Not finished", double-click it again: finished years are skipped.
4. Upload the new files (`data/US500_M1_bid_2011.npz` and the others, about 5 MB each) to GitHub:
   open https://github.com/paulolarry94-eng/T.citybank/tree/claude/loving-davinci-uzjf3z/data
   → **Add file → Upload files** → drag them in (up to 100 files at a time) → **Commit changes** on that branch.
   Then tell Claude "data uploaded".

Mac or Linux: `python3 tools/dukascopy_m1.py --four 2011 2025` from the unzipped folder.

## Route 2: dukascopy-node (if you have Node.js)
`npx dukascopy-node -i usa500idxusd -from 2011-01-01 -to 2012-01-01 -t m1 -p bid -f csv` (one file per year;
instruments `usa500idxusd`, `deuidxeur`, `lightcmdusd`, `xagusd`). Upload the CSVs, or convert them with
`python tools/ingest_m1.py *.csv`.

## Also: your broker's own prices and costs (Q1)
In MT5 (Exness), compile and run `mt5/NorthStarExport.mq5` (uncompiled source: send any compile errors to Claude). In its
`InpSymbols` input, list the four markets with the names your Market Watch shows (on Exness these are usually US500, DE30,
USOIL and XAGUSD, sometimes with a letter added). Upload the output folder to the repo. This gives the real spreads and swaps that
the tests need. Dukascopy gives the long history.
