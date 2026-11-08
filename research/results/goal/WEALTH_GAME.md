# The Wealth Game at 25% risk a trade (owner, 2026-11-08)

Rules as given: risk 25% of the balance on a 1:4 trade; at 4x the level's start, withdraw half; 12 levels.
Simulated: 100 trades (about a year at 2 a week), 200,000 players per row. Built by research/goal/wealth_game.py.

Arithmetic check: level 1's second target is $400 (200 + 200), not $408; every later number in the plan is 2% too
high (level 12 withdrawal $409,600, not $417,792; all 12 withdrawals $819,000, not $835,380).

## 1. Which win rate the plan needs (no costs)

| Win rate at 1:4 | Edge a trade | Account growth a trade at 25% risk | Best risk (Kelly) |
|---|---|---|---|
| 18.0% | -0.10R | -10.5% | 0.0% |
| 20.0% | +0.00R | -8.7% | 0.0% |
| 25.0% | +0.25R | -4.2% | 6.2% |
| 29.3% | +0.46R | -0.0% | 11.6% |
| 30.0% | +0.50R | +0.7% | 12.5% |
| 40.0% | +1.00R | +11.0% | 25.0% |

Growth turns positive only above a 29.3% win rate; 25% risk is the best size only at 40% (+1R a trade).
As written (no losses), the 12 levels need 24 wins in a row: 1 in 6e16 at 20%, 1 in 17 million at 50%.

## 2. 100 trades at 25% risk, costs 0.0R a trade

| Win rate | Pass level 1 (bank $200) | Reach level 5 | Finish level 12 | Median money after 100 trades | End below $100 | Fall of 50%+ at some point |
|---|---|---|---|---|---|---|
| 18% | 14% | 0.0% | 0.00% | $0.00 | 86% | 100% |
| 20% | 20% | 0.1% | 0.00% | $0.01 | 80% | 100% |
| 25% | 45% | 2.8% | 0.00% | $10.17 | 54% | 100% |
| 30% | 75% | 19.1% | 0.01% | $794.69 | 23% | 100% |
| 40% | 99% | 87.0% | 4.80% | $117,602.35 | 1% | 100% |

## 2. 100 trades at 25% risk, costs 0.2R a trade

| Win rate | Pass level 1 (bank $200) | Reach level 5 | Finish level 12 | Median money after 100 trades | End below $100 | Fall of 50%+ at some point |
|---|---|---|---|---|---|---|
| 18% | 6% | 0.0% | 0.00% | $0.00 | 94% | 100% |
| 20% | 9% | 0.0% | 0.00% | $0.00 | 91% | 100% |
| 25% | 21% | 0.2% | 0.00% | $0.01 | 78% | 100% |
| 30% | 45% | 2.9% | 0.00% | $15.59 | 54% | 100% |
| 40% | 93% | 52.6% | 0.19% | $9,126.15 | 6% | 100% |

## 3. Same edge, smaller risk (win rate 25% at 1:4, costs 0.2R: +0.05R a trade, like our best strategies)

| Risk a trade | Pass level 1 within 100 trades | Median money after 100 trades | End below $100 | Lose 90% |
|---|---|---|---|---|
| 25% | 21.5% | $0.01 | 78% | 77.3% |
| 10% | 22.7% | $21.54 | 71% | 36.4% |
| 5% | 11.3% | $74.69 | 64% | 2.2% |
| 2% | 0.2% | $100.94 | 46% | 0.0% |
| 1% | 0.0% | $102.73 | 46% | 0.0% |

Kelly for this edge (mean / variance of R) is about 1% a trade; 25% is about 23 times that.
