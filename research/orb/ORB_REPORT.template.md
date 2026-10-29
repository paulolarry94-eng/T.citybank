# ORB 50 — The Expansion & Continuation System

Research report, strategy specification and final verdict. Every number below comes from the code in
`research/orb/` run on the 15-year 1-minute dataset in `data/`; tables are generated from the saved
result files by `report_md.py`.

## Verdict

**There is no statistically defensible edge in ORB 50, in any of the forms tested. Do not trade it and do
not build the MT5 Expert Advisor.**

- 118,898 configurations were run across 4 instruments (gold, EURUSD, GBPUSD, USDJPY), 4 session opens
  (Tokyo, London, New York 08:00, New York 09:30) and 4 opening-range lengths (5/15/30/60 minutes).
- Before costs, the plain opening-range breakout earns about **+0.01R per trade**: a coin flip. Costs are
  0.10–0.15R per trade because opening-range stops are small, so after costs it loses about **−0.10R per
  trade**, consistently, in all three periods (development −0.107R, validation −0.096R, final
  out-of-sample −0.088R).
- Of 103,040 Model A/B/C configurations, 18 reached t > 2 in the development years (11 of them with at least
  150 trades), all gold, London, pullback version. With this many trials, t would need to exceed 5.1 to mean anything; the deflated Sharpe
  ratio of every finalist is 0.000.
- Walk-forward (re-select the best stable settings from the previous 3 years, trade them blind the next
  year) **lost money in 26 of 27 model-years**.
- The four "best" configurations required by Part 9D were locked and committed before the final years
  were read. **All four lose in 2023–2025** (−0.12 to −0.16R per trade).
- The trend-filtered gold configurations (B and X) made their in-sample profit from **shorts during gold's
  2011–2015 bear market**; their longs lost in every period, including the 2023–2025 gold bull run. That is a
  short bias in a falling market, not an opening-range effect. The gold pullback configuration (C) was
  profitable on both sides in 2011–2019 and lost on both sides in 2020–2022.
- The full specification as written (EMA filter + volatility filter + two-candle pullback + stop beyond
  the pullback swing + chandelier + break-even) is the **worst** variant: −0.20R development, −0.23R final
  out-of-sample, because the tight pullback-swing stop makes costs about a quarter of the risk.

## 1. Data inspection (Part 1)

| instrument | asset class | years | how the file was built | M1 bars kept | spreads | activity (volume) |
|---|---|---|---|---|---|---|
| XAUUSD | spot gold, OTC | 2011-05-10 to 2025 (gap 2018-06-19 to 2019-01-01) | ticks to M1 for 2011–2018, uploaded M1 bid for 2019–2025 | 4.88 M | bid/ask in tick years | tick counts in tick years only |
| EURUSD | spot FX, OTC | 2011–2025 | ticks to M1 for 2011–2021, uploaded M1 for 2022–2025 | 5.54 M | bid/ask in tick years | tick counts in tick years only |
| GBPUSD | spot FX, OTC | 2011–2025 | ticks to M1 for 2011–2017, uploaded M1 for 2018–2025 | 5.45 M | bid/ask in tick years | tick counts in tick years only |
| USDJPY | spot FX, OTC | 2011–2025 | uploaded M1 for every year | 5.54 M | none | Dukascopy volume, every year |

Checks (`data_audit.py`, `session_audit.py`, results in `results/orb_data_audit.json` and `orb_session_audit.json`):

- **Timestamps are UTC** in every file: the US payrolls spike lands exactly on 08:30 New York time in all 15 years.
- 0 duplicate timestamps, 0 out-of-order rows, no hole longer than 4 days except gold's missing second half of 2018.
- Uploaded files pad weekends/holidays with flat "no-tick" bars (up to 20% of rows). They are dropped, as MT5 has no bar for a minute without ticks.
- On 2024-10-09/10 the EUR/GBP/JPY uploads have 457–653 bars whose high/low sit up to 0.3 pip inside the open/close. These are clamped (high = max(o,h,c), low = min(o,l,c)).
- **The 00:00–00:59 UTC hour is missing every day in the tick-built gold (2011–2018) and GBPUSD (2011–2017) files.** That hour holds the Tokyo open, so a Tokyo opening range cannot be rebuilt for those years. Tokyo is therefore tested only on EURUSD and USDJPY. Earlier studies in this repo that held gold or GBP positions through that hour had a one-hour blind spot (exits fall on the next available minute).
- Resolution: 1-minute bars rebuild 5/15/30/60-minute opening ranges exactly. A session is used only if at least 80% of the range's minutes exist; 95.6–99.2% of weekdays qualify per session.
- Real exchange volume does not exist for spot FX or spot gold. Tick counts are activity, not volume; the volume filter was tested only where activity exists in every year (USDJPY).

**Sessions** (local time with daylight saving, converted to UTC day by day):

| session | local open – close | UTC in winter | UTC in summer |
|---|---|---|---|
| Tokyo (TOK) | 09:00–15:00 Asia/Tokyo (no DST) | 00:00–06:00 | 00:00–06:00 |
| London (LDN) | 08:00–16:30 Europe/London | 08:00–16:30 | 07:00–15:30 |
| New York 08:00 (NY8) | 08:00–16:00 America/New_York | 13:00–21:00 | 12:00–20:00 |
| New York 09:30 (NY930) | 09:30–16:00 America/New_York | 14:30–21:00 | 13:30–20:00 |

The March and November weeks when US and UK clocks disagree are handled (e.g. 12 March 2024: NY 08:00 = 12:00 UTC while London 08:00 = 08:00 UTC).

**Costs.** All-in round trip (spread + commission + slippage): gold $0.45, EURUSD 1.5 pips, GBPUSD 1.8 pips, USDJPY 1.2 pips. Measured median spreads in the first three hours of the sessions (tick years): gold $0.30, EURUSD 0.3 pip, GBPUSD 0.9 pip. With a typical $7/lot commission the assumptions are roughly 20–40% conservative, so every table also shows expectancy **before costs** as the upper bound. All positions close inside their session, before the 17:00 New York rollover, so no swap is paid. Account replays use contract sizes (100 oz gold, 100,000 units FX), 0.01-lot steps and a 0.01-lot minimum.

## 2. What was built (Parts 2–4)

Modular code in `research/orb/`:

| file | job |
|---|---|
| `core.py` | data loading, session tables (DST), H4 trend bias, relative activity |
| `strategy.py` | the per-session state machine for Models A, B, C and the reversal test (strategy logic only) |
| `execution.py` | order fills and position management on 1-minute bars (execution only) |
| `reference.py` | a slow, literal re-implementation used to cross-check the fast engine |
| `experiments.py`, `refine.py`, `ablation.py` | the controlled experiment stages (optimisation) |
| `selection.py`, `walkforward.py`, `validate.py`, `final.py` | selection, walk-forward, validation, robustness, guarded final test |
| `metrics.py`, `report.py`, `report_md.py` | Part 7 statistics, figures, this report |

The fast engine and the reference implementation produced **identical trades (0 mismatches over 5,536 trades, 9 configurations, 2 markets)**.

Execution rules (fixed for every test):
- Decisions use completed 5-minute bars only; the H4 trend uses only the last H4 bar that had closed (broker-clock H4, as an MT5 chart draws it).
- Market entries fill at the next minute's open; longs pay the ask (bid + cost).
- Pending stop/limit orders are checked minute by minute. Limits need price to trade through the level; a touch is not a fill.
- If a stop and a target are touched in the same minute, the stop is taken. A stop jumped by a gap fills at the worse opening price.
- Break-even and trailing changes apply from the next minute.
- A trade is skipped if its stop is closer than 3× the cost (also covers broker stop-level limits).
- One trade per session. No new entries, and pending orders expire, three hours after the open. Positions close at the session close.
- No duplicate entries from one breakout: a side re-arms only after a bar closes back inside the range.
- Latency: entries already wait for the next minute; adding one or two more minutes was tested.

## 3. Protocol (Parts 5–6)

- **Chronological split 60/20/20:** development 2011–2019, validation 2020–2022, final out-of-sample 2023–2025.
- The experiment grids could only see 2011–2022: the final years were masked in code. Selection read development years only.
- **Robust selection:** a configuration's score is the lower of its own t-statistic and the median t of its neighbours (same settings, one parameter one grid step away), with at least 150 development trades. This favours broad stable regions over isolated peaks.
- **Validation** was read only for a short list fixed in advance (development score ≥ 1.0, plus the best Model A).
- **Walk-forward** inside 2011–2022: train 3 years, test the next year, for 2014–2022.
- **Final test:** the four Part 9D configurations were committed to git (commit `1476a60`) before one logged run over 2011–2025. The ablation table was run once more on 2023–2025, for reporting only. Every look at the final years is recorded in `results/orb_oos_log.json`.
- **Multiple testing:** deflated Sharpe ratio (Bailey & López de Prado) over the 117,834 configurations in the selection universe; Bonferroni bar t = 5.06 over all trials and t = 2.64 over the six short-listed configurations.

| stage | what varies | runs |
|---|---|---|
| E0 baseline | canonical ORB, 5 exits, every market/session/length | 280 |
| E1 Model A | entry (market / stop above breakout bar / retest at 0.1, 0.25, 0.5 ATR) x stop (far side, breakout-bar swing, 2 ATR, midpoint) x buffer (0, .05, .1, .2 ATR) x target (session close, 1.5, 2, 2.5, 3R) | 22,400 |
| E2 Model B | H4 bias (close, whole body, neutral zone 0.25/0.5 ATR, slope) x EMA 20/50/100 x entry x stop x buffer x target | 40,320 |
| E3 Model C | pullback (1/2/3 candles, last or highest pullback high; ATR retrace .25/.5/.75/1) x displacement (0, .5, 1 ATR) x stop (far side, pullback swing, 2 ATR) x target x bias on/off | 40,320 |
| E4 management | break-even (off, .75, 1, 1.25R) x chandelier (off, 2, 2.5, 3, 3.5 ATR) x partial (off, 50% at 1R) x ATR period (10, 14, 20) | 11,448 |
| E5 filters | OR width bands, volatility regime, impulsive bar, failed attempts, activity | 1,554 |
| E6 reversal | failed breakout faded, 1 or 2 failures, 2 stops, 4 exits, 2 buffers | 1,792 |
| ablation | Part 8 ladder on all 56 market/session/length combinations | 784 |
| **total** | | **118,898** |

## 4. Results

### 4.1 Every model, development years 2011–2019

{{STAGES}}

Canonical ORB (market entry, far-side stop, 2R) by session and instrument, mean over range lengths:

{{SESSIONS}}

London is the least bad session (the only one with a positive expectancy before costs, +0.06R). The New York and Tokyo opens are negative even before costs. Longer ranges lose less, mainly because wider stops make costs a smaller share of risk.

![baseline](figures/01_baseline_map.png)
![t-stats](figures/02_grid_tstats.png)

### 4.2 Management and filters (Parts 3–4)

Change in expectancy from adding one element to the canonical ORB, median over the 56 market/session/length bases:

{{MANAGEMENT}}

{{FILTERS}}

- Break-even, chandelier exits and partial profits change expectancy by about ±0.01R: **noise**.
- Skipping the impulsive breakout bar does not help: chasing is not the problem.
- Cancelling after failed attempts does nothing; fading failed breakouts (E6) has no edge either (best t = 0.33).
- The activity filter on USDJPY is negative in validation.
- One filter helps consistently: **skipping sessions whose opening range is in the narrowest 20% of the last 100** (+0.011R development, better in 70% of bases; +0.016R validation, better in 80%). Trading only when daily volatility is above its 1-year median also helps a little. Neither turns a losing base into a winner.

### 4.3 Ablation (Part 8)

All 56 market/session/length combinations pooled:

{{ABL_ALL}}

London session only:

{{ABL_LDN}}

Gold, London only:

{{ABL_XAU}}

What each component does:
- **EMA trend filter:** removes about 40% of trades and changes expectancy by +0.004R in development, −0.004R in validation and +0.018R in the final years. Small, not reliable.
- **Volatility filter (20th–80th percentile):** no improvement. Only cutting the narrowest ranges helps (section 4.2).
- **Retest entry:** clearly **worse** (−0.03 to −0.04R in every period). Breakouts that come back to the level are disproportionately the ones that fail.
- **Two-candle pullback entry:** the only component that improves every period (+0.03 to +0.04R), and still negative after costs.
- **Chandelier and break-even:** no reliable effect.
- **Stop beyond the pullback swing (the full spec):** the worst change. Tight stops halve the trade count (most fall under the 3x-cost minimum) and push costs to about 0.23R per trade.

![ablation](figures/05_ablation.png)

### 4.4 Walk-forward (2014–2022)

{{WALKFORWARD}}

Picking the best stable ORB settings from recent history and trading them the next year lost money in 26 of 27 model-years, even when it only traded when the training evidence was good ("gated").

![walk-forward](figures/04_walkforward.png)

In-sample and out-of-sample expectancy are correlated ({{ISOOS_CORR}}), but that comes from persistent losers (bad sessions stay bad). The best 1% of configurations in-sample ({{ISOOS_N}} configs) averaged **{{ISOOS_TOP}}R per trade** in validation.

![in-sample vs out-of-sample](figures/03_is_vs_oos.png)

### 4.5 Validation of the short list (2020–2022)

{{VALIDATION}}

The strongest development candidate (gold London pullback, +0.25R, t = 2.3) is **significantly negative** in validation (−0.29R, t = −2.7). Gold 2019 was already an uploaded-file year and was that candidate's best year, and EURUSD failed in 2020–21 while still on tick-built data, so the break is real, not a data-source artefact.

### 4.6 The four best configurations (Part 9D) and the final test

{{FINAL_NAMES}}

Full Part 7 statistics ($100,000 account, 0.5% risk per trade, lot-rounded, after costs):

{{FINAL}}

Robustness on 2011–2022 (before the final years were read): cost and latency stress, deflated Sharpe, and 3-year Monte Carlo resampling by whole months:

{{STRESS}}

Extra latency only affects market-order entries (B and X). A and C enter with resting stop orders, so their delay rows equal the base. Configuration X survives 1.5x costs in 2011–2022 but not 2x, and was chosen with knowledge of 2020–2022, so only its 2023–2025 result is a clean test, and that result is negative.

Market regimes (trend from the daily 200-day average and its slope; volatility from daily ATR against its 1-year median; shock = inside a listed disruption window such as the 2015 SNB unpeg, the 2016 Brexit vote, the 2020 COVID crash, the 2022 gilt crisis, the 2024 yen carry unwind or the 2025 tariff shock):

{{REGIMES}}

![equity](figures/06_equity.png)
![drawdown](figures/07_drawdown.png)
![annual](figures/08_annual.png)
![monthly](figures/09_monthly_X.png)
![trade distribution](figures/10_trade_dist.png)
![sensitivity](figures/11_sensitivity.png)
![in-sample vs final](figures/12_is_vs_oos_final.png)

Note on the sensitivity chart: the gold Model C region is broad and stable in-sample (every pullback rule and displacement is positive), exactly what Part 5 asks for, and it still failed. A stable region inside one regime is not robustness across regimes.

## 5. What worked, what failed, and why

**Worked (relatively):** the two-candle pullback entry (+0.03R), skipping the narrowest 20% of opening ranges (+0.01–0.02R), London over New York/Tokyo, longer ranges over 5-minute ranges. None of these makes ORB profitable after costs.

**Failed:** pure ORB in every market/session/length; the H4 EMA filter as an edge source; retest entries; break-even; chandelier exits; partials; impulsive-bar, failed-attempt and activity filters; fading failed breakouts; the full combined specification.

**Why:**
1. **No continuation edge at these opens.** Spot FX and spot gold trade around the clock, so the London and New York "opens" are not price-discovery auctions. Opening-range breakouts continue about as often as they fail: +0.01R before costs, pooled.
2. **Costs are large relative to ORB stops.** A stop at the far side of a 15-minute range is typically 4–9 times the cost, so every trade pays 0.10–0.15R before it starts (0.23R with pullback-swing stops).
3. **Selection bias.** With 100,000+ variants, some look good by chance. The best in-sample 1% were negative later; the deflated Sharpe ratio of every finalist is 0.
4. **Regime dependence.** The trend-filtered gold results were shorts in a gold bear market; the filter did not turn that into an all-weather effect (their longs lost in every period, including the 2023–2025 bull market). The gold pullback version worked on both sides in 2011–2019 and stopped working on both sides from 2020.

**Instruments:** none qualifies. **Sessions:** none qualifies; London is least bad, the New York opens and Tokyo for EURUSD are worst. **Conditions to avoid (if anyone trades ORB anyway):** the New York opens, very narrow opening ranges, tight structure-based stops, retest entries.

Not tested because the data does not contain it: equity-index futures at their cash open (ES/NQ at 09:30 New York), where published ORB research is concentrated. That would need exchange data with a real opening auction.

## 6. Strategy specification (Part 9B)

Exact rules of the engine, so every number here can be reproduced or ported. Shown for configuration X (the "best robust combined"); the other configurations differ only in the parameters listed in section 4.6 and `results/orb_final.json`.

Notation: day d; session open T_o and close T_c in local time converted to UTC; opening-range length L = 60 minutes; cost c = $0.45; prices are bid.

1. **Opening range.** Window [T_o, T_o + L) on 1-minute bars. ORH = max high, ORL = min low. Valid only if at least 0.8·L minutes exist and ORH > ORL.
2. **Execution bars.** 5-minute bars aligned to UTC multiples of 5 minutes. ATR_j = simple average of the true range over the last 14 bars.
3. **Entry window.** Bars with open time in [T_o + L, T_o + 3h).
4. **Trend bias.** H4 bars start at 02, 06, 10, 14, 18, 22 UTC. EMA20 of H4 closes. At 5-minute bar j, use the last H4 bar k that closed at or before bar j's close. Bias = +1 if close_k − EMA_k > 0.25·ATR14(H4)_k; −1 if < −0.25·ATR14(H4)_k; otherwise 0.
5. **Range filter.** w_d = (ORH − ORL) / ATR14 of daily UTC bars (last completed day). Trade the session only if w_d is at or above the 20th percentile of w over the previous 100 sessions (at least 20 needed).
6. **Long signal.** The first bar j in the window with close_j > ORH, long side armed, bias_j = +1. Short mirror: close_j < ORL, bias_j = −1.
7. **Entry.** Market order at the open of the first minute after bar j closes. Long fill = bid open + c; short fill = bid open.
8. **Stop.** Long: ORL (sell on bid ≤ ORL). Short: ORH (buy when ask = bid + c ≥ ORH). Risk = |fill − stop|. Skip if risk < 3c.
9. **Exit.** Stop as above, filled at the stop or the worse open after a gap; otherwise at the open of the first minute at or after T_c (16:30 London). No target, no break-even, no trailing.
10. **Limits.** At most one trade per session per instrument. Pending orders (other models) expire at T_o + 3h.
11. **Sizing.** lots = floor(0.005 · equity / (risk · 100 oz) / 0.01) · 0.01; skip if below 0.01 lot.

Model C (configuration C) replaces steps 6–8. After the breakout close, wait until the highest high since the breakout exceeds ORH + 0.5·ATR (displacement). Then require 3 consecutive bearish bars. Place a buy stop at the highest high of those pullback bars, following further pullback bars. Cancel if a bar closes back below ORH or at T_o + 3h. Stop at ORL. Exit at the session close.

## 7. MT5 Expert Advisor

Not built. Part 9E asks for an EA only if the results justify it, and they do not. The rules in section 6 are complete enough to port one later (one terminal, one chart per instrument), but no tested configuration has a positive out-of-sample expectancy to implement.

## 8. Reproduce

```
cd research/orb
python3 data_audit.py && python3 session_audit.py       # Part 1
python3 experiments.py E0 E1 E2 E3 E6                    # grids (2011-2022 only)
python3 refine.py E4 E5 && python3 ablation.py           # management, filters, ablation
python3 walkforward.py && python3 component_effects.py && python3 ablation_report.py
python3 final.py                                         # locked configs, final years (logged)
python3 report.py && python3 report_md.py                # figures and this report
```

Every experiment (parameters plus per-year trade count, sum of R, sum of R², wins, losses and cost) is in `results/orb_experiments/*.csv.gz`.
