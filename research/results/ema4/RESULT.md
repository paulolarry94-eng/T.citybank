# Owner's 4-flip EMA pattern — result (2026-11-02)

**Verdict: rejected.** 0 of 640 configurations (5 timeframes x 128 settings, 12 markets, all hours) pass the Truth Lab's gate;
the pre-registered where/when search finds no market x timeframe x session cell that works. Rules were fixed with the owner's
answers before any result (`research/ema4/PREREGISTRATION.md`, commits ecc3328 and the look-ahead fix). 2023-25 not opened.

## By timeframe (fixed typical setting: entry at the 4th candle's close, stop 4th candle + 0.25 ATR, 2R; `PROFILE.md`)
| Timeframe | Grade | 2011-19 trades | Win rate | R/trade | Before costs | Cost | 2020-22 trades | R/trade |
|---|---|---|---|---|---|---|---|---|
| M5 | A+ | 4,332 | 30% | −0.153 | +0.001 | 0.15R | 2,108 | −0.058 |
| M5 | A+ and B+ | 12,135 | 30% | −0.136 | +0.022 | 0.16R | 5,501 | −0.081 |
| M15 | A+ | 1,759 | 34% | −0.086 | +0.032 | 0.12R | 746 | −0.083 |
| M30 | A+ | 971 | 33% | −0.138 | −0.043 | 0.10R | 437 | −0.058 |
| H1 | A+ | 519 | 39% | −0.067 | +0.005 | 0.07R | 180 | −0.021 |
| H1 | A+ and B+ | 1,506 | 38% | −0.042 | +0.037 | 0.08R | 529 | −0.032 |
| **H4** | **A+** | **106** | **48%** | **+0.137** | +0.179 | 0.04R | 46 | −0.043 |
| **H4** | **A+ and B+** | **282** | **44%** | **+0.106** | +0.156 | 0.05R | 115 | +0.056 |

- M5 to H1: about zero before costs on every timeframe; costs of 0.06-0.16R a trade make all of them lose (P1).
- H4 is the only positive timeframe, but on few trades (1-3 per market per year), t 1.7-1.9 in 2011-19, and 2020-22 about 0.
  It came mostly from gold, GBPUSD, USDJPY, EURUSD and WTI; indices lost. Picking those now would be hindsight.
- Lab grid (all 640): 15% positive in 2011-19, 5% in both 2011-19 and 2020-22, median −0.093R; every positive one is H4.
- Entry at the close beat the 50% limit (medians −0.078R vs −0.113R; P2); target size and A+ vs A+B+ changed little.

## Does the engulfing grade matter? Control = the same trade on REJECTED four-flips (`controls.json`)
| Timeframe | 2011-19: graded minus rejected (median of 128) | configs t >= 2 | 2020-22 |
|---|---|---|---|
| M5 | +0.034R | 44 | +0.051R |
| M15 | +0.060R | 24 | −0.032R |
| M30 | +0.008R | 0 | −0.036R |
| H1 | +0.030R | 1 | +0.017R |
| H4 | +0.136R | 33 | **−0.099R** (rejected H4 patterns made +0.27R) |
The grade helped a little in 2011-19 and not reliably after. On M5 it helped in both periods, but both lose after costs.

## Where and when (learn 2011-19, check 2020-22; `WHERE_WHEN.md`)
180 cells, 69 with enough trades; the best of 128 settings per cell reached at most t 2.4 in 2011-19 (what picking the best
of 128 gives by luck), 0 cells reached t >= 3, 0 passed. Best: GER40 M5 London (+0.24R, t 2.4) -> 2020-22 +0.03R (t 0.2).

## In cycles (`research/results/truth/ema4_flip_v1/CYCLES_LEAGUE.md`)
Best configuration by edge quality: H4 A+, close entry, 2R: s +0.18 in 2011-19 (needed 0.42), 12 trades a year over all 12
markets (a 360-trade lifecycle would take 30 years), 80% of its 10-trade cycles positive, and s −0.09 in 2020-22.

## Replay of the owner's charts: 5 of 7 calls (`research/ema4/README.md`, charts in `charts/`).
