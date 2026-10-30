# Fair Value Gaps (ICT) — mechanical test

Bullish FVG: candle 3's low above candle 1's high (the gap left by the displacement candle 2);
bearish mirror. 7,872 configurations (`grid.py`) on gold, EURUSD, GBPUSD and USDJPY, M15/H1/H4,
1-minute fills with all-in costs; fills before 2023 only, selection on 2011–2019, validation
2020–2022, one logged look at 2023–2025 (`final_check.py`).

Tested: retrace entry at the gap edge or the midpoint ("consequent encroachment"), inversion FVG
(gap closed through, retest from the other side), gap-fill fade, displacement filter (0 / 1.0 /
1.5 ATR), gap size (0.1 / 0.3 ATR), ICT stop beyond candle 1 vs a stop just beyond the gap, daily
bias, killzones (M15: 07–10 and 12–15 UTC), targets 1.5 / 2 / 3R or none, chandelier 3 ATR.

## Results

- 7.8% of configurations positive in 2011–2019; one with t > 2. Before costs the medians are
  −0.05 to +0.04R: the gap itself carries almost no information.
- Median R per trade after costs, 2011–19 / 2020–22: M15 −0.15 to −0.24 (costs eat it); H1 −0.08 to
  −0.16; H4 −0.04 to −0.06 / around 0. The gap-fill fade wins often (45%) but on moves too small to pay.

| ingredient | change in R per trade, 2011–19 / 2020–22 |
|---|---|
| displacement ≥ 1.5 ATR vs none | +0.017 / +0.006 |
| gap ≥ 0.3 ATR vs 0.1 | +0.005 / +0.013 |
| midpoint (CE) entry vs gap edge | −0.027 / −0.030 |
| stop just beyond the gap vs beyond candle 1 | −0.070 / −0.061 |
| daily bias | −0.009 / +0.007 |
| killzones (M15) | +0.005 / +0.001 |
| chandelier 3 ATR | −0.001 / −0.003 |
| no target vs 2R | +0.007 / +0.022 |

- Universal rules (one setting for all four markets) passing the development gate: 14 of 1,968; the
  best has t 1.36 and fails validation.
- A watch-list cluster chosen with validation in view (H4, displacement ≥ 1.5 ATR, midpoint entry,
  stop beyond candle 1, no target: +0.06 / +0.42R) **lost in 2023–2025 (−0.02R)**.

| H4, displacement ≥ 1.5 ATR, stop beyond candle 1, no target | 2011–19 | 2020–22 | 2023–25 |
|---|---|---|---|
| retrace to the midpoint (CE) | +0.064 | +0.422 | −0.021 |
| retrace to the gap edge | −0.015 | +0.181 | +0.047 |
| **enter at the next open after candle 3** | **+0.070** | **+0.124** | **+0.091** |
| same, 2R target | +0.018 | +0.053 | +0.002 |

## Verdict

Waiting for price to come back into the gap does not pay: the trades that do come back are
disproportionately the ones that fail (the same adverse selection found with ORB retests). The
information is in the displacement itself. Following it immediately is weakly positive in every
period, and that is the effect the expansion follow-through strategy in the four-strategy
system already trades (H4 bar ≥ 2.5 ATR closing near its extreme, with trend). FVG adds no new edge
beyond it.
