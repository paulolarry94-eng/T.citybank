# Batch 01 — results (2026-11-02)

**Outcome: 0 of 13 candidates survive. 11 could not be tested here (no data, or not tradeable on MT5 Prime); the 2 that
could (9 month-end rebalancing, 11 US close flow) were rejected at the Truth Lab's development gate. 8 configurations were
tried in total; the 2023–25 holdout was not opened for either.** Pre-registration: `research/batch01/PREREGISTRATION.md`
(commit 6eb237f, before any result).

## Candidate 11 — leveraged / vol-target rebalancing into the US close (`us_close_flow_v1`)
US500 + NAS100, enter 15:30 or 15:45 New York with the day's move on big-move days, exit 16:00. RoboForex Prime costs.

| Configuration | 2011–19 net R (t) | before costs | 2020–22 net R (t) | before costs | Control (small-move days) 2011–19 |
|---|---|---|---|---|---|
| prev close, 15:30 | −0.032 (−4.5) | +0.011 (t 1.6) | +0.031 (+2.1) | +0.043 (t 2.8) | about the same loss; differential t 0.2 / 1.4 |
| prev close, 15:45 | −0.040 (−7.4) | +0.002 | +0.002 | +0.013 | differential t −1.5 / −2.2 |
| open, 15:30 | −0.040 (−6.0) | +0.003 | −0.008 | +0.004 | differential t 1.4 / 0.8 |
| open, 15:45 | −0.053 (−9.7) | −0.011 | −0.024 | −0.013 | differential t −1.9 / −1.0 |

Before costs the last 15–30 minutes did not follow big moves in 2011–19 (about zero); costs (0.04R a trade in 2011–19, when
index prices were lower) made every configuration negative. Big-move days did no better than small-move days, so there is
no flow effect beyond the control. One configuration was positive in 2020–22 (t 2.8 before costs); the rule failed its
gate, and picking that slice now would be hindsight.

## Candidate 9 — month-end rebalancing against the month's move (`monthend_rebalance_v1`)
US500, NAS100, GER40, UK100; enter at the close 3 or 1 business days before month-end against the month-to-date move;
exit at the last business day's close. Prime costs (UK100 lab), lab swaps.

| Configuration | 2011–19 net R (t) | before costs and swaps | 2020–22 net R (t) | before costs and swaps |
|---|---|---|---|---|
| 3 days, all months | −0.006 (−0.1) | +0.103 (t 2.3) | −0.147 (−2.0) | −0.108 |
| 3 days, strong months | +0.071 (0.9) | +0.172 (t 2.3) | −0.261 (−3.6) | −0.224 |
| 1 day, all months | +0.000 (0.0) | +0.046 (t 1.7) | −0.069 (−1.7) | −0.053 |
| 1 day, strong months | +0.038 (1.0) | +0.081 (t 2.1) | −0.088 (−1.6) | −0.073 |

In 2011–19 the month-end reversal existed before costs and swaps (t about 2), but overnight index swaps took nearly all of
it. In 2020–22 it was negative in every configuration even before costs, so a swap-free account would not rescue it. It
"beat" its control (the same rule mid-month) only because the control lost heavily in 2011–19: fading the month's move in
mid-month lost money in a rising market. "Strong months" had too few trades for the lab's 200-trade gate (pre-stated).

## Batch rule
| Candidate | Lab | t ≥ 3 | Beats control | Replicates | Batch verdict |
|---|---|---|---|---|---|
| 11 US close flow | Rejected at gate | ✘ | ✘ | ✘ | REJECTED |
| 9 Month-end rebalancing | Rejected at gate | ✘ | (only vs a losing control) | ✘ (2020–22 negative) | REJECTED |

Evidence: `research/results/truth/us_close_flow_v1/`, `research/results/truth/monthend_rebalance_v1/`,
`research/results/batch01/controls.json`, `research/results/batch01/gross.json`.

## Lab fix found by this batch
A grid setting named `n_before` crashed the lab (setting names starting with `n_` were read as the lab's own trade-count
columns). Fixed in `research/truth/protocol.py`; test `TestPooledColumns` fails without the fix. No results existed when it
crashed.
