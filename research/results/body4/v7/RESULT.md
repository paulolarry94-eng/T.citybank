# Body-engulf range v7: the curated version, and how realistic the costs are (2026-11-09)

**Verdict: rejected, and costs are not the reason.** Our RoboForex Prime cost model matches the figures you sent (EURUSD
spread 0.1 + commission 0.25 pip), and on these setups it costs only about 0.1R a trade. The curated version (the 2 lookback
candles also at least 60% body, M5/M15, 13:00-17:00 UTC, 10 Prime markets, 3R-6R) trades only about 9 times a year across
all 10 markets, and what it does trade does not hold up: the best setting made +0.23R a trade on 86 trades in 2011-19,
then -0.57R on 28 trades in 2020-22, and it still lost in 2020-22 at zero cost (-0.41R).

- Pre-registered before any v7 result: `research/body4/PREREGISTRATION_V7.md` (commit 7cea2ab).
- Truth Lab: `research/results/truth/body4_range_v7/REPORT.md`: 0 of 16 configurations pass; 25% positive in 2011-19, 0% in
  both 2011-19 and 2020-22; median -0.121R a trade.
- Study: `research/body4/study_v7.py` -> `study_v7.json`. Examples: `examples/` (`research/body4/examples_v7.py`).

## 1. How realistic is the cost?
| | The figures you sent | Our RoboForex Prime model |
|---|---|---|
| EURUSD spread | 0.1-0.2 pip | 0.1 pip (Prime published average) |
| Commission | $2 a lot round trip = 0.2 pip | $10 per $1 million each side = 0.25 pip round trip |
| Slippage | not counted | 0.2 pip, only when a stop or the 20:30 close fills (a stop becomes a market order) |
| Swaps | 0 (flat intraday) | 0 (flat at 20:30 UTC) |
| Total | 0.3-0.4 pip | 0.35 pip on a target exit, 0.55 pip on a stop exit |

What matters is the cost against the stop. Median stop of these setups: EURUSD M5 5.1 pips (6.3 in 13-17 UTC), M15 9.4
pips; so EURUSD costs 0.06-0.11R a trade. Other markets cost more: EURGBP 0.13-0.21R, US500 0.16-0.21R, WTI 0.16-0.28R,
JP225 0.30-0.39R.

The arithmetic in the plan you sent charges the cost only on winning trades. Losing trades pay it too:
| 4-pip stop, 12-pip target (3R) | Win | Loss | Wins needed to break even |
|---|---|---|---|
| No costs | +3.00R | -1.00R | 25.0% |
| Their figures (0.3 pip) | +2.92R | -1.07R | 26.9% (they wrote "1:2.93"; the real payoff is 1:2.72) |
| Our Prime model (0.35 pip, 0.55 on stops) | +2.91R | -1.14R | 28.1% |
| Pro account (1.3 pip spread) | +2.67R | -1.32R | 33.1% (they wrote "1:2.26"; the real payoff is 1:2.02) |

So the Prime account is the right choice for this kind of trading, and our model already uses Prime's prices.

## 2. The curated version (R per trade; Prime costs / without slippage / zero cost)
| Setting | 2011-19 | 2020-22 | 2023-25 |
|---|---|---|---|
| Lookback candles 60% body, 3R | 82 trades, +0.09 / +0.13 / +0.23R | 26, -0.30 / -0.26 / -0.14R | 20, -0.07 / -0.04 / +0.05R |
| Lookback candles 60% body, 4R | 85, +0.15 / +0.19 / +0.29R | 27, -0.41 / -0.36 / -0.25R | 21, +0.14 / +0.18 / +0.26R |
| **Lookback candles 60% body, 5R (primary)** | 86, +0.23 / +0.27 / +0.37R (t 0.9) | 28, -0.57 / -0.53 / -0.41R (t -2.3) | 22, +0.18 / +0.21 / +0.30R (t 0.4) |
| Lookback candles 60% body, 6R | 86, +0.18 / +0.23 / +0.33R | 29, -0.55 / -0.51 / -0.40R | 22, +0.27 / +0.30 / +0.39R |
| v6 lookback (direction only), 3R | 644, -0.11 / -0.07 / +0.04R | 215, -0.18 / -0.14 / -0.05R | 192, -0.17 / -0.14 / -0.03R |
| v6 lookback, 4R | 686, -0.10 / -0.05 / +0.06R | 227, -0.25 / -0.21 / -0.11R | 208, -0.11 / -0.07 / +0.04R |
| v6 lookback, 5R | 704, -0.10 / -0.05 / +0.06R | 234, -0.28 / -0.24 / -0.15R | 216, -0.17 / -0.13 / -0.02R |
| v6 lookback, 6R | 710, -0.16 / -0.11 / -0.00R | 239, -0.29 / -0.24 / -0.15R | 219, -0.19 / -0.15 / -0.04R |

- The primary (chosen on 2011-19) fails: 2020-25 pooled -0.24R a trade on 50 trades (t -1.0). The Jan-Oct 2026 check is not
  needed: it cannot change the verdict, so that data stays unseen.
- Without your new lookback-body rule there are 8 times more trades, and they lose in every period after costs and are about
  zero before costs. With it, 2011-19 looks better on 82-86 trades (t below 1), and that did not carry into 2020-22.
- 3R was reached by 25.6% of trades in 2011-19 (82 trades), then 11.5% and 10.0%; 25% is needed at zero cost, about 28%
  after costs.
- EURUSD, the market in the plan you sent: with your full rules 22 trades in 2011-19 at -0.42R a trade (-0.34R at zero
  cost); with the v6 lookback 108 trades at -0.24R (-0.15R at zero cost).

## 3. The two-week view (primary, Prime costs)
| Per two weeks | 2011-19 | 2020-22 | 2023-25 |
|---|---|---|---|
| Trades | 0.37 | 0.36 | 0.28 |
| Fortnights with no trade at all | 70% | 72% | 78% |
| Fortnights with 2 or more wins | 0.4% | 0% | 0% |
| Average R | +0.09R | -0.21R | +0.05R |
| R a year (= % a year at 1% risk) | +2.2 | -5.4 | +1.3 |

With every filter stacked, the system trades about once every 5-6 weeks across all 10 markets, so "2 wins every 2 weeks"
cannot happen, and a handful of trades a year cannot be told apart from luck.

## Where this leaves it
The body-engulf range has now been tested in seven versions plus a gold study (5,342 settings and conditions). The account
and cost choice is right (Prime), and costs on these setups are modest; the pattern itself has no edge before costs in the
periods with enough trades to judge.
