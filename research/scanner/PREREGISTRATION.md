# Daily London scanner — pre-registration

Written and committed BEFORE any scanner result was computed (2026-10-30). Idea (user): every trading
day, scan all markets during the London session, rank every setup found, take only the best one, one
trade at a time across the whole account.

## 1. Data, costs, execution
Same as North Star (`../northstar/PREREGISTRATION.md` §1): Dukascopy M1, XAUUSD / EURUSD / GBPUSD /
USDJPY, all-in costs $0.45 / 1.5 / 1.8 / 1.2 pips, decisions on closed M15 bars, market entry at the next
bar's first minute (longs pay the ask), minute-by-minute stops, same-minute stop+target = stop, gaps fill
at the worse open, trades spanning a data hole discarded. **Intraday only:** every trade is closed at
16:30 London time at the latest, so no financing is paid. Monday–Friday London days.

Reference values at each decision (all from CLOSED bars): A = ATR14 of the last closed D1 bar (broker
day, 22:00 UTC); PDH/PDL = that bar's high/low; T = sign(EMA20 − EMA50) of D1 closes; Asian range =
high/low of M15 bars from 00:00 to 07:00 London. A candidate is dropped if its stop distance at decision
(from the signal close) is < max(0.10 A, 3 x cost) or > 1.0 A.

## 2. Setup families (fixed; no parameter is tuned)
Decision bars close between 08:00 and 15:00 London unless stated. "First" = first occurrence that day.

| Code | Setup | Side | Stop | Target |
|---|---|---|---|---|
| ABO | First close beyond the Asian high/low, 08:00–11:00 (Asian range ≥ 0.1 A) | breakout side | Asian midpoint, at most 0.5 A away | 1.5R |
| AFD | Bar trades beyond the Asian high (low) and closes back inside, 08:00–11:00; first per side | fade | day's extreme so far ± 0.05 A | 1.5R |
| PDB | First close beyond PDH / PDL; first per side | breakout | 0.3 A | 1.5R |
| PDF | Bar trades beyond PDH (PDL) and closes back inside; first per side | fade | day's extreme so far ± 0.05 A | 1.5R |
| TPB | D1 trend T ≠ 0; previous M15 close on the counter side of the M15 EMA20, this close back on the trend side, 09:00–14:00; first per day | with T | lowest low (highest high) of the last 4 bars ∓ 0.05 A | 2R |
| OMO | At 09:00: move since the 08:00 open ≥ 0.25 A | with the move | 0.3 A | 2R |
| EUH | EURUSD only, Tue–Thu, decision at 09:00 (entry 09:00) | short | 0.5 A | none; exit 13:00 London |
| MRX | 12:00–14:00: close ≥ 0.8 A away from the 00:00 London open; first per day | fade | 0.4 A | 1R |

EUH is the known seasonal leg from the earlier book (selected on 2011–2018); results are reported with
and without it.

## 3. Ranking — the "surest" setup, using only the past
Each candidate belongs to a cell. Its score at decision time = shrunk mean R of all EARLIER candidates of
the same cell whose trades had already closed: score = sum R / (n + 30) (shrinks to 0 when the cell has
little history). Cells: **S1** = family x market x side x trend-aligned; **S2** = family x market.
No future information enters a score; the ranker is out-of-sample at every moment.

## 4. Policies (all on the identical candidate pool)
- ALL: every candidate taken independently (the pool's average).
- FIFO: one trade at a time, first candidate wins (random among same-bar candidates).
- RANDOM: one trade at a time, random among candidates at the same decision bar (200 repeats).
- BEST(S, θ, cap): one trade at a time; at each decision bar while flat, take the highest-scoring
  candidate if its score > θ; θ ∈ {0, 0.03, 0.06, 0.10}R; cap ∈ {1 trade per day, unlimited};
  S ∈ {S1, S2}. 16 variants.

## 5. Periods and selection
Scores warm up on 2011–2012. Policies are evaluated from 2013. Development 2013–2019: the BEST variant
with the highest development t (≥ 200 trades) is selected. Validation 2020–2022 and final 2023–2025 are
reported once for that variant (logged). Also reported for every variant, so the spread across variants
is visible.

## 6. Acceptance (same bar as North Star Tier A, adapted)
1. E > 0 in development, validation and 2023–2025, after costs.
2. 2023–2025: PF ≥ 1.10, t ≥ 2.0, ≥ 100 trades.
3. Neighbours: the θ one step either side and the other cap setting also have development E > 0.
4. Cost stress (costs x1.5, +1 minute entry delay) on 2013–2022: E > 0.
5. Selection value: on decision bars with ≥ 2 candidates, the chosen candidate beats the average of the
   others in 2023–2025 (paired), and BEST beats RANDOM's median in 2023–2025.
6. Without EUH the selected variant is still E > 0 in 2023–2025 (the edge is not just one known leg).
Pass all → deployment-ready candidate. Pass 1, 3, 4 with 2023–25 E > 0 and PF ≥ 1.05 → forward-test
candidate. Otherwise rejected.
