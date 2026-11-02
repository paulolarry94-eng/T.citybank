# Batch 01 — pre-registration (2026-11-02, written before any result)

Owner submission: 13 "payer flow" candidates with controls, kill criteria and a batch protocol (one look at 2023–25, t ≥ 3,
replication, independence accounting). This file records what can be tested here, what cannot and why, and the exact rules
for what is run. Nothing below was chosen after seeing data.

## Triage: what we can test and trade

Our data: M1 bid bars 2011–2025 for EURUSD, GBPUSD, USDJPY, XAUUSD, XAGUSD, WTI, US500, NAS100, GER40, UK100, JP225, and
pysystemtrade's daily futures (each instrument: the contract its system holds, one carry contract and one forward contract;
not the front/second pair an index roll trades). The owner trades MT5 CFDs (RoboForex Prime: FX, metals, energies and the
indices DE40, JP225, US500, USTECH, US30).

| # | Candidate | Testable here? | Tradeable on MT5 Prime? | Status |
|---|---|---|---|---|
| 1 | Commodity index roll, energy | No: needs daily front and second-month prices per contract | No (calendar spreads) | Not run: data |
| 2 | Commodity index roll, metals/ags | No: same | No | Not run: data |
| 3 | VIX futures roll | No: needs ETP roll sizes and VX term structure | No VIX on Prime | Not run |
| 4 | CDX/iTraxx roll | No data; about 8–16 trades (owner pre-flagged the gate) | No | Not run |
| 5 | G10 dividend repatriation FX | No: needs a dividend payment calendar with sizes | Yes (FX) | Not run: data |
| 6 | EM local debt coupon reinvestment | No: no EM FX or coupon calendar | Unknown | Not run: data |
| 7 | Treasury month-end index extension | Partly (bond futures, daily); the rule needs new-issue cash bonds | No bonds on Prime | Not run |
| 8 | Quarter-end cross-currency basis | No basis data | No | Not run |
| 9 | Month-end 60/40 and pension rebalancing | **Yes** (US500, NAS100, GER40, UK100, M1) | **Yes** | **Run: monthend_rebalance_v1** |
| 10 | Dealer gamma pin | No: needs option open interest by strike | Yes (indices) | Not run: data (option-expiry week already rejected) |
| 11 | Leveraged / vol-target ETF rebalancing at the close | **Yes** (US500, NAS100, M1) | **Yes** | **Run: us_close_flow_v1** |
| 12 | Korea NPS FX hedging | No KRW data; 5–15 events (owner pre-flagged) | Unknown | Not run |
| 13 | First Notice Day exit | No: same as 1–2 | No | Not run |

## Priors (memory, checked before testing)
Every index calendar idea tested so far was rejected: turn of month (tom_indices_v1/v2), option-expiry week
(opex_week_indices_v1/v2), payday, oil→equity; London 4 pm and ECB fixes rejected; the Tokyo fix (known payer AND direction)
survived. Candidates 9 and 11 differ from the rejected ones in the way P22 says matters: the direction comes from the
payer's obligation (against the month's move; with the day's move), not from the calendar alone.

## What is run (rules in the strategy files, fingerprinted by the lab)
- `research/truth/strategies/us_close_flow_v1.py` — 4 configurations, US500 + NAS100, M5, RoboForex Prime costs.
- `research/truth/strategies/monthend_rebalance_v1.py` — 4 configurations, US500 + NAS100 + GER40 + UK100, M30, Prime costs
  (UK100: lab standard; not on Prime), lab swaps.
- Each goes through the full Truth Lab (gate, neighbours, validation, walk-forward, stress, deflated Sharpe, ONE logged look
  at 2023–25, tiers, cost ladder, cycle goal). Total selectable configurations in the batch: 8.

## Controls and the batch rule (research/batch01/controls.py)
Control = the same rule on the non-flow sample: below-median-move days (11); the 10th business day of the month instead of
month-end (9). Controls are never selected. A candidate is called REAL only if: (1) the lab says Tier A or B; (2) the selected
configuration has t ≥ 3 in 2011–19 after costs; (3) it beats its control in 2011–19 (differential > 0, Welch t ≥ 2); (4) it
replicates: positive in 2020–22 and positive in every market in 2011–19. Tier B failing 2–4 = MONITOR. Else REJECTED.

## Trade counts (mechanics check, no results seen)
us_close_flow_v1: about 1,080-1,100 development trades per configuration per market. monthend_rebalance_v1: "all" about
390-410 development trades pooled over 4 markets; "strong" about 150-170 pooled, below the lab's 200-trade gate, so the
"strong" configurations can be reported but never selected. Both files pass the look-ahead check.

## Stated expectations (from priors, before running)
Both rejected or at most MONITOR; any surviving s well below the 0.42 that +2% per 10-trade cycle inside 3.6% needs (P28).
