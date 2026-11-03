# Last push: month-end FX hedge rebalancing at the London 4 pm fix — result (2026-11-03)

**Verdict: rejected.** A real flow in 2011-19 that reversed afterwards. Pre-registered (`research/flows/PREREGISTRATION_MONTHEND_HEDGE.md`);
strategy `monthend_hedge_fix_v1`; 6 configurations; EURUSD/GBPUSD/USDJPY; RoboForex Prime costs; one logged 2023-25 look.

| Period | Selected (entry 14:00 London, all months) | Trades | R per trade | t | Edge quality s | Cycle at 3.6% cap |
|---|---|---|---|---|---|---|
| 2011-19 | flow worked: all 6 settings positive, all 3 markets, both halves | 315 | +0.096 | +2.1 | +0.117 | +0.21% |
| 2020-22 | reversed (12:00 and 14:00 entries t -3 to -4) | 103 | -0.319 | -4.2 | -0.41 | -0.08% |
| 2023-25 (unseen) | no edge (EURUSD +0.10, GBPUSD +0.03, USDJPY -0.24R) | 106 | -0.032 | -0.5 | -0.05 | -0.03% |

- Control (same rule on the 10th business day): the month-end flow beat it by about 0.1R in 2011-19 (t 1.0-3.05), so the
  2011-19 effect was a real flow, not the dollar's drift; it did not survive.
- Reading: the flow was published (Melvin & Prins 2015) and is now traded ahead of; a payer with a known direction can still
  be competed away (P22 update). Stress (costs x1.5, +1 minute) was negative over 2011-22; deflated Sharpe 0.86.
Reports: `research/results/truth/monthend_hedge_fix_v1/` (REPORT, controls.json).
