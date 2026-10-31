# Dark Mimas (Marco Solito) — what it is and whether it helps the goal

**Verdict: rejected.** On EURUSD and GBPUSD 2011–2025, every version of both settings files loses money:
108 of 108 configurations at realistic Exness Zero costs, with or without swaps. The classic setup loses even before
costs. The grid setup closes 96–98% of its baskets in profit and still loses.

## What the owner sent
- `Dark_Mimas_User_Manual.pdf` (11 pages) and four `.set` files (MT4 and MT5 copies of two settings):
  - **Classic Mode No Grid**: buy at the Dark Oscillator's green arrow and sell at its red arrow, close on the opposite
    signal, no stop loss, 0.01 lot. This is always in the market and flips at every arrow.
  - **"Not Open Orders" set**: the same entry plus an averaging grid: 0.01 lot every 5 pips against the last order
    (at a new bar's open), up to 50 orders per side, buy and sell baskets at once. Each basket closes at 5 pips from
    its average (profit) or 50 pips from its average (loss). No spread filter (MaxSpread 2000).
- The EA and its Dark Oscillator are compiled. The oscillator's formula is not published: the product page says only
  that it is "based on Counter Trend strategy" and "does Not repaint". So the replay tests the family the settings
  describe, using three reconstructions of a smooth oscillator that colours by slope (declared in
  `dark_mimas_sim.py` before any run).

## The vendor (public facts, 2026-10-31)
| | |
|---|---|
| Seller | Marco Solito (`msolito59`), 36 MQL5 products; Dark Mimas, Dark Venus, Dark Moon and others are free; Dark Algo $399, Dark Nova $499 |
| Dark Mimas page | "Scalping"; "a very high-rate of winning trades"; "Optimization experience is required"; "My tests are indicative"; no backtest report, no live signal; version 1.20, last updated June 2021 |
| Manual | strongly recommends an "ECN broker" and a VPS, with affiliate links to IC Markets, RoboForex and a VPS seller |
| Live signals | two, both MT4, both started 2025-05-30 with a $100 deposit, 1:500 leverage |

| Signal | Shown growth | Money deposited | Balance | Max drawdown on balance | Max drawdown on equity | Pairs |
|---|---|---|---|---|---|---|
| Dark Nova 3 Pairs | +1,166% | $1,950 | $3.6k | 8.4% | **51%** | AUDCAD, NZDCAD, AUDNZD |
| Dark Algo | +676% | $2,200 | $3.5k (equity $2.56k, so about $900 of losses still open) | 25% | **53%** | EURUSD |

How to read this:
- **Growth figures:** MQL5's growth % is time-weighted. Starting with $100 and topping up later makes it look huge.
  In money terms, Dark Algo has made about $1,250 realised on $2,200 deposited, and much less on equity.
- **Drawdown:** a drawdown on equity much larger than on balance means losing positions are held open, which is the
  grid/averaging signature (P15).
- **Pairs:** AUDCAD, NZDCAD and AUDNZD are the classic range-bound grid pairs.

Neither signal is labelled as Dark Mimas, and neither is old enough (about 2 years) to have met a strong trend year.

## Replay (EURUSD, GBPUSD M1 2011–2025; M5, M15, H1; oscillator versions R1–R3)
Costs: lab standard (1.5 and 1.8 pips), Exness Zero realistic (1.0 pip: measured Zero spread + $7/lot commission +
0.2 pip slippage) with swaps or swap-free, and a no-cost diagnostic.

**Classic, no grid** (18 configurations per cost profile)
| Profile | Pips per trade | Trades a year | Winners | Profit factor | 2011–25 per 0.01 lot | Profitable configs |
|---|---|---|---|---|---|---|
| No costs (diagnostic) | −0.17 to −0.65 | 700–11,800 | 22–34% | 0.87–0.98 | −$300 to −$6,200 | 0 of 18 |
| Exness Zero, swap-free | −1.17 to −1.65 | | | 0.64–0.91 | −$1,400 to −$23,300 | 0 of 18 |
| Exness Zero + swaps | −1.18 to −1.92 | | | 0.63–0.90 | −$1,700 to −$23,600 | 0 of 18 |

The signal loses before costs. Turns of a smoothed oscillator on these pairs arrive after the move, and the system
then pays costs thousands of times a year.

**Grid ("Not Open Orders" set)** (18 configurations per profile)
| Profile | Baskets won | 2011–25 per 0.01 lot | Worst equity drawdown | Losing years (of 15) | Profitable configs |
|---|---|---|---|---|---|
| No costs (diagnostic) | 96–98% | −$600 to +$5,000 | $430–$1,470 | 3–10 | 12 of 18 |
| Exness Zero, swap-free | 96–98% | −$1,600 to −$11,200 | $1,600–$11,600 | 11–15 | 0 of 18 |
| Exness Zero + swaps | 96–98% | −$1,900 to −$12,800 | $1,900–$13,100 | 11–15 | 0 of 18 |

The grid earns about $0.70–$1.00 per winning basket and loses $17–$47 per stopped basket. Before costs that roughly
breaks even. Each extra order pays costs, and the costs make it a steady loser.

Configurations tried: 3 oscillators × 3 timeframes × 2 markets × 2 settings × 4 cost profiles = 144 runs
(108 tradable). No parameter was tuned. The vendor says users must optimise their own settings; optimising until
something looks good is exactly the hindsight the project forbids (P10).

## What we learn
1. **A 96–98% basket win rate with a net loss** is the same shape as Gold Hunter (P15) and the EUR reversal (P16).
2. **Free EA, affiliate broker links, a paid VIP product.** The business model pays the vendor whether or not the
   EA makes money. Judge only by long, equity-based, independent records.
3. **Their best evidence (the two signals) shows 51–53% equity drawdowns in under two years**, with losses held open.
   That is far outside the project's risk limits.
4. Nothing here adds an edge. The useful lessons are the method: reconstruct, replay, and judge by equity.

Evidence: `research/gridbot/dark_mimas_sim.py`, `research/results/gridbot/dark_mimas.json`.
Sources: mql5.com product 66348 (Dark Mimas MT5), product 64140 (Dark Oscillator MT5), seller page msolito59,
signals 2312398 and 2312403 (read 2026-10-31).
