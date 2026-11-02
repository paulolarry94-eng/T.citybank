# The owner's 3:30 EMA retest edge — result (2026-11-02)

**Verdict: rejected for 2011–2022.** All 48 configurations lost money after costs in 2011–19 and again in 2020–22, on almost
every market and in every year: −0.16R to −0.22R per trade. Before costs the pattern is about break-even (−0.03R to +0.02R),
so the setup does not pick direction better than chance; the cost of a one-candle stop (about 0.17R a trade) makes it lose.
**2026 is different:** with the owner's own 15:30 (Nigerian time) anchor, Jan–Oct 2026 was positive on both data feeds we
have, but only in US summer time and on few trades, and 2026 is the period the owner built the idea on. It is a lead to
test forward, not an edge.

Rules, code and checks: `research/owner330/PREREGISTRATION.md` (fixed before any result, commits e888de6, e68f660),
`research/truth/strategies/owner330_ema_retest_v1.py`, 13 unit tests, replay of the owner's ten example days (9 of 10 match),
random audit charts (`AUDIT.md`). Costs: RoboForex Prime published averages (spread + commission + slippage); no overnight
trades, so no swaps. US NFP, CPI and FOMC days skipped.

## 1. In cycles (the owner's units): 10 trades = a cycle, 360 trades = a lifecycle
All 12 markets, trades in time order, fills before 2023. Needed for +2% per cycle inside a 3.6% lifecycle drawdown: edge
quality s ≥ 0.42. Full league of all 48 configurations: `research/results/truth/owner330_ema_retest_v1/CYCLES_LEAGUE.md`.

| Configuration | Period | Trades a year | Win rate | R per trade | Edge quality s | Average cycle | Positive cycles | Worst cycle | Lifecycles (360 trades each, about 14–16 months) |
|---|---|---|---|---|---|---|---|---|---|
| Best by s: 15:30 WAT, entry A, 4R | 2011–19 | 274 | 21% | −0.157 | −0.084 | −1.6R | 32% | −10R | −10R, −105R, −116R, −38R, −36R, −64R |
| | 2020–22 | 313 | 21% | −0.143 | −0.082 | −1.4R | 36% | −11R | −60R, −32R |
| 2nd: 9:30 New York, entry A, 4R | 2011–19 | 311 | 21% | −0.170 | −0.097 | −1.7R | 31% | −10R | −62R, −18R, −83R, −119R, −75R, −34R, +2R |
| | 2020–22 | 371 | 20% | −0.166 | −0.094 | −1.7R | 32% | −11R | −78R, −69R, −34R |
| Owner's base: 15:30 WAT, entry A, 3R | 2011–19 | 274 | 23% | −0.183 | −0.114 | −1.8R | 33% | −10R | −43R, −89R, −116R, −62R, −53R, −72R |
| | 2020–22 | 313 | 23% | −0.169 | −0.107 | −1.7R | 39% | −10R | −64R, −55R |

At 1% risk per trade, −1.6R per cycle is −1.6% per cycle; a −60R lifecycle is −60%. No risk level turns a negative edge
into growth: the 3.6% cap only shrinks the loss (risk about 0.03% per trade, −0.04% to −0.05% per cycle). Across all 48
configurations: s from −0.18 to −0.08, positive cycles 22–37%. What the settings changed (2011–19 averages): the plain stop
entry A lost least (−0.175R; pullback entries B3/B6/B12 −0.20 to −0.21R); target 2R/3R/4R and the two anchors made almost no
difference (within 0.01R); breakeven at +1R was worse in 16 of 24 pairs (by 0.004R on average).

## 2. Costs: the pattern has no raw edge
| Configuration (2011–19, 12 markets) | Net R | Before costs | Cost per trade |
|---|---|---|---|
| 9:30 New York, A, 2R | −0.173 | −0.007 | 0.166R |
| 15:30 WAT, A, 4R | −0.157 | +0.017 | 0.174R |
| 9:30 New York, B6, 3R | −0.201 | −0.034 | 0.167R |

The stop is one M5 candle (gold about $1.20 in 2011–19, EURUSD about 5 pips), so a 0.16-dollar or 0.55-pip round trip is
0.10–0.25R. Even at zero cost the best configuration would make +0.02R a trade (edge quality about 0.01): no cost level
reaches the cycle goal.

## 3. By market (all 48 configurations, 2011–19)
| Market | Median R per trade | Configurations positive | Positive in 2011–19 and 2020–22 |
|---|---|---|---|
| EURUSD | −0.040 | 14 of 48 | 14 (all New York anchor; best +0.10R, t 1.1) |
| USDJPY | −0.094 | 2 | 0 |
| GER40 | −0.115 | 8 | 0 |
| XAGUSD | −0.116 | 8 (about 25 trades each) | 0 |
| XAUUSD | −0.163 | 0 | 0 |
| US500 | −0.181 | 0 | 0 |
| WTI | −0.200 | 6 | 4 |
| NAS100 | −0.262 | 0 | 0 |
| GBPUSD | −0.295 | 0 | 0 |
| JP225 | −0.302 | 0 | 0 |
| EURGBP | −0.318 | 0 | 0 |
| UK100 | −0.322 | 0 | 0 |

38 of 576 market-configuration cells were positive in 2011–19 and 18 of them also in 2020–22, 14 of those EURUSD with the
New York anchor: small (t ≤ 1.1), and it lost in 2026 (−0.18R to −0.56R a trade). Picking it now would be hindsight.

## 4. Control: the same rules two hours later (11:30 New York / 16:30 UTC)
| Period | 3:30 rules (typical) | Control | Difference |
|---|---|---|---|
| 2011–19 | −0.16R to −0.22R | −0.19R to −0.38R | +0.08R on average, t up to 2.9 |
| 2020–22 | −0.14R to −0.23R | −0.13R to −0.33R | about 0 (t −0.7 to +1.3) |

In 2011–19 the 3:30 timing lost less than a quiet later hour (smaller candles there make costs a bigger share), and the gap
disappeared in 2020–22. Owner's rule (t ≥ 3, beats control, replicates): **REJECTED**. `controls.json`.

## 5. 2026 (the owner's period): positive with the 15:30 anchor, only in US summer
Jan–Oct 2026, the five markets with 2026 minute data (XAUUSD, EURUSD, GBPUSD, USDJPY from Exness ticks; EURGBP from
HistData). Not a clean test: the owner learned the pattern on these months.

| | 15:30 WAT anchor (24 configurations) | 9:30 New York anchor (24) |
|---|---|---|
| Exness data | 23 of 24 positive, median +0.17R | 0 of 24 positive, median −0.14R |
| HistData data (second feed, same months) | 24 of 24 positive, median +0.19R | 0 of 24, median −0.26R |

Both feeds agree, so it is not a data artifact (`check_2026.json`, `check_2026_histdata.json`; the HistData 2026 clock was
checked against Exness week by week). Where it came from (`season_split.json`):

| 15:30 WAT anchor, 3R, 5 markets | Season | 2011–2022 | 2026 |
|---|---|---|---|
| Entry A | US winter (15:30 WAT = 9:30 New York) | −0.084R (460 trades) | −0.084R (20) |
| Entry A | US summer (15:30 WAT = 10:30 New York) | −0.272R (1,106, t −6.2) | **+0.229R (73, t 1.1)** |
| Entry B3 | US winter | −0.155R (376) | −0.203R (18) |
| Entry B3 | US summer | −0.269R (887, t −5.5) | **+0.423R (65, t 1.8)** |

- The owner's October charts used the 15:30 WAT candle, which in US summer time is **10:30 New York**, one hour after the
  open; in winter it is the 9:30 open candle.
- All of 2026's profit came from the summer months with the 10:30 New York candle. In 2011–2022 that same timing was the
  worst of all (−0.27R a trade, every year negative). 2026 differs from that history at about t 2.4–3.0, but the anchor time,
  the markets and the rules were all chosen by the owner in 2026, and two of 48 configurations are shown, so selection
  explains part of it.
- 2026 by month (entry A, 3R): 7 of 10 months positive; carried by USDJPY (+0.78R, 18 trades) and gold (+0.34R, 20); EURGBP
  −0.56R (9).
- Even taken at face value, 2026 summer's edge quality (0.13 for entry A, 0.23 for B3) is below the 0.42 the cycle goal
  needs. The whole of 2026 scores +0.16% (entry A, 3R) and +0.49% (B3, 3R) per 10-trade cycle inside a 3.6% drawdown, not +2%.

## 6. What would settle it
1. **Forward test in US summer.** From 1 Nov 2026 to mid-March 2027 the 15:30 WAT candle is the 9:30 New York candle again,
   the timing that lost in 2026 and in history. The 10:30-New-York pattern that worked in 2026 can only be forward-tested from
   mid-March 2027. A paper log from then (scanner rules exactly as coded) gets about 12 trades a month on these five markets
   (about 25 on all twelve). About 40 trades tell "like 2026" (+0.2R) from "like history" (−0.27R); about 200 are needed to
   show the 2026 level is above zero (t ≥ 2).
2. **Or one look at 2023–25** (the holdout, never opened for this strategy): did the 10:30-New-York summer pattern turn
   positive before 2026? Pre-registered in `PREREGISTRATION.md` ("Proposed look"); it can be done once and cannot be undone,
   so it waits for the owner's word.

## Files
`research/results/truth/owner330_ema_retest_v1/` (REPORT.md, CYCLES_LEAGUE.md, cycles_league.json, controls.json, grid),
`research/results/owner330/` (REPLAY.md, AUDIT.md + audit/, CHECK_2026.md, check_2026*.json, season_split.json, charts/).

---

# v2: the owner's correction (pullback touch, stop placement, 1:1) — rejected too (2026-11-02)
After the audit charts the owner corrected one rule (US500 8 Apr 2014: the reference is the cross after a pullback that
touched the range; entry at its high) and asked to find the right stop and test 1:1. Pre-registered before any v2 result
(`research/owner330/PREREGISTRATION_V2.md`, commit ec22950): 16 configurations = anchor (15:30 WAT / 9:30 New York) x stop
(reference candle extreme / pullback extreme) x buffer (0, 0.1, 0.25, 0.5 x ATR14 of M5), target 1R. The corrected US500 day
now enters at the owner's marked high and wins 1:1 (`v2/US500_2014-04-08_v2.png`).

| Stop (15:30 WAT anchor) | 2011-19 win rate | Win rate needed after costs | Net R a trade | Stopped trades that later hit the target | 2020-22 win / net R | 2026 win / net R (5 markets) |
|---|---|---|---|---|---|---|
| Candle extreme, no buffer | 40.4% | 58.7% | −0.189 | 52% | 41.8% / −0.161 | 46.9% / −0.061 |
| Candle + 0.5 ATR | 44.5% | 56.6% | −0.107 | 31% | 43.2% / −0.133 | 45.6% / −0.083 |
| Pullback extreme, no buffer | 42.4% | 57.3% | −0.147 | 39% | 42.0% / −0.158 | 48.1% / −0.043 |
| **Pullback + 0.5 ATR (best)** | **45.8%** | **55.8%** | **−0.078** | 23% | 43.3% / −0.131 | 50.0% / −0.005 |

- 0 of 16 configurations pass the lab's gate; none is positive in 2011-19 (all 16: win rate 40-46% vs 56-59% needed; t −4 to
  −10). The 9:30 New York anchor is the same or worse. Full table: `V2_STUDY.md`; lab: `research/results/truth/owner330_ema_retest_v2/`.
- Wider stops do what the owner expected: fewer trades get wicked out (52% → 23% of stopped trades later reached the
  target) and the cost share falls (0.17R → 0.12R), but the win rate only rises 40% → 46%. Before costs the best is +0.04R a
  trade: even with zero costs, edge quality would be about 0.04 against the 0.42 the cycle goal needs. The best setting is at
  the edge of the grid (0.5 ATR); wider is untested.
- 2026 (the owner's own period) is negative at 1:1 for all 16, on both data feeds (best −0.005R, 50% wins). The 2026 summer
  profit of v1 came from trades running to 3R, not from a high hit rate.
- Control (anchor 2 h later): the 3:30 rules lose less in 2011-19 (t 2.3-5.1) but not in 2020-22 (t −0.3 to 1.6).
- By market (best setting, 2011-19): only GER40 positive (54% wins, +0.10R, 323 trades), 1 of 12: picking it now is hindsight.
- In cycles (best setting): edge quality −0.08, 36% of 10-trade cycles positive, 7 of 8 lifecycles negative.
- 2023-25 not opened (nothing passed the gate).
