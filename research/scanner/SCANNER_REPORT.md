# Daily London scanner — results

Question (user): every London session, scan all markets, take only the best setup available, one trade at
a time across the account. Rules fixed before any result in `PREREGISTRATION.md` (commit before the run).

## Verdict: rejected
The pre-registered variant (picked on 2013–2019) loses money in 2020–22 and 2023–25 and fails all six
acceptance criteria. No variant of the 16 is reliably positive.

## What was built
- `candidates.py`: 8 intraday setup families x 4 markets (gold, EUR, GBP, JPY). They produce
  **61,787 candidate trades on 3,882 London days (about 16 per day)**. Each one is simulated minute by
  minute with costs, and every trade is flat by 16:30 London (no overnight financing). Cross-check: the
  EUR session-short family reproduces the book's stored leg trade for trade (2,321/2,321 entries,
  correlation 0.994).
- `policy.py`: a ranker that scores every setup **only from earlier, already-closed trades** of the
  same kind (shrunk average R). The one-trade-at-a-time scanner takes the highest score at each
  15-minute decision while flat. It is compared on the identical pool against "take everything" and
  "random pick".

## Results (R per trade after costs; `../results/scanner/policies.csv`)

| Policy | 2013–19 | 2020–22 | 2023–25 | 2023–25 at 1% risk |
|---|---|---|---|---|
| Take every setup | −0.070 (t −10.7) | −0.079 | −0.072 | — |
| One at a time, random pick (median of 200) | −0.070 | −0.111 | −0.077 | −40%/yr |
| One at a time, best score (16 variants) | −0.053 to +0.022 | −0.134 to +0.100 | −0.153 to +0.031 | −14% to +6%/yr |
| **Pre-registered pick: best score, family x market cells, score > 0.06R** | **+0.022 (t 0.52, 639 trades)** | **−0.134 (84)** | **−0.153 (15)** | −3%/yr |

Acceptance (`selected.json`): every criterion fails. The variant is not positive in every period; its
2023–25 sample is tiny; its neighbouring variants are negative; under costs x1.5 with a 1-minute delay
it is −1.03R (1 trade); its selection value turns negative after 2019; and it fails without the EUR leg.

## What the scanner does and doesn't do
- **The ranking works as a filter.** Picking the best-scored setup instead of a random one lifts the
  average from about −0.07R to about −0.01R. In 2013–19 the chosen setup beat the others available at
  the same moment by +0.09R (t 1.6). It reliably avoids the worst setups.
- **It cannot create an edge that the pool doesn't have.** Before costs the 61,787 setups average only
  **+0.015R per trade**, and costs take **0.076R** (median). That raw edge stays about 0.01–0.02R at
  every stop size, so wider stops don't rescue it. Gross by family: EUR session short +0.086,
  opening momentum +0.077, previous-day breakout +0.035; the rest are about 0 or negative.
- **Demanding a higher score ("surest only") just removes trades.** No group of setups keeps a high
  past score, so at a 0.10R threshold the scanner takes 0–111 trades in 2023–25.

## What would be needed
A one-trade-at-a-time scanner is a sound structure. It needs ingredients that are positive on their
own after costs. The intraday evidence here, as in the ORB and liquidity studies, says London-session
patterns on these markets do not clear the spread. The only intraday pieces with real gross edge
(EUR session short, opening momentum) are already in or near the book.

Diagnostic note: the family-level averages over all years were printed once during the simulator
cross-check, before the policy run. That printout informed no rule; the ranker and variants were
already fixed.

Reproduce: `python3 candidates.py && python3 policy.py` (about 2 minutes on 4 cores).
