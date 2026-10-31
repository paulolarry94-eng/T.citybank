# Liquidity-grab study — results (2026-10-31)

Rules fixed before any result in `PREREGISTRATION.md`. Same data, costs, swaps, fills and tiers as North
Star. 4 markets (XAUUSD, EURUSD, GBPUSD, USDJPY), 2011–2025, 780 configurations per market.

| Concept | Settings | Pass dev gate | Positive in dev | Median dev E | Positive dev AND val at Exness-like costs |
|---|---|---|---|---|---|
| LG1 swing-failure sweep (SFP) of resting swing highs/lows | 384 | 0 | 13% | −0.11R | 17% |
| LG2 sweep of equal-highs / equal-lows pools | 192 | 0 | 17% | −0.12R | 18% |
| LG3 sweep then market-structure shift (ICT) | 192 | 7 | 10% | −0.09R | 23% |
| LG4 New York sweeps the London-morning range | 12 | 0 | 0% | −0.06R | 0% |

Only candidate (LG3, H1, pivot 5, 5-bar window, no target): 2011–19 +0.126R (t 1.7, 651 trades), 2020–22
−0.060R, 2023–25 −0.185R (232 trades, t −1.9; EUR +0.01, gold −0.16, GBP −0.37, JPY −0.22). Its neighbours
are unstable and its deflated Sharpe is 0.000. At Exness-like costs (x0.5, no swap) it is +0.187 /
−0.006 / −0.139. **Rejected.**

Together with the earlier 596 level-sweep variants (Asian range, previous day/week, Turtle Soup,
candle sweeps), about 1,400 liquidity-grab configurations have been tested on these markets. The only
one that has survived is the GBP weekly follow-through, already in the book, and it trades *with*
the move after the grab, not against it.
