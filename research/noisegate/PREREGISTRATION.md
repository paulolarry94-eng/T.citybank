# Noise gate on the survivors — pre-registration (2026-11-06, written before any result)

Owner: "Do you know about noise gates and how it works? Can you test it".

## What a noise gate is
In audio, a noise gate lets sound through only while it is louder than a threshold. Four settings define it: the
**threshold** (when it opens), **hysteresis** (it closes at a lower level than it opens, so it does not chatter),
**hold** (once open it stays open a minimum time) and attack/release (how fast it opens and closes).
In trading, the "loudness" is how much of recent price movement was a clean move rather than back-and-forth noise.
We use Kaufman's **efficiency ratio**: ER = |close now - close N bars ago| / sum of |bar-to-bar changes| over those N bars.
ER 1 = a straight line, ER near 0 = pure chop.

## Why we test it on the survivors
A gate is a filter. It cannot create an edge where there is none (P8, P21), so it is tested only on the 13 strategies
that already have one (11-leg book, Tokyo fix, EURUSD reversal), every trade at 1R, Exness Zero costs + swaps (the same
profile as the cycle scoreboard; swap-free reported separately). The question for the cycle goal: does it raise the edge
quality s (now 0.06-0.13; +2% per cycle inside 3.6% needs about 0.42)?

## The gate (fixed)
- Bars from M1 bids (closes only). fast: H1 bars, ER over 24 bars. slow: D1 bars (day starts 21:00 UTC), ER over 20 bars.
- Threshold relative to the market's own past year (causal rolling quantile of ER: 6,000 H1 bars / 250 D1 bars).
  Opens when ER >= the theta quantile; closes when ER < the (theta - 0.10) quantile (hysteresis);
  hold: once open, stays open at least 6 H1 bars (fast) / 5 D1 bars (slow). Attack/release = one bar (instant).
- theta in {0.50, 0.67}. A trade uses the gate state of the last bar CLOSED at or before its entry time.
- Markets by leg: EUR_* EURUSD, XAU_* XAUUSD, JPY_* and tokyo_fix USDJPY, GBP_* GBPUSD, GBPJPY = GBPUSD x USDJPY closes,
  EURGBP_* EURGBP, eurusd_* EURUSD.

## Two policies (fixed by leg type before results)
- **textbook**: every leg trades only while the gate is OPEN (clean movement).
- **by-type**: trend/breakout legs (VolBreakout, Donchian, EMA20-50, WeeklySweep_FollowThrough) trade while OPEN;
  reversion legs (S1_reversion, RSI2, Bollinger, close_beyond_reversal) trade while CLOSED (reversion likes noise);
  time/flow legs (EuroHours, tokyo_fix) trade while OPEN (no prior; exploratory).
Grid: 2 horizons x 2 thresholds x 2 policies = **8 configurations**.

## Scoring and decision
- Pool all 13 legs' trades in time order; edge quality s = mean R / sd R; cycle units with research/truth/cyclegoal.py.
- Periods: 2011-19 development, 2020-22 validation. Selection: the highest 2011-19 pooled s among configurations whose s
  beats the ungated pool in BOTH periods (if none, the gate is rejected without a look).
- Control: random gates that keep the same number of trades per leg (2,000 draws): p-value of the s improvement, 2011-19.
  The blocked trades are reported too.
- Then ONE look at 2023-25 for the selected configuration (note: the legs' own 2023-25 trades were seen before; the gate
  rule is new) and the 11 book legs' untouched Jan-Oct 2026 trades.
- Keep the gate only if: s higher than ungated in 2011-19 and 2020-22, random-gate p < 0.05, and 2023-25 gated s >= ungated s.
