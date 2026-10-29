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
