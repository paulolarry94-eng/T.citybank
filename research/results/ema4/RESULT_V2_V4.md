# 4-flip EMA pattern, v2-v4 (owner's corrections of 2026-11-03) — result

**Verdict: rejected.** None of the corrected versions passes the Truth Lab's gate; none has a setting that made money in both
2011-19 and 2020-22 with a meaningful number of trades except by chance; the full-engulfing grade does no better than
four-flips without it. Each version was pre-registered before its results (`research/ema4/PREREGISTRATION_V2/V3/V4.md`).
12 markets, M5-H4, all hours, RoboForex Prime costs, close daily, news days skipped; 2023-25 not opened.

| Version | Rule | Settings | With >= 200 trades | Positive 2011-19 | Positive 2011-19 AND 2020-22 | Median R/trade | Best (2011-19 -> 2020-22) |
|---|---|---|---|---|---|---|---|
| v1 | 4th closes beyond the 3rd candle's OPEN | 640 | 544 | 28 | 26 | -0.105 | H4 close c4 2R A+B+: +0.106 (t 1.9) -> +0.056 (t 0.7) |
| v2 | FULL engulfing (beyond the 3rd's low/high); 3 stops; trailing and EMA exits | 1,260 | 819 | 25 | 22 | -0.120 | M15 50% all4 trail2 A+: +0.088 (t 1.1) -> +0.117 (t 0.8) |
| v3 | + each break from the other side of the EMA | 1,260 | 812 | 23 | 11 | -0.115 | H1 50% all4 3R A+B+: +0.055 (t 0.9) -> -0.119 |
| v4 | + obvious breaks (open and close 0.05/0.1/0.2 ATR clear of the EMA) | 2,520 | 826 | 39 | **0** | -0.117 | M30 close c4 4R A+B+ (0.1): +0.078 (t 1.0) -> -0.081 |

- Before costs the pattern is about zero on M5-H1 in every version; costs (0.06-0.16R a trade) make it lose (P1).
- The full engulfing does not select better trades: engulfing minus non-engulfing four-flips, median over all settings,
  v2 -0.002R / -0.013R, v3 -0.004R / -0.017R (2011-19 / 2020-22).
- Stricter "obvious" breaks lose a little less (M5 median -0.147 -> -0.105R from 0.05 to 0.2 ATR) but leave too few trades
  (0.2 ATR: about 135 M5 trades in 9 years over 12 markets; H4 about 3).
- Trailing stops and the EMA exit did not beat fixed targets (medians: 2x ATR trail -0.077R, best of the exits; 1R -0.112R).
- Where/when (learn 2011-19, check 2020-22): 0 of 180 cells in v2, v3 and v4.
- The top of the raw cycle league (edge quality 0.24-0.27) is settings with 2-40 trades in 9 years: noise, not an edge.
Reports: `research/results/truth/ema4_flip_v{2,3,4}/`, `research/results/ema4/WHERE_WHEN_v{2,3,4}.md`, `PROFILE_v{2,3}.md`.
