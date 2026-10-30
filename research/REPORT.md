# TimelessCity × SEESARE P26 — the honest Pareto (2011–2025)

Generated from the real record: Dukascopy prices 2011–2025 (gold from May 2011; gold
2018-06-19 → 2018-12-31 missing, trades spanning it discarded). Every trade replays the
v2.42 EA rules under the fill law: entry at the next minute's open plus cost (gold $0.45,
EUR 1.5 pip, GBP 1.8 pip, JPY 1.2 pip — measured tick spreads were lower), same-minute
stop+target = loss, gapped stops fill at the worse open. Scripts: `research/`.

## 1. The scanner reproduces the records
| Leg | Records | Rebuild |
|---|---|---|
| S1 gold+EUR M20+M30 | 13/yr, 62%, +0.24R | 12/yr, 60%, +0.20R |
| S2 USDJPY H4 | 24/yr, 45%, +0.28R, OOS +0.36 | 22/yr, 45%, +0.27–0.29R, OOS +0.36–0.41 |
| S3 gold H4 both | .set +0.24R / dossier +0.16R | +0.15–0.18R (dossier right) |
The dossier's "S2 +0.03R → +0.11R" line is wrong; the .set is right.

## 2. Funnel (138 variants: 4 pairs × M15–D1 × long/short/both, both bar clocks)
Gates: in-sample 2011–18 E > +0.15R and Sharpe > 0.37 (benchmark median) · OOS 2019–25
holds ≥ half · t ≥ 1.96 · correlation < 0.20. **Two legs pass:**
| Leg | /yr | Win | avgW/avgL | E | PF | IS → OOS | t |
|---|---|---|---|---|---|---|---|
| S1 reversion gold H1+M30 long | 4.4 | 65% | +1.00/−1.00 | +0.29R | 1.82 | +0.31 → +0.27 | 2.37 |
| S2 trend USDJPY H4 long | 21.9 | 45% | +1.85/−1.00 | +0.27R | 1.49 | +0.16 → +0.41 | 2.66 |
Near-miss used only in C: gold H4 trend long, 3×ATR (15/yr, +0.33R, OOS +0.52, but
in-sample only +0.09 — mostly the 2019–25 gold bull). GBP: nothing passes. EUR S1 fades
OOS (+0.26 → +0.08). Every yen short loses.

## 3. Pareto inside the hard walls (0 breaches in 20,000,000 lifecycles, verified)
| | A Max timelessness | B Balanced | C Max return inside walls |
|---|---|---|---|
| Legs | S1 gold H1+M30 + S2 | same | + gold H4 trend long |
| Risk per trade | S1 0.054% · S2 0.022% | S1 0.109% · S2 0.044% | S1 0.122% · trends 0.049% |
| Envelope (20M worst) | 1.80% | 3.58% | 3.58% |
| Real 2011–25 drawdown | 0.38% | 0.76% | 0.70% |
| **Yearly** | **0.20%** | **0.39%** | **0.68%** |
| Bi-weekly | 0.008% | 0.015% | 0.026% |
| Trades/month | 2.2 | 2.2 | 3.4 |
| 360 trades take | 166 months | 166 months | 105 months |
| Avg heat | 0.03% | 0.05% | 0.06% |
| Integrity | 100% (no closes < 15 min apart) | 100% | 100% |
Sizing: fixed fractional. The brief's hierarchy (3%→0.24%, descent 2/3/4, ascent 1) was
tested in every portfolio and lost: with win rates of 45–65% it drifts to its bottom levels
(0.41%/yr at the same envelope; the 12-level version earned 0%).
Multiplier: the formula gives S1 0.37× the trend legs' risk; a full exemption gives 8.4×;
the measured Kelly ratio is ~2.5×. Data weights (S1 1.0 : trend 0.4) won every comparison —
a *partial* exemption is what 15 years justify.
Harvest: share of a cycle's profit = 0.8 × (1 − envelope used / 3.6%) × (1 − open heat / 8%),
paid only when a 10-trade cycle ends profitable at a new high; the payout lowers the high-water
mark so it never counts as drawdown. Integrity multiplies in but stayed at 100%.

## 4. What 120%/yr actually costs (real record; outside the walls)
| Real-record max drawdown | 3.6% | 10% | 20% | 30% |
|---|---|---|---|---|
| C's legs, yearly | 3.6% | 10.2% | 21.6% | 34.1% |
| 1-in-100 lifecycle drawdown | 6.7% | 18.1% | 34.9% | 50.2% |
**120%/yr is reached only by C's legs at 28% risk per S1 trade, with an 89% drawdown.**
The two funnel-proven legs alone peak at 67%/yr; the original 4-chart book at 76%/yr.

## 5. Why the goal is out of reach
The goal assumes ~240 trades/yr at +0.3–0.5% each. The real edges give 26–41 trades/yr at
+0.27–0.33R. To make 120% from that, every trade must risk ~25%+ of equity. The 3.6% wall
with 0 breaches in 20M lifecycles is a one-in-millions tail standard; it forces risk to
~0.1% per trade.

---

# Payout edition (brief revised: everything in the risk OS may change, 3.6% may be breached, goal = fortnightly payouts)

## New families tried (awesome-systematic-trading families our data can test)
Intraday momentum, short-term reversal, weekly time-series momentum, session seasonality:
104 more variants, **none passes the funnel**. Intraday windows lose in *both* directions after
costs (the spread eats small moves); gold weekly momentum works only in the 2019-25 bull.
The 4-market edge set stays: S1 reversion (gold H1+M30+M20, EUR M20+M30), S2 yen trend, S3
gold trend. Gold S1 with the H1 layer added: 6.8/yr, 62% win, +0.245R, PF 1.65, IS +0.20 ->
OOS +0.28 (the dossier's S1 record, reproduced).

## What made payouts work: trade count + a bank, not a ladder
- The P26 descent ladder is dropped; fixed sizing beat it in every test.
- Every 14 days, profit above the trading base moves to an internal bank; the broker
  withdrawal is a fixed amount taken from the bank. Losses are always repaid by later profit
  before anything is banked, so the trading base is never eaten.
- Weights: every S1 leg 1.0, every trend leg 0.4 (measured Kelly ratio).

## Results (real 2011-2025 record, and 2,000 histories rebuilt from reshuffled quarters)
| Setting | S1 / trend risk | Heat cap | Payout per fortnight | Paid on time: real / typical / worst 1-in-20 | Paid per year | Trading drawdown: real / typical / 1-in-20 / worst |
|---|---|---|---|---|---|---|
| Steady | 3.0% / 1.2% | 8% | 0.50% of base | 95% / 97% / 78% | 12.4-12.7% | 22.8% / 21% / 29% / 45% |
| Balanced | 4.0% / 1.6% | 10% | 0.75% of base | 94% / 95% / 71% | 18.3-18.6% | 29.3% / 27% / 37% / 56% |
| Max | 5.0% / 2.0% | 10% | 1.00% of base | 92% / 93% / 66% | 24.0-24.4% | 35.3% / 33% / 44% / 65% |
In no history did trading capital fall below half. The heat wall must be 10% for Max (at 8%
it refuses 70 trades and on-time payouts fall to 79%). A drawdown throttle cut drawdown but
missed more payouts, so it is off.

Presets: `mt5/payout_presets/{Steady,Balanced,Max}/` (4 charts, one terminal). The EA's built-in
harvest is a suggestion only; the 14-day bank/withdraw rule above is the payout schedule.

## Still true
120%/yr is not available from these edges at any survivable drawdown. The way to raise the
fortnightly payout at the same drawdown is more uncorrelated legs: the trend engine on more
markets (silver 2019-25, oil, US/EU indices, more FX), each through the same funnel.

---

# Timeless four-market book (brief: risk OS removed; known strategies, all timeframes, all four markets; horizon = timelessness)

## Search
Published / widely used families on M15, M30, H1, H4, D1 for gold, EUR/USD, GBP/USD, USD/JPY:
Donchian/Turtle breakouts, EMA crossovers, RSI(2) (Connors), Bollinger reversion, IBS reversion,
Larry Williams volatility breakout, opening-range breakout, multi-timeframe trend; plus the
existing S1/S2/S3. 356 variants + the earlier legs. New gate - TIMELESS: positive in each era
(2011-15, 2016-18, 2019-25) - on top of in-sample, out-of-sample, t-stat and neighbour checks.
- Only H4/D1 trend, daily volatility breakout and a few reversion legs survive; M15/M30
  everything loses to the spread; EUR/USD and GBP/USD contribute nothing timeless.

## The book (7 strategies, 242 trades/yr = 9.3 per fortnight)
| Strategy | Market / TF | /yr | E | eras 11-15 / 16-18 / 19-25 | Weight |
|---|---|---|---|---|---|
| S2 Donchian 20, 2xATR, 1.5R chandelier, long | USDJPY H4 | 21.9 | +0.27R | +0.16 / +0.16 / +0.41 | 0.20 |
| S1 Impulse4 reversion, 1:1 | XAUUSD H1+M30+M20 | 7.0 | +0.25R | +0.13 / +0.39 / +0.28 | 0.74 |
| Donchian 20, Turtle exit (10-bar opposite break) | XAUUSD H4 | 46.0 | +0.16R | +0.13 / +0.23 / +0.16 | 0.16 |
| Williams volatility breakout k=0.7 | USDJPY D1 | 134.6 | +0.06R | +0.08 / +0.04 / +0.05 | 0.13 |
| Donchian 55, 2xATR, 1.5R chandelier, both | USDJPY D1 | 5.5 | +0.33R | +0.50 / +0.01 / +0.39 | 0.47 |
| RSI(2) < 5 / > 95 with 200-SMA filter | USDJPY D1 | 9.2 | +0.10R | +0.15 / +0.09 / +0.07 | 1.00 |
| EMA 20/50 cross, both | XAUUSD H4 | 17.4 | +0.23R | +0.22 / +0.42 / +0.17 | 0.25 |
Weights = inverse monthly-R volatility on 2011-2018 only (risk balance). Book: monthly Sharpe
1.16 (2011-18: 1.15, 2019-25: 1.19), t 4.50, positive in all eras, 13/15 positive years.

## Risk (fixed fractional; per-trade risk = base x weight)
| Base | Heat cap | CAGR | Real DD | Reshuffled DD typical / 1-in-20 / worst | Payout/fn (on time real/typical/1-in-20) |
|---|---|---|---|---|---|
| 1.5% | 10% | 11.3% | 9.1% | 10 / 14 / 24% | 0.25% (93/98/87%) |
| 2.0% | 10% | 14.1% | 11.7% | 13 / 18 / 31% | 0.30% (93/98/88%) |
| **3.0%** | **20%** | **22.6%** | **17.3%** | **19 / 26 / 43%** | **0.45% (93/98/89%)** |
| 4.0% | 20% | 28.1% | 22.0% | 24 / 34 / 53% | 0.55% (93/99/89%) |
| 5.0% | 20% | 31.5% | 24.6% | 29 / 41 / 61% | 0.65% (93/99/89%) |
Recommended for a timeless horizon: base 3%, heat cap 20%. Payout set at 60% of the expected
fortnightly return; the rest compounds. No reshuffled history halved the capital at any setting.

## To trade it
The v2.42 EA already runs S1 and Donchian-with-chandelier (S2, JPY D1 55). Four modes are new:
Donchian Turtle exit, EMA cross, Williams volatility breakout, RSI(2). One terminal, 7 charts.

---

# Daily liquidity study (Asian range, PDH/PDL, PWH/PWL; sweeps, responses, combinations)

436 variants on all four markets: sweep & reclaim (Asian / previous day / previous week),
failed sweep -> breakout, reaction follow-through, stacked sweeps (Asian + PDH), weekly-range
bias; M5/M15/H1 confirmation; targets 1R/2R/3R/mid/opposite; stops down to 0.08 x ATR;
London-only, NY-only and full-session windows. **None passes; none of the 216 tighter-stop /
session variants is positive in all three eras.** With ZERO costs the core ideas earn
-0.02R to +0.06R per trade: there is essentially no directional information in them on these
markets; real costs make them negative. (Ledger L-004 again: the entry pattern is ~0% of results.)

One survivor: GBP/USD weekly follow-through (sweep of last week's high/low, reclaim, travel to
the opposite weekly level, H1 close beyond it -> continuation, stop at last week's midpoint,
2R target, exit Friday 20:00 UTC): 3.8/yr, +0.22R, eras +0.20 / +0.28 / +0.22, IS +0.225 /
OOS +0.221, t 1.80. Added to the timeless book as its 8th strategy (first GBP leg):
monthly Sharpe 1.16 -> 1.23 (IS 1.27 / OOS 1.21), t 4.50 -> 4.77, positive years 13 -> 14/15.
At base 3% / heat cap 20%: CAGR 21.4%, real DD 17.0%, reshuffled DD typical 16% / 1-in-20 23% /
worst 36%, never halved; 0.45% payout per fortnight on time in 98% of typical histories.

---

# Daily structure, round two ("try again")

New angles, 160 variants on four markets: trend-aligned intraday sweeps (daily EMA20/50
direction only, hold into next day, target the opposite daily pool); daily- and weekly-candle
sweeps (take PDH/PWH, close back inside, multi-day hold) and their failed-sweep continuations;
Turtle Soup Plus One (Raschke); NR4/NR7 breakouts (Crabel).
**None passes; none is even a timeless candidate.** Median E per family: trend-aligned sweeps
-0.08R, candle sweeps -0.03R, Turtle Soup -0.07R, NR4/NR7 -0.03 to -0.05R.
Note: Turtle Soup first looked strong (GBP +0.65R, t 3.0). That came from a look-ahead bug in
my stop (it used the entry day's full low). With the stop fixed to the signal day's low it
falls to +0.32R, t 1.45, negative in 2016-18.

## Where daily/weekly levels DO help: as filters on the book's legs
Every filter below improves BOTH halves (2011-18 and 2019-25) and is positive in all eras:
| Leg | Keep only | Kept | Dropped |
|---|---|---|---|
| S2 yen Donchian H4 long | breakout already beyond last week's high | +0.36R (IS +0.31 / OOS +0.43) | +0.23R (IS +0.05) |
| Gold EMA 20/50 H4 | entry still inside yesterday's range | +0.57R (IS +0.65 / OOS +0.48) | -0.09R |
| Yen volatility breakout D1 | breakout also beyond yesterday's high/low | +0.07R (IS +0.08 / OOS +0.07) | +0.01R |
(Selection caveat: 3 kept out of 10 splits examined.)

## Filtered 8-strategy book (186 trades/yr, 7.2 per fortnight)
Monthly Sharpe 1.32 (IS 1.46, OOS 1.22), t 5.13, eras all positive, 61% positive months,
14/15 positive years. Out-of-sample Sharpe is unchanged (1.21 -> 1.22); the gain is lower
drawdown for the same return.
| Base | Heat cap | CAGR | Real DD | Reshuffled DD typical / 1-in-20 / worst | Payout/fn (on time real/typ/1-in-20) |
|---|---|---|---|---|---|
| 3% | 20% | 22.2% | 15.0% | 14 / 20 / 28% | 0.45% (94/98/90%) |
| 4% | 20% | 30.2% | 19.6% | 19 / 26 / 36% | 0.60% (94/98/90%) |

# ORB 50 — Expansion & Continuation System (full study: `orb/ORB_REPORT.md`)

118,898 configurations of opening-range breakout (pure, H4-EMA trend-filtered, pullback continuation,
failed-breakout reversal, management and filter variants) on gold, EURUSD, GBPUSD and USDJPY at the
Tokyo, London and two New York opens, 5/15/30/60-minute ranges, 1-minute fills, 60/20/20 chronological
split, walk-forward, deflated Sharpe, and one logged final test on 2023-2025.
**No defensible edge.** Plain ORB is +0.01R before costs and about -0.10R after, in every period.
Walk-forward lost in 26 of 27 model-years. The four best configurations (locked before the final years
were read) all lose in 2023-2025 (-0.12 to -0.16R per trade). Not added to the book; no EA built.
Data note found here: the tick-built gold (2011-18) and GBPUSD (2011-17) files have no 00:00-00:59 UTC
data on any day.

# Hunt 2 — expanded book + drawdown brake + fortnightly payouts (full write-up: `hunt/HUNT2_REPORT.md`)

New, uncorrelated leg from a structural flow: EURUSD weakens during European working hours
(short 09:00-13:00 London, Tue-Thu, +0.041R, t 2.95, all eras positive). Two weak cross-pair legs
(GBPJPY H4 Donchian, EURGBP D1 Bollinger). Expanded 11-leg book: monthly Sharpe 1.32 -> 1.52
(2019-25: 1.22 -> 1.35), 15/15 positive years. Risk systems compared at equal drawdown risk:
a linear drawdown brake (risk x 1 at the peak down to x 0.3 at the budget) gives the same or better
median return with much thinner tails; volatility targeting does worse. With a 4% per-trade cap:
Steady 0.75%/fortnight (19%/yr, DD ~15%), Balanced 1.00%/fortnight (26%/yr, DD ~25%, 1-in-20 31%),
Max 1.25%/fortnight (32%/yr, heat cap 30%). Growth mode: 28% / 44% / 50% real CAGR.
Caveat: new legs were selected with 2019-2025 visible; a 0.05R-per-trade edge decay makes
payouts unreliable.
