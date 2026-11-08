# Body-engulf range v4: what makes the losses, safe windows, 2R-10R, and the RR hit 50% of the time (2026-11-08)

**Verdict: rejected.** 0 of 3,456 settings make money after costs (12 markets pooled, M1-H4, 2011-19). The safe window
cuts the loss but turns nothing positive. No reward:risk of 2 or more is hit anywhere near 50% of the time: hit rates at
2R-10R are what pure chance gives. Half of all trades get only 0.3R-0.9R in profit before being stopped.
Pre-registered: `research/body4/PREREGISTRATION_V4.md`. Lab: `research/results/truth/body4_range_v4/REPORT.md`.
Files: `attribution.json` (losses), `study_v4.json` (3,456 settings), `RR_CURVE.md` / `rr_curve.json` (hit-rate curve).

## 1. What made the losses (v3 main settings, 10R, 121,822 trades 2011-22; `attribution.json`)
Per trade: price move -0.03R (about zero), spread -0.13R, commission -0.11R, slippage -0.11R, swaps -0.01R = -0.39R.
The move has no edge, so costs decide. Gaps through the stop cost 0.05R a trade on average (inside the move).
| Group | Trades | R per trade | Costs (spread + commission + slippage) | Gap loss |
|---|---|---|---|---|
| Asia entries (23:00-07:00 UTC) | 36,512 | -0.43 | 0.40R | 0.14R |
| London (07:00-12:00) | 32,115 | -0.34 | 0.33R | 0.01R |
| London-New York overlap (12:00-16:00) | 28,949 | -0.31 | 0.29R | 0.00R |
| New York (16:00-20:30) | 24,246 | -0.51 | 0.36R | 0.02R |
| US news days (NFP, CPI, FOMC) / other days | 13,626 / 108,196 | -0.39 / -0.39 | same | same |
Costs per trade by timeframe: M1 0.42R, M5 0.26R, M15 0.18R, M30 0.14R, H1 0.11R, H4 0.06R. Most expensive markets:
XAGUSD 0.58R, UK100 0.43R, EURGBP 0.42R, JP225 0.40R, WTI 0.40R; cheapest GER40 0.22R, EURUSD 0.27R.
**The 50 biggest losers:** 46 were a gap through the stop, 27 held overnight, 23 an index market closed overnight (GER40,
UK100: a stop of a few points jumped by the next morning's open; the worst was the Brexit vote, -22.6R), 18 Asian-session
entries, 14 a one-hour hole in the price data, only 4 on US news days.
(Trades that happened to stay open overnight look profitable, +1.8R, only because the losers were stopped the same day:
that cannot be chosen in advance.)

## 2. The safe window (setups 07:00-19:00 UTC, no US news days, everything flat at 20:30 UTC)
Better than "all hours" in 90% of 1,712 paired settings (2011-19, +0.045R a trade) and 90% of 1,438 (2020-22, +0.053R),
but still negative everywhere: median -0.175R vs -0.211R; best (H4, 2R, 50% entry, breakeven, 10% buffer) -0.06R in
2011-19 and -0.22R in 2020-22.

## 3. 2R to 10R
| Target | Best target-hit rate of any setting, 2011-19 (2020-22) | Pure chance 1/(1+RR) | Safe window M15 main settings: hit, R per trade, before costs |
|---|---|---|---|
| 2R | 30% (30%) | 33% | 25%, -0.14R, +0.01R |
| 3R | 22% (23%) | 25% | 17%, -0.14R, +0.02R |
| 4R | 18% (17%) | 20% | 12%, -0.14R, +0.01R |
| 5R | 15% (13%) | 17% | 8%, -0.14R, +0.03R |
| 6R | 13% (11%) | 14% | 6%, -0.13R, +0.04R |
| 7R | 11% (11%) | 13% | 5%, -0.14R, +0.04R |
| 8R | 10% (10%) | 11% | 4%, -0.15R, +0.03R |
| 9R | 8% (8%) | 10% | 3%, -0.14R, +0.03R |
| 10R | 7.5% (7.2%) | 9% | 2%, -0.14R, +0.03R |
The safe window hits less often (the 20:30 UTC close ends trades before they get far) but loses less.
Before costs the only consistent cell is M15 in the safe window (+0.01 to +0.04R in 2011-19, +0.04 to +0.11R in
2020-22, t at most 1.2): too small to pay its 0.18R of costs.

## 4. Which RR is hit 50% of the time (`RR_CURVE.md`)
Half of all trades reach only this much profit before their stop (breakeven off, no target, 2011-19): safe window M1
0.39R, M5 0.71R, M15 0.75R, M30 0.76R, H1 0.62R, H4 0.39R; all hours 0.30-0.81R (2020-22 the same). A target that small
needs about 65-70% wins after costs. No configuration of the 3,456 hits 50% at 2R or more (best 30%).
