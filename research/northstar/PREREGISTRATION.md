# North Star — pre-registration

Written and committed BEFORE any North Star experiment was run. Thresholds below are not to be
changed after results are seen; any later change must be recorded as an amendment with its reason
and date, and the original kept.

## 1. Data, costs, execution (same as all earlier studies)

- Data: Dukascopy 1-minute bid bars, UTC, XAUUSD / EURUSD / GBPUSD / USDJPY, 2011–2025
  (gold 2011-05 onward, gap 2018-06-19 → 2019-01-01; trades spanning a data hole are discarded).
- All-in round-trip cost (spread + commission + slippage): XAUUSD $0.45, EURUSD 1.5 pips,
  GBPUSD 1.8 pips, USDJPY 1.2 pips (≈20–40% above measured ECN levels).
- Fill law: decisions on completed bars only; market entries at the next bar's first minute
  (longs pay the ask = bid + cost); pending limit/stop orders filled minute by minute (limits must
  trade through by 0.1 x cost); same-minute stop + target = stop; gaps fill at the worse open;
  stop and trail changes act from the next minute; one position at a time per strategy and market
  (no duplicate entries); stop distance must be ≥ 3 x cost and ≤ the module's ATR cap.
- **Financing (new):** every position pays a financing charge per 22:00 UTC rollover it is held
  through (x3 on Wednesday): XAUUSD $0.20/oz, EURUSD 0.6 pip, GBPUSD 0.6 pip, USDJPY 0.8 pip, charged
  in both directions (no positive carry credited). A conservative constant approximation of real,
  rate-dependent swaps; sensitivity at x2 is reported.
- **Session restriction (new):** no new entries and no pending-order fills from 20:30 to 23:00 UTC
  (rollover spread widening).
- Pending orders expire as defined per module; a setup is consumed after one trade.

## 2. Periods

Development 2011–2019 (selection), validation 2020–2022 (confirmation of a short list),
final out-of-sample 2023–2025 (one logged look per locked configuration). Walk-forward: train 3
years → test the next year, 2014–2022, re-selecting by the same rule each year. Development eras
for stability: 2011–2015 and 2016–2019.

## 3. New modules and grids (declared in full; nothing outside these grids is searched)

Timeframes: M5, M15, M30, H1, H4 (H4 = broker clock, 22/02/06/10/14/18 UTC). ATR = 14-bar SMA of
true range on the module's timeframe. Management for every module: target {2R, 3R, none} x
chandelier trail {none, 3 ATR}; no breakeven (earlier studies: breakeven adds no out-of-sample
edge); time stop 50 bars. Optional bias filter on every module: last CLOSED H4 bar's close above
(long) / below (short) its EMA50.

**SD — supply and demand bases.** Leg-in candle: body ≥ k x ATR (k ∈ {1.0, 1.5}); base: nb ∈ {1, 2, 3}
consecutive candles each with range ≤ 0.6 ATR; leg-out candle: body ≥ k x ATR and close beyond the
base extreme by ≥ 0.1 ATR. RBR = up/up (long), DBD = down/down (short), DBR = down/up (long), RBD =
up/down (short); continuation (RBR, DBD) and reversal (DBR, RBD) are separate modules. Entry:
`break` = next open after the leg-out close; `retest` = limit at the base's proximal edge (base high
for longs) valid 20 bars, cancelled by a close beyond the base's distal edge. Stop: base distal edge
∓ 0.1 ATR; stop cap 4 ATR.

**FVG — fair value gaps.** Bullish: low(c3) > high(c1); gap = [high(c1), low(c3)]; bearish inverse.
Minimum width w ∈ {0.1, 0.3} ATR (narrower gaps rejected). Known only after c3 closes. A gap is
partially filled while price trades into it without closing beyond its far edge (still valid) and
fully filled / invalid once a candle closes beyond its far edge. Stop for all models: beyond c1's
far extreme ∓ 0.1 ATR; stop cap 4 ATR.
- A retest: limit at depth d ∈ {0 (near edge), 0.5 (midpoint)} of the gap, placed buffer b ∈ {0, 0.1}
  ATR before that level, valid for a maximum gap age g ∈ {10, 30} bars.
- B pullback confirmation: price trades into the gap; an opposite-colour candle whose low (long) is
  inside the gap is the pullback candle; a later candle closing beyond the pullback candle's high
  (long) triggers entry at the next open; all within age g ∈ {10, 30}.
- C structure shift: model A (d 0, b 0, g 30) only for gaps whose displacement candle (c2) closes
  beyond the most recent confirmed swing high (long) / low (short); swing pivot k = 3, confirmed
  before c2.
- D 4H alignment: model A only with the H4 EMA50 bias.
Timeframes for FVG: M5, M15, M30, H1.

**QM — Quasimodo.** Confirmed pivots: a pivot high at bar j is the strict highest high of bars
j−k..j+k and becomes known at the close of bar j+k (k ∈ {2, 3, 5}); pivot lows likewise; pivots
alternate (consecutive same-type pivots keep the more extreme). Bullish QM on the latest four
alternating pivots L1 (low), H1 (high), L2 (low), H2 (high) with: L2 < L1 − m x ATR (lower-low
break; m ∈ {0.25, 0.5}), H1 − L2 ≥ 1.0 ATR, H2 < H1 (lower high). Trigger: the first close above
level ∈ {H2, H1} after H2 is confirmed, within 30 bars. Entries: `break` = next open after the
trigger close; `retest` = limit at the QM level L1 + t x ATR (t ∈ {0, 0.25}) valid 30 bars, cancelled
by a close below L2. Stop: L2 − 0.1 ATR; stop cap 5 ATR. Bearish inverse. Timeframes M15, M30, H1, H4.

**Combinations (filters on a primary module's entries, tested for incremental value):**
QM + FVG (a same-direction FVG formed within the 10 bars before the entry decision), RBR + FVG
(same), RBR + QM (a same-direction QM trigger within the 30 bars before the entry decision), and
"all new modules" as a portfolio of the best configuration of each module (not one AND condition).

## 4. Test order

1 RBR and DBD; 2 DBR and RBD; 3 FVG-A; 4 FVG-B; 5 QM; 6 QM + FVG; 7 RBR + FVG; 8 RBR + QM;
9 all new modules combined; 10 promising modules against the original strategies (ORB finalists,
the four-strategy rules, the 11-leg book).

## 5. Selection and acceptance criteria

Per module: development gate (pooled over markets: ≥ 200 trades, E > 0 in both development eras,
≥ 3 of 4 markets positive); rank by pooled development t; the top configuration per module is the
module's candidate; validation and walk-forward are reported for every candidate.

**Tier A — deployment-ready candidate** (all required):
1. Expectancy after costs AND financing > 0 in development, validation and final out-of-sample.
2. Final out-of-sample: profit factor ≥ 1.10, t ≥ 2.0, ≥ 100 trades.
3. Walk-forward pooled expectancy > 0.
4. Parameter stability: every one-step neighbour in the module's grid has development E > 0;
   median neighbour development t ≥ 1.0.
5. Cost stress: development+validation expectancy > 0 with costs x1.5, financing x2, and +1 minute
   latency on market entries.
6. Breadth: final out-of-sample positive in ≥ 2 markets.
**Tier B — forward-test candidate:** criteria 1, 4 and 5, final out-of-sample E > 0 and PF ≥ 1.05.
**Rejected:** anything else. If nothing reaches Tier A, the report states that no deployment-ready
configuration has been established.

Multiple testing: the number of configurations per module is reported with the deflated Sharpe
ratio of each candidate; the final out-of-sample look is limited to the module candidates and
the combinations named in section 4 (each look is logged).

## 6. Portfolio risk manager (thresholds fixed here)

Sizing: fixed fractional risk per trade on current equity x leg weight (inverse monthly-R volatility
on development years). Never increased after strong returns. Caps: per trade 2%; total open risk 10%;
per instrument 4%; same instrument and same direction across strategies 3%; net USD-direction open
risk 6% (gold long, EURUSD long, GBPUSD long and USDJPY short count as USD-short).

States (evaluated before every new entry):
- **GREEN:** drawdown from peak < 10%, no amber or red trigger. Full risk.
- **AMBER** (any): drawdown ≥ 10%; day's loss ≥ 3%; rolling 5-day loss ≥ 6%; a strategy's last 30
  trades average < −0.25R (that strategy only); open risk > 80% of the cap; median slippage of the
  last 20 fills > 2x assumed (live only). Action: new-trade risk x 0.5; flagged in the weekly report.
- **RED** (any): drawdown ≥ 20%; day's loss ≥ 6%; data feed stale > 5 minutes in trading hours;
  ≥ 3 order rejections in a day; spread > 4x normal at decision time; margin level < 300% (live only).
  Action: no new entries; open positions keep their server-side stops (never widened, never added to);
  positions are closed at market only if their stop cannot be confirmed on the server.
  Recovery: operator acknowledgement plus all checks passing; resume in AMBER; return to GREEN when
  drawdown < 10% and 10 trading days pass without a new trigger. In backtests the operator
  acknowledgement is modelled as 10 trading days of pause.

Compared on identical trades: fixed fractional only; GREEN/AMBER/RED; the earlier drawdown brake.
Portfolio acceptance: real max drawdown ≤ 30% and 1-in-20 reshuffled drawdown ≤ 35% at the chosen risk.

## 7. Honesty rules

No claim of compiled code, passed tests or verified edge without the artifact. Missing earlier
outputs are listed as missing, not reconstructed from memory.

## Amendment 1 — 2026-10-30, before any grid result (clarifications only; no threshold changed)

Written after the unit tests passed and after one timing smoke test (FVG-A, w 0.1, d 0, b 0, g 30,
2R target, gold only, all years mixed) — no grid, ranking or validation result has been seen.

1. **Grid dimensions.** Every module's grid = its pattern parameters x management {2R, 3R, none} x
   trail {none, 3 ATR} x bias {off, on}. FVG-D is reported as the bias-on half of the FVG-A grid.
   SD continuation is one module (RBR long + DBD short); RBR and DBD are also reported separately
   (long and short sums are logged per year), likewise DBR / RBD.
2. **One-step neighbours** (criterion A4): configurations that differ in exactly one ORDERED parameter
   by one position in its declared list — timeframe, k, nb, m, w, d, b, g, QM pivot k, target
   (2R, 3R, none), trail (none, 3 ATR), retest offset t. Categorical choices (entry break/retest,
   bias on/off, QM level near/far, FVG model) define variants and are not stepped.
3. **Walk-forward** (criterion A3): for each test year 2014–2022, the configuration is re-selected
   inside the module's grid by the module rule (pooled over markets, ≥ 3 of 4 markets positive,
   ≥ 100 trades, E > 0, rank by t) on the 3 preceding years; that configuration's test-year trades
   are pooled over the 9 test years.
4. **Combination filters** (experiments 6–8), declared now: FVG filter = any same-direction FVG with
   w ≥ 0.1 ATR on the primary's timeframe whose third candle closed within the 10 bars up to and
   including the entry decision bar; QM filter = a same-direction QM trigger (pivot k 3, m 0.25, level
   near, break) on the primary's timeframe within the 30 bars up to the decision bar. Each filter is
   applied to the primary module's full grid; the filtered grid is selected by the module rule, and
   incremental value = paired change in development E between filtered and unfiltered versions of the
   same configuration.
5. **Stress** (criterion A5) from logged sums: E_stress = (sum R − 0.5 x sum cost R − 1.0 x sum
   financing R) / n, plus a separate re-run with entries delayed 1 minute (market orders only; resting
   limit orders are unaffected by latency in this model). All three applied together.
6. **Deflated Sharpe** uses the module's full grid size as the number of trials, monthly R returns.

## Amendment 2 — 2026-10-30, before any risk-manager simulation

Reason: the RED rule in §6 cannot be exited when RED was caused by the drawdown trigger — no new
entries means equity cannot recover above the 20% line, so "all checks passing" never happens.
Fix: after the operator acknowledgement (backtest: 10 trading days ≈ 14 calendar days), trading
resumes in AMBER and the drawdown RED trigger re-arms only on a further 5% loss from the equity at
acknowledgement (or is reset when the account returns to GREEN). Daily-loss RED is unchanged.
Also fixed now: the portfolio candidate for the risk comparison is chosen by the tier rules
(§5) — no new module reached Tier A or B, so the comparison runs on the pre-existing 11-leg book
(frozen legs, financing applied), with book + four strategies as the reference used earlier. Leg
weights: inverse monthly-R volatility on 2011–2019, largest weight 1. The base risk is chosen on
2011–2022 only (largest risk with real max drawdown ≤ 30% and 1-in-20 reshuffled ≤ 35% under RAG);
2023–2025 is then reported at that risk.
