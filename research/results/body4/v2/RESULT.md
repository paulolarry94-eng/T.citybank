# Body-engulf range at 1:2 and 1:1 (owner: "try 1:2R and 1:1R") — result (2026-11-08)

**Verdict: rejected, like 4R.** All 384 settings lose after costs (12 markets pooled, M1-H4, 2011-19 and 2020-22); the
best with 200+ trades loses 0.10R a trade. Before costs the smaller targets are slightly NEGATIVE: the fills come after a
pull-back that tends to keep going. No 2023-25 look (nothing passed the gate).
Pre-registered: `research/body4/PREREGISTRATION_V2.md`. Lab: `research/results/truth/body4_range_v2/REPORT.md`.
Side by side with 4R: `TARGETS.md` (this folder). Details: `study.json`, `gross.json`.

## Main settings with breakeven OFF (every trade a clean win or loss), 12 markets pooled, 2011-19
| Timeframe | 4R: wins / needed | 2R: wins / needed | 1R: wins / needed | R per trade 4R / 2R / 1R |
|---|---|---|---|---|
| M1 | 16% / 29% | 25% / 48% | 34% / 72% | -0.47 / -0.47 / -0.55 |
| M5 | 18% / 25% | 28% / 42% | 40% / 63% | -0.28 / -0.29 / -0.31 |
| M15 | 20% / 24% | 31% / 39% | 44% / 59% | -0.16 / -0.17 / -0.20 |
| M30 | 20% / 23% | 30% / 38% | 44% / 57% | -0.18 / -0.17 / -0.18 |
| H1 | 21% / 22% | 31% / 37% | 44% / 56% | -0.14 / -0.15 / -0.17 |
| H4 | 28% / 21% | 34% / 35% | 42% / 53% | -0.16 / -0.16 / -0.20 |
"Needed" = the win rate that breaks even after this timeframe's costs. A 1:1 trade must win more than half the time even
before costs; these setups win 34-47% (2020-22 the same). H4 at 4R is the only row above its line, on 502 trades, and
it still loses after swaps and Friday closes (-0.16R).

## Paired comparisons (all else equal)
| Question | 2011-19 | 2020-22 |
|---|---|---|
| 2R vs 1R | 2R better in 85% of 1,495 pairs (+0.03R) | 79% (+0.03R) |
| Breakeven at 50% of the target vs none | breakeven had the higher profit factor in only 15% of 1,800 pairs | 16% |
| Entry 50% vs 70% | 50% better in 84% (+0.12R) | 81% (+0.12R) |
| Stop buffer 0% vs 20% | 20% better in 83% (+0.10R) | 79% (+0.10R) |
| Lookback on vs off | no difference (48% / 49%) | |

## Other checks
- Before costs: 40 of 384 settings positive in 2011-19, 14 in both periods, best t 1.3 (chance level).
- Best market x timeframe (learn 2011-19, check 2020-22): 63 picks, 1 positive in both periods (USDJPY H1 2R: +0.06R,
  t 1.0, then +0.04R, t 0.4) — not evidence of an edge.
- Small targets trade less: price often reaches a 1R target before pulling back to the entry, and the owner's cancel rule
  removes those orders (M1: 44,500 trades at 4R, 19,000 at 1R).
