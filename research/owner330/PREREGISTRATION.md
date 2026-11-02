# Owner's 3:30 EMA retest edge — pre-registration (2026-11-02, before any backtest result)

Source: the owner's 20 TradingView charts (15-29 Oct 2026; gold, GBPUSD, EURGBP, USDJPY; images kept in the session, not in
the repo) and the owner's written answers. Code: `research/truth/strategies/owner330_ema_retest_v1.py` (the lab fingerprints
it); tests: `research/truth/tests/test_owner330.py`.

## The rules (owner's words → code)
| Step | Owner | Code |
|---|---|---|
| Anchor | "at 3:30 a candle breaks the 10 EMA"; "opens one side, closes the other"; "always 9:30 New York ... open to optimisation" | M30 candle at the anchor time; SELL if open > EMA > close, BUY if open < EMA < close, EMA = 10-period EMA of M30 closes as it stood when the candle opened. Anchors tested: `wat1530` (15:30 Nigerian time = 14:30 UTC, as in the owner's October charts) and `ny0930` (09:30 New York, moves with US daylight saving). In October the two differ by an hour. |
| Range | "wick to wick, full high to low" | The anchor candle's high and low. |
| Retest | "just the next candle after 3:30 ... you're in the retest" | No extra condition: the M5 search starts with the first M5 candle after the anchor closes. |
| Reference | "price finally breaks out of the EMA, within the 3:30 candle range"; previous M5 close on the other side | First M5 candle with previous close on the other side of the M5 10 EMA and this close on the bias side, whose high-low touches the range (changed after the replay, see below). One per day. |
| Cancel | "if the M5 just wicks the range and does not close above, it's valid" | An M5 CLOSE beyond the opposite end of the range cancels the day (also a pending order). Wicks don't. |
| Entry | "entry at candle low (sell) / high (buy), SL at the other end"; "after it breaks ... next candle is entry, correction but test both"; "test for the optimal" waiting time | A: stop order at the reference low (sell). B3/B6/B12: price first trades through the low, then a limit at the low catches the pullback within 3/6/12 M5 candles. |
| Big candle | "50% of a candle if it's more displaced than previous ones" ; "1.5x average size" | Reference range ≥ 1.5 × average range of the 10 M5 candles before it → limit at its 50% level, stop at its far end (both A and B). |
| Target | "test 2R, 3R, 4R also with breakeven and no breakeven" | 2R / 3R / 4R; breakeven = stop to entry once +1R is reached. |
| Time | "time exit end of New York session close ... no trades to next day" | Close at 16:00 New York (US cash close). Orders expire then. |
| News | "skip big news day" | Skip US NFP, CPI and FOMC decision days (official dates, `research/truth/calendars/us_news_days.json`). |
| Markets | "test for all the markets, same 3:30 M5 strategy" | XAUUSD XAGUSD EURUSD GBPUSD USDJPY EURGBP WTI US500 NAS100 GER40 UK100 JP225 (EURGBP downloaded from HistData for this test). |

## Choices the owner did not specify (fixed now, stated plainly)
1. EMA settings: 10-period EMA of closes on M30 and M5 (TradingView's default `ema(close, 10)`).
2. Anchor "opens on one side": judged against the EMA as it stood when the candle opened. On a chart the line drawn ON the
   candle already includes its close, so an open within a hair of the line can look valid on the chart and not in real
   time (the owner's USDJPY 27 Oct test is such a case). No minimum margin is added.
3. Time exit 16:00 New York. In US winter the lab's rollover block (no fills 20:30-23:00 UTC) removes the last 30 minutes
   of entries.
4. Breakeven trigger at +1R; on the fill minute neither the target nor the breakeven move is checked; same minute stop
   first (all conservative).
5. Trades whose stop is closer than 3 × the round-trip cost are skipped (lab standard).
6. Costs: RoboForex Prime published averages (spread + commission + 0.2-pip-class slippage), `costs_roboforex_prime.json`;
   XAGUSD (published figure implausible) and UK100 (not on Prime) use the lab's standard costs. No swaps (no overnight).

## Test
- Truth Lab, unchanged protocol: development 2011-19 gate (≥ 200 trades, both halves positive, ≥ 75% of markets positive),
  neighbours, validation 2020-22, walk-forward, stress (costs ×1.5, +1 minute), deflated Sharpe over 48 configurations,
  ONE logged look at 2023-25, tiers.
- Grid: anchor 2 × entry 4 (A, B3, B6, B12) × target 3 × breakeven 2 = **48 configurations**, 12 markets.
- Selection is cycle-centric (owner): gate-passing configurations are ranked by 2011-19 edge quality s (mean R / spread of
  R), which sets the return per 10-trade cycle inside a drawdown cap (P28). Set in the strategy file (`SELECT_BY = "s"`).
- Control (never selected): the same rules with the anchor 2 hours later (16:30 UTC / 11:30 New York), `controls.py`.
- Owner's stricter rule also reported: REAL only if t ≥ 3 in 2011-19, beats the control, holds up in 2020-22 and in
  every market.

## Reports (cycle-centric, as the owner asked)
For every configuration (2011-19 and 2020-22 only; the holdout stays closed): trades, trades a year, win rate, edge quality,
the return per 10-trade cycle at a 3.6% / 5% lifecycle drawdown cap, share of positive cycles, cycles a year, how long a
360-trade lifecycle takes, and lifecycles completed. For the selected configuration also 2023-25 (the one look).

## What is not clean
- 2026 is NOT an out-of-sample period for this strategy: the owner built and illustrated it on recent charts (Oct 2026).
  The cleanest data for it is 2011-2022 (which the owner has not studied) and the 2023-25 holdout.
- The replay check runs on the owner's own example days (Oct 2026) to confirm the code makes the owner's calls; it is an
  implementation check, not evidence of an edge (P18: case studies select winners).

## Priors (memory, told to the owner)
Intraday session patterns on these markets were rejected after costs: ORB at the New York open, the London best-setup
scanner, the Leg 34 pocket scan across 11 markets × 6 timeframes × 3 sessions (P1, P14, P21). This idea differs in using
the owner's specific anchor + EMA + retest sequence and a fixed R target; the expectation from priors is rejection.

## Changes made after the replay check, before any backtest (2026-11-02)
The replay (`research/owner330/replay.py`, `research/results/owner330/REPLAY.md`, charts in `research/results/owner330/charts/`)
ran the scanner on the owner's ten example days (Oct 2026). Two things changed because of it; no 2011-2025 result had been
produced.
1. **Data: HistData's clock was one hour late in daylight-saving periods.** The owner's EURGBP 23 Oct chart did not match our
   data; measured week by week against independent, correctly timed data, every HistData market (EURGBP, XAGUSD, US500,
   NAS100, UK100, JP225, GER40 to Jan 2020, WTI to Dec 2023) was stamped New York local time with US daylight saving in
   2011-2018 and with UK daylight saving from 2019, although documented as EST without daylight saving. Fixed in the data
   files (`tools/histdata_clock.py --fix`; after the fix 832/833 EURGBP weeks and 743/743 XAGUSD weeks align; index opens land
   on the exchange open minute in summer and winter). `tools/histdata_m1.py` now converts correctly.
2. **"Within the range" = the reference candle touches the range.** The owner's gold 29 Oct reference (16:40) closed below the
   range low, but its high reached into it, and the owner took it. Requiring the close inside the range rejected it;
   requiring the candle to touch the range matches all ten examples. The owner's GBPUSD 28 Oct "16:00 no setup" is explained
   by the fresh-cross rule (every M5 close from 16:00 to 16:40 was already above the EMA).
3. Technical: the scanner's compiled functions no longer use numba's file cache (it failed when the lab loads strategy files
   under another module name).

Replay result after the changes: the scanner makes the owner's call on 9 of 10 days (references within one M5 candle, entry
and stop levels within cents/0.4 pip of the owner's). The miss: EURGBP 27 Oct, where the owner's 16:00 reference closed
exactly on the M5 EMA in our data (0.83664 vs 0.83664): a sub-pip feed difference. Note: 28 Oct 2026 was an FOMC day; the
backtest skips such days as the owner asked.

## Result (2026-11-02) and a proposed look (NOT made; it waits for the owner's word)
The lab rejected the strategy at the development gate: all 48 configurations lost after costs in 2011-19 and 2020-22
(`research/results/owner330/RESULT.md`). No configuration was selected, so the lab made no 2023-25 look. Jan-Oct 2026 (the
owner's own period, not a clean test) was positive for the 15:30 WAT anchor, only in US summer time, when 15:30 WAT is 10:30
New York (`season_split.json`). Written down now, before anyone sees 2023-25 for this strategy:

**Proposed one look at 2023-25.** Question: did the 15:30 WAT anchor in US summer time turn positive before 2026?
- Computed exactly: this strategy file as fingerprinted (7a93770f7272...), anchor wat1530, entries A and B3, target 3R,
  breakeven off; trades from 2023-01-01 to 2025-12-31 split by US daylight-saving season at the entry time (summer is the
  question, winter is reported too); the five markets with 2026 data (XAUUSD, EURUSD, GBPUSD, USDJPY, EURGBP) as the test,
  all twelve markets reported alongside; RoboForex Prime published costs; mean R, t and trades per year.
- Decision rule: **shift began before 2026** if the five-market 2023-25 summer mean is above 0 for both entries and t >= 2
  for at least one: then a forward test from mid-March 2027 is worth running. **No shift** if the summer mean is <= 0 for
  both entries: 2026 is treated as noise plus selection and Q25 is closed as rejected. Anything else: unclear, forward test
  only.
- One look, logged (date, fingerprint, this rule) in `research/results/owner330/look_2023_25.json`. Changing any rule after
  it requires a new strategy name.
