# North Star — final strategy research and validation report

Date: 2026-10-30. Branch `claude/loving-davinci-uzjf3z`. Rules fixed in `PREREGISTRATION.md` (committed
before any experiment; three dated amendments, each written before the results it governs).

## Verdict

**No deployment-ready configuration has been established.** Nothing reached Tier A.

- **New modules (supply/demand, FVG, Quasimodo, and their combinations): all rejected.** Supply/demand
  and every FVG model fail the development gate. Not one of the 1,056 FVG settings (models A–C; model D
  is model A with the H4 filter) is profitable after costs in 2011–2019. Quasimodo's best setting is positive in all three periods, but it is an isolated peak:
  the same rule on M30 and H4 loses money, and its deflated Sharpe is 0.011 after 1,728 trials.
- **Only forward-test candidate (Tier B): the existing 11-leg book**, unchanged, with financing now
  charged. Out-of-sample 2023–2025: +0.044R per trade, PF 1.12, t 1.18, positive in all 3 years. The
  95% interval of its out-of-sample expectancy [−0.029, +0.117]R includes zero, so the edge is **not
  verified** for that period. Over 2011–2025 it is +0.069R per trade, t 4.3, 14/15 positive years.
- **Risk:** plain fixed-fractional sizing at a lower risk beats the GREEN/AMBER/RED state machine on
  2011–2022 at equal tail risk. The demo policy is therefore **FF+RED**: 1% base risk x leg weight,
  all exposure caps, RED kept as a circuit breaker, AMBER logged only.
- **MT5:** governor source written; **nothing compiled** (no MetaEditor in this environment). The
  strategy legs are not yet implemented in MQL5 except older versions of 3 legs in TimelessCity.

## 1. Master comparison (Part 1, Part 11)
`results/northstar/master_comparison.csv.gz` — **240,594 configurations across 40 studies** (the 27
earlier studies from the ledger + 10 North Star modules + 3 financed re-scores). Per-study summary:
`results/northstar/master_summary.csv`. Earlier outputs that could not be found are listed in
`results/northstar/missing_artifacts.md`. One more gap found during this work: the script that built
the three filtered book legs was never committed. It is now rebuilt from the written rules in
`regen_filtered.py`; two legs match the stored trades exactly, gold EMA matches 113 of 118.

| Study group | Configs | Share positive in development | Survivors |
|---|---|---|---|
| ORB 50 (E0–E6, AB) | 118,898 | 0.3%–19% | none (all four finalists negative out-of-sample) |
| Four strategies (grid + locked) | 102,260 | 39% | 4 locked rules; with financing their 2023–25 E ≈ 0 |
| FVG (earlier grid) + North Star FVG A–C (D = A with H4 filter) | 8,928 | 0–8% | none |
| Malaysian SnR, liquidity, daily structure, gold/multi labs | ~3,000 | 10–24% | a few book legs |
| North Star SD continuation / reversal | 1,440 | 20–23% | none pass the gate (samples too small; every side < 0) |
| North Star Quasimodo (+FVG) | 3,456 | 8–9% | 2 candidates, both rejected |
| 11-leg book (financed) | 11 legs | 10/11 legs positive in development | **Tier B forward-test candidate** |

## 2. Controlled experiments 1–10 (Part 6)
Grids, gate and tiers exactly as pre-registered (`grid.py`, `analyze.py`, `confirm.py`, `oos.py`).
Costs + financing + rollover block throughout; development 2011–19, validation 2020–22, one logged
2023–25 look per candidate (`results/northstar/oos_log.json`).

| # | Experiment | Configs | Passed dev gate | Candidate | Dev E / t | Val E | Walk-fwd E | 2023–25 E (n, PF) | DSR | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | RBR / DBD continuation | 720 | 0 | — | — | — | — | — | — | Rejected |
| 2 | DBR / RBD reversal | 720 | 0 | — | — | — | — | — | — | Rejected |
| 3 | FVG-A retest (+ C structure, D H4-aligned) | 768 / 96 / 384 | 0 | — | — | — | — | — | — | Rejected |
| 4 | FVG-B pullback confirmation | 192 | 0 | — | — | — | — | — | — | Rejected |
| 5 | Quasimodo | 1,728 | 18 | H1, pivot 3, m 0.5, break above H1, 2R, H4 bias | +0.130 / 2.44 | +0.067 | +0.014 | +0.043 (147, 1.09) | 0.011 | Rejected (neighbours, OOS t) |
| 6 | QM + FVG | 1,728 | 11 | H1, pivot 3, m 0.5, far, 3R | +0.104 / 2.21 | −0.056 | −0.057 | +0.113 (201, 1.25) | 0.000 | Rejected |
| 7 | RBR + FVG | 720 | 0 | — | — | — | — | — | — | Rejected |
| 8 | RBR + QM | 720 | 0 | — | — | — | — | — | — | Rejected |
| 9 | All new modules | — | — | only QM-family candidates exist; nothing to combine | | | | | | Rejected |
| 10 | vs original strategies | — | — | see §3 | | | | | | |

Quasimodo's stability check, development E of each one-step neighbour: M30 −0.030, H4 −0.032,
pivot 2 +0.049, pivot 5 +0.154, m 0.25 +0.101, 3R +0.134, trail +0.059. It fails the rule that every
neighbour must be positive. In 2023–25 it made money only on USDJPY (+0.33R); gold −0.18, GBP −0.04,
EUR +0.01.

**Ablation (`ablation.csv`; paired change in development E, all else fixed):**
- Timeframe dominates. Moving FVG from M5 to H1 adds +0.15R and improves 100% of pairs; QM M15→H1
  adds +0.05R (94% of pairs). Short timeframes lose to costs, so M1/M5/M15 execution (Part 7) is not
  viable at these costs.
- Limit "retest" entries hurt every module: QM −0.081R (97% of pairs worse), SD −0.035 to −0.084R.
  That is the adverse selection of resting orders.
- FVG midpoint depth hurts (96% of pairs worse). The 0.1 ATR buffer and the minimum width help only
  slightly.
- The H4 EMA50 bias, 2R vs 3R vs no target, and the 3-ATR trail each change E by less than 0.01R.
- Supply/demand: every RBR, DBD, DBR and RBD variant with ≥ 100 development trades loses money.
- Combination filters add nothing. The FVG filter on QM gives a median +0.004R; on RBR, 0.000R.
  The QM filter on RBR gives −0.022R.

## 3. Candidate comparison (Part 9) — R after costs AND financing (`candidates.json`)

| Candidate | 2011–25 n | E (R) | PF | Sharpe (monthly) | Sortino | Max DD (R) | Recovery | + years | 2023–25 E [95% CI] | 2023–25 PF | Corr. with book |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Book, 11 legs (weighted)** | 6,100 | +0.069 | 1.18 | **1.21** | **2.95** | **10.1** | **14.2** | **14/15** | +0.044 [−0.029, +0.117] | 1.12 | 1.00 |
| Book + four (23 legs) | 12,378 | +0.064 | 1.17 | 1.20 | 2.73 | 31.7 | 9.2 | 13/15 | +0.023 [−0.029, +0.076] | 1.06 | 0.67 |
| Four strategies (16 legs) | 6,278 | +0.059 | 1.15 | 0.80 | 1.48 | 28.9 | 5.1 | 9/15 | +0.005 [−0.071, +0.080] | 1.01 | 0.25 |
| QM candidate | 730 | +0.100 | 1.23 | 0.56 | 0.95 | 16.9 | 4.3 | 11/15 | +0.043 [−0.142, +0.228] | 1.09 | 0.09 |
| QM + FVG candidate | 986 | +0.076 | 1.17 | 0.48 | 0.80 | 29.0 | 2.6 | 10/15 | +0.113 [−0.056, +0.282] | 1.25 | 0.08 |
| ORB finalists A/B/C/X | 569–3,219 | −0.007 to +0.080 | 0.99–1.13 | −0.08 to 0.40 | | 43–96 | | 6–10/15 | −0.12 to −0.16 (all < 0) | 0.76–0.82 | −0.05 to 0.17 |

Financing (new in North Star) costs the multi-day legs real money: four strategies 2023–25 +0.036 →
+0.005R; book +0.063 → +0.044R; ORB is intraday and unaffected. Cost stress (costs x1.5, financing x2)
on 2011–2022: book +0.030R, four +0.021R, QM +0.075R (QM's figure includes the +1 minute delay re-run).

Why the book and not the others: it is the only candidate that meets Tier B (E > 0 in every period,
stress positive, 2023–25 PF ≥ 1.05) under rules fixed in advance. It is also the simplest of the
surviving portfolios. Its stability evidence comes from the earlier funnel, which used a different
neighbour definition and was not re-run here. Caveat: the book's 2023–25 years were inside the earlier
2019–25 out-of-sample window used when the book was assembled, so they are not a fresh holdout. The
forward test is the real holdout.

## 4. Portfolio risk manager (Part 8) — `risk.py`, `ns_portfolio.py`, `portfolio.json`
Identical trades, sizing policies compared on 2011–2022; risk chosen on 2011–2022 only.

| Book, 2011–2022 | Base risk | CAGR | Max DD | 1-in-20 reshuffled DD |
|---|---|---|---|---|
| Fixed fractional (FF) | 1.25% | 13.6% | 10.4% | 16.4% |
| FF | 1.5% | 16.4% | 12.4% | 19.3% |
| FF + caps | 2.0% | 15.5% | 12.5% | 25.0% |
| GREEN/AMBER/RED (RAG) | 2.0% | 12.6% | 13.1% | 18.3% |
| Drawdown brake | 2.0% | 13.9% | 12.6% | 19.7% |
| **FF+RED (demo policy)** | **1.0%** | **10.1%** | **8.3%** | **13.2%** |

- AMBER time comes almost entirely from the ≥ 10% drawdown trigger. Halving size there slows the
  recovery, which is why RAG loses to plain lower risk. At the rule-chosen 2% in 2023–25, RAG made
  +1.5%/yr (DD 15.9%), against +8.9%/yr (DD 14.3%) for FF + caps.
- The pre-registered RED rule could never be exited after a drawdown trigger, because no trades means
  no recovery. Amendment 2 fixes this: RED re-arms after a further 5% loss from the acknowledgement.
- **Demo policy, computed once after the decision (amendment 3): 2023–2025 CAGR +6.0%, max DD 10.3%,
  no RED event, 55% of fortnights positive (median fortnight +0.18%).** Book + four under the same
  policy: +4.4%/yr, DD 24.6%, 2 RED events. Adding the four strategies hurts.
- Unit tests confirm compounding, every cap, AMBER and 5-day triggers, the RED pause with its exact
  re-arm count, day-loss RED and shadow AMBER (`tests/test_northstar.py`, 29 tests passing).

## 5. Weekly monitoring (Part 10) — `weekly.py`
Produces the 12 sections from the governor's CSV logs. Every line is tagged FACT, ESTIMATE or RULE.
Rules R1–R5 are fixed in the script header. A strategy is only put "under review" with ≥ 30 live
trades and t < −2.33 against its backtest, or a losing streak above its 99th percentile, and is never
called broken. Example output from 2025 backtest trades: `WEEKLY_REPORT_EXAMPLE.md`. It flags GBPJPY
for review (38 trades, t −2.46) and shows that about 3,800 trades are needed before the sign of the
expectancy is known at 95%, which is several years at 7.8 trades per week.

## 6. Reproduction
```
cd research/northstar
python3 -m unittest discover -s tests            # 29 tests
python3 ledger.py                                 # master ledger of earlier studies
python3 grid.py                                   # 7,392 configs x 4 markets (~3 min, 4 cores)
python3 analyze.py && python3 confirm.py && python3 oos.py    # oos.py reuses its logged looks
python3 ablation.py && python3 rescore.py && python3 regen_filtered.py
python3 ns_portfolio.py && python3 candidates.py && python3 master.py
python3 weekly.py --build-expected && python3 weekly.py --example
python3 parity_export.py
```
Data: Dukascopy M1 bid bars loaded by `research/engine.py` (not in git; same loader as all studies).

## 7. Demo forward-test plan
1. **Compile.** Build `NorthStarGovernor.mq5` and any strategy EA in MetaEditor; fix and record every
   compile error. Nothing below starts until the build is clean.
2. **Parity.** Implement each leg in MQL5 (only 3 have earlier versions in TimelessCity). Run the
   Strategy Tester with real ticks for 2023–2025 and compare against
   `results/northstar/parity/<leg>.csv`. Pass: ≥ 95% of trades matched on entry time (±1 bar) and
   side, and R within 0.1 on matched trades; explain every difference. Legs that fail stay off.
3. **Demo, 6 months minimum** at the FF+RED policy (1% base risk x weight), all caps, governor
   running, weekly report every Friday. Expected per week: −1.3% to +1.9% (5–95%), 5–11 trades.
4. **Decide after 6 months on pre-set rules.** Continue to small live only if:
   - no unexplained execution breach occurred;
   - median slippage is within R3;
   - live expectancy is not below the backtest with t < −2.33;
   - drawdown stayed within the 1-in-20 band (13%).

   Six months is still not proof (§5). Live sizing would start at half the demo risk.

## 8. Copy-trading readiness: **not ready**
- No verified edge: the 2023–25 interval includes zero, and there is no forward-test record.
- No compiled or parity-tested EA for 8 of the 11 legs.
- Expected return at the demo risk is about 6–10% a year with 8–13% drawdowns. Followers on fee
  structures that take a share of profits would keep little of that.
- Requirements before offering it to others: 12+ months of audited demo/live record matching the
  backtest bands, a compiled and parity-tested EA, written risk disclosure, and broker swap/spread
  verified on the copy platform.

## 9. Unresolved risks and limitations
- **Selection bias:** the book's legs came from wide searches (tens of thousands of configurations
  across the studies). The DSR and Bonferroni checks in the earlier studies cover each study, not the
  whole programme.
- **2023–25 depended on gold:** gold legs averaged +0.25R per trade; GBPUSD −0.09R; EUR, JPY and the
  crosses were about zero.
- **Financing is a constant approximation.** Real swaps depend on rates and the broker, and some carry
  is positive; it is reported at x2 in the stress test.
- **Model limits:** P&L is realised at exit (no intratrade mark-to-market for day-loss triggers);
  open risk uses initial stops; the live-only triggers (slippage, stale feed, rejects, spread,
  margin) cannot be backtested.
- **Crosses** (GBPJPY, EURGBP) were researched on synthetic prices built from the USD pairs; real
  cross spreads and quotes may differ.
- **Gold EMA leg** reproduces 113/118 stored trades from its written filter rule (5 unexplained).
- **Uncompiled code:** `NorthStarRisk.mqh` and `NorthStarGovernor.mq5` have never been compiled or
  run. `TimelessCity.mq5` legs are not parity-tested.
- **Regime risk:** 14/15 positive years is history, not a guarantee. The RED breaker and the weekly
  rules limit damage but cannot create an edge.
